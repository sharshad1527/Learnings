import sounddevice as sd
import soundfile as sf

class PlaybackManager:
    def __init__(self, file_path):
        """Initializes the audio engine without starting playback."""
        self.file_path = file_path
        self.audio_file = sf.SoundFile(file_path)

        # State tracking
        self.is_playing = False

        # The Master Clock variables
        self.current_frame = 0
        self.sample_rate = self.audio_file.samplerate

        # Pre-configure the stream, but do NOT start it yet
        self.stream = sd.OutputStream(
            samplerate=self.audio_file.samplerate,
            channels=self.audio_file.channels,
            callback=self._audio_callback
        )

    def _audio_callback(self, outdata, frames, time_info, status):
        """The internal background thread that feeds the soundcard."""
        if status:
            print(f"Audio Status Warning: {status}")

        # Fetch the exact number of frames needed
        data = self.audio_file.read(frames, always_2d=True)
        valid_frames = len(data)
        outdata[:valid_frames] = data

        # the Master Clock
        self.current_frame += valid_frames

        # Handle End of File (EOF)
        if valid_frames < frames:
            outdata[valid_frames:] = 0
            self.is_playing = False
            raise sd.CallbackStop()

    def play(self):
        """Starts or resumes playback."""
        if not self.is_playing:
            self.is_playing = True
            self.stream.start()
            print("Playback started/resumed.")
        
    def pause(self):
        """Pauses playback. The file pointer stays exactly where it is."""
        if self.is_playing:
            self.is_playing = False
            self.stream.stop()
            print("Playback paused.")

    def stop(self):
        """Stops playback and rewinds to the beginning."""
        self.is_playing = False
        self.stream.stop()
        self.audio_file.seek(0) # Rewind the file pointer to frame 0
        print("Playback stopped and rewound.")

    def close(self):
        """Releases resources. Critical to call this when exiting the app!"""
        self.stream.close()
        self.audio_file.close()

        # reset clock
        self.current_frame = 0
        print("Audio resources released.")

    def get_current_audio_time_ms(self):
        """
        The absolute source of truth for playback time.
        Calculates milliseconds based purely on frames processed.
        """
        if self.sample_rate == 0:
            return 0.0
        return (self.current_frame / self.sample_rate) * 1000.0
        
# ==========================================
# Testing the Class
# ==========================================

def playbackTest():
    import time
    manager = PlaybackManager('test.wav')
    
    try:
        manager.play()
        time.sleep(2)  # Listen for 2 seconds
        
        manager.pause()
        time.sleep(1.5) # Silence for 1.5 seconds
        
        manager.play() # Should resume exactly where it left off
        time.sleep(2)
        
        manager.stop() # Should stop and reset
        time.sleep(1)
        
        manager.play() # Should start from the very beginning
        time.sleep(2)
        
    finally:
        manager.close() # Always clean up!

def clockTest():
    import time
    manager = PlaybackManager('test.wav')


    try:
        manager.play()
        
        # Poll the clock for 5 seconds
        for _ in range(50):
            current_time = manager.get_current_audio_time_ms()
            print(f"Master Clock: {current_time:.2f} ms")
            time.sleep(0.1) 
            
        manager.stop()
        
    finally:
        manager.close()

if __name__ == "__main__":
    clockTest()