# Composer

A tiny web-based composing machine. No install, no build step — open `index.html`
(or visit the GitHub Pages link) and start clicking steps.

## Features

- **Beats** — a 5-track, 16-step drum sequencer (Kick, Snare, Hi-Hat, Clap, Tom).
- **Melody** — a 14-note, 16-step piano roll (two octaves of C major).
- **Two sound sources for drums** — synthesized in real time via the Web Audio
  API, or short procedurally-generated `.wav` samples (see `samples/`).
- **Four synth waveforms** for melody notes — sine, triangle, square, sawtooth.
- **Tempo control** — 60–200 BPM.
- **Save / Load** — patterns persist to `localStorage` in your browser.
- **Record** — captures the live playback and downloads it as a `.webm` audio file.

Everything runs client-side; there's no backend and nothing is uploaded anywhere.

## Running it

Just open [index.html](index.html) in a browser, or serve the folder with any
static file server (needed for the sample `.wav` files to load via `fetch`,
since some browsers block `fetch` on `file://` URLs):

```bash
python -m http.server 8000
# then visit http://localhost:8000
```

## GitHub Pages

This folder is a static site with no dependencies, so it can be served as-is
by GitHub Pages. If Pages is enabled for this repository (Settings → Pages →
Deploy from branch → `main` / root), it will be reachable at:

```
https://<username>.github.io/<repo>/Composer/
```

## Regenerating the drum samples

`samples/generate_samples.py` is the script that produced the bundled `.wav`
files (pure Python standard library, no dependencies). It's kept for
reference — the app itself only ever loads the committed `.wav` files, it
does not run Python.

```bash
cd samples
python generate_samples.py
```
