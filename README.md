# Vocal Formant Wavetable Generator

This Python script extracts formant characteristics from a vocal `.wav` file and generates a wavetable compatible with [Ewan Bristow's FreakyTable](https://ewanbristow.com/freakytable.html) and [Kilohearts Filter Table](https://kilohearts.com/products/filter_table) audio plugins. Using Praat’s Burg method via the `parselmouth` library, it isolates vowel-shaping resonances for a precise, controlled filter profile.

# Functionality
- Analyzes formants in a vocal audio file using Praat’s Burg method.
Burg method references:
[Sound: To Formant (burg)...
](https://www.fon.hum.uva.nl/praat/manual/Sound__To_Formant__burg____.html)
[praat_formant_burg: Formant estimation using the Praat burg algorithm](https://rdrr.io/github/humlab-speech/superassp/man/praat_formant_burg.html)
- Applies a formant envelope to the spectral content of individual audio frames over time to create a wavetable.
- Optimized for clean vocal samples (IE sustained vowels).
- Ensure input .wav sample rate matches the target output (default: 44100 Hz) for accurate formant analysis. Dynamic input file samplerate functionality coming soon.

# Comparison to using a raw vocal sample as a wavetable
Unlike using a raw vocal sample as a wavetable, which includes pitch, noise, and articulation etc... this script isolates and emphasizes vowel-shaping resonances. It suppresses pitch and non-formant overtones, producing a clearer, more controlled filter profile for vowel-like effects.

# Requirements
- Python 3.6+
- Required libraries: `parselmouth`, `numpy`, `soundfile`
```
pip install parselmouth numpy soundfile
```

## Key Parameters

| Parameter          | Effect                                       | Range     |
|--------------------|----------------------------------------------|-----------|
| `--blend`          | Balances formant envelope and original spectrum | 0.0–1.0 |
| `--formant-q`      | Controls width of formant peaks (narrow to wide) | 5–30   |
| `--formant-strength` | Scales magnitude of formant peaks          | 0.1–3.0+  |
| `--contrast-mode`  | Squashes non-formant content for emphasis    | Boolean   |
| `--max-frames`     | Number of wavetable frames                  | Default: 256 |
| `--frame-length`   | Samples per frame                           | Default: 2048 |
| `--spectral-tilt`  | High-frequency roll-off                     | 0.0–1.0   |

# Usage

```
C:\Users\phix\formant_table>python3 formant_table.py --help
usage: formant_table.py [-h] [-o OUTPUT] [--max-frames MAX_FRAMES] [--frame-length FRAME_LENGTH]
                               [--sample-rate SAMPLE_RATE] [--blend BLEND] [--formant-q FORMANT_Q]
                               [--spectral-tilt SPECTRAL_TILT] [--fft-bins FFT_BINS] [--num-formants NUM_FORMANTS]
                               [--formant-strength FORMANT_STRENGTH] [-c]
                               input

Generate formant-isolated wavetable from vocal sample.

positional arguments:
  input                 Input vocal .wav file

options:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        Output wavetable .wav file (default: <inputname>-wt.wav)
  --max-frames MAX_FRAMES
                        Number of frames in wavetable (default: 256)
  --frame-length FRAME_LENGTH
                        Samples per frame (default: 2048)
  --sample-rate SAMPLE_RATE
                        Output sample rate (default: 44100)
  --blend BLEND         Blend original spectrum and formants (0–1, default: 0.7)
  --formant-q FORMANT_Q
                        Formant peak sharpness (default: 12.0)
  --spectral-tilt SPECTRAL_TILT
                        High-frequency tilt (0–1, default: 0.4)
  --fft-bins FFT_BINS   FFT bin resolution (default: 512)
  --num-formants NUM_FORMANTS
                        Number of formants to extract (default: 4)
  --formant-strength FORMANT_STRENGTH
                        Scale magnitude of formant envelope (default: 1.0)
  -c, --contrast-mode   Activate contrast mode to emphasize formants by reducing non-formant frequencies.

C:\Users\phix\formant_table>python3 formant_table.py lets_go.wav --formant-strength 2.0
[!]  'lets_go-wt.wav' exists. Overwrite? [y/N]: y

[OK] Generated wavetable: lets_go-wt.wav
   Frames: 256 | Frame size: 2048 | Sample rate: 44100
   Blend: 0.7 | Formant Q: 12.0 | Spectral tilt: 0.4 | Strength: 2.0
```
