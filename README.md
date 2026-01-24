# 🎵 MyTunes Pro (Korean)

**현대적인 CLI 유튜브 뮤직 플레이어 (v1.4.4)**  
터미널 환경에서 **YouTube 음악을 검색하여 듣는** 가볍고 빠른 키보드 중심의 플레이어입니다.  
한국어 입력 환경에서도 **숫자 키(1~5)**를 통해 지연 없는 쾌적한 조작이 가능합니다.

> **💡 개발 배경**  
> 이 프로그램은 하루 종일 터미널을 보는 개발자들이 **작업 흐름을 끊지 않고** 편하게 음악을 듣기 위해 만들어졌습니다.  
> 특히 **모니터가 없는(Headless) 미니 PC (Debian Server)**를 거실이나 책상의 '뮤직 스테이션'으로 활용하고자 했던 개인적인 필요에서 시작되었습니다.  
> 복잡한 설정 없이, 터미널 하나만 있으면 어디서든 당신만의 오디오 플레이어가 됩니다.

![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## 📸 Screenshots
| | |
| :---: | :---: |
| ![Main](screenshots/screenshot_1.webp) | ![Search](screenshots/screenshot_2.webp) |
| ![Play](screenshots/screenshot_3.webp) | ![List](screenshots/screenshot_4.webp) |

---

## ✨ 주요 기능

- **강력한 검색**: `yt-dlp` 엔진을 사용하여 광고 없는 고음질 오디오 스트리밍.
- **쾌적한 조작**: `curses` 기반 TUI로 빠르고 직관적인 인터페이스.
- **연속 재생**: 한 곡이 끝나면 **리스트의 다음 곡을 자동으로 재생**합니다.
- **이어듣기**: 중단된 위치부터 **이어서 재생**할지 선택할 수 있습니다.
- **한글 최적화**: 한글 자소 조합 대기 시간 없이 즉시 반응하는 **숫자 단축키** 지원.
- **스마트 기능**: 즐겨찾기, 재생 기록(최대 100곡), 자동 음악 필터링 검색.
- **비주얼**: 현대적인 심볼 아이콘(⌕, ★, ◷)과 깔끔한 디자인.

이 프로그램은 오디오 재생을 위해 **mpv**가 시스템에 설치되어 있어야 합니다. (검색 엔진 `yt-dlp`는 자동 설치됩니다.)

## 🚀 빠른 설치 (Quick Install)

터미널에서 아래 명령어를 입력하여 즉시 설치하세요:

```bash
pip install mytunes-pro
```

설치 후 터미널 어디서든 **`mytunes`**를 입력하면 실행됩니다!

---

## 🛠 상세 설치 가이드

### macOS

Homebrew를 통해 필수 도구를 설치하고 아래 가이드를 따르세요.

1. **필수 도구 설치**:

   ```bash
   brew install mpv yt-dlp python3
   ```

2. **프로그램 다운로드 및 설정**:

   ```bash
   git clone https://github.com/postgresql-co-kr/mytunes.git
   cd mytunes
   python3 -m venv venv
   venv/bin/pip install -r requirements.txt
   ```

3. **단축축 아이콘 만들기 (zsh 기준)**:

   ```bash
   echo "alias mp='~/mytunes/venv/bin/python3 ~/mytunes/mytune.py'" >> ~/.zshrc
   source ~/.zshrc
   ```

4. **실행**:
   터미널 어디서든 **`mp`**를 입력하세요!

### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install mpv python3 python3-pip python3-venv
```

### Windows (WSL) - 초보자용 완전 정복 가이드

Windows 사용자라면 이 가이드만 따라하세요. (복사 & 붙여넣기만 하면 됩니다!)

**1단계: WSL 및 Debian 설치**
1. **`Windows` 키 + `X`** -> **Windows PowerShell (관리자)** 실행.
2. 아래 명령어 복사 & 붙여넣기 후 엔터:
   ```powershell
   wsl --install -d Debian
   ```
3. 설치 완료 메시지가 뜨면 **재부팅**합니다.

**2단계: 윈도우 터미널 설정 (필수)**
기본 터미널보다 훨씬 편리한 **Windows Terminal** 사용을 강력 추천합니다.

1. **설치 및 실행**:
   - **`Win` + `X`** -> **터미널** 실행 (없다면 Microsoft Store에서 설치).
   - 아이콘 우클릭 -> **작업 표시줄에 고정**.
2. **기본값 설정 (편의성 UP)**:
   - 터미널 설정(`Ctrl` + `,`) -> **[시작]** 탭 -> **기본 프로필**을 **Debian**으로 변경 후 저장.
   - 이제 터미널을 켜면 Debian이 바로 열립니다!
3. **폰트 설정 (선택)**:
   - 화면이 깨진다면 **[D2Coding](https://github.com/naver/d2codingfont/releases)** 폰트 설치를 권장합니다.
   - 설정 -> **Debian** 프로필 -> **[모양]** -> **글꼴**에서 **D2Coding** 선택.

**3단계: 계정 설정 및 필수 도구 설치**
1. **Debian** 창이 열리면 **User Name**(영문), **Password** 설정.
2. 설정 완료 후, 아래 박스 내용을 **한 번에 복사**해서 터미널에 붙여넣고 엔터! (비밀번호 입력)
   ```bash
   sudo apt update && sudo apt install git curl wget unzip mpv python3 python3-venv -y
   ```

**4단계: MyTunes 설치 및 실행**
이제 프로그램을 다운로드하고 실행합니다. 아래 내용을 한 줄씩 입력하세요.

1. **설치하기**:
   ```bash
   git clone https://github.com/postgresql-co-kr/mytunes.git
   cd mytunes
   python3 -m venv venv
   venv/bin/pip install -r requirements.txt
   ```

2. **단축 아이콘 만들기 (한 번만 실행)**:
   ```bash
   echo "alias mp='~/mytunes/venv/bin/python3 ~/mytunes/mytune.py'" >> ~/.bashrc
   source ~/.bashrc
   ```

3. **실행**:
   참 쉽죠? 이제 언제든지 **`mp`** 입력하면 실행됩니다!
   ```bash
   mp
   ```
4. **최신 버전으로 업데이트**:
   새로운 기능이나 버그 수정이 있을 때 아래 명령어로 간단히 업데이트할 수 있습니다.
   ```bash
   cd ~/mytunes
   git pull
   ```

---

## ⌨️ 조작 방법 (Controls)

**MyTunes Pro**는 키보드만으로 모든 기능을 제어합니다.  
한글 입력 상태에서도 끊김 없는 조작을 위해 **숫자 단축키** 사용을 권장합니다.
(한글 입력 중에는 알파벳 단축키가 즉시 인식되지 않을 수 있으므로, 숫자키나 Enter를 활용하세요.)

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
| **`6`** | **뒤로가기** | 이전 화면으로 이동 (단축키 `Q`, `H`와 동일) |
| **`ESC`** | **배경재생** | **음악 끄지 않고 나가기** (백그라운드 재생) |

### 🧭 기본 탐색
| 키 | 동작 |
| :--- | :--- |
| `↑` / `↓` / `k` / `j` | 리스트 위/아래 이동 (Vim 키 지원) |
| `Enter` / `l` | **선택 / 재생** (한글 `ㅣ`도 지원) |
| `Space` | 재생 / 일시정지 (Play/Pause) |
| `-` / `+` | **볼륨 조절** (- / +) |
| `,` / `.` | 10초 뒤로 / 앞으로 감기 |
| `<` / `>` | **30초** 뒤로 / 앞으로 감기 (Shift) |
| `Backspace` / `h` / `q` | 뒤로 가기 / 검색어 지우기 |
| `/` | **검색** (Vim Style) |

---

## 📂 데이터 저장
- 즐겨찾기와 재생 기록은 홈 디렉토리의 `~/.pymusic_data.json` 파일에 영구 저장됩니다.
- 프로그램 종료 후 다시 실행해도 데이터가 유지됩니다.

---
---

# 🎵 MyTunes Pro (English)

**Modern CLI YouTube Music Player (v1.4.4)**  
A lightweight, keyboard-centric terminal player for streaming YouTube music.  
Designed for speed and efficiency, with optimized controls for international keyboard imports.

> **💡 Preface**  
> This project was created to give developers a seamless way to enjoy music without leaving their terminal environment.  
> It basically started from a personal need to turn a **headless mini-PC running Debian Server** into a dedicated living room music station (with no monitor or GUI).  
> Just bring your terminal, and you have a full-featured audio player.

## ✨ Key Features
- **Powerful Search**: High-quality audio streaming via `yt-dlp`.
- **Pagination**: Explicit **[ Load Next 20... ]** button to load more results.
- **Sequential Play**: Automatically plays the next song in the list.
- **Smart Resume**: Option to resume playback from where you left off.
- **Fast TUI**: Responsive `curses` interface.
- **Smart Shortcuts**: Instant number keys (1-5) for quick navigation.
- **Visuals**: Clean aesthetic with system-style glyphs (⌕, ★, ◷).

## 🛠 Prerequisites

### macOS

Follow these steps to set up everything on your Mac.

1. **Install Prerequisites**:

   ```bash
   brew install mpv yt-dlp python3
   ```

2. **Clone & Setup**:

   ```bash
   git clone https://github.com/postgresql-co-kr/mytunes.git
   cd mytunes
   python3 -m venv venv
   venv/bin/pip install -r requirements.txt
   ```

3. **Create Alias (zsh)**:

   ```bash
   echo "alias mp='~/mytunes/venv/bin/python3 ~/mytunes/mytune.py'" >> ~/.zshrc
   source ~/.zshrc
   ```

4. **Run**:
   Just type **`mp`** anywhere!

### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install mpv python3 python3-pip python3-venv
```

### Windows (WSL) - Complete Beginner's Guide

Follow these steps to install everything from scratch. Just copy & paste!

**Step 1: Install WSL & Debian**
1. Press **`Windows` + `X`** -> Select **PowerShell (Admin)**.
2. Copy & paste this command and Enter:
   ```powershell
   wsl --install -d Debian
   ```
3. **Restart** computer.

**Step 2: Windows Terminal Setup (Recommended)**
Use **Windows Terminal** for the best experience.

1. **Install & Run**:
   - Press **`Win` + `X`** -> Open **Terminal** (Or install from Microsoft Store).
   - Right-click icon -> **Pin to Taskbar**.
2. **Set Default Profile**:
   - Open Settings (`Ctrl` + `,`) -> **Startup** -> Change **Default profile** to **Debian**.
   - Save. Now Debian opens automatically when you launch Terminal!
3. **Font Setup (Optional)**:
   - If icons look weird, install a **[Nerd Font](https://www.nerdfonts.com/)** (e.g., Cascadia Code NF).
   - Go to Settings -> **Debian** -> **Appearance** -> **Font face**.

**Step 3: Account & Tool Setup**
1. After restart (or in new Debian tab), set **User Name** and **Password**.
2. Copy & paste this block to install tools (Type password when asked):
   ```bash
   sudo apt update && sudo apt install git curl wget unzip mpv python3 python3-venv -y
   ```

**Step 4: Download & Install**
Run these commands one by one:

1. **Install App**:
   ```bash
   git clone https://github.com/postgresql-co-kr/mytunes.git
   cd mytunes
   python3 -m venv venv
   venv/bin/pip install -r requirements.txt
   ```

2. **Create Shortcut (One-time setup)**:
   ```bash
   echo "alias mp='~/mytunes/venv/bin/python3 ~/mytunes/mytune.py'" >> ~/.bashrc
   source ~/.bashrc
   ```

3. **Run**:
   Just type **`mp`** anytime!
   ```bash
   mp
   ```
4. **How to Update**:
   You can easily update to the latest version with new features or bug fixes.
   ```bash
   cd ~/mytunes
   git pull
   ```

## ⌨️ English Controls

### ⚡️ Instant Shortcuts (Number Keys)
Works instantly even with non-English keyboard layouts.

| Key | Function | Description |
| :--- | :--- | :--- |
| **`1`** | **Search** | Open search bar (Same as `S`) |
| **`2`** | **Favs** | View favorites list (Same as `F`) |
| **`3`** | **Hist** | View history (Same as `R`) |
| **`4`** | **Main** | Go to Main Menu (Same as `M`) |
| **`5`** | **Add/Del** | Toggle Favorite (Same as `A`) |
| **`+`** | **Vol Up** | Volume +5% (Same as `=`) |
| **`-`** | **Vol Down** | Volume -5% (Same as `_`) |
| **`6`** | **Back** | Go back (Same as `Q`, `H`) |
| **`ESC`** | **Bg Play** | **Exit app but keep music playing** |

### 🧭 Navigation
| Key | Action |
| :--- | :--- |
| `↑` / `↓` / `k` / `j` | Move selection (Vim style supported) |
| `Enter` / `l` | **Select / Play** (Includes `L`) |
| `Space` | Play / Pause |
| `Space` | Play / Pause |
| `-` / `+` | **Volume** (- / +) |
| `,` / `.` | Seek -10s / +10s |
| `<` / `>` | **Seek -30s / +30s** (Shift) |
| `Backspace` / `h` / `q` | Go back |
| `/` | **Search** (Vim Style) |
