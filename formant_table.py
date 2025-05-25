#!/usr/bin/env python3

import argparse
import os
import numpy as np
import soundfile as sf
import parselmouth  # Praat wrapper

def formant_envelope(formants, freqs, formant_q, spectral_tilt, contrast_mode=False, formant_strength=1.0):
    envelope = np.zeros_like(freqs)
    for f in formants:
        if f is not None and not np.isnan(f) and f > 0:
            envelope += np.exp(-formant_q * ((freqs - f) / f)**2)

    if envelope.max() > 0:
        envelope /= envelope.max()

    envelope *= spectral_tilt ** (freqs / freqs.max())

    if contrast_mode:
        envelope = envelope**2

    envelope *= formant_strength
    return envelope

def detect_voiced_regions(sound, threshold_db=40):
    intensity = sound.to_intensity()
    times = np.linspace(0, sound.duration, int(sound.duration * 1000))
    voiced_times = [t for t in times if intensity.get_value(t) and intensity.get_value(t) > threshold_db]
    return voiced_times

def extract_formant_wavetable(input_wav, output_wav,
                              max_frames=256,
                              frame_length=2048,
                              sample_rate=None,
                              num_formants=4,
                              formant_q=12.0,
                              blend=0.7,
                              spectral_tilt=0.4,
                              contrast_mode=False,
                              formant_strength=1.0,
                              preserve_timing=False):

    sound = parselmouth.Sound(input_wav)
    original_sr = sound.sampling_frequency
    output_sr = sample_rate if sample_rate else original_sr
    print(f"[INFO] Input SR: {original_sr}, Output SR: {output_sr}")

    signal = sound.values[0]
    duration = sound.duration

    formant_analysis = sound.to_formant_burg(
        time_step=0.01,
        max_number_of_formants=num_formants,
        maximum_formant=5500
    )

    if preserve_timing:
        frame_times = detect_voiced_regions(sound)
        print(f"[INFO] Detected {len(frame_times)} voiced frames for timing preservation.")
    else:
        frame_times = [(i / max_frames) * duration for i in range(max_frames)]

    n_fft = frame_length
    wavetable = []

    for t in frame_times:
        frame_start = int(t * original_sr)
        frame_end = frame_start + frame_length

        audio_slice = np.zeros(frame_length)
        available = len(signal) - frame_start
        if available > 0:
            audio_slice[:min(frame_length, available)] = signal[frame_start:frame_start + min(frame_length, available)]

        windowed = audio_slice * np.hanning(frame_length)
        spectrum = np.abs(np.fft.rfft(windowed, n=n_fft))
        freqs = np.linspace(0, original_sr / 2, len(spectrum))

        current_formants = [formant_analysis.get_value_at_time(n, t) for n in range(1, num_formants + 1)]

        if all(f is None or np.isnan(f) or f <= 0 for f in current_formants):
            print(f"[!] Warning: No valid formants at t = {t:.3f}s")

        envelope = formant_envelope(
            current_formants,
            freqs,
            formant_q,
            spectral_tilt,
            contrast_mode,
            formant_strength
        )

        enhanced = (1 - blend) * spectrum + blend * (spectrum * envelope)
        mirrored = np.concatenate([enhanced, enhanced[-2:0:-1]])
        frame_waveform = np.fft.irfft(mirrored)
        frame_waveform = frame_waveform[:frame_length]
        frame_waveform /= np.max(np.abs(frame_waveform)) + 1e-8

        wavetable.append(frame_waveform)

    wavetable_audio = np.concatenate(wavetable).astype(np.float32)

    try:
        sf.write(output_wav, wavetable_audio, int(output_sr))
    except Exception as e:
        print(f"[X] Failed to write file: {e}")
        return

    print(f"\n[OK] Generated wavetable: {output_wav}")
    print(f"   Frames: {len(frame_times)} | Frame size: {frame_length} | Sample rate: {int(output_sr)}")
    print(f"   Blend: {blend} | Q: {formant_q} | Tilt: {spectral_tilt} | Strength: {formant_strength}\n")

def main():
    parser = argparse.ArgumentParser(description="Generate formant-isolated wavetable from a vocal sample.")
    parser.add_argument("input", help="Input vocal .wav file")
    parser.add_argument("-o", "--output", help="Output wavetable .wav (default: <inputname>-wt.wav)")
    parser.add_argument("--max-frames", type=int, default=256, help="Wavetable frames (default: 256)")
    parser.add_argument("--frame-length", type=int, default=2048, help="Samples per frame (default: 2048)")
    parser.add_argument("--sample-rate", type=int, default=None, help="Override output sample rate (default: match input)")
    parser.add_argument("--blend", type=float, default=0.7, help="0 = dry, 1 = full formant shaping (default: 0.7)")
    parser.add_argument("--formant-q", type=float, default=12.0, help="Formant width (Q factor, default: 12.0)")
    parser.add_argument("--spectral-tilt", type=float, default=0.4, help="Exponential high-freq rolloff (default: 0.4)")
    parser.add_argument("--num-formants", type=int, default=4, help="Number of formants to extract (default: 4)")
    parser.add_argument("--formant-strength", type=float, default=1.0, help="Envelope gain (default: 1.0)")
    parser.add_argument("-c", "--contrast-mode", action="store_true", help="Boost formant peaks and suppress other freqs")
    parser.add_argument("--preserve-timing", action="store_true", help="Preserve natural timing by only extracting voiced regions")

    args = parser.parse_args()

    if not os.path.isfile(args.input):
        print(f"[X] File not found: {args.input}")
        return

    output_path = args.output if args.output else os.path.splitext(args.input)[0] + "-wt.wav"

    if os.path.exists(output_path):
        confirm = input(f"[!] '{output_path}' exists. Overwrite? [y/N]: ").strip().lower()
        if confirm != 'y':
            print("[X] Operation canceled.")
            return

    extract_formant_wavetable(
        input_wav=args.input,
        output_wav=output_path,
        max_frames=args.max_frames,
        frame_length=args.frame_length,
        sample_rate=args.sample_rate,
        num_formants=args.num_formants,
        formant_q=args.formant_q,
        blend=args.blend,
        spectral_tilt=args.spectral_tilt,
        contrast_mode=args.contrast_mode,
        formant_strength=args.formant_strength,
        preserve_timing=args.preserve_timing
    )

if __name__ == "__main__":
    main()
