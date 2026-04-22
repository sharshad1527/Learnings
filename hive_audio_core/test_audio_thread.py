import sounddevice as sd  # pip install sounddevice
import soundfile as sf    # pip install soundfile
import time

# 1 open the file as a stream (Does Not Load the whole file into memory)
audio_file = sf.SoundFile('test.wav')

# 2. Define the Low Level callback funtion
def audio_callback(outdata, frames, time, status):
    if status:
        print(f"Status Warning: {status}")
    
    # Read exactly 'frames' amount of data from the file
    # sound file automaticly remmebers where it left off reading
    data = audio_file.read(frames, always_2d=True)

    # Calculate how many frames we got
    valid_frames = int(len(data))
    
    # Write the read data into output buffer that goes to the soundcard 
    outdata[:valid_frames] = data

    # if the ended before we could fill the required "frames"
    # we pad the rest of buffer with slience (Zeros) and stop the stream
    if valid_frames < frames:
        outdata[valid_frames:] = 0 
        raise sd.CallbackStop()

# 3. Initialize the output stream 
stream = sd.OutputStream(
    samplerate=audio_file.samplerate,
    channels=audio_file.channels,
    callback=audio_callback
)

# 4. start the stream 
# This kicks off the background C-thread. It is completely non-blocking.
stream.start()
print("Audio is playing in the background...")

# 5. Keep the main Python thread alive so the script doesn't exit immediately.
# In my final app, the PySide6 GUI loop will keep the main thread alive.

try:
    while stream.active:
        time.sleep(0.1) 
except KeyboardInterrupt:
    stream.stop()
    print("\nPlayback stopped manually.")
finally:
    audio_file.close()