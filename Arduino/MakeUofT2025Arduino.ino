#include <SPI.h>
#include <Adafruit_GFX.h>
#include <TFT_ILI9163C.h>

// Color definitions
#define BLACK   0x0000
#define BLUE    0x001F
#define RED     0xF800
#define GREEN   0x07E0
#define CYAN    0x07FF
#define MAGENTA 0xF81F
#define YELLOW  0xFFE0  
#define WHITE   0xFFFF

#define __CS 10
#define __DC 9

int heartPin = A0;

TFT_ILI9163C display = TFT_ILI9163C(__CS,8, __DC);

String gptInput = "";
int heartRate = 83;
int tempurature = 25;

bool isRecording = false;

int buttonPin = 2;
int buttonState = HIGH;
int lastButtonState = HIGH;
unsigned long lastDebounceTime = 0;
const unsigned long debounceDelay = 50;
int counter = 0;


void setup(void) {
  display.begin();
  Serial.begin(9600);

  pinMode(buttonPin, INPUT_PULLUP);


  uint16_t time = millis();
  time = millis() - time;

  display.clearScreen();
  display.setCursor(0,0);
  display.print(gptInput);
  delay(1000);

  display.clearScreen();
}

void loop() {
  //heartRate = analogRead(heartPin);
  //Serial.println(heartRate);

  int reading = digitalRead(buttonPin);

  if (reading != lastButtonState) {
    lastDebounceTime = millis();
  }
  if ((millis() - lastDebounceTime) > debounceDelay) {
    if (reading != buttonState) {
      buttonState = reading;
      if (buttonState == HIGH && isRecording == true) {
        Serial.println("stop");
        isRecording = false;
      } else if(buttonState == LOW){
        Serial.println("record");
        isRecording = true;
      }
    }
  }
  lastButtonState = reading;
  if (Serial.available() > 0) {
    gptInput = Serial.readStringUntil('\n');
  }
  if(counter > 10){
    display.clearScreen();
    counter = 0;
  }
  else{
    counter++;
  }
  
  // --- Draw Heart Rate Section ---
  // Draw heart icon above heart rate
  drawHeartIcon(10, 10);
  display.setCursor(10, 40);
  display.setTextColor(RED);
  display.setTextSize(2);
  display.print(heartRate);
  
  // --- Draw Temperature Section ---
  // Draw thermometer icon above temperature
  drawThermometerIcon(70, 10);
  display.setCursor(70, 40);
  display.setTextColor(BLUE);
  display.setTextSize(2);
  display.print(tempurature);
  
  // --- Draw GPT Input Section ---
  // Draw a simple GPT logo above the text
  drawGPTLogo(10, 60);
  display.setCursor(10, 80);
  display.setTextColor(WHITE);
  display.setTextSize(1);
  display.print(gptInput);

  
}


// Draws a simple heart icon using two circles and a triangle
void drawHeartIcon(int x, int y) {
  int r = 5; // radius for the circles
  // Left circle
  display.fillCircle(x + r, y + r, r, RED);
  // Right circle
  display.fillCircle(x + 3*r, y + r, r, RED);
  // Bottom triangle
  display.fillTriangle(x, y + r, x + 4*r, y + r, x + 2*r, y + 4*r, RED);
}

// Draws a simple thermometer icon with a rectangle and a circle at the bottom
void drawThermometerIcon(int x, int y) {
  int w = 8, h = 20;
  // Draw the tube
  display.drawRect(x, y, w, h, BLUE);
  // Draw the bulb at the bottom
  display.fillCircle(x + w/2, y + h, w/2, BLUE);
}

// Draws a simple GPT logo (a filled rectangle with the letters "GPT")
void drawGPTLogo(int x, int y) {
  int logoW = 30, logoH = 15;
  display.fillRect(x, y, logoW, logoH, MAGENTA);
  display.setCursor(x + 2, y + 2);
  display.setTextColor(WHITE);
  display.setTextSize(1);
  display.print("GPT");
}
