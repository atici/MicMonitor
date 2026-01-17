# MicMonitor 🎙️

Ultra-low latency audio noise gate for real-time microphone monitoring with background noise suppression.

## What It Does

MicMonitor plays your microphone audio back to you in real-time with:
- **Noise Gate**: Automatically cuts out sounds below a threshold to eliminate background noise
- **Ultra-Low Latency**: ~1-3ms delay (imperceptible)
- **Volume Control**: Adjust playback volume
- **Smooth Gating**: No clicks or pops

Perfect for monitoring your microphone while gaming, streaming, or recording.

## Installation

```bash
# Clone the repository
git clone https://github.com/atici/MicMonitor.git
cd MicMonitor

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Basic Usage
```bash
# Run with default settings
python micmon.py

# Choose a latency profile
python micmon.py minimum

# Set custom volume
python micmon.py minimum 80
```

### Profiles
- `ultra` - ~0.67ms (may be unstable)
- `minimum` - ~1.3ms (recommended)
- `balanced` - ~2.7ms (default)
- `stable` - ~5.3ms

### Volume
Enter a number from 1-200 (percentage)
- `50` = quieter
- `100` = normal
- `150` = louder

### Examples
```bash
python micmon.py minimum 100    # Low latency, normal volume
python micmon.py balanced 80    # Balanced, quieter
python micmon.py stable 150     # Stable, louder
```

## Configuration

Edit the `PRESETS` dictionary in `micmon.py`:

```python
PRESETS = {
    'minimum': {'block_size': 64, 'threshold': -25, 'desc': 'Minimum latency'},
}
```

- `block_size`: Lower = less latency (32, 64, 128, 256)
- `threshold`: -25 = moderate, -35 = gentle, -15 = aggressive

## Running on Startup (Windows)

Create `start_micmonitor.vbs`:
```vbscript
Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "C:\path\to\python.exe C:\path\to\micmon.py minimum 100", 0, False
```

Place in startup folder: Press `Win + R`, type `shell:startup`, press Enter

## Troubleshooting

- **High latency**: Try `balanced` or `stable` profile
- **Audio glitches**: Use larger block size
- **Too much background noise**: Lower threshold in PRESETS (e.g., -25 to -30)
