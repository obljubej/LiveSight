# importing os module for environment variables
import os
# importing necessary functions from dotenv library
from dotenv import load_dotenv, dotenv_values 
# loading variables from .env file
load_dotenv() 

import RPi.GPIO as GPIO
import time
import sounddevice as sd
import soundfile as sf
import numpy as np
import openai

import serial
import time

# Open the serial port. Adjust '/dev/ttyACM0' if needed.
ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
time.sleep(2)  # Give time for the connection to be established

openai.api_key = os.getenv("OPEN_AI_API_KEY")

# -----------------------
# Configuration Variables
# -----------------------
BUTTON_PIN = 18         # GPIO pin connected to the button
RECORD_SECONDS = 5      # Duration of the recording in seconds
AUDIO_FILENAME = "recording.wav"
SAMPLE_RATE = 44100     # Sample rate for recording (adjust as needed)
CHANNELS = 1            # Number of audio channels

# Set your OpenAI API key

# -----------------------
# Setup GPIO
# -----------------------
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Use internal pull-up resistor

def record_audio_until_release(filename, fs, channels):
    print("Recording started. Hold the button until finished...")

    # This list will hold chunks of recorded audio data.
    recorded_chunks = []

    # Callback function to capture audio chunks.
    def callback(indata, frames, time_info, status):
        if status:
            print(status)
        recorded_chunks.append(indata.copy())

    # Open an InputStream with the callback.
    with sd.InputStream(samplerate=fs, channels=channels, callback=callback):
        # Keep recording while the button remains pressed.
        while GPIO.input(BUTTON_PIN) == GPIO.LOW:
            time.sleep(0.1)  # Polling delay

    # Concatenate all chunks into one numpy array.
    audio_data = np.concatenate(recorded_chunks, axis=0)
    sf.write(filename, audio_data, fs)
    print("Recording finished and saved as", filename)

def transcribe_audio(filename):
    print("Transcribing audio with Whisper...")
    with open(filename, "rb") as audio_file:
        transcript = openai.Audio.transcribe("whisper-1", audio_file)
    text = transcript["text"]
    print("Transcription:", text)
    return text

def query_gpt(prompt):
    print("Sending prompt to GPT...")
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an assistant."},
            {"role": "user", "content": "You are displaying to a small screen so keep the answers to less than 30 words: " + prompt}
        ]
    )
    answer = response["choices"][0]["message"]["content"]
    return answer

def main():
    # try:
    #     while True:
    #         # Get input from the user
    #         message = input("Enter a message to send to Arduino: ")
    #         # Send the message with a newline character
    #         ser.write((message + "\n").encode('utf-8'))
    #         time.sleep(0.1)  # Short delay to allow processing
    #         if ser.in_waiting:
    #             line = ser.readline().decode('utf-8').rstrip()  # Read a line and decode to UTF-8
    #             print("Received:", line)
    # except KeyboardInterrupt:
    #     print("Exiting program")
    # finally:
    #     ser.close()
    print("Press the button to record")
    try:
        while True:
            # Button is active low (pressed = 0)
            if GPIO.input(BUTTON_PIN) == GPIO.LOW:
                # Debounce: wait a short period and check again
                time.sleep(0.05)
                if GPIO.input(BUTTON_PIN) == GPIO.LOW:
                    print("Button pressed!")

                    # Record audio
                    record_audio_until_release(AUDIO_FILENAME, SAMPLE_RATE, CHANNELS)

                    # Transcribe the recorded audio
                    transcript_text = transcribe_audio(AUDIO_FILENAME)

                    # Get GPT response
                    gpt_response = query_gpt(transcript_text)
                    print("\nGPT Response:")
                    print(gpt_response)

                    # Wait until the button is released to avoid multiple triggers
                    while GPIO.input(BUTTON_PIN) == GPIO.LOW:
                        time.sleep(0.1)
                    print("Ready for next recording. Press the button again.\n")

            time.sleep(0.1)  # Polling delay

    except KeyboardInterrupt:
        print("Exiting program...")
    finally:
        GPIO.cleanup()

if __name__ == "__main__":
    main()