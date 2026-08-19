(() => {
    "use strict";

    const STEPS = 16;
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

    const state = {
        beatPattern: Object.fromEntries(BEAT_ROWS.map((r) => [r.id, Array(STEPS).fill(false)])),
        melodyPattern: Object.fromEntries(MELODY_ROWS.map((n) => [n, Array(STEPS).fill(false)])),
        bpm: 120,
        drumSource: "sample",
        waveform: "triangle",
        playing: false,
    };

    let audioCtx = null;
    let masterGain = null;
    let recordDestination = null;
    let mediaRecorder = null;
    let recordedChunks = [];
    let noiseBuffer = null;
    const sampleBuffers = {};

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

    function noteToFreq(note) {
        const NOTE_INDEX = { C: 0, D: 2, E: 4, F: 5, G: 7, A: 9, B: 11 };
        const letter = note[0];
        const octave = parseInt(note.slice(1), 10);
        const midi = NOTE_INDEX[letter] + (octave + 1) * 12;
        return 440 * Math.pow(2, (midi - 69) / 12);
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

    function scheduleStep(step, time) {
        BEAT_ROWS.forEach((row) => {
            if (state.beatPattern[row.id][step]) triggerDrum(row.id, time);
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
            currentStep = (currentStep + 1) % STEPS;
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

    let lastHighlighted = -1;
    function highlightStep(step) {
        if (lastHighlighted >= 0) {
            document.querySelectorAll(`[data-step="${lastHighlighted}"]`).forEach((el) => el.classList.remove("playhead"));
        }
        document.querySelectorAll(`[data-step="${step}"]`).forEach((el) => el.classList.add("playhead"));
        lastHighlighted = step;
    }

    function clearPlayhead() {
        if (lastHighlighted >= 0) {
            document.querySelectorAll(`[data-step="${lastHighlighted}"]`).forEach((el) => el.classList.remove("playhead"));
        }
        lastHighlighted = -1;
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

    function buildGrid(container, rows, pattern, cssClass) {
        container.innerHTML = "";
        rows.forEach((row) => {
            const id = typeof row === "string" ? row : row.id;
            const label = typeof row === "string" ? row : row.label;

            const rowEl = document.createElement("div");
            rowEl.className = "grid-row";

            const labelEl = document.createElement("div");
            labelEl.className = "row-label";
            labelEl.textContent = label;
            rowEl.appendChild(labelEl);

            for (let step = 0; step < STEPS; step++) {
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
        buildGrid(document.getElementById("beatGrid"), BEAT_ROWS, state.beatPattern, "beat-grid");
        buildGrid(document.getElementById("melodyGrid"), MELODY_ROWS, state.melodyPattern, "melody-grid");
    }

    // ---- Persistence ----

    function savePattern() {
        const payload = {
            beatPattern: state.beatPattern,
            melodyPattern: state.melodyPattern,
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
            state.bpm = data.bpm ?? state.bpm;
            state.drumSource = data.drumSource ?? state.drumSource;
            state.waveform = data.waveform ?? state.waveform;

            document.getElementById("bpmRange").value = state.bpm;
            document.getElementById("bpmValue").textContent = `${state.bpm} BPM`;
            document.getElementById("drumSource").value = state.drumSource;
            document.getElementById("waveform").value = state.waveform;

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
    }

    document.addEventListener("DOMContentLoaded", init);
})();
