#!/usr/bin/env python3
"""
Generates the short one-shot drum samples used by Composer's sample-based
sound source. Pure standard library (wave + math + random) - no numpy.
Run once with `python generate_samples.py`; committed .wav files are the
output, this script is kept for reference/regeneration only.
"""

import wave
import math
import random
import struct
import os

SAMPLE_RATE = 44100


def envelope(i, n, attack, decay_pow=2.0):
    t = i / n
    if t < attack:
        return t / attack
    release = (t - attack) / (1 - attack)
    return max(0.0, (1 - release) ** decay_pow)


def write_wav(name, samples):
    path = os.path.join(os.path.dirname(__file__), name)
    with wave.open(path, "w") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(SAMPLE_RATE)
        frames = b"".join(
            struct.pack("<h", max(-32767, min(32767, int(s * 32767))))
            for s in samples
        )
        f.writeframes(frames)
    print(f"wrote {path} ({len(samples)} samples, {len(samples)/SAMPLE_RATE:.3f}s)")


def kick(duration=0.35):
    n = int(SAMPLE_RATE * duration)
    out = []
    for i in range(n):
        t = i / SAMPLE_RATE
        freq = 150 * math.exp(-t * 18) + 40
        phase = 2 * math.pi * freq * t
        s = math.sin(phase) * envelope(i, n, attack=0.01, decay_pow=2.2)
        out.append(s * 0.95)
    return out


def snare(duration=0.2):
    n = int(SAMPLE_RATE * duration)
    out = []
    random.seed(2)
    for i in range(n):
        t = i / SAMPLE_RATE
        tone = math.sin(2 * math.pi * 180 * t) * 0.35
        noise = (random.random() * 2 - 1) * 0.9
        env = envelope(i, n, attack=0.005, decay_pow=3.0)
        out.append((tone + noise) * env * 0.9)
    return out


def hihat(duration=0.09):
    n = int(SAMPLE_RATE * duration)
    out = []
    random.seed(3)
    prev = 0.0
    for i in range(n):
        noise = random.random() * 2 - 1
        # crude high-pass: subtract a lagged copy to kill low end
        hp = noise - prev
        prev = noise
        env = envelope(i, n, attack=0.002, decay_pow=4.0)
        out.append(hp * env * 0.6)
    return out


def clap(duration=0.25):
    n = int(SAMPLE_RATE * duration)
    out = []
    random.seed(4)
    bursts = [0.0, 0.02, 0.035, 0.05]
    for i in range(n):
        t = i / SAMPLE_RATE
        noise = random.random() * 2 - 1
        env = 0.0
        for b in bursts:
            if t >= b:
                local = envelope(i - int(b * SAMPLE_RATE), n, attack=0.002, decay_pow=5.0)
                env = max(env, local)
        out.append(noise * env * 0.8)
    return out


def tom(duration=0.3):
    n = int(SAMPLE_RATE * duration)
    out = []
    for i in range(n):
        t = i / SAMPLE_RATE
        freq = 220 * math.exp(-t * 10) + 90
        phase = 2 * math.pi * freq * t
        s = math.sin(phase) * envelope(i, n, attack=0.01, decay_pow=2.0)
        out.append(s * 0.9)
    return out


if __name__ == "__main__":
    write_wav("kick.wav", kick())
    write_wav("snare.wav", snare())
    write_wav("hihat.wav", hihat())
    write_wav("clap.wav", clap())
    write_wav("tom.wav", tom())
