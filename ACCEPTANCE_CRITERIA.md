# Acceptance Criteria — AI Transcript Tool

## Phase 1 (Core Transcription App)

### Functional Requirements

| # | Criteria | How to Test | Status |
|---|---|---|---|
| F1 | App accepts MP4 files of any length (up to 4 hours) | Upload a short MP4, a 1h MP4, and a ~2h MP4 | ⬜ |
| F2 | Transcribes Ukrainian speech correctly | Upload a meeting recorded in Ukrainian, review transcript for accuracy | ⬜ |
| F3 | Transcribes English speech correctly | Upload a meeting recorded in English, review transcript for accuracy | ⬜ |
| F4 | Handles mixed Ukrainian + English in one recording | Upload a bilingual meeting, verify both languages appear correctly | ⬜ |
| F5 | Timestamps appear in `[HH:MM:SS]` format | Check transcript output format visually | ⬜ |
| F6 | Each transcript segment has a timestamp | Scan through transcript — every line starts with a timestamp | ⬜ |
| F7 | Transcript is viewable in the browser after processing | After upload + transcription, text appears on the page | ⬜ |
| F8 | Transcript is downloadable as a `.txt` file | Click Download button, open the file, verify contents match | ⬜ |
| F9 | "Copy all" button copies full transcript to clipboard | Click Copy All, paste into Notes/Word, verify full text is there | ⬜ |
| F10 | Progress indicator shown during transcription | Upload a file and watch the screen — should show progress, not freeze | ⬜ |

### Non-functional Requirements

| # | Criteria | How to Test | Status |
|---|---|---|---|
| NF1 | App works fully offline after setup | Disconnect from Wi-Fi, run app, upload MP4, verify transcription completes | ⬜ |
| NF2 | 1-hour MP4 processes in under 20 minutes | Time a 1-hour recording from upload to completed transcript | ⬜ |
| NF3 | App does not crash or freeze on recordings up to 4 hours | Upload a 2h+ recording, verify it completes without error | ⬜ |
| NF4 | Setup completable by non-technical user in under 30 minutes | Follow the README from scratch on a fresh machine | ⬜ |
| NF5 | No login, account, or API key required | Open the app — no sign-in screen, no key prompt | ⬜ |

---

## Phase 2 (Mini-Player + Editing — Future)

> Not in scope for Phase 1. Listed here for planning purposes.

| # | Criteria | Status |
|---|---|---|
| P2-1 | In-app audio/video mini-player visible below the transcript | 🔲 Future |
| P2-2 | Clicking a `[HH:MM:SS]` timestamp in the transcript jumps the player to that moment | 🔲 Future |
| P2-3 | Playback speed controls available: 0.5×, 1×, 1.5×, 2× | 🔲 Future |
| P2-4 | Double-clicking a transcript segment opens it for inline editing | 🔲 Future |
| P2-5 | An "Edit" button per segment also triggers inline editing mode | 🔲 Future |
| P2-6 | Edited transcript can be re-downloaded as `.txt` | 🔲 Future |

---

## Status Key

| Symbol | Meaning |
|---|---|
| ⬜ | Not yet tested |
| ✅ | Passing |
| ❌ | Failing — needs fix |
| 🔲 | Future / out of scope |
