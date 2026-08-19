(() => {
    "use strict";

    const BEAT_STEPS = 16;
    const STORAGE_KEY = "composer_pattern_v1";

    const BEAT_ROWS = [
        { id: "kick", label: "Kick" },
        { id: "snare", label: "Snare" },
        { id: "hihat", label: "Hi-Hat" },
        { id: "clap", label: "Clap" },
        { id: "tom", label: "Tom" },
    ];

    // High to low, two-octave C major scale.
    const MELODY_ROWS = [
        "C5", "B4", "A4", "G4", "F4", "E4", "D4",
        "C4", "B3", "A3", "G3", "F3", "E3", "D3",
    ];

    const SAMPLE_FILES = {
        kick: "samples/kick.wav",
        snare: "samples/snare.wav",
        hihat: "samples/hihat.wav",
        clap: "samples/clap.wav",
        tom: "samples/tom.wav",
    };

    // General MIDI drum map (channel 10).
    const DRUM_MIDI_NOTES = { kick: 36, snare: 38, hihat: 42, clap: 39, tom: 45 };

    const state = {
        beatPattern: Object.fromEntries(BEAT_ROWS.map((r) => [r.id, Array(BEAT_STEPS).fill(false)])),
        melodyPattern: Object.fromEntries(MELODY_ROWS.map((n) => [n, Array(BEAT_STEPS).fill(false)])),
        melodySteps: BEAT_STEPS,
        bpm: 120,
        drumSource: "sample",
        waveform: "triangle",
        playing: false,
        advanced: false,
    };

    let audioCtx = null;
    let masterGain = null;
    let recordDestination = null;
    let mediaRecorder = null;
    let recordedChunks = [];
    let noiseBuffer = null;
    const sampleBuffers = {};
    let midiAccess = null;

    let currentStep = 0;
    let nextNoteTime = 0;
    let timerID = null;
    const scheduledSteps = [];
    let rafID = null;

    const LOOKAHEAD_MS = 25;
    const SCHEDULE_AHEAD_SEC = 0.1;

    function ensureAudio() {
        if (audioCtx) return;
        audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        masterGain = audioCtx.createGain();
        masterGain.gain.value = 0.9;
        masterGain.connect(audioCtx.destination);

        recordDestination = audioCtx.createMediaStreamDestination();
        masterGain.connect(recordDestination);

        noiseBuffer = createNoiseBuffer();
        loadSamples();
    }

    function createNoiseBuffer() {
        const buffer = audioCtx.createBuffer(1, audioCtx.sampleRate * 1, audioCtx.sampleRate);
        const data = buffer.getChannelData(0);
        for (let i = 0; i < data.length; i++) data[i] = Math.random() * 2 - 1;
        return buffer;
    }

    async function loadSamples() {
        for (const [name, url] of Object.entries(SAMPLE_FILES)) {
            try {
                const res = await fetch(url);
                const arrayBuffer = await res.arrayBuffer();
                sampleBuffers[name] = await audioCtx.decodeAudioData(arrayBuffer);
            } catch (err) {
                console.warn(`Could not load sample "${name}":`, err);
            }
        }
    }

    // ---- Sound sources ----

    function noteNameToMidi(note) {
        const NOTE_INDEX = { C: 0, D: 2, E: 4, F: 5, G: 7, A: 9, B: 11 };
        const letter = note[0];
        const octave = parseInt(note.slice(1), 10);
        return NOTE_INDEX[letter] + (octave + 1) * 12;
    }

    function midiToFreq(midiNote) {
        return 440 * Math.pow(2, (midiNote - 69) / 12);
    }

    function noteToFreq(note) {
        return midiToFreq(noteNameToMidi(note));
    }

    function envGain(time, peak, attack, decay) {
        const gain = audioCtx.createGain();
        gain.gain.setValueAtTime(0, time);
        gain.gain.linearRampToValueAtTime(peak, time + attack);
        gain.gain.exponentialRampToValueAtTime(0.001, time + attack + decay);
        return gain;
    }

    function playBuffer(buffer, time, gainValue = 1) {
        const src = audioCtx.createBufferSource();
        src.buffer = buffer;
        const gain = audioCtx.createGain();
        gain.gain.value = gainValue;
        src.connect(gain);
        gain.connect(masterGain);
        src.start(time);
    }

    function synthKick(time) {
        const osc = audioCtx.createOscillator();
        osc.type = "sine";
        osc.frequency.setValueAtTime(150, time);
        osc.frequency.exponentialRampToValueAtTime(40, time + 0.15);
        const gain = envGain(time, 1, 0.005, 0.3);
        osc.connect(gain);
        gain.connect(masterGain);
        osc.start(time);
        osc.stop(time + 0.35);
    }

    function synthTom(time) {
        const osc = audioCtx.createOscillator();
        osc.type = "sine";
        osc.frequency.setValueAtTime(220, time);
        osc.frequency.exponentialRampToValueAtTime(90, time + 0.2);
        const gain = envGain(time, 0.9, 0.005, 0.3);
        osc.connect(gain);
        gain.connect(masterGain);
        osc.start(time);
        osc.stop(time + 0.35);
    }

    function synthNoiseHit(time, { filterType, freq, peak, attack, decay, duration }) {
        const src = audioCtx.createBufferSource();
        src.buffer = noiseBuffer;
        const filter = audioCtx.createBiquadFilter();
        filter.type = filterType;
        filter.frequency.value = freq;
        const gain = envGain(time, peak, attack, decay);
        src.connect(filter);
        filter.connect(gain);
        gain.connect(masterGain);
        src.start(time);
        src.stop(time + duration);
    }

    function synthSnare(time) {
        synthNoiseHit(time, { filterType: "highpass", freq: 900, peak: 0.9, attack: 0.002, decay: 0.15, duration: 0.2 });
    }

    function synthHihat(time) {
        synthNoiseHit(time, { filterType: "highpass", freq: 6000, peak: 0.5, attack: 0.001, decay: 0.05, duration: 0.09 });
    }

    function synthClap(time) {
        [0, 0.02, 0.035].forEach((offset) => {
            synthNoiseHit(time + offset, { filterType: "bandpass", freq: 1200, peak: 0.7, attack: 0.001, decay: 0.08, duration: 0.12 });
        });
    }

    const SYNTH_DRUMS = { kick: synthKick, snare: synthSnare, hihat: synthHihat, clap: synthClap, tom: synthTom };

    function triggerDrum(name, time) {
        if (state.drumSource === "sample" && sampleBuffers[name]) {
            playBuffer(sampleBuffers[name], time, 0.9);
        } else {
            SYNTH_DRUMS[name](time);
        }
    }

    function triggerNote(freq, time, duration) {
        const osc = audioCtx.createOscillator();
        osc.type = state.waveform;
        osc.frequency.value = freq;
        const gain = envGain(time, 0.5, 0.01, duration);
        osc.connect(gain);
        gain.connect(masterGain);
        osc.start(time);
        osc.stop(time + duration + 0.05);
    }

    // ---- Scheduler ----

    function stepDuration() {
        return 60 / state.bpm / 4; // 16th notes
    }

    function loopLength() {
        return Math.max(BEAT_STEPS, state.melodySteps);
    }

    function scheduleStep(step, time) {
        const beatStep = step % BEAT_STEPS;
        BEAT_ROWS.forEach((row) => {
            if (state.beatPattern[row.id][beatStep]) triggerDrum(row.id, time);
        });
        MELODY_ROWS.forEach((note) => {
            if (state.melodyPattern[note][step]) triggerNote(noteToFreq(note), time, stepDuration() * 0.9);
        });
        scheduledSteps.push({ step, time });
    }

    function scheduler() {
        while (nextNoteTime < audioCtx.currentTime + SCHEDULE_AHEAD_SEC) {
            scheduleStep(currentStep, nextNoteTime);
            nextNoteTime += stepDuration();
            currentStep = (currentStep + 1) % loopLength();
        }
        timerID = setTimeout(scheduler, LOOKAHEAD_MS);
    }

    function drawLoop() {
        if (!audioCtx) return;
        let latest = null;
        while (scheduledSteps.length && scheduledSteps[0].time <= audioCtx.currentTime) {
            latest = scheduledSteps.shift();
        }
        if (latest) highlightStep(latest.step);
        rafID = requestAnimationFrame(drawLoop);
    }

    const lastHighlighted = { beatGrid: -1, melodyGrid: -1 };
    function highlightGrid(containerId, step) {
        const container = document.getElementById(containerId);
        const previous = lastHighlighted[containerId];
        if (previous >= 0) {
            container.querySelectorAll(`[data-step="${previous}"]`).forEach((el) => el.classList.remove("playhead"));
        }
        container.querySelectorAll(`[data-step="${step}"]`).forEach((el) => el.classList.add("playhead"));
        lastHighlighted[containerId] = step;
    }

    function highlightStep(step) {
        highlightGrid("beatGrid", step % BEAT_STEPS);
        highlightGrid("melodyGrid", step % state.melodySteps);
    }

    function clearPlayhead() {
        Object.keys(lastHighlighted).forEach((containerId) => {
            if (lastHighlighted[containerId] >= 0) {
                document.getElementById(containerId).querySelectorAll(`[data-step="${lastHighlighted[containerId]}"]`).forEach((el) => el.classList.remove("playhead"));
            }
            lastHighlighted[containerId] = -1;
        });
    }

    function startPlayback() {
        ensureAudio();
        if (audioCtx.state === "suspended") audioCtx.resume();
        state.playing = true;
        currentStep = 0;
        nextNoteTime = audioCtx.currentTime + 0.05;
        scheduledSteps.length = 0;
        scheduler();
        rafID = requestAnimationFrame(drawLoop);
    }

    function stopPlayback() {
        state.playing = false;
        clearTimeout(timerID);
        cancelAnimationFrame(rafID);
        clearPlayhead();
        scheduledSteps.length = 0;
    }

    // ---- Grid UI ----

    function buildGrid(container, rows, pattern, cssClass, stepCount) {
        container.innerHTML = "";
        container.style.minWidth = `${70 + stepCount * 30}px`;

        rows.forEach((row) => {
            const id = typeof row === "string" ? row : row.id;
            const label = typeof row === "string" ? row : row.label;

            const rowEl = document.createElement("div");
            rowEl.className = "grid-row";
            rowEl.style.gridTemplateColumns = `70px repeat(${stepCount}, 1fr)`;

            const labelEl = document.createElement("div");
            labelEl.className = "row-label";
            labelEl.textContent = label;
            rowEl.appendChild(labelEl);

            for (let step = 0; step < stepCount; step++) {
                const cell = document.createElement("div");
                cell.className = "cell" + (step % 4 === 0 ? " beat-marker" : "");
                cell.dataset.row = id;
                cell.dataset.step = String(step);
                if (pattern[id][step]) cell.classList.add("active");
                cell.addEventListener("click", () => {
                    pattern[id][step] = !pattern[id][step];
                    cell.classList.toggle("active");
                    if (pattern[id][step]) previewCell(cssClass, id);
                });
                rowEl.appendChild(cell);
            }

            container.appendChild(rowEl);
        });
    }

    function previewCell(cssClass, id) {
        ensureAudio();
        if (audioCtx.state === "suspended") audioCtx.resume();
        const time = audioCtx.currentTime;
        if (cssClass === "beat-grid") {
            triggerDrum(id, time);
        } else {
            triggerNote(noteToFreq(id), time, 0.25);
        }
    }

    function refreshGridDom() {
        buildGrid(document.getElementById("beatGrid"), BEAT_ROWS, state.beatPattern, "beat-grid", BEAT_STEPS);
        buildGrid(document.getElementById("melodyGrid"), MELODY_ROWS, state.melodyPattern, "melody-grid", state.melodySteps);
    }

    function setMelodySteps(newSteps) {
        MELODY_ROWS.forEach((note) => {
            const arr = state.melodyPattern[note];
            state.melodyPattern[note] = newSteps > arr.length
                ? arr.concat(Array(newSteps - arr.length).fill(false))
                : arr.slice(0, newSteps);
        });
        state.melodySteps = newSteps;
        refreshGridDom();
    }

    // ---- Persistence ----

    function savePattern() {
        const payload = {
            beatPattern: state.beatPattern,
            melodyPattern: state.melodyPattern,
            melodySteps: state.melodySteps,
            bpm: state.bpm,
            drumSource: state.drumSource,
            waveform: state.waveform,
        };
        localStorage.setItem(STORAGE_KEY, JSON.stringify(payload));
        setStatus("Saved.");
    }

    function loadPattern() {
        const raw = localStorage.getItem(STORAGE_KEY);
        if (!raw) {
            setStatus("Nothing saved yet.");
            return;
        }
        try {
            const data = JSON.parse(raw);
            state.beatPattern = data.beatPattern;
            state.melodyPattern = data.melodyPattern;
            state.melodySteps = data.melodySteps ?? MELODY_ROWS.reduce((max, n) => Math.max(max, data.melodyPattern[n].length), BEAT_STEPS);
            state.bpm = data.bpm ?? state.bpm;
            state.drumSource = data.drumSource ?? state.drumSource;
            state.waveform = data.waveform ?? state.waveform;

            document.getElementById("bpmRange").value = state.bpm;
            document.getElementById("bpmValue").textContent = `${state.bpm} BPM`;
            document.getElementById("drumSource").value = state.drumSource;
            document.getElementById("waveform").value = state.waveform;
            document.getElementById("melodySteps").value = String(state.melodySteps);

            refreshGridDom();
            setStatus("Loaded.");
        } catch (err) {
            setStatus("Couldn't load saved pattern.");
            console.warn(err);
        }
    }

    function clearAll() {
        BEAT_ROWS.forEach((row) => state.beatPattern[row.id].fill(false));
        MELODY_ROWS.forEach((note) => state.melodyPattern[note].fill(false));
        refreshGridDom();
        setStatus("Cleared.");
    }

    // ---- Recording ----

    function toggleRecord(button) {
        ensureAudio();
        if (audioCtx.state === "suspended") audioCtx.resume();

        if (!mediaRecorder || mediaRecorder.state === "inactive") {
            recordedChunks = [];
            mediaRecorder = new MediaRecorder(recordDestination.stream);
            mediaRecorder.ondataavailable = (e) => {
                if (e.data.size > 0) recordedChunks.push(e.data);
            };
            mediaRecorder.onstop = () => {
                const blob = new Blob(recordedChunks, { type: "audio/webm" });
                const url = URL.createObjectURL(blob);
                const a = document.createElement("a");
                a.href = url;
                a.download = `composer-take-${Date.now()}.webm`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                setTimeout(() => URL.revokeObjectURL(url), 2000);
                setStatus("Recording saved to downloads.");
            };
            mediaRecorder.start();
            if (!state.playing) startPlayback();
            button.textContent = "⏹ Stop Rec";
            button.classList.add("recording");
            setStatus("Recording...");
        } else {
            mediaRecorder.stop();
            button.textContent = "🎙️ Record";
            button.classList.remove("recording");
        }
    }

    // ---- MIDI input (live play-through) ----

    async function connectMIDI() {
        const statusEl = document.getElementById("midiStatus");
        if (!navigator.requestMIDIAccess) {
            statusEl.textContent = "Web MIDI isn't supported in this browser.";
            return;
        }
        try {
            midiAccess = await navigator.requestMIDIAccess();
            wireMIDIInputs();
            midiAccess.onstatechange = wireMIDIInputs;
        } catch (err) {
            statusEl.textContent = "MIDI access was denied.";
            console.warn(err);
        }
    }

    function wireMIDIInputs() {
        const statusEl = document.getElementById("midiStatus");
        const inputs = Array.from(midiAccess.inputs.values());
        inputs.forEach((input) => {
            input.onmidimessage = handleMIDIMessage;
        });
        statusEl.textContent = inputs.length
            ? `Connected: ${inputs.map((i) => i.name).join(", ")}`
            : "No MIDI inputs found.";
    }

    function handleMIDIMessage(event) {
        const [statusByte, note, velocity] = event.data;
        const command = statusByte & 0xf0;
        if (command !== 0x90 || velocity === 0) return; // only note-on triggers a sound

        ensureAudio();
        if (audioCtx.state === "suspended") audioCtx.resume();
        triggerNote(midiToFreq(note), audioCtx.currentTime, 0.4);
    }

    // ---- MIDI export ----

    function writeVarLen(value, bytes) {
        let buffer = value & 0x7f;
        while ((value >>= 7)) {
            buffer <<= 8;
            buffer |= (value & 0x7f) | 0x80;
        }
        while (true) {
            bytes.push(buffer & 0xff);
            if (buffer & 0x80) buffer >>= 8;
            else break;
        }
    }

    function buildStandardMidiFile(trackBytes, ppq) {
        const header = [
            0x4d, 0x54, 0x68, 0x64, // "MThd"
            0x00, 0x00, 0x00, 0x06, // header length
            0x00, 0x00, // format 0
            0x00, 0x01, // 1 track
            (ppq >> 8) & 0xff, ppq & 0xff,
        ];
        const trackHeader = [
            0x4d, 0x54, 0x72, 0x6b, // "MTrk"
            (trackBytes.length >>> 24) & 0xff,
            (trackBytes.length >>> 16) & 0xff,
            (trackBytes.length >>> 8) & 0xff,
            trackBytes.length & 0xff,
        ];
        return new Uint8Array([...header, ...trackHeader, ...trackBytes]);
    }

    function exportMIDI() {
        const PPQ = 96;
        const ticksPerStep = PPQ / 4;
        const events = [];

        for (let step = 0; step < loopLength(); step++) {
            const tick = step * ticksPerStep;
            const beatStep = step % BEAT_STEPS;

            BEAT_ROWS.forEach((row) => {
                if (!state.beatPattern[row.id][beatStep]) return;
                const note = DRUM_MIDI_NOTES[row.id];
                events.push({ tick, on: true, channel: 9, note, velocity: 100 });
                events.push({ tick: tick + Math.max(1, Math.round(ticksPerStep * 0.5)), on: false, channel: 9, note, velocity: 0 });
            });

            MELODY_ROWS.forEach((noteName) => {
                if (!state.melodyPattern[noteName][step]) return;
                const note = noteNameToMidi(noteName);
                events.push({ tick, on: true, channel: 0, note, velocity: 90 });
                events.push({ tick: tick + Math.max(1, Math.round(ticksPerStep * 0.9)), on: false, channel: 0, note, velocity: 0 });
            });
        }

        events.sort((a, b) => a.tick - b.tick || (a.on ? 1 : -1) - (b.on ? 1 : -1));

        const trackBytes = [];
        const microsPerQuarter = Math.round(60000000 / state.bpm);
        writeVarLen(0, trackBytes);
        trackBytes.push(0xff, 0x51, 0x03, (microsPerQuarter >> 16) & 0xff, (microsPerQuarter >> 8) & 0xff, microsPerQuarter & 0xff);

        let lastTick = 0;
        events.forEach((ev) => {
            writeVarLen(ev.tick - lastTick, trackBytes);
            lastTick = ev.tick;
            trackBytes.push((ev.on ? 0x90 : 0x80) | (ev.channel & 0x0f), ev.note & 0x7f, ev.velocity & 0x7f);
        });

        writeVarLen(0, trackBytes);
        trackBytes.push(0xff, 0x2f, 0x00); // end of track

        const bytes = buildStandardMidiFile(trackBytes, PPQ);
        const blob = new Blob([bytes], { type: "audio/midi" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `composer-pattern-${Date.now()}.mid`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        setTimeout(() => URL.revokeObjectURL(url), 2000);
        setStatus("MIDI file downloaded.");
    }

    // ---- Wiring ----

    function setStatus(text) {
        document.getElementById("status").textContent = text;
    }

    function init() {
        refreshGridDom();

        const playBtn = document.getElementById("playBtn");
        playBtn.addEventListener("click", () => {
            if (state.playing) {
                stopPlayback();
                playBtn.textContent = "▶ Play";
                playBtn.classList.remove("playing");
                setStatus("Stopped.");
            } else {
                startPlayback();
                playBtn.textContent = "⏸ Stop";
                playBtn.classList.add("playing");
                setStatus("Playing.");
            }
        });

        document.getElementById("clearBtn").addEventListener("click", clearAll);

        const bpmRange = document.getElementById("bpmRange");
        const bpmValue = document.getElementById("bpmValue");
        bpmRange.addEventListener("input", () => {
            state.bpm = parseInt(bpmRange.value, 10);
            bpmValue.textContent = `${state.bpm} BPM`;
        });

        document.getElementById("drumSource").addEventListener("change", (e) => {
            state.drumSource = e.target.value;
        });

        document.getElementById("waveform").addEventListener("change", (e) => {
            state.waveform = e.target.value;
        });

        document.getElementById("saveBtn").addEventListener("click", savePattern);
        document.getElementById("loadBtn").addEventListener("click", loadPattern);
        document.getElementById("recordBtn").addEventListener("click", (e) => toggleRecord(e.currentTarget));

        const advancedToggle = document.getElementById("advancedToggle");
        const advancedPanel = document.getElementById("advancedPanel");
        advancedToggle.addEventListener("click", () => {
            state.advanced = !state.advanced;
            advancedPanel.classList.toggle("hidden", !state.advanced);
            advancedToggle.classList.toggle("playing", state.advanced);
        });

        document.getElementById("melodySteps").addEventListener("change", (e) => {
            setMelodySteps(parseInt(e.target.value, 10));
        });

        document.getElementById("midiConnectBtn").addEventListener("click", connectMIDI);
        document.getElementById("midiExportBtn").addEventListener("click", exportMIDI);
    }

    document.addEventListener("DOMContentLoaded", init);
})();
