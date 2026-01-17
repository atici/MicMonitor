import sounddevice as sd
import numpy as np


class AudioNoiseGate:
    def __init__(
        self,
        threshold=-35,
        block_size=64,
        sample_rate=48000,
        attack_time=0.0005,
        release_time=0.02,
        volume_db=0.0,
    ):
        """
        Ultra-low latency audio noise gate.

        Optimized for minimal latency with smooth gating.
        """
        self.threshold = threshold
        self.block_size = block_size
        self.sample_rate = sample_rate
        self.volume_db = np.clip(volume_db, -60.0, 12.0)  # -60dB to +12dB
        self.volume = 10 ** (self.volume_db / 20.0)  # Convert dB to linear gain

        # Pre-compute attack/release coefficients
        self.attack_coef = np.exp(-1.0 / (sample_rate * attack_time))
        self.release_coef = np.exp(-1.0 / (sample_rate * release_time))
        self.current_gain = 1.0

        # Threshold as amplitude (pre-computed)
        self.threshold_amplitude = 10 ** (threshold / 20.0)
        self.inv_ratio = 0.1  # 1/10 ratio

    def audio_callback(self, indata, outdata, frames, time_info, status):
        """Optimized callback - minimal operations."""
        audio = indata[:, 0]

        # Fast RMS calculation
        rms = np.sqrt(np.mean(np.square(audio)))

        # Gate logic
        target_gain = (
            1.0
            if rms > self.threshold_amplitude
            else np.maximum((rms / self.threshold_amplitude) ** self.inv_ratio, 0.01)
        )

        # Smooth envelope
        coef = (
            self.attack_coef if target_gain > self.current_gain else self.release_coef
        )
        self.current_gain += (target_gain - self.current_gain) * (1 - coef)

        # Output
        outdata[:, 0] = audio * self.current_gain * self.volume

    def start(self):
        """Start the audio stream."""
        latency_ms = self.block_size / self.sample_rate * 1000

        print(f"🎙️  MicMonitor - Ultra-Low Latency Audio Gate")
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"Threshold:  {self.threshold} dB")
        print(f"Volume:     {self.volume_db:+.1f} dB ({self.volume * 100:.0f}%)")
        print(f"Latency:    {latency_ms:.2f} ms")
        print(f"Block size: {self.block_size} samples")
        print(f"Sample rate: {self.sample_rate} Hz")
        print(f"\n🎧 Press Ctrl+C to stop\n")

        try:
            with sd.Stream(
                samplerate=self.sample_rate,
                blocksize=self.block_size,
                channels=1,
                dtype="float32",
                latency="low",
                callback=self.audio_callback,
                prime_output_buffers_using_stream_callback=True,
            ):
                import time

                while True:
                    time.sleep(0.1)
        except KeyboardInterrupt:
            print("\n👋 Stopped")
        except Exception as e:
            print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    import sys

    # Presets
    PRESETS = {
        "ultra": {
            "block_size": 32,
            "threshold": -25,
            "desc": "Ultra-low (~0.67ms) - May be unstable",
        },
        "minimum": {
            "block_size": 64,
            "threshold": -25,
            "desc": "Minimum latency (~1.3ms)",
        },
        "balanced": {
            "block_size": 128,
            "threshold": -25,
            "desc": "Balanced (~2.7ms) - Recommended",
        },
        "stable": {"block_size": 256, "threshold": -25, "desc": "Stable (~5.3ms)"},
    }

    # Default values
    profile = "balanced"
    volume_percent = 100  # 100%

    # Parse command line arguments
    if len(sys.argv) > 1:
        # First arg is profile
        profile_arg = sys.argv[1].lower()
        if profile_arg in PRESETS:
            profile = profile_arg
        else:
            print(f"❌ Unknown profile: {profile_arg}")
            print(f"\nAvailable profiles:")
            for name, data in PRESETS.items():
                print(f"  {name:10} - {data['desc']}")
            print(f"\nUsage: python {sys.argv[0]} [profile] [volume]")
            print(f"Example: python {sys.argv[0]} balanced 80    (80% volume)")
            print(f"         python {sys.argv[0]} minimum 50    (50% volume)")
            print(f"         python {sys.argv[0]} minimum 150   (150% volume)")
            sys.exit(1)

    # Second arg is volume percentage (optional)
    if len(sys.argv) > 2:
        try:
            volume_percent = float(sys.argv[2])
            if volume_percent < 1 or volume_percent > 200:
                print(f"❌ Volume must be between 1-200%")
                sys.exit(1)
        except ValueError:
            print(f"❌ Invalid volume: {sys.argv[2]}")
            print(f"Volume must be a number (e.g., 80 for 80%, 150 for 150%)")
            sys.exit(1)

    preset = PRESETS[profile]

    # Convert percentage to dB (logarithmic)
    # 100% = 0 dB, 50% = -6 dB, 200% = +6 dB
    volume_db = 20 * np.log10(volume_percent / 100.0)

    # Show selected settings
    print(f"Profile: {profile.upper()} - {preset['desc']}")
    print(f"Volume:  {volume_percent:.0f}% ({volume_db:+.1f} dB)")
    if len(sys.argv) == 1:
        print(f"\n💡 Tip: Use 'python {sys.argv[0]} <profile> <volume>' to customize")
        print(f"   Example: python {sys.argv[0]} minimum 80  (80% volume)\n")
    else:
        print()

    # Create gate with selected preset
    gate = AudioNoiseGate(
        threshold=preset["threshold"],
        block_size=preset["block_size"],
        sample_rate=48000,
        volume_db=volume_db,
    )

    gate.start()
