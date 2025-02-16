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
AUDIO_FILENAME = "recording.wav"
SAMPLE_RATE = 44100     # Sample rate for recording (adjust as needed)
CHANNELS = 1            # Number of audio channels

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
        line = ""
        while line != "stop":
            if ser.in_waiting:
                line = ser.readline().decode('utf-8').rstrip()
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
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an assistant."},
            {"role": "user", "content": "You are displaying to a small screen so keep the answers to less than 20 words: " + prompt}
        ]
    )
    answer = response["choices"][0]["message"]["content"]
    return answer

def main():
    print("Press the button to record")
    try:
        while True:
            line = ""
            if ser.in_waiting:
                line = ser.readline().decode('utf-8').rstrip()
            # Button is active low (pressed = 0)
            if line == "record":
                print("Button pressed!")

                # Record audio
                record_audio_until_release(AUDIO_FILENAME, SAMPLE_RATE, CHANNELS)

                # Transcribe the recorded audio
                transcript_text = transcribe_audio(AUDIO_FILENAME)

                # Get GPT response
                gpt_response = query_gpt(transcript_text)
                print("\nGPT Response:")
                print(gpt_response)
                ser.write((gpt_response + "\n").encode('utf-8'))
                time.sleep(0.1)  # Short delay to allow processing

                print("Ready for next recording. Press the button again.\n")

            time.sleep(0.1)  # Polling delay

    except KeyboardInterrupt:
        print("Exiting program...")
    finally:
        GPIO.cleanup()

if __name__ == "__main__":
    main()
