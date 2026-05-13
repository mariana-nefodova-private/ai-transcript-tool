# Transcript Tool — Project Plan

## Context
Mariana (non-technical PM) needs a macOS app to transcribe MP4 meeting recordings into timestamped plain text. The app must support Ukrainian and English, require zero ongoing cost, and run entirely on her laptop. There is no minimum recording length. Maximum supported length is 4 hours (if a hard limit is technically necessary).

**Architecture:** Use **Whisper** (OpenAI's free, open-source AI model) for transcription. Whisper runs *locally on the Mac* — no API calls, no tokens, no internet needed after setup. It has excellent accuracy for Ukrainian and English. A simple browser-based UI (Flask + Chrome/Safari) is used so no complex Mac app packaging is needed.

---

## Tech Stack

| Layer | Tool | Why |
|---|---|---|
| Transcription AI | OpenAI Whisper (local, `openai-whisper` Python package) | Free, offline, Ukrainian + English, timestamps built-in |
| Audio extraction | FFmpeg | Standard tool for MP4 → audio conversion |
| Backend | Python 3.11+ | Best ecosystem for Whisper + Flask |
| UI | Flask + HTML/CSS/JS (opens in browser) | No app packaging complexity |

---

## Application Flow

1. User runs `python app.py` in Terminal (or via a shell alias)
2. Browser opens automatically at `http://localhost:5000`
3. User selects or drags an MP4 file onto the page
4. App extracts audio using FFmpeg (background process)
5. Whisper transcribes with timestamps (background, with live progress bar)
6. Transcript shown in browser; copyable in one click; downloadable as `.txt` file

---

## Output Format

```
[00:00:00] Welcome everyone to today's meeting.
[00:00:15] Сьогодні ми обговоримо квартальний план.
[00:00:45] Let's start with the Q1 review...
```

One timestamp per segment (~sentence boundary), plain `.txt` output.

---

## Repository Structure

```
ai-transcript-tool/
├── README.md                   ← Setup & usage guide (non-technical language)
├── PROJECT_PLAN.md             ← This document
├── ACCEPTANCE_CRITERIA.md      ← Testable checklist
├── app/
│   ├── app.py                  ← Flask server + routes
│   ├── transcriber.py          ← Whisper transcription logic
│   ├── templates/
│   │   └── index.html          ← Upload UI + results view
│   ├── static/                 ← CSS + JS
│   └── requirements.txt        ← Python deps (flask, openai-whisper, ffmpeg-python)
└── setup.sh                    ← One-command setup script (brew + pip install)
```

---

## Acceptance Criteria (Phase 1)

### Functional
- [ ] App accepts MP4 files
- [ ] Transcribes Ukrainian speech correctly
- [ ] Transcribes English speech correctly
- [ ] Handles mixed Ukrainian/English in the same recording
- [ ] Produces timestamps in `[HH:MM:SS]` format, one per segment
- [ ] Output is downloadable as a plain `.txt` file
- [ ] Transcript is also viewable in the browser after processing
- [ ] Shows a progress indicator while transcription is running (not a blank screen)
- [ ] One-click "Copy all" button copies the full transcript to clipboard

### Non-functional
- [ ] Works offline after initial setup
- [ ] Processes a 1-hour MP4 in under 20 minutes on a modern MacBook
- [ ] Does not crash or freeze on recordings up to 4 hours
- [ ] Setup steps are completable by a non-technical user in under 30 minutes
- [ ] No login, no account, no API keys required to use the app

### Out of scope (Phase 1)
- Speaker identification / diarization
- In-app audio/video player (→ Phase 2)
- Inline transcript editing (→ Phase 2)
- Cloud sync or file sharing
- Mobile or Windows support

---

## Setup Steps (documented in README)

1. Open Terminal
2. Run `setup.sh` — installs Homebrew (if missing), Python, FFmpeg, and Whisper
3. Run `python app/app.py` to start the server
4. Browser opens at `http://localhost:5000`
5. Drop in an MP4 → get a `.txt` transcript

---

## Phase 2 Plan (future, not in scope now)

- In-app audio/video mini-player embedded below the transcript
- Clicking a `[HH:MM:SS]` timestamp jumps the player to that position
- Playback speed controls: 0.5×, 1×, 1.5×, 2×
- Inline transcript editing — double-click a segment or press an Edit button to correct the transcribed text

---

## Implementation Steps

1. **Create GitHub repo** — initialize `ai-transcript-tool` with README + docs
2. **Push `PROJECT_PLAN.md` and `ACCEPTANCE_CRITERIA.md`** to the repo
3. **Build backend** — `transcriber.py` wrapping Whisper with timestamp extraction
4. **Build Flask server** — file upload endpoint, transcription job runner, result endpoint
5. **Build UI** — drag-and-drop upload, progress bar, transcript display, copy + download buttons
6. **Write `setup.sh`** — automated one-command install script
7. **Write `README.md`** — step-by-step setup guide for non-technical users
8. **Test** — verify with real Ukrainian + English MP4s, file sizes up to 4h
