# 🎵 MyTunes Pro (Korean)

**현대적인 CLI 유튜브 뮤직 플레이어**  
터미널 환경에서 가볍고 빠르게 동작하는 키보드 중심의 뮤직 플레이어입니다.

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

> **[English Verison](README_EN.md)**

## ✨ 주요 기능

- **미니멀리스트 디자인**: 복잡한 박스나 장식 없이 깔끔한 텍스트 UI를 제공합니다.
- **키보드 중심 조작**: 방향키와 단축키로 모든 기능을 제어할 수 있습니다.
- **유튜브 연동**: `yt-dlp`와 `mpv`를 통해 고품질 오디오를 스트리밍합니다.
- **크로스 플랫폼**: macOS 및 Linux (Debian/Ubuntu) 환경에 최적화되어 있습니다.
- **스마트 기능**: 즐겨찾기, 재생 기록 저장, 자동 완성 검색 기능을 지원합니다.

## 🛠 필수 요구사항

시스템에 **mpv** (플레이어)와 **yt-dlp** (스트리밍 도구)가 설치되어 있어야 합니다.

### macOS

```bash
brew install mpv yt-dlp
```

### Linux (Debian/Ubuntu)

```bash
sudo apt update
sudo apt install mpv
pip install -U yt-dlp
```

## 🚀 설치 및 사용법

1. **저장소 복제 (Clone)**

   ```bash
   git clone https://github.com/postgresql-co-kr/mytunes.git
   cd mytunes
   ```

2. **가상 환경 설정**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **의존성 패키지 설치**

   ```bash
   pip install -r requirements.txt
   ```

4. **실행 (한국어 버전)**

   ```bash
   python mytune.py
   ```

   **(English Version)**

   ```bash
   python mytune_en.py
   ```

## ⌨️ 조작 방법

| 키 | 동작 |
| :--- | :--- |
| **이동** | **메뉴 탐색** |
| `↑` / `↓` | 항목 선택 이동 |
| `Enter` | 선택 / 재생 |
| `/` | **음악 검색** |
| `q` | 뒤로 가기 / 종료 |

---
**Troubleshooting**: If you encounter `403 Forbidden` errors, please update yt-dlp:
```bash
pip install -U yt-dlp
```

---
[postgresql.co.kr](https://postgresql.co.kr)
