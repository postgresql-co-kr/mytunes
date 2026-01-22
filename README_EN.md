# 🎵 MyTunes Pro

**Modern CLI YouTube Music Player**  
A minimalist, keyboard-driven terminal player that **searches and streams YouTube music**. Built for speed.

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## ✨ Features

- **Minimalist Design**: Zero clutter, no complex TUI boxes.
- **Keyboard-First**: Navigate menus effortlessly with arrow keys and shortcuts.
- **YouTube Integration**: High-quality audio streaming via `yt-dlp` and `mpv`.
- **Cross-Platform**: Optimized for Linux (Debian/Ubuntu). macOS support is **Experimental**.
- **Multi-language**: Supports English and Korean (selectable on first run).
- **Smart Features**: Favorites, History, and Search with auto-complete support.

## 🛠 Prerequisites

You need **mpv** (player) and **yt-dlp** (streamer) installed on your system.

### macOS (Experimental)

```bash
brew install mpv yt-dlp
```

### Linux (Debian/Ubuntu)

```bash
sudo apt update
sudo apt install mpv
pip install -U yt-dlp
```

## 🚀 Installation & Usage

1. **Clone the repository**

   ```bash
   git clone https://github.com/Start-to/mytunes.git
   cd mytunes
   ```

   *(Note: Replace `Start-to` with your actual GitHub username if different)*

2. **Set up virtual environment**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Run MyTunes**

   ```bash
   python mytune.py
   ```
   > You will be asked to select your language on the first run.

## ⌨️ Controls

| Key | Action |
| :--- | :--- |
| **Turns** | **Menu Navigation** |
| `↑` / `↓` | Move selection |
| `Enter` | Select / Play |
| `/` | **Search Music** |
| `q` | Go Back / Exit |

---
**Troubleshooting**:
- **macOS Playback Issues**: If playback fails on macOS, check if your terminal has necessary permissions (Microphone/Automation). Also ensure `yt-dlp` is up to date.
- **403 Forbidden**: Verify `yt-dlp` is updated: `pip install -U yt-dlp`

---
[postgresql.co.kr](https://postgresql.co.kr)
