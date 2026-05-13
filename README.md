# AI Transcript Tool

Transcribe MP4 meeting recordings to timestamped plain text. Runs fully on your Mac — no internet, no subscriptions, no API keys needed after setup.

**Supports:** Ukrainian 🇺🇦 and English 🇬🇧  
**Input:** MP4 video files (any length, up to ~4 hours)  
**Output:** Plain `.txt` file with timestamps like `[00:05:23] Text here...`

---

## One-time Setup

> You only need to do this once. It takes about 20–30 minutes.

**Step 1 — Open Terminal**

Press `Cmd + Space`, type `Terminal`, press Enter.

**Step 2 — Run the setup script**

In Terminal, paste this command and press Enter:

```bash
cd ~/AI-trascript-tool && bash setup.sh
```

This will automatically install everything the app needs (Python packages, Whisper AI model). You may be asked for your Mac password — this is normal.

**Step 3 — Wait for it to finish**

You'll see text scrolling. When it says `Setup complete!` you're ready.

---

## Running the App

Every time you want to use the app:

**Step 1 — Open Terminal** and paste:

```bash
cd ~/AI-trascript-tool && source venv/bin/activate && python app/app.py
```

**Step 2 — Your browser opens automatically** at `http://localhost:5000`

**Step 3 — Upload your MP4**

- Drag your MP4 file onto the page, or click "Choose file"
- Click **Transcribe**
- Wait for the progress bar to complete (a 1-hour recording takes ~10–15 minutes)

**Step 4 — Get your transcript**

- The transcript appears on the page
- Click **Copy All** to copy to clipboard
- Click **Download .txt** to save the file

**Step 5 — Stop the app**

When done, go back to Terminal and press `Ctrl + C`.

---

## Troubleshooting

**App won't start?**
Make sure you ran the setup script first. Try running it again.

**Browser doesn't open automatically?**
Open your browser manually and go to `http://localhost:5000`

**Transcription seems slow?**
This is normal for long recordings. A 1-hour MP4 takes roughly 10–15 minutes. Do not close the browser tab while it's running.

---

## Project Docs

- [Project Plan](PROJECT_PLAN.md)
- [Acceptance Criteria](ACCEPTANCE_CRITERIA.md)
