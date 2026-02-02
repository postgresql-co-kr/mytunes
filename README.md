# 🎵 MyTunes Pro - Professional TUI Edition v2.1.1

## 🚀 Terminal-based Media Workflow Experiment v2.1.1

> [!IMPORTANT]
> **Legal Disclaimer:** This project is a personal, non-commercial research experiment for developer education.
> It does not host, provide, or distribute any media content.
> All media sources are independently accessed and configured by the user.
> Users are solely responsible for ensuring that their usage complies with the terms of service of any third-party platforms accessed via this tool.

MyTunes Pro is a developer-focused **CLI Media Tool** for experimenting with terminal-based media workflows.
It utilizes the Python `curses` library to provide a structured TUI (Terminal User Interface) for handling media URLs, 
leveraging the `mpv` engine for local media processing and playback.

> **💡 Project Note**  
> This tool was designed for personal research into how terminal users can interact with media sources without interrupting their developer workflow. 
> It explores the integration between local CLI environments (like Headless Debian Servers) and external media handling utilities.

![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

---

## 📸 Screenshots
| | |
| :---: | :---: |
| ![Main](https://raw.githubusercontent.com/postgresql-co-kr/mytunes/master/screenshots/screenshot_1.webp) | ![Search](https://raw.githubusercontent.com/postgresql-co-kr/mytunes/master/screenshots/screenshot_2.webp) |
| ![Play](https://raw.githubusercontent.com/postgresql-co-kr/mytunes/master/screenshots/screenshot_3.webp) | ![List](https://raw.githubusercontent.com/postgresql-co-kr/mytunes/master/screenshots/screenshot_4.webp) |

---

## ✨ Core Features

- **Media Handling**: Support for loading and processing media URLs using external extraction tools.
- **TUI Workflow**: Efficient, low-latency interface built on the `curses` library.
- **Workflow Persistence**: Handles sequential media loading and state restoration.
- **Terminal Optimization**: Performance-focused design that prioritizes keyboard-driven interactions.
- **Smart Management**: Optional user-configured collections, interaction history, and metadata handling.
- **External Integration**: Capabilities to load media links into external viewer/player environments.

---

## 💻 Environment & Integration

**MyTunes Pro** is a CLI-based tool. It can integrate with externally installed media processing tools.

- **External Tools**: This project can interface with user-installed utilities like `mpv` and media extraction tools. No third-party tools are bundled with this software.
- **macOS/Linux**: Native terminal support.
- **Windows**: Recommended to use with **WSL (Windows Subsystem for Linux)**.

---

## 🚀 Quick Install

We strongly recommend using **`pipx`** on modern macOS/Linux systems (PEP 668).

### 1. Recommended Method (pipx)
Automatically creates an isolated environment and registers the command.

```bash
# Ensure ensuredpath is run to register the command after pipx install!
pipx install mytunes-pro
pipx ensurepath
source ~/.zshrc  # or source ~/.bashrc (apply immediately to current terminal)
```

### 2. Standard pip Method
If you encounter the `externally-managed-environment` error, add the following flag:

```bash
pip install mytunes-pro --break-system-packages
```

After installation, type **`mp`** anywhere in the terminal to run!

### 🔄 Update
If already installed, simply use the command below to update to the latest features:

```bash
pipx upgrade mytunes-pro
```

---

## 🛠 Prerequisites

Please install the necessary tools for your operating system before running.

### macOS (Using Homebrew)
```bash
brew install mpv python3 pipx
```

### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install mpv python3 python3-pip pipx python3-venv -y
```

### Windows (WSL Guide)

Guide for Windows users where Korean search might not work or installation is difficult.

> **❓ What is WSL?**  
> It allows you to run Linux environments directly on Windows. MyTunes works perfectly in this environment.

1. **Install WSL**:
   - Right-click `Start` -> Run `Terminal (Admin)`.
   - Enter the command below and **Reboot**:
     ```powershell
     wsl --install -d Debian
     ```

2. **Install Essentials**:
   ```bash
   sudo apt update && sudo apt install mpv python3-pip pipx -y
   ```

3. **Install MyTunes**:
   ```bash
   pipx install mytunes-pro
   pipx ensurepath
   source ~/.bashrc  # Apply settings immediately
   ```

---

## 🧑‍💻 Manual Installation (For Developers)

Follow these steps to modify source code or use the development version.

1. **Clone Repository**:
   ```bash
   git clone https://github.com/postgresql-co-kr/mytunes.git
   cd mytunes
   ```

2. **Setup Virtual Environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # macOS/Linux
   pip install -r requirements.txt
   ```

3. **Run**:
   ```bash
   python3 mytune.py
   ```

---

## ⌨️ Controls

**MyTunes Pro** is controlled entirely by keyboard.  
We recommend using **Number Keys** for lag-free operation even in multi-language input modes.

### ⚡️ Instant Hotkeys (Number Keys)
Executes immediately without worrying about input language status.

| Key | Function | Description |
| :--- | :--- | :--- |
| **`1`** | **Search** | Open music search (Same as `S`) |
| **`2`** | **Favorites** | View favorites list (Same as `F`) |
| **`3`** | **History** | View recently played 100 tracks (Same as `R`) |
| **`4`** | **Main** | Return to main screen (Same as `M`) |
| **`5`** | **Add/Del** | Toggle favorite for selected track (Same as `A`) |
| **`+`** | **Vol UP** | Volume +5% (Same as `=`) |
| **`-`** | **Vol DOWN** | Volume -5% (Same as `_`) |
| **`F7`** | **Open YouTube** | View current track in browser |
| **`E`** | **Equalizer** | Cycle EQ presets (Auto/Flat/Pop/Rock/Jazz/etc.) |
| **`6`** | **Back** | Go to previous screen (Same as `Q`, `h`) |
| **`L`** | **Forward** | Go forward to previous screen (`Right Arrow`) |
| **`ESC`** | **Background** | **Exit without stopping music** (Background Play) |

### 🧭 Basic Navigation
| Key | Action |
| :--- | :--- |
| `↑` / `↓` / `k` / `j` | Move selection Up/Down (Vim keys supported) |
| `Enter` / `l` | **Select / Play** |
| `Space` | Play / Pause |
| `-` / `+` | **Volume Control** |
| `,` / `.` | Rewind / Forward 10s |
| `<` / `>` | Rewind / Forward 30s (Shift) |
| `Backspace` / `h` / `q` | Go Back / Clear Search |
| `L` | **Go Forward** |
| `/` | **Search** (Vim Style) |

---

## 📂 Data Storage
- Favorites and playback history are permanently saved in `~/.pymusic_data.json` in your home directory.
- Data is preserved even after restarting the program.

---
---

# 🎵 MyTunes Pro (Experimental Media Tool - KR)

## 🚀 터미널 기반 미디어 워크플로우 실험 v2.1.0

> [!IMPORTANT]
> **법적 면책 고지:** 본 프로젝트는 개발자 교육 및 연구를 목적으로 하는 개인적, 비상업적 실험입니다. 
> 본 소프트웨어는 어떠한 미디어 콘텐츠도 직접 호스팅하거나 배포하지 않습니다. 
> 모든 미디어 소스는 사용자의 로컬 환경에서 직접 구성되고 접근되며, 사용자는 외부 플랫폼의 이용 약관을 준수할 책임이 있습니다.

MyTunes Pro는 개발자를 위해 설계된 **CLI 미디어 실험 도구**입니다.
Python `curses` 라이브러리를 통해 터미널 환경에서 미디어 URL을 로드하고 관리하며, 
사용자가 설치한 `mpv` 등의 외부 도구와 연동하여 미디어 워크플로우를 테스트할 수 있습니다.

## ✨ 주요 특징

- **미디어 핸들링**: 외부 추출 도구를 사용한 미디어 URL 로드 및 처리 지원.
- **TUI 워크플로우**: `curses` 라이브러리 기반의 효율적인 터미널 인터페이스.
- **작업 유지**: 순차적 미디어 로딩 및 마지막 작업 상태 복원 기능.
- **환경 연동**: 사용자에 의해 구성된 외부 미디어 도구와의 연동 지원. (본 소프트웨어는 외부 도구를 포함하여 배포하지 않습니다.)

---

## 📸 스크린샷 (Screenshots)
| | |
| :---: | :---: |
| ![Main](https://raw.githubusercontent.com/postgresql-co-kr/mytunes/master/screenshots/screenshot_1.webp) | ![Search](https://raw.githubusercontent.com/postgresql-co-kr/mytunes/master/screenshots/screenshot_2.webp) |
| ![Play](https://raw.githubusercontent.com/postgresql-co-kr/mytunes/master/screenshots/screenshot_3.webp) | ![List](https://raw.githubusercontent.com/postgresql-co-kr/mytunes/master/screenshots/screenshot_4.webp) |

---

## 🚀 빠른 설치 (Quick Install)

최신 macOS/Linux 시스템(PEP 668)에서는 **`pipx`** 사용을 강력히 권장합니다.

### 1. 추천 방식 (pipx)
자동으로 격리된 환경을 만들고 명령어를 등록해줍니다.

```bash
# pipx install 이후 명령어 등록을 위해 ensurepath 실행 시점 확인!
pipx install mytunes-pro
pipx ensurepath
source ~/.zshrc  # 또는 source ~/.bashrc (현재 터미널에 즉시 적용)
```

### 2. 일반 pip 방식
만약 `externally-managed-environment` 에러가 발생한다면 아래 플래그를 추가하세요:

```bash
pip install mytunes-pro --break-system-packages
```

설치 후 터미널 어디서든 **`mp`**를 입력하면 실행됩니다!

### 🔄 최신 버전 업데이트 (Update)
이미 설치되어 있다면 아래 명령어로 간단히 최신 기능을 반영하세요:

```bash
pipx upgrade mytunes-pro
```

---

## 🛠 환경별 요구사항 (Prerequisites)

실행 전 각 운영체제에 맞는 필수 도구들을 설치해 주세요.

### macOS (Homebrew 사용)
```bash
brew install mpv python3 pipx
```

### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install mpv python3 python3-pip pipx python3-venv -y
```

### Windows (초보자용 WSL 가이드)

Windows 환경에서 한글 검색이 안 되거나 설치가 어려운 분들을 위한 가이드입니다.

> **❓ WSL이란?**  
> 윈도우 안에서 리눅스를 앱처럼 쓸 수 있게 해줍니다. MyTunes는 이 환경에서 완벽하게 작동합니다.

1. **WSL 설치하기**:
   - `시작` 버튼 우클릭 -> `터미널(관리자)` 실행.
   - 아래 명령어 입력 후 **재부팅**:
     ```powershell
     wsl --install -d Debian
     ```

2. **필수 도구 설치**:
   ```bash
   sudo apt update && sudo apt install mpv python3-pip pipx -y
   ```

3. **MyTunes 설치**:
   ```bash
   pipx install mytunes-pro
   pipx ensurepath
   source ~/.bashrc  # 설정 즉시 반영
   ```

---

## 🧑‍💻 개발자용 수동 설치 (Manual Installation)

직접 소스크드를 수정하거나 개발 버전을 사용하려면 아래 과정을 따르세요.

1. **저장소 클론**:
   ```bash
   git clone https://github.com/postgresql-co-kr/mytunes.git
   cd mytunes
   ```

2. **가상환경 설정**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # macOS/Linux
   pip install -r requirements.txt
   ```

3. **실행**:
   ```bash
   python3 mytune.py
   ```

---

## ⌨️ 조작 방법 (Controls)

**MyTunes Pro**는 키보드만으로 모든 기능을 제어합니다.  
한글 입력 상태에서도 끊김 없는 조작을 위해 **숫자 단축키** 사용을 권장합니다.

### ⚡️ 즉시 반응 단축키 (숫자키)
한영 전환 없이 언제든 누르면 즉시 실행됩니다.

| 키 | 기능 | 설명 |
| :--- | :--- | :--- |
| **`1`** | **검색 (Search)** | 음악 검색창 열기 (단축키 `S`와 동일) |
| **`2`** | **즐겨찾기 (Fav)** | 저장된 즐겨찾기 목록 보기 (단축키 `F`와 동일) |
| **`3`** | **기록 (History)** | 최근 재생한 100곡 보기 (단축키 `R`와 동일) |
| **`4`** | **메인 (Main)** | 메인 화면으로 돌아가기 (단축키 `M`와 동일) |
| **`5`** | **추가/삭제** | 선택한 곡 즐겨찾기 토글 (단축키 `A`와 동일) |
| **`+`** | **볼륨 UP** | 볼륨 +5% (단축키 `=`와 동일) |
| **`-`** | **볼륨 DOWN** | 볼륨 -5% (단축키 `_`와 동일) |
| **`F7`** | **유튜브 열기** | 현재 곡을 브라우저에서 보기 |
| **`E`** | **이퀄라이저** | EQ 프리셋 전환 (Auto/Flat/Pop/Rock/Jazz 등) |
| **`6`** | **뒤로가기** | 이전 화면으로 이동 (단축키 `Q`, `h`와 동일) |
| **`L`** | **앞으로** | 이전 화면에서 앞화면으로 다시 이동 (`Right Arrow`) |
| **`ESC`** | **배경재생** | **음악 끄지 않고 나가기** (백그라운드 재생) |

### 🧭 기본 탐색
| 키 | 동작 |
| :--- | :--- |
| `↑` / `↓` / `k` / `j` | 리스트 위/아래 이동 (Vim 키 지원) |
| `Enter` / `l` | **선택 / 재생** |
| `Space` | 재생 / 일시정지 (Play/Pause) |
| `-` / `+` | **볼륨 조절** (- / +) |
| `,` / `.` | 10초 뒤로 / 앞으로 감기 |
| `<` / `>` | **30초** 뒤로 / 앞으로 감기 (Shift) |
| `Backspace` / `h` / `q` | 뒤로 가기 / 검색어 지우기 |
| `L` | **앞으로 가기** |
| `/` | **검색** (Vim Style) |

---

## 📂 데이터 저장
- 즐겨찾기와 재생 기록은 홈 디렉토리의 `~/.pymusic_data.json` 파일에 영구 저장됩니다.
- 프로그램 종료 후 다시 실행해도 데이터가 유지됩니다.

---
---

## 🔄 Changelog

### v2.1.1 (2026-02-02)
- **WSL UI Polish**: Hides Equalizer (EQ) labels and status in the TUI when running on WSL to avoid confusion, as the feature is disabled in that environment for stability.
- **Improved Feedback**: Provides a clear status message when the 'E' key is pressed on WSL.

### v2.1.0 (2026-02-02)
- **Zero-Freeze IPC Resilience**: Implemented a "Fast-Fail" mechanism that detects mpv process death within 0.1ms via `poll()`, preventing TUI freezes.
- **Fail-Early Polling**: Main loop now aborts all remaining IPC property checks immediately if any call fails, maintaining a smooth 5fps even on broken connections.
- **Connection Throttling**: Added a 1.5-second "cool-down" period for reconnection attempts to minimize blocking time on Windows/WSL environments.
- **Multibyte Harmony**: Explicitly configured `locale.setlocale` to ensure stable emoji and CJK character rendering across different terminal environments.
- **Improved Autoplay Stability**: Autoplay logic now skips status checks when the socket is unhealthy to prevent feedback loops.

### v2.0.8 (2026-02-02)
- **Windows/WSL Socket Recovery**: Fixed UI freezing when mpv socket disconnects during window switching.
- **IPC Resilience**: Added socket pre-check and failure counter to prevent blocking on broken connections.
- **Automatic Recovery**: New playback automatically restarts mpv if socket is unhealthy.

### v2.0.7 (2026-02-02)
- **Performance Optimization**: Improved keyboard responsiveness on Windows/WSL by implementing EQ detection caching.
- **Data Management**: Limited resume data to 500 entries with automatic FIFO cleanup to prevent JSON bloat.
- **Cache System**: Added 200-entry EQ genre cache to skip redundant keyword matching for repeated tracks.

### v2.0.6 (2026-02-02)
- **10-Band Equalizer**: Added professional-grade 10-band EQ with presets (Flat, Pop, Rock, Jazz, Classical, Full Bass, Dance, Club, Live, Soft).
- **Auto EQ Detection**: Intelligent genre detection from track title/channel info automatically applies optimal EQ preset.
- **Keyboard Shortcut**: Press `E` to cycle through EQ presets in real-time without interrupting playback.
- **Multilingual Genre Keywords**: Auto EQ supports genre detection in 12 languages including Korean, Japanese, Chinese, Spanish, and more.

### v2.0.5 (2026-02-01)
- **Input Feedback Refinement**: Transitioned from blinking warnings to a static Bold Yellow status message for better accessibility and premium feel.
- **Auto-clear Optimization**: Implemented a 5-second auto-clear timer for all transient status messages.
- **Zero Latency Feedback**: Added instant redraw mechanisms to ensure input warnings appear immediately upon key press.
- **Stability Fixes**: Resolved a critical attribute error that caused crashes when selecting menu items.
- **SSL Compatibility**: Improved `urllib3` compatibility for macOS systems using LibreSSL.

### v2.0.4 (2026-02-01)
- **Legal Polish**: Comprehensive scrubbing of brand identifiers and service-oriented terminology across the ecosystem.
- **Localization**: Fully localized Korean landing page and technical experiment descriptions.
- **Educational Focus**: Added explicit project disclaimers to all web footers.
- **Project Scope**: Solidified positioning as a "Media Handling Experiment" rather than a music player.

### v2.0.3 (Input Handling & Unicode Stability)

- **Input Logic**: Replaced legacy `getch()` with `get_wch()` in all UI dialogs (`ask_resume`, `show_copy_dialog`) for robust wide-character and Unicode support.
- **Architecture**: Refactored the input handling system into a modular, command-based architecture (v2.0.3).
- **Decoupling**: Separated input collection (`get_next_event`), event normalization, and command execution.
- **Improved ESC Handling**: Enhanced detection of ESC and multi-byte sequences (including Option+Backspace) for smoother navigation.

### v2.0.2 (Stability & Browser Optimization)

- **Browser Launch**: Switched to fully decoupled `subprocess.Popen` logic for browser opening. This eliminates occasional TUI freezes when launching Media Links (F7) or Dashboard (F8) by bypassing `webbrowser` library limitations.
- **App Mode Restore**: Fixed and improved Chrome/Brave App Mode (Popup) for the Live Station on macOS.
- **Improved Remote Detection**: Refined SSH/WSL detection to ensure local browser features are correctly enabled where possible.

### v2.0.1 (Keymap Refinement & Version Sync)

- **Navigation**: Added browser-style Forward navigation (`L` / `Right Arrow`).
- **Keybinding Optimization**: Updated History mapping to `R` / `3` and refined Back/Forward logic.
- **IME Stability**: Removed unstable Korean character mappings (`ㄴ`, `ㄹ`, `ㄱ`, 등) to prevent ghost key issues in the TUI.
- **Global Synchronization**: Synchronized version v2.0.1 across CLI, TUI, and Web interfaces.

### v1.9.9 (Domain Migration & Realtime Sync)

- **Domain Migration**: Updated all branding and internal links to support `mytunes-pro.com`.
- **Realtime Stability**: Fixed critical state-management bugs in the live dashboard that caused list clearing and duplicated track entries.
- **Improved Empty State**: Redesigned the "SIGNAL LOST" screen into a more descriptive "READY TO RECEIVE" interface for better UX.

### v1.9.8 (Realtime Stabilization)

- **UI Refinement**: Implemented in-list "Now Playing" sticky behavior with auto-scroll synchronization for a seamless browsing experience.
- **Queue System Optimization**: Capped incoming track queue at 200 items with a "200+" notification indicator for high-traffic stability.
- **Popup UI Consistency**: Unified Live Station popup dimensions to 620x900 across Web and TUI.
- **Improved Media Playback**: Optimized the media player hook to resolve initialization race conditions and syntax edge cases.

### v1.9.7 (Analytics)

- **Analytics**: Integrated Google Analytics 4 (GA4) into the landing page and realtime feed to track visitor traffic and usage patterns.

### v1.9.6 (Realtime UX)

- **Incoming Queue System**: The Realtime Feed (`/live`) now queues incoming shared tracks instead of disrupting the list immediately. A "SHOW NEW TRACKS" button appears, allowing users to update the feed at their convenience, ensuring a stable viewing experience.

### v1.9.5

- **Code Cleanup**: Removed deprecated and unreachable WSL subprocess launch logic to ensure codebase cleanliness and prevent confusion. The application now exclusively uses the stable `webbrowser` module for WSL.

### v1.9.4

- **Ultimate WSL Fix**: Switched to using Python's standard `webbrowser` module for opening links in WSL. This fully delegates browser launching to the system (Windows host), ensuring maximum stability and eliminating all `subprocess` or `cmd.exe` related conflicts.

### v1.9.3

- **Hotfix for Startup**: Fixed a syntax error introduced in v1.9.2 that prevented the application from starting.

### v1.9.2

- **Disable WSL Profile Isolation**: To ensure maximum stability and prevent `cmd.exe` conflicts, MyTunes now temporarily disables profile isolation (forced window size/position) on WSL. It runs using the default Chrome profile, guaranteeing reliable launching.

### v1.9.1

- **Fix CMD Output Pollution (WSL)**: Resolved an issue where `cmd.exe` printed "UNC paths are not supported" warnings when executed from a WSL directory, corrupting the temporary path retrieval. Now parses output safely and executes from `/mnt/c` to prevent warnings.

### v1.9.0

- **Fix WSL Profile Error**: Switched to using the **native Windows TEMP directory** (e.g., `C:\Users\...\AppData\Local\Temp`) for the browser profile in WSL. This prevents file locking issues caused by Chrome treating `\\wsl$\` paths as network drives.

### v1.8.9

- **Robust WSL Path Fix**: Resolved an issue where direct browser launching (non-fallback) in WSL was still using Linux paths for the profile, causing "User Data Directory" creation errors. Path conversion is now applied globally before launch.

### v1.8.8

- **WSL Path Conversion**: Implemented `wslpath -w` logic to correctly convert Linux-style temp paths to Windows format when launching Chrome via `cmd.exe` on WSL.

### v1.8.7

- **Syntax Fix (WSL)**: Corrected a typo in the browser launch command that caused a crash on Linux/WSL systems.

### v1.8.6

- **Browser Popup Optimization (Context7)**: Improved Live Station (F8) experience with optimized CLI flags for a perfectly minimalist UI.
- **Forced Window Dimensions**: Implemented profile isolation using a timestamped `user-data-dir` to ensure window size and position are always respected, overriding session memory.
- **UI Cleanup**: Automatically hides distraction-bars (translation, password, automation infobars) and enables instant autoplay for live streams.

### v1.8.5

- **Looping Navigation (Menu Wrapping)**: Pressing UP at the first item now wraps to the last item, and pressing DOWN at the last item wraps to the first.
- **Improved UI Flow**: Enhanced keyboard navigation experience across all list views (Main, Search, Favorites, History).

### v1.8.4

- **Python Crash Fix (WSL)**: Eliminated premature termination by implementing `start_new_session=True` for browser launches, isolating them from the TUI process group.
- **Hybrid Browser Strategy**: Switched to the standard `webbrowser` library for F7 (Media links) for maximum internal stability.
- **Global Error Protection**: Wrapped the main application loop in an exception guard to catch and log transient OS errors without crashing the entire app.
- **Refined Process Cleanup**: Specialized the `pkill` logic to prevent accidental self-termination while maintaining reliable MPV management.

### v1.8.3

- **Direct Binary Execution (WSL)**: Resolved shell parsing issues by bypassing `cmd.exe` and directly executing Windows browser binaries via `/mnt/c/` paths.
- **App Mode Reliability**: Guaranteed 712x800 popup mode by ensuring flags are delivered directly to the browser process without intermediate shell mangling.
- **Fixed URL Resolution**: Eliminated the "Empty URL" bug by standardizing argument passing between WSL and Windows.

### v1.8.1

- **Fixed App Mode (WSL/Win)**: Guaranteed the browser opens in a clean "App Mode" popup by fixing shell quoting issues in the launch command.
- **URL Resolution Fix**: Resolved the "Empty URL" bug on WSL/Windows by ensuring the `--app` flag is correctly parsed by the native Windows shell.
- **Reliable Popup UI**: Standardized on `start "" chrome` for WSL to ensure flags are never misidentified as window titles.

### v1.8.0

- **Stabilized Browser Launch (Windows/WSL)**: Completely removed the `--user-data-dir` flag for all Windows-based environments. This permanently resolves the "cannot read or write" directory errors while maintaining reliable 712x800 window sizing through pure app-mode flags.
- **Clean CMD Execution**: Simplified the WSL-to-Windows transition by using standard `cmd.exe` calls without complex path or variable expansion, ensuring consistent behavior across all systems.

### v1.7.9

- **Pure CMD-based Launch (WSL/Win)**: Final fix for WSL-to-Windows browser launch using `cmd.exe /c` with native `%LOCALAPPDATA%` expansion.
- **Directory Reliability**: Ensured Chrome data directory creation and access by using native Windows shell commands, eliminating the "cannot read or write" errors seen in v1.7.8.
- **Stable Window Sizing**: Guaranteed 712x800 window size for Live Station (F8) from WSL by correctly isolating browser profiles via native Windows paths.

### v1.7.8

- **Native PowerShell Profile Management**: Resolved directory read/write errors in WSL by moving all profile creation and path handling to the Windows side via PowerShell.
- **Improved Security & Isolation**: Profiles are now created in the standard Windows `LOCALAPPDATA` directory with native permissions, ensuring Chrome can always access its data.
- **Backslash Consistency**: Forced backslash-only paths through pure PowerShell logic, fixing the mixed-slash issue seen in WSL.

### v1.7.7

- **PowerShell Launch (WSL/Win)**: Switched to `powershell.exe` for launching browsers from WSL to ensure robust argument parsing and path handling.
- **Directory Fix**: Resolved "cannot read or write" error on Windows/WSL by utilizing `$env:TEMP` directly within a native shell context.
- **Reliable Sizing**: Guaranteed window size application by combining isolated profiles with PowerShell's superior process management.

### v1.7.6

- **Isolated Browser Profile**: Guaranteed window sizing for the Live Station (F8) on Windows/WSL by forcing an isolated browser profile using the Windows `%TEMP%` directory.
- **WSL Path Translation**: Implemented automatic Windows temp path resolution in WSL to enable session persistence and profile isolation.

### v1.7.5

- **WSL Integration**: Fully optimized browser launch from WSL by utilizing `cmd.exe` to trigger native Windows browsers.
- **F7 Windows Resolve**: Fixed an issue where Media links (F7) wouldn't open in WSL environments.
- **F8 App Mode (WSL/Win)**: Enhanced flags to ensure "App Mode" (no address bar) works consistently even when launched from WSL.

### v1.7.4

- **Windows UI Refinement**: Forced Chrome "App Mode" on Windows by reordering flags and disabling extensions/default-apps to ensure a clean popup without an address bar.
- **Improved Isolation**: Switched to higher-frequency session rotation for Live Station (F8) to guarantee window size and position persistence fixes.

### v1.7.3

- **Windows Fixes**: Resolved issue where F7 (Media) failed to open browsers on Windows by implementing `os.startfile` logic.
- **F8 Initialization**: Improved Live Station (F8) window sizing on Windows by forcing a clean session state.
- **Robustness**: Enhanced cross-platform browser redirection logic to ensure consistent behavior.

### v1.7.2

- **Windows Optimization**: Fixed an issue where the Live Station (F8) window size was not correctly applied on Windows.
- **Improved Browser Support**: Added Microsoft Edge to the automatic browser detection list.
- **Robust Launch Logic**: Enhanced browser internal flags for a better initial window experience.

### v1.7.1

- **Performance & Logic Optimization**: Standardized browser launch logic for Live Station (F8) across Mac, Windows, and Linux.
- **UI Polish**: Silenced browser launch warnings in the terminal and added professional UI flags (disable translation/bubble) for a cleaner experience.
- **Improved Popup Behavior**: Optimized web interface to reuse the same window for Live Station, matching CLI application behavior.
- **Global Sync**: Version 1.7.1 synchronization across all platforms.

### v1.6.0

- **Global Version Synchronization**: Synchronized version 1.6.0 across CLI, README, and Web interface.

### v1.5.6

- **Refined Search History Display**: Improved the search preview logic to use a temporary 'search' view state, providing a smoother experience when opening and canceling search.
- **Bug Fix**: Resolved an issue where the 'Search Results History' was not displaying correctly in the background.

### v1.5.5

- **Search Result History**: Automatically saves up to 200 search results.
- **Enhanced Search UX**: Previously searched items are displayed in the background automatically when opening search.
- **Deduplication**: Automatically removes duplicate search results to keep history clean.

### v1.5.4

- **Documentation Refinement**: Clarified installation steps and removed redundant WSL locale guide.
- **Code Cleanup**: Reverted unnecessary locale settings in source code.

### v1.5.3

- **Locale Optimization**: Removed complicated locale generation steps for Windows/WSL users. Now relies on standard system locale or simple `C.UTF-8` fallback.

### v1.5.2

- **Documentation**: Major README overhaul for beginner friendliness. Added dedicated Windows/WSL "Zero-to-Hero" guide.

### v1.5.0

- **Release**: Milestone v1.5.0 release with polished documentation and stable features.
