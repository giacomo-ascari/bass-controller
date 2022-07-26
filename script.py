# pip install -r requirements.txt
# https://www.chciken.com/digital/signal/processing/2020/05/13/guitar-tuner.html
import sounddevice as sd
import numpy as np
import scipy.fftpack
import os

# General settings
SAMPLE_FREQ = 44100 # sample frequency in Hz
WINDOW_SIZE = 44100 # window size of the DFT in samples
WINDOW_STEP = 21050 # step size of window
WINDOW_T_LEN = WINDOW_SIZE / SAMPLE_FREQ # length of the window in seconds
SAMPLE_T_LENGTH = 1 / SAMPLE_FREQ # length between two samples in seconds
windowSamples = [0 for _ in range(WINDOW_SIZE)]
CONCERT_PITCH = 440
ALL_NOTES = ["A","A#","B","C","C#","D","D#","E","F","F#","G","G#"]
VOLUME_THR = 200

def main():
    # Start the microphone input stream
    try:
        devices = sd.query_devices()
        print(devices)
        deviceInd = int(input("\nChoose input device: "))
        with sd.InputStream(
            device=deviceInd,
            channels=1,
            callback=callback,
            blocksize=WINDOW_STEP,
            samplerate=SAMPLE_FREQ):
            while True:
                pass
    except KeyboardInterrupt as e:
        print("\nClosing...")
    except Exception as e:
        print(str(e))

# This function matches the note to the keystroke
keymap = {
    # first string
    "E1":   "Space",
    "F1":   "A",
    "F#1":  "S",
    "G1":   "D",
    "G1#":  "F",
    # second string
    "A1":   "Ctrl",
    "A#1":  "Q",
    "B1":   "W",
    "C2":   "E",
    "C2#":  "R"
    # third string
}
def eval_note(note, volume):
    if volume < VOLUME_THR:
        for (_note, _key) in keymap:
            pass # release _key
    else:
        for (_note, _key) in keymap:
            if _note != note:
                pass # release _key
        # press note

# This function finds the closest note for a given pitch
# Returns: note (e.g. A4, G#3, ..), pitch of the tone
def find_closest_note(pitch):
  i = int(np.round(np.log2(pitch/CONCERT_PITCH)*12))
  closest_note = ALL_NOTES[i%12] + str(4 + (i + 9) // 12)
  closest_pitch = CONCERT_PITCH*2**(i/12)
  return closest_note, closest_pitch

# The sounddecive callback function
# Provides us with new data once WINDOW_STEP samples have been fetched
def callback(indata, frames, time, status):
  global windowSamples
  if status:
    print(status)
  if any(indata):
    windowSamples = np.concatenate((windowSamples,indata[:, 0])) # append new samples
    windowSamples = windowSamples[len(indata[:, 0]):] # remove old samples
    magnitudeSpec = abs( scipy.fftpack.fft(windowSamples)[:len(windowSamples)//2] )

    for i in range(int(30/(SAMPLE_FREQ/WINDOW_SIZE))):
      magnitudeSpec[i] = 0 #suppress mains hum

    maxInd = np.argmax(magnitudeSpec)
    maxFreq = maxInd * (SAMPLE_FREQ/WINDOW_SIZE)
    closestNote, closestPitch = find_closest_note(maxFreq)

    os.system('cls' if os.name=='nt' else 'clear')
    print(f"Closest note: {closestNote} {maxFreq:.1f}/{closestPitch:.1f} ({magnitudeSpec[maxInd]:.1f})")
  else:
    print('no input')

if __name__ == "__main__":
    main()