#!/usr/bin/env python3
"""
MyTunes Pro - Modern CLI YouTube Music Player
A professional-grade terminal music player with keyboard-friendly controls.
Supports Debian Linux and macOS.
"""
import os
import json
import subprocess
import socket
import time
import sys
import shutil
import unicodedata
import readline  # For proper Korean input handling

try:
    from simple_term_menu import TerminalMenu
except ImportError:
    print("\n❌ 필수 라이브러리가 없습니다: simple-term-menu")
    print("   pip install simple-term-menu")
    sys.exit(1)

# === [Dependencies] ===
# Removed rich imports

try:
    import psutil
except ImportError:
    print("\n❌ 필수 라이브러리가 없습니다: psutil")
    print("   pip install psutil")
    sys.exit(1)

# === [Configuration] ===
DATA_FILE = os.path.expanduser("~/.pymusic_data.json")
MPV_SOCKET = "/tmp/mpv_socket"
APP_NAME = "MyTunes Pro"
APP_VERSION = "2.0.0"



# === [Theme Colors] ===
THEME = {
    "primary": "\033[96m",   # Cyan
    "secondary": "\033[95m", # Magenta
    "accent": "\033[93m",    # Yellow
    "success": "\033[92m",   # Green
    "warning": "\033[93m",   # Yellow
    "error": "\033[91m",     # Red
    "muted": "\033[90m",     # Grey
    "reset": "\033[0m"       # Reset
}

# === [Data Management] ===

def load_data() -> dict:
    """Load saved data from file."""
    if not os.path.exists(DATA_FILE):
        return {"history": [], "favorites": []}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {"history": [], "favorites": []}

def save_data(data: dict) -> None:
    """Save data to file."""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_status() -> tuple[str, str]:
    """Check if mpv is running. Returns (status_text, style)."""
    for proc in psutil.process_iter(['name']):
        try:
            if proc.info['name'] and 'mpv' in proc.info['name'].lower():
                return ("● PLAYING", THEME["success"])
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return ("○ STOPPED", THEME["muted"])

# === [Music Playback] ===

def stop_music() -> None:
    """Stop all mpv processes gracefully."""
    for proc in psutil.process_iter(['name']):
        try:
            if proc.info['name'] and 'mpv' in proc.info['name'].lower():
                proc.terminate()
                proc.wait(timeout=3)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
            pass
    time.sleep(0.2)

def play_stream(url: str) -> None:
    """Play a YouTube URL with mpv. Passes original URL to allow mpv to load chapters."""
    stop_music()
    
    if os.path.exists(MPV_SOCKET):
        try:
            os.remove(MPV_SOCKET)
        except OSError:
            pass
    
    # Use preexec_fn=os.setpgrp for Linux/macOS stability in background
    popen_kwargs = {"stdout": subprocess.DEVNULL, "stderr": subprocess.DEVNULL}
    if os.name != "nt":
        popen_kwargs["preexec_fn"] = os.setpgrp
        
    subprocess.Popen(
        ["mpv", "--no-video", f"--input-ipc-server={MPV_SOCKET}", url],
        **popen_kwargs
    )

def send_mpv_cmd(command: list) -> bool:
    """Send IPC command to mpv."""
    try:
        if not os.path.exists(MPV_SOCKET):
            return False
        
        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        client.settimeout(1.0)
        client.connect(MPV_SOCKET)
        
        cmd_str = json.dumps({"command": command}) + "\n"
        client.send(cmd_str.encode('utf-8'))
        client.close()
        return True
        return True
    except (socket.error, OSError):
        return False

def get_mpv_property(prop: str):
    """Get a property from mpv via IPC."""
    try:
        if not os.path.exists(MPV_SOCKET):
            return None
        
        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        client.settimeout(1.0)
        client.connect(MPV_SOCKET)
        
        cmd = {"command": ["get_property", prop]}
        client.send((json.dumps(cmd) + "\n").encode('utf-8'))
        
        response = client.recv(4096).decode('utf-8')
        client.close()
        
        data = json.loads(response)
        return data.get("data")
    except (socket.error, OSError, json.JSONDecodeError):
        return None

def add_to_history(item: dict, data: dict) -> None:
    """Add item to history (remove duplicates, limit to 50)."""
    new_history = [h for h in data['history'] if h['url'] != item['url']]
    new_history.insert(0, item)
    data['history'] = new_history[:50]
    save_data(data)

# === [Spinner (Original)] ===

class Spinner:
    """Thread-based spinner for search indication."""
    def __init__(self, message="검색 중..."):
        self.message = message
        self.stop_running = False
        self.thread = None
        import itertools
        self.cycle = itertools.cycle(['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'])

    def start(self):
        import threading
        self.stop_running = False
        self.thread = threading.Thread(target=self._animate)
        self.thread.start()

    def stop(self):
        self.stop_running = True
        if self.thread:
            self.thread.join()

    def _animate(self):
        while not self.stop_running:
            sys.stdout.write(f'\r\033[K{next(self.cycle)} {self.message}')
            sys.stdout.flush()
            time.sleep(0.08)
        sys.stdout.write('\r\033[K')
        sys.stdout.flush()

# === [YouTube Search] ===

def search_youtube(query: str) -> list:
    """Search YouTube and return video list."""
    videos = []
    spinner = Spinner(f"'{query}' 검색 중...")
    spinner.start()
    
    try:
        cmd = [
            "yt-dlp", f"ytsearch10:{query}", "--dump-json",
            "--flat-playlist", "--no-playlist", "--skip-download"
        ]
        result = subprocess.check_output(
            cmd, stderr=subprocess.DEVNULL, timeout=20
        ).decode("utf-8")
        
        for line in result.strip().split("\n"):
            if line:
                try:
                    d = json.loads(line)
                    url = d.get("url")
                    if not url or "http" not in url:
                        url = f"https://www.youtube.com/watch?v={d.get('id')}"
                    
                    duration = d.get("duration", 0)
                    if duration:
                        mins, secs = divmod(int(duration), 60)
                        duration_str = f"{mins}:{secs:02d}"
                    else:
                        duration_str = "--:--"
                    
                    videos.append({
                        "title": d.get("title", "Unknown Title"),
                        "url": url,
                        "duration": duration_str,
                        "channel": d.get("channel", d.get("uploader", "Unknown"))
                    })
                except json.JSONDecodeError:
                    continue
                    
    except subprocess.TimeoutExpired:
        print("\n⏱ 검색 시간 초과")
        time.sleep(1.5)
    except subprocess.CalledProcessError as e:
        print(f"\n❌ 검색 오류: {e}")
        time.sleep(1.5)
    except FileNotFoundError:
        print("\n❌ yt-dlp가 설치되지 않았습니다")
        time.sleep(1.5)
    finally:
        spinner.stop()
    
    return videos

# Legacy UI components removed

def truncate_title(title: str, max_width: int) -> str:
    """Truncate title considering wide characters."""
    current_width = 0
    result = ""
    
    for char in title:
        char_width = 2 if unicodedata.east_asian_width(char) in ('W', 'F', 'A') else 1
        if current_width + char_width > max_width - 2:
            result += "…"
            break
        current_width += char_width
        result += char
    
    return result

# === [Menu Functions] ===

def show_list_menu(items: list, data: dict, title: str) -> None:
    """Display a list menu and enter player controller on selection."""
    if not items:
        print(f"\n[{THEME['warning']}]📭 목록이 비어있습니다[/]")
        time.sleep(1)
        return
    
    try:
        cols = shutil.get_terminal_size().columns
    except OSError:
        cols = 80
    
    # Format menu items with duration and channel info
    menu_items = []
    for i, item in enumerate(items):
        num = f"{i+1:2d}."
        duration = item.get('duration', '')
        channel = item.get('channel', '')
        
        # Calculate available width for title
        prefix_len = len(num) + 1
        suffix = ""
        if duration:
            suffix = f" [{duration}]"
        if channel and cols > 80:
            suffix = f" │ {channel[:15]}{suffix}"
        
        max_title_width = min(cols - prefix_len - len(suffix) - 8, 60)  # Cap at 60 chars
        truncated = truncate_title(item['title'], max(max_title_width, 20))
        
        menu_items.append(f"{num} {truncated}{suffix}")
    
    menu_items.append("")  # Separator
    menu_items.append("◀ 뒤로 가기 (Back)")
    
    # Truncate title for menu header
    try:
        cols = shutil.get_terminal_size().columns
    except OSError:
        cols = 80
    
    truncated_menu_title = truncate_title(title, cols - 10)
    
    # Clear screen like original code
    os.system('clear')
    
    menu = TerminalMenu(
        menu_items,
        title=f"  🎵 {truncated_menu_title}\n  {'─' * min(40, cols - 6)}\n",
        menu_cursor="  ❯ ",
        menu_cursor_style=("fg_cyan", "bold"),
        menu_highlight_style=("bg_blue", "bold"),
        cycle_cursor=True,
        clear_screen=True,
        skip_empty_entries=True,
    )
    
    idx = menu.show()
    
    if idx is not None and idx < len(items):
        player_controller(items, idx, data)

def player_controller(playlist: list, start_index: int, data: dict) -> None:
    """Full-featured player controller with keyboard navigation."""
    current_index = start_index
    
    # Start playback
    current_item = playlist[current_index]
    play_stream(current_item['url'])
    add_to_history(current_item, data)
    
    while True:
        current_item = playlist[current_index]
        title = current_item['title']
        
        # Check favorite status
        is_fav = any(f['url'] == current_item['url'] for f in data['favorites'])
        fav_icon = "★" if is_fav else "☆"
        fav_action = "즐겨찾기 해제 (Unfavorite)" if is_fav else "즐겨찾기 등록 (Favorite)"
        
        # Now Playing display - simplified
        try:
            cols = shutil.get_terminal_size().columns
        except OSError:
            cols = 80
        
        truncated_title = truncate_title(title, min(cols - 10, 50))
        
        player_title = (
            f"\n 🎵 NOW PLAYING [{current_index + 1}/{len(playlist)}]\n"
            f" {'─' * 35}\n"
            f"  {truncated_title}\n"
            f" {'─' * 35}"
        )
        
        # Player controls menu
        options = [
            "▶▶ 다음 챕터 (Chapter Next)",
            "◀◀ 이전 챕터 (Chapter Prev)",
            "⏭  다음 곡 (Next Track)",
            "⏮  이전 곡 (Prev Track)",
            "⏯  재생/일시정지 (Pause/Resume)",
            f"{fav_icon}  {fav_action}",
            "⏹  정지 (Stop)",
            "◀  메뉴로 돌아가기 (Back)",
        ]
        
        menu = TerminalMenu(
            options,
            title=player_title,
            menu_cursor="➤ ",
            menu_cursor_style=("fg_green", "bold"),
            menu_highlight_style=("bg_blue", "bold"),
            cycle_cursor=True,
            clear_screen=True,
        )
        
        idx = menu.show()
        
        if idx == 0:  # Chapter Next
            send_mpv_cmd(["add", "chapter", "1"])
        elif idx == 1:  # Chapter Prev
            send_mpv_cmd(["add", "chapter", "-1"])
        elif idx == 2:  # Next Track
            current_index = (current_index + 1) % len(playlist)
            current_item = playlist[current_index]
            play_stream(current_item['url'])
            add_to_history(current_item, data)
        elif idx == 3:  # Prev Track
            current_index = (current_index - 1) % len(playlist)
            current_item = playlist[current_index]
            play_stream(current_item['url'])
            add_to_history(current_item, data)
        elif idx == 4:  # Pause/Resume
            send_mpv_cmd(["cycle", "pause"])
        elif idx == 5:  # Toggle Favorite
            if is_fav:
                data['favorites'] = [f for f in data['favorites'] if f['url'] != current_item['url']]
            else:
                data['favorites'].insert(0, current_item)
            save_data(data)
        elif idx == 6:  # Stop
            stop_music()
            break
        elif idx == 7 or idx is None:  # Back
            break

def get_status_text() -> str:
    """Check if mpv is running and return status string."""
    for proc in psutil.process_iter(['name']):
        try:
            if proc.info['name'] and 'mpv' in proc.info['name'].lower():
                return "🔊 재생 중"
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return "🔇 정지됨"

def main() -> None:
    """Main application loop."""
    while True:
        data = load_data()
        status = get_status_text()
        
        # Build dashboard (original style)
        dash = (
            f"\n 🎵 MyTunes Pro v{APP_VERSION}\n"
            f"  :::::postgresql.co.kr:::::\n"
            f" {'─' * 35}\n"
            f"  상태: {status}\n"
            f"  보관: ⭐ {len(data['favorites'])} / 🕒 {len(data['history'])}\n"
            f" {'─' * 35}\n"
            f"  [↑↓] 이동  [Enter] 선택  [q] 종료"
        )
        
        options = [
            "🔍 검색 및 재생",
            "⭐ 즐겨찾기 보관함",
            "🕒 최근 재생 기록",
            "⏹  재생 정지",
            "🚪 프로그램 종료"
        ]
        
        main_menu = TerminalMenu(
            options,
            title=dash,
            menu_cursor="➤ ",
            menu_cursor_style=("fg_yellow", "bold"),
            menu_highlight_style=("bg_blue", "bold"),
            cycle_cursor=True,
            clear_screen=True,
            accept_keys=("enter", "/"),
        )
        
        choice = main_menu.show()
        
        # "/" key triggers search
        if main_menu.chosen_accept_key == "/":
            choice = 0
        
        if choice == 0:  # Search
            os.system('clear')
            try:
                import termios
                termios.tcflush(sys.stdin, termios.TCIOFLUSH)
            except (ImportError, Exception):
                pass
            try:
                # Add "Back" hint to the prompt
                query = input("\n🔎 검색어 입력 (Enter는 뒤로): ").strip()
            except EOFError:
                query = ""
            except KeyboardInterrupt:
                query = ""
                
            if query and query.lower() not in ("back", "b"):
                results = search_youtube(query)
                show_list_menu(results, data, f"검색 결과: {query}")
                
        elif choice == 1:  # Favorites
            show_list_menu(data['favorites'], data, "⭐ 즐겨찾기")
            
        elif choice == 2:  # History
            show_list_menu(data['history'], data, "🕒 최근 재생")
            
        elif choice == 3:  # Stop
            stop_music()
            
        elif choice == 4 or choice is None:  # Exit
            os.system('clear')
            print("\n👋 종료합니다.\n")
            break

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        os.system('clear')
        sys.exit(0)
