#!/usr/bin/env python3
"""
MyTunes Pro - Professional TUI Edition v1.0
# Premium CLI Media Workflow Experiment with Curses Interface
Enhanced with Context7-researched MPV IPC & Resize Handling
"""
import warnings
# Suppress urllib3 NotOpenSSLWarning (LibreSSL compatibility)
# This must be defined before ANY imports that might trigger urllib3
warnings.filterwarnings("ignore", message=".*urllib3 v2 only supports OpenSSL 1.1.1+.*")

try:
    import urllib3
    # Optional: also ignore by category if already imported
    from urllib3.exceptions import NotOpenSSLWarning
    warnings.filterwarnings("ignore", category=NotOpenSSLWarning)
except: pass

import curses
import curses.textpad
import json
import os
import subprocess
import sys
import threading
import time
import unicodedata
import socket
import locale
import signal
import warnings
import webbrowser
import tempfile
import shutil
import requests


# Ensure Unicode support
# locale.setlocale(locale.LC_ALL, '')

# === [Configuration] ===
DATA_FILE = os.path.expanduser("~/.pymusic_data.json")
MPV_SOCKET = "/tmp/mpv_socket"
LOG_FILE = "/tmp/mytunes_mpv.log"
PID_FILE = "/tmp/mytunes_mpv.pid"
APP_NAME = "MyTunes Pro"
APP_VERSION = "2.1.0"

# Initial Locale Setup for WSL/Windows Multibyte/Emoji Harmony
try:
    import locale
    locale.setlocale(locale.LC_ALL, '')
except:
    pass

# WSL Detection: EQ/IPC robustness logic
IS_WSL = False
if hasattr(os, 'uname'):
    try:
        IS_WSL = "microsoft" in os.uname().release.lower()
    except: pass


# === [Strings & Localization] ===
STRINGS = {
    "ko": {
        "title": "MyTunes Pro v{}",
        "search_label": "검색",
        "fav_label": "즐겨찾기",
        "hist_label": "최근 재생",
        "quit_label": "⏻ 완전 종료 (음악 끔)",
        "search_prompt": "검색어 입력: ",
        "searching": "검색 중입니다... 잠시만 기다려주세요.",
        "no_results": "검색 결과가 없습니다.",
        "empty_list": "리스트가 비어있습니다.",
        "playing": "▶ {}",
        "paused": "❚❚ {}",
        "stopped": "⏹ 정지됨",
        "fav_added": "★ 즐겨찾기에 추가됨",
        "fav_removed": "☆ 즐겨찾기 해제됨",
        "header_r1": "[S/1]검색 [F/2]즐겨찾기 [R/3]기록 [M/4]메인 [A/5]즐겨찾기추가 [Q/6]뒤로",
        "header_r1": "[S/1]검색 [F/2]즐겨찾기 [R/3]기록 [M/4]메인 [A/5]즐겨찾기추가 [Q/6]뒤로",
        "header_r2": "[F7]유튜브 [E]이퀄라이저 [SPC]Play/Stop [+/-]볼륨 [D/Del]삭제",
        "help_guide": "[j/k]이동 [En]선택 [h/q]뒤로 [S/1]검색 [F/2]즐겨찾기 [R/3]기록 [M/4]메인 [F7]유튜브",
        "menu_main": "☰ 메인 메뉴",
        "menu_search_results": "⌕ 미디어 콘텐츠 검색",
        "menu_favorites": "★ 나의 즐겨찾기",
        "menu_history": "◷ 재생 기록",
        "menu_bg_play": "⧉ 백그라운드 재생 (나가기)",
        "lang_toggle": "⚙ 언어 변경 (English)",
        "favorites_info": "즐겨찾기 저장 위치: {}",
        "hist_info": "최근 재생 기록 (최대 100곡)",
        "time_fmt": "{}/{}",
        "vol_fmt": "볼륨: {}%",
        "ime_warning": "영문 모드로 전환 후 단축키를 눌러주세요.",
        "invalid_key": "잘못된 키 입력: '{}'"
    },
    "en": {
        "title": "MyTunes Pro v{}",
        "search_label": "Search",
        "fav_label": "Favorites",
        "hist_label": "History",
        "quit_label": "⏻ Full Quit (Stop Music)",
        "search_prompt": "Search Query: ",
        "searching": "Searching... Please wait.",
        "no_results": "No results found.",
        "empty_list": "List is empty.",
        "playing": "▶ {}",
        "paused": "❚❚ {}",
        "stopped": "⏹ Stopped",
        "fav_added": "★ Added to Favorites",
        "fav_removed": "☆ Removed from Favorites",
        "header_r1": "[S/1]Srch [F/2]Favs [R/3]Hist [M/4]Main [A/5]AddFav [Q/6]Back",
        "header_r1": "[S/1]Srch [F/2]Favs [R/3]Hist [M/4]Main [A/5]AddFav [Q/6]Back",
        "header_r2": "[F7]YT [E]EQ [SPC]Play/Stop [+/-]Vol [<>]Seek [D/Del]Del",
        "help_guide": "[j/k]Move [En]Select [h/q]Back [S/1]Srch [F/2]Fav [R/3]Hist [M/4]Main [F7]YT",
        "menu_main": "☰ Main Menu",
        "menu_search_results": "⌕ Search Media Content",
        "menu_favorites": "★ My Favorites",
        "menu_history": "◷ History",
        "menu_bg_play": "⧉ Background Play (Leave)",
        "lang_toggle": "⚙ Switch Language (한국어)",
        "favorites_info": "Favorites stored at: {}",
        "hist_info": "Recent Playback History (Max 100)",
        "time_fmt": "{}/{}",
        "vol_fmt": "Vol: {}%",
        "ime_warning": "Switch to English for shortcuts.",
        "invalid_key": "Invalid key: '{}'"
    }

}

# === [Audio Presets] ===
# === [Audio Presets] ===
# Standard "Most Used" Presets (Amplified/Professional tuned)
EQUALIZER_PRESETS = {
    "Flat":      [0] * 10,
    "Pop":       [-2, -1, 3, 5, 5, 4, 2, 0, -1, -2],   # Vocals punchy
    "Rock":      [5, 4, 3, -2, -4, -3, 0, 3, 5, 5],    # V-Shape (Bass/Highs)
    "Jazz":      [4, 4, 2, 6, 6, 6, 2, 4, 8, 8],       # Balanced warmth
    "Classical": [0, 6, 6, 3, 0, 0, 3, 6, 8, 8],       # Clean & Airy
    "Full Bass": [8, 8, 8, 5, 2, 0, 0, 0, 0, 0],       # Bass focus (Safe)
    "Dance":     [6, 8, 4, 0, 0, 0, 4, 6, 6, 6],       # Beat driven
    "Club":      [0, 0, 4, 6, 6, 6, 4, 0, 0, 0],       # Mid-bass punch
    "Live":      [-4, 0, 2, 4, 5, 5, 4, 2, 3, 4],      # Stadium feel
    "Soft":      [2, 2, 1, 0, 0, 0, -1, -2, -3, -4]    # Easy listening
}
EQUALIZER_KEYS = ["Auto"] + list(EQUALIZER_PRESETS.keys())

class DataManager:
    def __init__(self):
        self.data = self.load_data()
        self.favorites_set = {f['url'] for f in self.data.get('favorites', []) if 'url' in f}
        self.lock = threading.Lock()
        
        # Auto-fetch country if missing
        if 'country' not in self.data:
             threading.Thread(target=self.fetch_country, daemon=True).start()

        
    def load_data(self):
        if not os.path.exists(DATA_FILE):
            return {"history": [], "favorites": [], "language": "ko", "resume": {}, "search_results_history": []}
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if "resume" not in data: data["resume"] = {}
                if "search_results_history" not in data: data["search_results_history"] = []
                return data
        except Exception:
            return {"history": [], "favorites": [], "language": "ko", "resume": {}, "search_results_history": []}

    def save_data(self):
        with self.lock:
            try:
                with open(DATA_FILE, "w", encoding="utf-8") as f:
                    json.dump(self.data, f, indent=2, ensure_ascii=False)
            except Exception: pass

    def get_progress(self, url):
        return self.data.get("resume", {}).get(url, 0)

    def set_progress(self, url, time_pos):
        if "resume" not in self.data: self.data["resume"] = {}
        self.data["resume"][url] = time_pos
        # Limit resume data to 500 entries (FIFO cleanup)
        if len(self.data["resume"]) > 500:
            # Remove oldest entries (first 100)
            keys = list(self.data["resume"].keys())
            for k in keys[:100]:
                del self.data["resume"][k]

    def add_history(self, item):
        self.data['history'] = [h for h in self.data['history'] if h['url'] != item['url']]
        self.data['history'].insert(0, item)
        self.data['history'] = self.data['history'][:100]
        self.save_data()

    def toggle_favorite(self, item):
        url = item.get('url')
        if not url: return False
        is_fav = url in self.favorites_set
        if is_fav:
            self.data['favorites'] = [f for f in self.data['favorites'] if f.get('url') != url]
            self.favorites_set.remove(url)
            status = False
        else:
            self.data['favorites'].insert(0, item)
            self.favorites_set.add(url)
            status = True
        self.save_data()
        return status

    def is_favorite(self, url):
        return url in self.favorites_set

    def fetch_country(self):
        """Fetch country code asynchronously and save."""
        apis = [
            ('https://ipapi.co/json/', 'country_code'),
            ('http://ip-api.com/json/', 'countryCode'),
            ('https://ipwho.is/', 'country_code')
        ]
        
        for url, key in apis:
            try:
                resp = requests.get(url, timeout=3)
                if resp.status_code == 200:
                    country = resp.json().get(key)
                    if country:
                        self.data['country'] = country
                        self.save_data()
                        return
            except:
                continue
        
        # Fallback to Locale
        try:
            loc, _ = locale.getdefaultlocale()
            if loc:
                country = loc.split('_')[-1]
                self.data['country'] = country
                self.save_data()
                return
        except: pass
        
        # Final Fallback
        if 'country' not in self.data:
            self.data['country'] = 'UN'
            self.save_data()

    def get_country(self):
        # If it's US or UN, maybe it was a mistake or fallback, try to refresh once per session?
        # Actually, let's just use what's there but allow re-fetch if requested.
        return self.data.get('country', 'UN')


    def get_search_history(self):
        return self.data.get('search_results_history', [])

    def add_search_results(self, items):
        """Add new search results to history, deduping and limiting to 200."""
        history = self.data.get('search_results_history', [])
        
        # Create a set of existing URLs for fast lookup if needed, 
        # but since we want to bring duplicates to top or merge, 
        # let's just filter out any incoming items that are already in history?
        # Requirement: "Accumulate actual result items... Dedup... Latest first"
        
        # Strategy: Prepend new items. Remove duplicates based on URL.
        # 1. Combine new + old
        combined = items + history
        
        # 2. Dedup (keep first occurrence)
        seen_urls = set()
        unique_history = []
        for item in combined:
            url = item.get('url')
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_history.append(item)
            elif not url: # Should not happen for valid items
                unique_history.append(item)
        
        # 3. Limit to 200
        self.data['search_results_history'] = unique_history[:200]
        self.save_data()

    def remove_favorite_by_index(self, index):
        if 0 <= index < len(self.data['favorites']):
            item = self.data['favorites'].pop(index)
            if item.get('url') in self.favorites_set:
                self.favorites_set.remove(item['url'])
            self.save_data()
            return True
        return False

    def remove_history_by_index(self, index):
        if 0 <= index < len(self.data['history']):
            self.data['history'].pop(index)
            self.save_data()
            return True
        return False

    def remove_search_history_by_index(self, index):
        if 0 <= index < len(self.data['search_results_history']):
            self.data['search_results_history'].pop(index)
            self.save_data()
            return True
        return False


# === [Player Logic with Advanced IPC] ===
class Player:
    def __init__(self):
        self.current_proc = None
        self.loading = False
        self.loading_ts = 0
        self.socket_fail_count = 0  # Track consecutive IPC failures
        self.socket_ok = True       # Socket health flag
        self.last_socket_warn = 0   # Rate limit for socket error warnings
        self.socket_retry_ts = 0    # Cool-down for reconnection attempts

        
        # Cleanup pre-existing instance if any
        # self.cleanup_orphaned_mpv() # Moved to play() per user request
        
    def cleanup_orphaned_mpv(self):
        # Precise pkill to avoid matching the main TUI process
        # Matches 'mpv ' (with space) or 'mpv' as exact process name
        try:
            subprocess.run(["pkill", "-x", "mpv"], stderr=subprocess.DEVNULL)
            # Second pass for variants or sub-arguments if needed
            subprocess.run(["pkill", "-f", "mpv --video=no"], stderr=subprocess.DEVNULL)
        except: pass
        
    def play(self, url, start_pos=0, initial_eq_preset="Flat"):
        # 1. Try to reuse existing instance via IPC (Graceful)
        if os.path.exists(MPV_SOCKET):
            try:
                # "loadfile" <url> "replace" stops current and plays new
                resp = self.send_cmd(["loadfile", url, "replace"])
                if resp and not resp.get("error"):
                    if start_pos > 0:
                        self.send_cmd(["seek", str(start_pos), "absolute"])
                    
                    # Apply EQ immediately for reused instance
                    if initial_eq_preset and initial_eq_preset != "Flat":
                        self.set_equalizer(initial_eq_preset)
                        
                    self.loading = True
                    self.loading_ts = time.time()
                    return # Success! No need to restart
            except:
                pass # Fallback to restart if IPC fails

        # 2. Fallback: Clean up and start fresh (Aggressive)
        self.cleanup_orphaned_mpv()
        # Reset socket health for fresh start
        self.socket_fail_count = 0
        self.socket_ok = True
        
        self.stop()
        self.loading = True
        self.loading_ts = time.time()
        if os.path.exists(MPV_SOCKET):
            try: os.remove(MPV_SOCKET)
            except OSError: pass
        
        # A. Core mpv flags (Universal)
        cmd = [
            "mpv", "--video=no", "--vo=null", "--force-window=no",
            "--audio-display=no", "--no-config",
            f"--input-ipc-server={MPV_SOCKET}", 
            "--idle=yes"
        ]
        
        # Inject Initial EQ (0ms Latency) - Skip on WSL (causes freezing)
        if not IS_WSL:
            eq_af = self._get_eq_af_string(initial_eq_preset)
            if eq_af:
                cmd.append(f"--af={eq_af}")
            
        cmd.append(url)
        
        # B. macOS Specific UI Optimizations
        if sys.platform == "darwin":
            # 'accessory' hides Dock but allows system resources
            cmd.append("--macos-app-activation-policy=accessory")
            
        # C. Media Source 403 Forbidden Bypass (Cross-platform robustness)
        # This uses the Android player client which is currently the most stable
        # and avoids HLS segment blocks on both Linux and macOS.
        cmd.extend([
            "--ytdl-format=bestaudio/best",
            "--ytdl-raw-options=extractor-args=youtube:player-client=android"
        ])
        
        # D. Bridge to updated yt-dlp in venv (Critical for parity)
        venv_bin = os.path.dirname(sys.executable)
        venv_yt_dlp = os.path.join(venv_bin, "yt-dlp")
        if os.path.exists(venv_yt_dlp):
            cmd.append(f"--script-opts=ytdl_hook-ytdl_path={venv_yt_dlp}")
            
        if start_pos > 0:
            cmd.append(f"--start={start_pos}")
        
        try:
            log = open(LOG_FILE, "a")
            log.write(f"\n--- Launching {url} at {time.ctime()} ---\n")
            log.flush()
        except:
            log = subprocess.DEVNULL
            
        # Capture BOTH stdout and stderr to see what mpv is doing
        kwargs = {"stdout": log, "stderr": log}
        if os.name != "nt": kwargs["preexec_fn"] = os.setpgrp
            
        try:
            self.current_proc = subprocess.Popen(cmd, **kwargs)
            # Save PID
            with open(PID_FILE, 'w') as f:
                f.write(str(self.current_proc.pid))
        except Exception as e:
            self.loading = False

    def stop(self):
        if self.current_proc:
            try:
                self.current_proc.terminate()
                self.current_proc.wait(timeout=1)
            except:
                # If terminate fails, try socket quit
                try: self.send_cmd(["quit"])
                except: pass
            self.current_proc = None
        
        # Cleanup PID file
        if os.path.exists(PID_FILE):
             try: os.remove(PID_FILE)
             except: pass

    def change_volume(self, delta):
        self.send_cmd(["add", "volume", delta])

    def send_cmd(self, command):
        """Send raw command list to MPV via JSON IPC with resilience."""
        # 1. Fast-Detect Process Death
        if self.current_proc and self.current_proc.poll() is not None:
            self.socket_ok = False
            self.current_proc = None
            return None

        # 2. Re-connection Cool-down (Throttle blocking connect() calls)
        now = time.time()
        if not self.socket_ok and now < self.socket_retry_ts:
            return None

        # 3. Pre-check: Skip if socket file doesn't exist
        if not os.path.exists(MPV_SOCKET):
            self.socket_fail_count += 1
            if self.socket_fail_count >= 2:
                self.socket_ok = False
                self.socket_retry_ts = now + 1.5 # 1.5s cool-down
            return None
            
        try:
            client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            client.settimeout(0.5) # Fast timeout (Optimization for Sleep/Wake/WSL resilience)
            client.connect(MPV_SOCKET)
            cmd_str = json.dumps({"command": command}) + "\n"
            client.send(cmd_str.encode('utf-8'))
            
            # Read response
            response = b""
            while True:
                chunk = client.recv(1024)
                if not chunk: break
                response += chunk
                if b"\n" in chunk: break
            
            client.close()
            # Success: Fully Restore health
            self.socket_fail_count = 0
            self.socket_ok = True
            return json.loads(response.decode('utf-8'))
        except:
            self.socket_fail_count += 1
            if self.socket_fail_count >= 2:
                self.socket_ok = False
                self.socket_retry_ts = now + 1.5 # 1.5s cool-down
            return None

    def get_property(self, prop):
        """Skip IPC if health is bad to prevent TUI freezing."""
        if not self.socket_ok:
            return None
        res = self.send_cmd(["get_property", prop])
        if res and "data" in res:
            return res["data"]
        return None
        
    def set_property(self, prop, value):
        if not self.socket_ok:
            return
        self.send_cmd(["set_property", prop, value])

    def toggle_pause(self):
        self.send_cmd(["cycle", "pause"])

    def seek(self, seconds):
        """Seek relative to current position."""
        self.send_cmd(["seek", seconds, "relative"])

    def _get_eq_af_string(self, preset_name):
        """Generate lavfi string for EQ preset."""
        gains = EQUALIZER_PRESETS.get(preset_name, EQUALIZER_PRESETS["Flat"])
        if preset_name == "Flat": return ""

        freqs = [31.25, 62.5, 125, 250, 500, 1000, 2000, 4000, 8000, 16000]
        filters = []
        for f, g in zip(freqs, gains):
            if g != 0:
                filters.append(f"equalizer=f={f}:width_type=o:width=1:g={g}")
        
        if not filters: return ""
        return "lavfi=[" + ",".join(filters) + "]"

    def set_equalizer(self, preset_name):
        """Apply 10-band equalizer preset using lavfi."""
        if IS_WSL:
            return  # Skip EQ on WSL (causes freezing)
        af_str = self._get_eq_af_string(preset_name)
        self.set_property("af", af_str)

# === [TUI Application] ===
class MyTunesApp:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.dm = DataManager()
        self.player = Player()
        self.lang = self.dm.data.get("language", "ko")
        self.running = True
        self.stop_on_exit = True
        self.view_stack = ["main"]
        self.forward_stack = [] # Browser-style forward history
        self.search_results = []
        self.selection_idx = 0
        self.scroll_offset = 0
        self.current_track = None
        self.cached_history = [] # Snapshot for stable history view
        self.status_msg = ""
        
        # Queue System
        self.queue = []
        self.queue_idx = -1
        
        # Audio EQ
        self.current_eq_index = 0  # Default to 0 -> Flat
        self.eq_overlay_time = 0   # For showing EQ change status temporarily
        
        # Search State
        self.current_search_query = None
        # self.search_page = 1 # Deprecated: Pagination Removed v2.0.2
        # self.is_loading_more = False # Deprecated
        
        # Playback State

        self.playback_time = 0
        self.playback_duration = 0
        self.is_paused = False
        self.last_save_time = time.time()
        self.status_set_time = 0
        self.auto_preset_name = "Pop" # Default Auto detected genre
        self._eq_cache = {}  # Cache: {url: detected_genre} to avoid re-computation
        
        # Throttling Counters
        self.loop_count = 0
        
        # Colors
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_CYAN, -1)     # UI Borders/Titles
        curses.init_pair(2, curses.COLOR_GREEN, -1)    # Now Playing
        curses.init_pair(3, curses.COLOR_YELLOW, -1)   # Highlights
        curses.init_pair(4, curses.COLOR_RED, -1)      # Warnings
        curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_BLUE) # Selection (White on Blue)
        curses.init_pair(6, curses.COLOR_WHITE, curses.COLOR_BLACK) # Status Bar / Normal
        
        curses.curs_set(0)
        self.stdscr.nodelay(True)
        self.stdscr.timeout(200) # Update loop every 200ms
        self.last_input_time = time.time() # For Idle Detection

        
        # Register Signal for Terminal Disconnect (Window Close)
        try:
            signal.signal(signal.SIGHUP, self.handle_disconnect)
        except: pass

        # Enable Mouse Support
        curses.mousemask(curses.ALL_MOUSE_EVENTS | curses.REPORT_MOUSE_POSITION)
        print("\033[?1003h") # Enable mouse tracking

        self.sent_history = {}


    def handle_disconnect(self, signum, frame):
        """Auto-background if terminal disconnects."""
        self.stop_on_exit = False
        self.running = False
        
    def t(self, key, *args):
        val = STRINGS.get(self.lang, STRINGS["en"]).get(key, "")
        if args: return val.format(*args)
        return val

    # ... [Utility Functions: get_display_width, truncate, draw_box same as before] ...
    def get_display_width(self, text):
        return sum(2 if unicodedata.east_asian_width(c) in 'WFA' else 1 for c in text)

    def truncate(self, text, max_width):
        w = 0; res = ""
        for c in text:
            cw = 2 if unicodedata.east_asian_width(c) in 'WFA' else 1
            if w + cw > max_width: break
            w += cw
            res += c
        return res

    def draw_box(self, win, y, x, h, w, title=""):
        win.attron(curses.color_pair(1))
        try:
            win.addstr(y, x, "┌" + "─" * (w - 2) + "┐")
            for i in range(1, h - 1):
                win.addstr(y + i, x, "│")
                win.addstr(y + i, x + w - 1, "│")
            win.addstr(y + h - 1, x, "└" + "─" * (w - 2) + "┘")
        except: pass
        if title:
            safe_title = f" {title} "
            if len(safe_title) < w - 4:
                win.addstr(y, x + 2, safe_title, curses.A_BOLD | curses.color_pair(3))
        win.attroff(curses.color_pair(1))

    def get_current_list(self):
        view = self.view_stack[-1]
        if view == "main":
            return [
                {"title": self.t("menu_search_results"), "id": "search_music"},
                {"title": self.t("menu_favorites"), "id": "fav_menu"},
                {"title": self.t("menu_history"), "id": "hist_menu"},
                {"title": self.t("menu_bg_play"), "id": "bg_play"},
                {"title": self.t("lang_toggle"), "id": "lang"},
                {"title": self.t("quit_label"), "id": "quit"}
            ]
        elif view == "search": return self.search_results
        elif view == "favorites": return self.dm.data['favorites']
        elif view == "history": return self.cached_history
        return []

    def update_playback_state(self):
        # Poll MPV for state with throttling to reduce CPU/IPC overhead
        try:
            # 0. Health Check: If socket is known-bad, exit immediately to keep TUI responsive
            if not self.player.socket_ok:
                return

            # 1. Mandatory every loop: Current time (for progress bar)
            t = self.player.get_property("time-pos")
            if t is None:
                # If even time-pos fails, bail out immediately to prevent cascaded delay
                return 

            self.playback_time = float(t)
            if self.player.loading and self.playback_time >= 0:
                self.player.loading = False
            
            # Update Resume Data (Memory) - Throttle save logic
            if self.current_track and self.playback_duration > 30:
                if self.playback_time / self.playback_duration > 0.99:
                    self.dm.set_progress(self.current_track['url'], 0)
                elif self.playback_time > 10:
                    self.dm.set_progress(self.current_track['url'], self.playback_time)


            # Safety: If loading takes too long (> 8s), force reset to allow error handling/skip
            now = time.time()
            if self.player.loading and (now - self.player.loading_ts > 8):
                self.player.loading = False
                self.status_msg = "⚠️ Load timed out. Skipping..."

            # 2. Frequent: Pause state (Every 2 loops ~400ms)
            if self.loop_count % 2 == 0:
                p = self.player.get_property("pause")
                if p is not None: self.is_paused = p

            # 3. Infrequent: Duration, Title, Idle state (Every 5 loops ~1s)
            if self.loop_count % 5 == 0:
                d = self.player.get_property("duration")
                if d is not None: self.playback_duration = float(d)
                
                title = self.player.get_property("media-title")
                if self.current_track is None and title:
                    url_path = self.player.get_property("path")
                    if not url_path: url_path = ""
                    self.current_track = {"title": title, "url": url_path}

                is_idle = self.player.get_property("idle-active")
                if is_idle and self.player.loading: 
                    self.player.loading = False
            
            # Periodic Save (Throttle 10s)
            if time.time() - getattr(self, 'last_save_time', 0) > 10:
                self.dm.save_data()
                self.last_save_time = time.time()

                 
        except: pass

    def format_time(self, seconds):
        if not seconds: return "00:00"
        m, s = divmod(int(seconds), 60)
        return f"{m:02d}:{s:02d}"

    def get_next_event(self):
        """Unified input collection and normalization (Unicode, special keys, macros)."""
        try:
            key = self.stdscr.get_wch()
        except curses.error: return None
        except: return None

        if key == -1: return None
        self.last_input_time = time.time()

        # 1. Resize handling
        if key == curses.KEY_RESIZE:
            self.stdscr.clear()
            self.stdscr.refresh()
            return "RESIZE"

        # 2. ESC / Combined sequences (Option+Backspace macro)
        if key == 27 or key == '\x1b':
            self.stdscr.timeout(50) # Tiny peek timeout
            try:
                nk = self.stdscr.getch()
                if nk == 127: return "DELETE" # Option+Backspace as DELETE
                if nk != -1: curses.ungetch(nk)
            except: pass
            finally: self.stdscr.timeout(200) # Reset to standard
            return "EXIT_BKG" # Standard ESC

        # 3. Mouse Click
        if key == curses.KEY_MOUSE:
            try:
                _, mx, my, _, bstate = curses.getmouse()
                if bstate & (curses.BUTTON1_CLICKED | curses.BUTTON1_RELEASED):
                    h, w = self.stdscr.getmaxyx()
                    branding = "mytunes-pro.com/postgresql.co.kr"
                    branding_x = w - 2 - len(branding)
                    if my == h - 2 and branding_x <= mx < w - 2:
                        rel_x = mx - branding_x
                        if rel_x < 15: return "OPEN_HOME"
                        if rel_x > 15: return "OPEN_PARTNER"
            except: pass
            return "MOUSE_CLICK"

        # 4. Standard Keys Mapping
        k_char = str(key).lower() if isinstance(key, str) else str(key)
        mapping = {
            str(curses.KEY_LEFT): "NAV_BACK", str(curses.KEY_BACKSPACE): "NAV_BACK", "127": "NAV_BACK",
            "q": "NAV_BACK", "6": "NAV_BACK", "h": "NAV_BACK",
            str(curses.KEY_RIGHT): "NAV_FORWARD", "l": "NAV_FORWARD",
            str(curses.KEY_UP): "MOVE_UP", "k": "MOVE_UP",
            str(curses.KEY_DOWN): "MOVE_DOWN", "j": "MOVE_DOWN",
            "\n": "ACTIVATE", "\r": "ACTIVATE", "10": "ACTIVATE", "13": "ACTIVATE", str(curses.KEY_ENTER): "ACTIVATE",
            "s": "SEARCH", "1": "SEARCH", "/": "SEARCH",
            "f": "FAVORITES", "2": "FAVORITES",
            "r": "HISTORY", "3": "HISTORY",
            "m": "MAIN_MENU", "4": "MAIN_MENU",
            " ": "TOGGLE_PAUSE",
            "-": "VOL_DOWN", "_": "VOL_DOWN",
            "+": "VOL_UP", "=": "VOL_UP",
            ",": "SEEK_BACK_10", ".": "SEEK_FWD_10",
            "<": "SEEK_BACK_30", ">": "SEEK_FWD_30",
            "a": "TOGGLE_FAV", "5": "TOGGLE_FAV",
            str(curses.KEY_F7): "OPEN_BROWSER",
            str(curses.KEY_DC): "DELETE", "d": "DELETE",
            "e": "CYCLE_EQ", "E": "CYCLE_EQ"
        }
        cmd = mapping.get(k_char)
        if cmd: return cmd
        return ("UNKNOWN", key)

    def handle_input(self):
        """Clean dispatcher: Get normalized command and execute it."""
        cmd = self.get_next_event()
        if not cmd: return

        # Reset transient state for valid commands
        is_transient = any(kw in self.status_msg for kw in ["Invalid key", "잘못된 키", "영문", "English"])
        if is_transient:
            self.status_msg = ""

        current_list = self.get_current_list()

        # 1. Functional Commands (Require Logic)
        if cmd == "NAV_BACK":
            if len(self.view_stack) > 1:
                self.forward_stack.append(self.view_stack.pop())
                self.selection_idx = 0; self.scroll_offset = 0; self.status_msg = ""
        
        elif cmd == "NAV_FORWARD":
            if self.forward_stack:
                self.view_stack.append(self.forward_stack.pop())
                self.selection_idx = 0; self.scroll_offset = 0; self.status_msg = ""

        elif cmd == "MOVE_UP":
            if self.selection_idx > 0:
                self.selection_idx -= 1
                if self.selection_idx < self.scroll_offset: self.scroll_offset = self.selection_idx
            elif current_list:
                self.selection_idx = len(current_list) - 1
                h, _ = self.stdscr.getmaxyx()
                self.scroll_offset = max(0, self.selection_idx - (h - 11))

        elif cmd == "MOVE_DOWN":
            if self.selection_idx < len(current_list) - 1:
                self.selection_idx += 1
                h, _ = self.stdscr.getmaxyx()
                if self.selection_idx >= self.scroll_offset + (h - 10):
                    self.scroll_offset = self.selection_idx - (h - 10) + 1
            elif current_list:
                self.selection_idx = 0; self.scroll_offset = 0

        elif cmd == "ACTIVATE":
            if time.time() - getattr(self, 'last_enter_time', 0) > 0.3:
                self.last_enter_time = time.time()
                self.activate_selection(current_list)

        elif cmd == "SEARCH":
            self.forward_stack = []; self.prompt_search()

        elif cmd == "FAVORITES":
            if self.view_stack[-1] != "favorites":
                self.forward_stack = []; self.view_stack.append("favorites"); self.selection_idx = 0
            self.status_msg = self.t("favorites_info", DATA_FILE)

        elif cmd == "HISTORY":
            if self.view_stack[-1] != "history":
                self.forward_stack = []; self.cached_history = list(self.dm.data['history'])
                self.view_stack.append("history"); self.selection_idx = 0
            self.status_msg = self.t("hist_info")

        elif cmd == "MAIN_MENU":
            self.forward_stack = []; self.view_stack = ["main"]; self.selection_idx = 0; self.scroll_offset = 0; self.status_msg = ""

        elif cmd == "TOGGLE_PAUSE": self.player.toggle_pause()
        elif cmd == "VOL_DOWN": self.player.change_volume(-5); self.status_msg = "Volume -5"
        elif cmd == "VOL_UP": self.player.change_volume(5); self.status_msg = "Volume +5"
        elif cmd == "SEEK_BACK_10": self.player.seek(-10)
        elif cmd == "SEEK_FWD_10": self.player.seek(10)
        elif cmd == "SEEK_BACK_30": self.player.seek(-30); self.status_msg = "Rewind 30s"
        elif cmd == "SEEK_FWD_30": self.player.seek(30); self.status_msg = "Forward 30s"
        
        elif cmd == "TOGGLE_FAV":
            if current_list and 0 <= self.selection_idx < len(current_list):
                target = current_list[self.selection_idx]
                if "url" in target:
                    is_added = self.dm.toggle_favorite(target)
                    self.status_msg = self.t("fav_added") if is_added else self.t("fav_removed")

        elif cmd == "DELETE":
            self.handle_deletion(current_list)

        elif cmd == "OPEN_BROWSER":
            if current_list and 0 <= self.selection_idx < len(current_list):
                url = current_list[self.selection_idx].get('url')
                if url: (self.show_copy_dialog("Media", url) if self.is_remote() else self.open_browser(url))

        elif cmd in ["OPEN_HOME"]:
            url = "https://mytunes-pro.com"
            if self.is_remote(): self.show_copy_dialog("MyTunes Home", url)
            else: self.open_browser(url, app_mode=False)

        elif cmd == "OPEN_PARTNER":
            self.open_browser("https://postgresql.co.kr")


        elif cmd == "RESIZE":
            self.stdscr.clear()
            self.stdscr.refresh()

        elif cmd == "EXIT_BKG":
            self.stop_on_exit = False; self.running = False

        elif cmd == "CYCLE_EQ":
            self.cycle_equalizer()

        elif isinstance(cmd, tuple) and cmd[0] == "UNKNOWN":
            key = cmd[1]
            if isinstance(key, str) and ord(key[0]) > 127:
                self.status_msg = self.t("ime_warning")
                self.status_set_time = time.time()
                self.draw() # Internal redraw for instant feedback
            elif isinstance(key, str) and key.isprintable():
                self.status_msg = self.t("invalid_key", key)
                self.status_set_time = time.time()
                self.draw() # Internal redraw for instant feedback

    def handle_deletion(self, current_list):
        """Sub-logic for DELETE command to keep dispatcher clean."""
        if not current_list or not (0 <= self.selection_idx < len(current_list)): return
        
        view = self.view_stack[-1]
        success = False
        if view == "favorites":
            success = self.dm.remove_favorite_by_index(self.selection_idx)
            if success: self.status_msg = "🗑️ Deleted from Favorites"
        elif view == "history":
            success = self.dm.remove_history_by_index(self.selection_idx)
            if success: self.cached_history = list(self.dm.data['history']); self.status_msg = "🗑️ Deleted from History"
        elif view == "search":
            if self.current_search_query is None:
                success = self.dm.remove_search_history_by_index(self.selection_idx)
                if success: self.search_results = self.dm.get_search_history(); self.status_msg = "🗑️ Deleted from Search History"
            else:
                try: self.search_results.pop(self.selection_idx); success = True; self.status_msg = "Removed from list"
                except: pass

    def cycle_equalizer(self):
        self.current_eq_index = (self.current_eq_index + 1) % len(EQUALIZER_KEYS)
        new_preset = EQUALIZER_KEYS[self.current_eq_index]
        
        if new_preset == "Auto":
            # Immediate trigger for current track
            auto_preset = self.detect_auto_eq(self.current_track) if self.current_track else "Pop"
            self.player.set_equalizer(auto_preset)
            self.status_msg = f"🎚 Auto: {auto_preset}"
        else:
            self.player.set_equalizer(new_preset)
            self.status_msg = f"🎚 EQ: {new_preset}"
            
        self.status_set_time = time.time()

    def detect_auto_eq(self, item):
        """
        Smart genre detection using weighted scoring.
        Analyzes Title and Author for keywords.
        """
        # Cache check: return cached result if available
        if not isinstance(item, str):
            url = item.get('url', '')
            if url and url in self._eq_cache:
                cached = self._eq_cache[url]
                self.auto_preset_name = cached
                return cached
            # Limit cache size to 200 entries
            if len(self._eq_cache) > 200:
                keys = list(self._eq_cache.keys())
                for k in keys[:50]:
                    del self._eq_cache[k]
        
        # Prepare texts
        title_text = ""
        extra_text = ""
        
        if isinstance(item, str): 
             title_text = item.lower()
        else:
             title_text = item.get('title', '').lower()
             extra_text = f"{item.get('author', '')} {item.get('channel', '')}".lower()
        
        scores = {k: 0 for k in EQUALIZER_PRESETS.keys() if k != "Flat"}
        
        # Keyword Maps (Genre -> [Keywords])
        # Specific genres should have unique keywords.
        rules = [
            ("Rock",      ["rock", "band", "metal", "grunge", "punk", "락", "밴드", "메탈", "coldplay", "linkin", "day6", "oasis", "nirvana", "ac/dc"]),
            ("Jazz",      ["jazz", "재즈", "blues", "piano", "cafe", "coffee", "morning", "카페", "피아노", "bgm", "study", "relaxing jazz", "smooth jazz", "dinner", "book"]),
            ("Classical", ["classic", "symphony", "orchestra", "violin", "cello", "mozart", "bach", "beethoven", "chopin", "클래식", "오케스트라", "교향곡", "concerto", "sonata"]),
            ("Club",      ["bass", "boost", "trap", "dubstep", "edm", "club", "remix", "dj", "electronic", "house", "techno", "mix"]),
            ("Dance",     ["dance", "party", "disco", "kpop", "k-pop", "idol", "choreography", "댄스", "아이돌", "newjeans", "bts", "ive", "aespa", "le sserafim", "blackpink", "twice"]),
            ("Full Bass", ["rap", "hip hop", "hiphop", "r&b", "soul", "mc", "beat", "힙합", "래퍼", "쇼미더머니", "eminem", "drake", "kanye"]),
            ("Live",      ["live", "concert", "performance", "stage", "fancam", "busking", "라이브", "콘서트", "무대", "직캠", "버스킹", "tour", "festa"]),
            ("Soft",      ["soft", "sleep", "relax", "healing", "lofi", "lo-fi", "ballad", "acoustic", "winter", "rain", "잔잔한", "발라드", "힐링", "수면", "감성", "새벽", "자장가", "어쿠스틱", "guitar", "piano", "roy kim", "로이킴", "paul kim", "폴킴"]),
            ("Pop",       ["pop", "billboard", "top 100", "best", "hits", "favorites", "팝", "가요", "인기", "노래모음", "chart", "trending"]),
            # Fallbacks / Overlaps
            ("Jazz",      ["lounge", "mood", "night", "bar", "wine"]), 
            ("Pop",       ["trot", "트로트", "임영웅", "나훈아", "송가인"]),
        ]

        # Scoring
        for genre, keywords in rules:
            if genre not in scores: continue
            for k in keywords:
                # Title Match (High Priority)
                if k in title_text:
                    score = 3
                    # Boost specific keywords even more
                    if genre == "Jazz" and k in ["jazz", "재즈", "cafe", "coffee", "lounge"]: score += 2
                    scores[genre] += score
                
                # Extra Match (Low Priority)
                elif k in extra_text:
                    scores[genre] += 1
                
        # Find winner
        best_genre = max(scores, key=scores.get)
        
        if scores[best_genre] > 0:
            self.auto_preset_name = best_genre
            # Save to cache
            if not isinstance(item, str) and item.get('url'):
                self._eq_cache[item['url']] = best_genre
            return best_genre
            
        # Default Fallback
        self.auto_preset_name = "Pop"
        # Cache fallback too
        if not isinstance(item, str) and item.get('url'):
            self._eq_cache[item['url']] = "Pop"
        return "Pop" 

    def play_music(self, item, interactive=True, preserve_queue=False):
        if not item.get("url"): return # Guard against dummy items
        
        self.current_track = item
        self.dm.add_history(item)
        
        # Apply Auto EQ if enabled
        # Apply Auto EQ if enabled
        target_eq_preset = "Flat"
        current_eq_mode = EQUALIZER_KEYS[self.current_eq_index]
        
        if current_eq_mode == "Auto":
            self.auto_preset_name = "..." 
            self.detect_auto_eq(item) # Updates self.auto_preset_name
            target_eq_preset = self.auto_preset_name
            self.status_msg = "" # Clear previous msgs
        else:
            target_eq_preset = current_eq_mode

        self.status_set_time = time.time()
        
        # Queue Management
        if not preserve_queue:
            # New Queue Context from current view
            current_list = self.get_current_list()
            # Copy list to queue (Filter only playable items)
            self.queue = [i for i in current_list if i.get("url")]
            # Find index in queue
            try:
                # Find by URL
                self.queue_idx = next(i for i, x in enumerate(self.queue) if x['url'] == item['url'])
            except StopIteration:
                self.queue_idx = -1
                self.queue = [] # Should not happen if item came from list
        
        start_pos = 0
        if 'url' in item:
            saved = self.dm.get_progress(item['url'])
            if saved > 10: 
                # Autoskip resume prompt in Autoplay (interactive=False)
                if interactive:
                    if self.ask_resume(saved, item.get('title', 'Unknown')): start_pos = saved
                else:
                    start_pos = 0
        
        self.player.play(item['url'], start_pos, initial_eq_preset=target_eq_preset)
        
        # Re-apply EQ logic (double check: mpv restart wipes af property?)
        # Yes, play() might restart mpv if socket fails.
        # But set_equalizer uses set_property which works via IPC *after* launch.
        # However, play() sends "loadfile" if existing, or restarts.
        # If restarted, we must re-apply EQ.
        # Ideally Player.play should handle restoring EQ state or we rely on MyTunesApp to do it.
        # But for now, let's just re-apply it here after a tiny delay or ensure Player persists it?
        # Actually Player doesn't persist state. MyTunesApp drives it.
        # So calling set_equalizer *after* play is correct.
        
        # Player.play() handles loading the file.
        # Since we set "af" via IPC AFTER play() starts in some logic, 
        # but here we set it before/during. set_property works anytime.
        
        # Reset state for new track
        self.playback_time = start_pos
        self.playback_duration = 0
        self.is_paused = False
        self.stdscr.nodelay(False) # Blocking input for dialog
        h, w = self.stdscr.getmaxyx()
        box_h, box_w = 8, 60
        box_y, box_x = (h - box_h) // 2, (w - box_w) // 2
        
    def ask_resume(self, saved_time, track_title):
        self.stdscr.nodelay(False) # Blocking input for dialog
        h, w = self.stdscr.getmaxyx()
        box_h, box_w = 8, 60
        box_y, box_x = (h - box_h) // 2, (w - box_w) // 2
        
        try:
            win = curses.newwin(box_h, box_w, box_y, box_x)
            win.keypad(True)
            try: win.bkgd(' ', curses.color_pair(1))
            except: pass
            
            win.attron(curses.color_pair(1)); win.box()
            
            title = " Resume Playback " if self.lang == 'en' else " 이어듣기 "
            val = self.format_time(saved_time)
            msg = f"Last Pos: {val}" if self.lang == 'en' else f"저장된 위치: {val}"
            opts = "[Enter] Resume  [0/R] Restart" if self.lang == 'en' else "[Enter] 이어서  [0/R] 처음부터"
            
            # Truncate title
            disp_title = self.truncate(track_title, box_w - 6)
            
            win.addstr(0, 2, title, curses.A_BOLD | curses.color_pair(3))
            win.addstr(2, 3, disp_title, curses.color_pair(2) | curses.A_BOLD)
            win.addstr(4, 3, msg, curses.color_pair(1))
            win.addstr(6, 3, opts, curses.color_pair(1) | curses.A_BOLD)
            
            win.refresh()
            
            # Flush input
            curses.flushinp()
            
            while True:
                try:
                    k = win.get_wch()
                except curses.error:
                    continue
                
                # ESC -> Background Play (Exit app)
                if k == 27 or k == '\x1b':
                    self.stop_on_exit = False
                    self.running = False
                    res = False
                    break
                
                # Enter / Space -> Resume
                if k in [10, 13, curses.KEY_ENTER, '\n', '\r', ' ']: 
                    res = True
                    break
                
                # 0 / R -> Restart
                k_char = str(k).lower() if isinstance(k, str) else ""
                if k_char in ['0', 'r']: 
                    res = False
                    break
                    
        except: res = True # Default to Resume on error
        
        # Cleanup
        self.stdscr.timeout(200) # Ensure timeout is restored, NOT nodelay(True)
        self.stdscr.touchwin()
        self.stdscr.refresh()
        return res

    def is_remote(self):
        """Check if running in a remote SSH session (excluding local WSL)."""
        if 'WSL_DISTRO_NAME' in os.environ or 'WSL_INTEROP' in os.environ:
            return False
        return 'SSH_CONNECTION' in os.environ or 'SSH_CLIENT' in os.environ or 'SSH_TTY' in os.environ

    def open_browser(self, url, app_mode=False):
        """Open browser using detached subprocess to prevent TUI freezing."""
        self.status_msg = f"🌐 Opening Link: {url[:30]}..."
        
        def run_open():
            try:
                # Prepare DEVNULL for fire-and-forget
                devnull = os.open(os.devnull, os.O_RDWR)
                popen_kwargs = {
                    'stdin': devnull,
                    'stdout': devnull,
                    'stderr': devnull,
                    'close_fds': True
                }
                
                # Use start_new_session for process group detachment (if possible)
                if hasattr(os, 'setsid') or sys.platform != 'win32':
                    popen_kwargs['start_new_session'] = True

                if sys.platform == 'darwin':
                    if app_mode:
                        # Attempt "App Mode" for Chrome/Brave on macOS
                        launched = False
                        browsers = [
                            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                            "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"
                        ]
                        for b_path in browsers:
                            if os.path.exists(b_path):
                                try:
                                    subprocess.Popen([b_path, f"--app={url}", "--window-size=600,800"], **popen_kwargs)
                                    launched = True
                                    break
                                except: pass
                        if not launched:
                            subprocess.Popen(['open', url], **popen_kwargs)
                    else:
                        subprocess.Popen(['open', url], **popen_kwargs)
                elif self.is_wsl():
                    # For WSL, we usually use cmd.exe /c start
                    subprocess.Popen(['cmd.exe', '/c', 'start', url], **popen_kwargs)
                else:
                    # Linux or others
                    subprocess.Popen(['xdg-open', url], **popen_kwargs)
                
                # Feedback logic: Success message then auto-clear
                self.status_msg = "✅ Browser Launched! (Check Browser)"
                time.sleep(2.5)
                if "Launched!" in self.status_msg:
                    self.status_msg = ""
            except Exception as e:
                # Log error silently to TUI status
                self.status_msg = f"❌ Browser Error: {str(e)[:20]}"

        # Still execute Popen in a thread to be extra safe, 
        # but Popen itself is now detached and redirected.
        threading.Thread(target=run_open, daemon=True).start()

    def is_wsl(self):
        try:
            if sys.platform != 'linux': return False
            if os.path.exists('/proc/version'):
                with open('/proc/version', 'r') as f:
                    return 'microsoft' in f.read().lower()
            return False
        except: return False

    def show_copy_dialog(self, title, url):
        """Show a dialog with the URL for manual copying in remote sessions."""
        self.stdscr.nodelay(False)
        h, w = self.stdscr.getmaxyx()
        box_h, box_w = 8, min(80, w - 4)
        box_y, box_x = (h - box_h) // 2, (w - box_w) // 2
        
        try:
            win = curses.newwin(box_h, box_w, box_y, box_x)
            win.keypad(True)
            try: win.bkgd(' ', curses.color_pair(1))
            except: pass
            
            win.attron(curses.color_pair(1)); win.box()
            
            # Title
            header = " Remote Link " if self.lang == 'en' else " 원격 링크 "
            win.addstr(0, 2, header, curses.A_BOLD | curses.color_pair(3))
            
            # Content
            lbl = "Open this URL in your local browser:" if self.lang == 'en' else "아래 주소를 로컬 브라우저에서여세요:"
            win.addstr(2, 3, lbl, curses.color_pair(1))
            
            # URL (Truncate if needed but try to show mostly)
            disp_url = self.truncate(url, box_w - 6)
            win.addstr(3, 3, disp_url, curses.color_pair(5) | curses.A_BOLD)
            
            # Exit instruction
            exit_msg = "[Enter/ESC] Close" if self.lang == 'en' else "[Enter/ESC] 닫기"
            win.addstr(6, box_w - len(exit_msg) - 2, exit_msg, curses.color_pair(1))
            
            win.refresh()
            curses.flushinp()
            
            # Wait for key
            while True:
                try:
                    k = win.get_wch()
                except curses.error:
                    continue

                if k in [10, 13, curses.KEY_ENTER, 27, '\n', '\r', '\x1b', ' ']: 
                    break
        except: pass
        finally:
            self.stdscr.timeout(200) # Restore non-blocking

    def activate_selection(self, items):
        if not items: return
        item = items[self.selection_idx]
        view = self.view_stack[-1]
        
        if view == "main":
            if item["id"] == "search_music": self.prompt_search()
            elif item["id"] == "fav_menu": 
                self.view_stack.append("favorites")
                self.selection_idx=0
                self.status_msg = self.t("favorites_info", DATA_FILE)
            elif item["id"] == "hist_menu": 
                self.cached_history = list(self.dm.data['history']) # Snapshot
                self.view_stack.append("history")
                self.selection_idx=0
                self.status_msg = self.t("hist_info")
            elif item["id"] == "bg_play":
                self.stop_on_exit = False
                self.running = False
            elif item["id"] == "lang":
                self.lang = "en" if self.lang == "ko" else "ko"
                self.dm.data["language"] = self.lang
                self.dm.save_data()
                self.status_msg = "" # Clear stale messages on language switch
            elif item["id"] == "quit": self.running = False
        else:
            self.play_music(item, interactive=True)


    def play_music(self, item, interactive=True, preserve_queue=False):
        if not item.get("url"): return # Guard against dummy items
        
        self.current_track = item
        self.dm.add_history(item)
        
        # Queue Management
        if not preserve_queue:
            # New Queue Context from current view
            current_list = self.get_current_list()
            # Copy list to queue (Filter only playable items)
            self.queue = [i for i in current_list if i.get("url")]
            # Find index in queue
            try:
                # Find by URL
                self.queue_idx = next(i for i, x in enumerate(self.queue) if x['url'] == item['url'])
            except StopIteration:
                self.queue_idx = -1
                self.queue = [] # Should not happen if item came from list
        
        start_pos = 0
        if 'url' in item:
            saved = self.dm.get_progress(item['url'])
            if saved > 10: 
                # Autoskip resume prompt in Autoplay (interactive=False)
                if interactive:
                    if self.ask_resume(saved, item.get('title', 'Unknown')): start_pos = saved
                else:
                    start_pos = 0
        
        self.player.play(item['url'], start_pos)
        # Reset state for new track
        self.playback_time = start_pos
        self.playback_duration = 0
        self.is_paused = False

    def input_dialog(self, title, prompt):
        """Show a centered input dialog with robust byte-level handling (Fixes Double Enter)."""
        self.stdscr.nodelay(False)
        
        h, w = self.stdscr.getmaxyx()
        box_h, box_w = 5, 60
        box_y, box_x = (h - box_h) // 2, (w - box_w) // 2
        
        win = curses.newwin(box_h, box_w, box_y, box_x)
        win.keypad(True)
        try: win.bkgd(' ', curses.color_pair(1))
        except: pass
        
        win.attron(curses.color_pair(1)); win.box()
        win.addstr(0, 2, f" {title} ", curses.A_BOLD | curses.color_pair(3))
        win.addstr(2, 2, prompt, curses.color_pair(1))
        win.attroff(curses.color_pair(1))
        win.refresh()
        
        curses.noecho()
        curses.curs_set(1)
        input_win = curses.newwin(1, box_w - 4 - len(prompt), box_y + 2, box_x + 2 + len(prompt))
        input_win.keypad(True)
        
        chars = []
        pending_bytes = b""
        
        while True:
            input_win.erase()
            display_text = "".join(chars)
            display_text = unicodedata.normalize('NFC', display_text)
            
            max_len = box_w - 6 - len(prompt)
            while self.get_display_width(display_text) > max_len:
                display_text = display_text[1:]
                display_text = "..." + display_text[3:] if len(display_text) > 3 else display_text
            
            try: input_win.addstr(0, 0, display_text)
            except: pass
            input_win.refresh()
            
            try:
                # Use getch (byte/int) instead of get_wch to catch raw Enter immediately
                key = self.stdscr.getch()
            except curses.error: continue
            
            if key == curses.ERR: continue

            # Resize
            if key == curses.KEY_RESIZE:
                self.stdscr.clear(); self.stdscr.refresh(); win.refresh()
                continue
                
            # Enter
            if key in [10, 13, curses.KEY_ENTER]:
                break
                
            # ESC -> Cancel
            if key == 27:
                chars = [] # Return empty
                break
                
            # Backspace
            if key in [127, curses.KEY_BACKSPACE]:
                if chars: chars.pop()
                pending_bytes = b"" # Reset any partial bytes
                continue
                
            # Special keys (Arrows etc)
            if key > 255:
                continue
                
            # Accumulate bytes for UTF-8 (Korean handling)
            pending_bytes += bytes([key])
            
            try:
                decoded = pending_bytes.decode('utf-8')
                decoded = unicodedata.normalize('NFC', decoded)
                chars.append(decoded)
                pending_bytes = b""
            except UnicodeDecodeError:
                # Wait for more bytes
                pass
        
        curses.curs_set(0)
        self.stdscr.timeout(200) # Ensure timeout is restored
        self.stdscr.touchwin(); self.stdscr.refresh()
        
        return "".join(chars).strip()

    def prompt_search(self):
        curses.flushinp()
        
        orig_view = self.view_stack[-1]
        orig_results = list(self.search_results)
        
        # Show search history in background using existing 'search' view
        history = self.dm.get_search_history()
        if history:
            self.search_results = history
            self.selection_idx = 0
            self.scroll_offset = 0
            if self.view_stack[-1] != "search":
                self.view_stack.append("search")
            self.status_msg = "" # Clear "List is empty" etc.
            self.draw()

        query = self.input_dialog(self.t("search_label"), self.t("search_prompt"))
        
        # Handling query result
        # Note: If user pressed ESC, input_dialog returns "" (per current implementation)
        # But wait, input_dialog logic: "ESC -> chars = []; break; return "".join(chars).strip()"
        # So ESC and empty Enter both return "". 
        # I should check if it's possible to distinguish.
        
        if query:
            self.status_msg = self.t("searching")
            self.draw()
            # v2.0.0 Refactor: Threaded Search
            threading.Thread(target=self.perform_search, args=(query,), daemon=True).start()
        else:
            # Revert if no query and we were just previewing history
            # But requirement 2: "If Enter with no query, preserve previous search results"
            # This is tricky because ESC and empty Enter currently both return "".
            # I will assume "" means "keep current view (history)".
            # If the user wants to CANCEL and go back to Main, they might need ESC.
            pass

    def perform_search(self, query):
        try:
            # v2.0.4 Fix: Don't set player.loading=True for Search. 
            # It triggers playback timeout (skipping) logic if search is slow.
            # self.player.loading = True 
            
            self.current_search_query = query
            self.status_msg = self.t("searching")
            
            # Resolve yt-dlp path
            yt_dlp_cmd = "yt-dlp"
            venv_bin = os.path.dirname(sys.executable)
            venv_yt_dlp = os.path.join(venv_bin, "yt-dlp")
            if os.path.exists(venv_yt_dlp) and os.access(venv_yt_dlp, os.X_OK):
                yt_dlp_cmd = venv_yt_dlp

            # v2.0.2 Optimization: 25 Items (Better space usage per user request)
            limit = 25
            search_query = f"{query} music"
            cmd = [
                yt_dlp_cmd, 
                f"ytsearch{limit}:{search_query}", 
                "--dump-json", "--flat-playlist", "--no-playlist", "--skip-download"
            ]
            
            try:
                result = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode('utf-8')
            except subprocess.CalledProcessError:
                result = "" 
                
            new = []
            seen_urls = set()
            for line in result.strip().split("\n"):
                if line:
                    try:
                        d = json.loads(line)
                        url = d.get("url")
                        if not url or "http" not in url: url = f"https://www.youtube.com/watch?v={d.get('id')}"
                        dur = d.get("duration", 0)
                        dur_str = f"{int(dur)//60}:{int(dur)%60:02d}" if dur else ""
                        # Dedup Check
                        if url not in seen_urls:
                             seen_urls.add(url)
                             # Extract Channel/Author
                             channel = d.get("uploader") or d.get("channel") or d.get("uploader_id") or "Unknown"
                             new.append({
                                 "title": d.get("title", "Unknown"), 
                                 "url": url, 
                                 "duration": dur_str,
                                 "author": channel,
                                 "channel": channel
                             })
                    except: pass
            
            # Enforce hard limit
            new = new[:limit]
            
            if new:
                self.search_results = new
                if self.view_stack[-1] != "search":
                    self.view_stack.append("search")
                self.selection_idx = 0; self.scroll_offset = 0
                
                # SAVE to History
                self.dm.add_search_results(new)
                
                self.status_msg = f"Search Done. ({len(new)} results)"
            else:
                self.status_msg = self.t("no_results")
                
        except Exception as e: self.status_msg = f"Error: {e}"
        finally:
            self.player.loading = False





    def draw(self):
        self.stdscr.erase()
        h, w = self.stdscr.getmaxyx()
        
        if h < 15 or w < 40:
            self.stdscr.addstr(0, 0, "Window too small!")
            return

        # Header (4 lines)
        self.draw_box(self.stdscr, 0, 0, 4, w, APP_NAME)
        title = self.t("title", APP_VERSION)
        
        # Row 1: Nav
        r1 = self.t("header_r1")
        gap1 = w - 4 - self.get_display_width(title) - self.get_display_width(r1)
        if gap1 < 2: gap1 = 2
        line1 = f"{title}{' '*gap1}{r1}"
        self.stdscr.addstr(1, 2, self.truncate(line1, w-4), curses.color_pair(1) | curses.A_BOLD)

        # Row 2: Actions
        r2 = self.t("header_r2")
        gap2 = w - 4 - self.get_display_width(r2)
        if gap2 < 2: gap2 = 2
        line2 = f"{' '*gap2}{r2}"
        self.stdscr.addstr(2, 2, self.truncate(line2, w-4), curses.color_pair(1) | curses.A_BOLD)

        # Footer (5 lines)
        footer_h = 5
        self.draw_box(self.stdscr, h - footer_h, 0, footer_h, w)
        
        # Footer Line 1: Progress Bar
        pct = 0
        if self.playback_duration > 0: pct = min(1.0, self.playback_time / self.playback_duration)
        
        time_str = f"{self.format_time(self.playback_time)} / {self.format_time(self.playback_duration)}"
        bar_w = w - 4 - len(time_str) - 3 # brackets + space
        
        if bar_w < 5: bar_w = 5
        fill_w = int(bar_w * pct)
        bar_str = f"[{'='*fill_w}{'-'*(bar_w-fill_w)}] {time_str}"
        self.stdscr.addstr(h - 4, 2, bar_str, curses.color_pair(3))

        # Footer Line 2: Song Title
        if self.current_track:
             status_icon = "❚❚" if self.is_paused else "▶"
             
             song_title = self.current_track['title']
             # Append Channel to Footer if available
             ch_name = self.current_track.get('channel') or self.current_track.get('author')
             if ch_name:
                 song_title += f"   [{ch_name}]"
                 
             song_title = self.truncate(song_title, w - 10)
             self.stdscr.addstr(h - 3, 2, f"{status_icon} {song_title}", curses.color_pair(2))
        else:
             self.stdscr.addstr(h - 3, 2, self.t("stopped"), curses.color_pair(1))

        # Footer Line 3: System Message & Branding
        branding = "mytunes-pro.com/postgresql.co.kr"
        branding_x = w - 2 - len(branding)
        
        # Draw Branding always - Bright/Bold White
        self.stdscr.addstr(h - 2, branding_x, branding, curses.color_pair(1) | curses.A_BOLD)
        
        # Draw Status Msg
        # Draw Status Msg
        displayed_msg = ""
        attr = curses.A_NORMAL
        
        if self.player.loading:
            displayed_msg = "⏳ Loading..."
            # For Auto EQ, show what we are loading into
            # if EQUALIZER_KEYS[self.current_eq_index] == "Auto":
            #      displayed_msg += f" [Auto: {self.auto_preset_name}]"
            attr = curses.color_pair(6) | curses.A_BLINK
        elif self.status_msg:
             # Auto-clear only transients
             is_transient = "Invalid key" in self.status_msg or "잘못된 키" in self.status_msg or "영문" in self.status_msg or "English" in self.status_msg
             if time.time() - self.status_set_time > 5 and is_transient:
                 self.status_msg = ""
             else:
                 displayed_msg = f"📢 {self.status_msg}"
                 attr = curses.color_pair(3) | curses.A_BOLD

        # Fallback: Persistent Auto EQ Status
        if not displayed_msg:
             eq_mode = EQUALIZER_KEYS[self.current_eq_index]
             if eq_mode == "Auto":
                  displayed_msg = f"🎚 Auto: {self.auto_preset_name}"
                  # Use standard bold (color from terminal default/white) as requested "글자만 표시"
                  attr = curses.A_BOLD 
             elif eq_mode != "Flat":
                  displayed_msg = f"🎚 EQ: {eq_mode}"
                  attr = curses.A_BOLD

        if displayed_msg:
             avail_w = branding_x - 4
             if avail_w > 5:
                self.stdscr.addstr(h - 2, 2, self.truncate(displayed_msg, avail_w), attr)

        # List Area (Remaining Middle)
        list_top = 4
        list_h = h - footer_h - list_top
        self.draw_box(self.stdscr, list_top, 0, list_h, w)
        
        items = self.get_current_list()
        # Inner drawing area
        inner_h = list_h - 2
        inner_y = list_top + 1
        
        if not items:
            self.stdscr.addstr(inner_y + 1, 2, self.t("empty_list"), curses.color_pair(4))
        else:
            for i in range(inner_h):
                idx = i + self.scroll_offset
                if idx >= len(items): break
                item = items[idx]
                y_pos = inner_y + i
                
                is_sel = (idx == self.selection_idx)
                # Check URL match first, fallback to Title match (for robustness with MPV paths)
                is_playing = False
                if self.current_track:
                    if item.get("url") and item.get("url") == self.current_track.get("url"):
                        is_playing = True
                    elif item.get("title") and item.get("title") == self.current_track.get("title"):
                        is_playing = True
                
                prefix = "▶ " if is_sel else "  "
                chk_icon = "♫ " if is_playing else ""
                fav_icon = "★ " if (item.get("url") and self.dm.is_favorite(item['url'])) else ""
                dur_txt = f"[{item.get('duration')}]" if item.get("duration") else ""
                
                avail_w = w - 4 - len(prefix) - len(chk_icon) - len(fav_icon) - len(dur_txt)
                if avail_w < 5: avail_w = 5
                
                title_txt = self.truncate(item.get('title',''), avail_w)
                
                # Channel Name Logic (Smart Display)
                channel_txt = ""
                box_w = 0
                if w > 80: # Only show if screen is wide enough
                    raw_ch = item.get('channel') or item.get('author') or ""
                    if raw_ch:
                        # Max channel width: 20 or 25% of width
                        max_ch_w = min(20, w // 4)
                        if len(raw_ch) > max_ch_w:
                            raw_ch = raw_ch[:max_ch_w-1] + "…"
                        channel_txt = f"[{raw_ch}]"
                        box_w = len(channel_txt) + 1 # +1 padding
                
                # Refine Title Width based on Channel presence
                real_avail_w = avail_w - box_w
                if real_avail_w < 5: real_avail_w = 5
                
                title_txt = self.truncate(item.get('title',''), real_avail_w)
                
                try:
                    curr_x = 2
                    # Base Style
                    if is_sel:
                         base_style = curses.color_pair(5) | curses.A_BOLD
                    elif is_playing:
                         base_style = curses.color_pair(2) | curses.A_BOLD
                    else:
                         base_style = curses.A_NORMAL
                    
                    # 1. Prefix
                    self.stdscr.addstr(y_pos, curr_x, prefix, base_style)
                    curr_x += len(prefix)
                    
                    # 2. Play Icon
                    if chk_icon:
                         self.stdscr.addstr(y_pos, curr_x, chk_icon, base_style)
                         curr_x += len(chk_icon)
                         
                    # 3. Fav Icon
                    f_style = base_style
                    if fav_icon and not is_sel: f_style = curses.color_pair(3) | curses.A_BOLD
                    if fav_icon:
                         self.stdscr.addstr(y_pos, curr_x, fav_icon, f_style)
                         curr_x += len(fav_icon)
                         
                    # 4. Title
                    self.stdscr.addstr(y_pos, curr_x, title_txt, base_style)
                    curr_x += self.get_display_width(title_txt)
                    
                    # 5. Channel Info (Right aligned relative to title space or fixed?)
                    if channel_txt:
                        self.stdscr.addstr(y_pos, curr_x + 1, channel_txt, base_style | curses.A_DIM)
                        # No update to curr_x needed for duration anchor, but good for safety
                    
                    # 6. Duration (Right Anchored)
                    if dur_txt:
                        dur_x = w - 2 - len(dur_txt)
                        self.stdscr.addstr(y_pos, dur_x, dur_txt, base_style)
                        
                except: pass
        
        self.stdscr.refresh()

    def check_autoplay(self):
        # Auto-play next track from Global Queue
        # Guard: Don't autoplay if we are currently loading a track
        if self.player.loading: return

        try:
            is_idle = self.player.get_property("idle-active")
            if is_idle and self.current_track and self.queue:
                if self.queue_idx + 1 < len(self.queue):
                     self.queue_idx += 1
                     next_item = self.queue[self.queue_idx]
                     try: self.play_music(next_item, interactive=False, preserve_queue=True)
                     except: pass
                else:
                    self.current_track = None 
        except: pass

    def run(self):
        while self.running:
            try:
                self.loop_count = (self.loop_count + 1) % 1000
                self.update_playback_state()
                self.check_autoplay()
                self.draw()
                self.handle_input()
                
                # Idle / Sleep Check
                # If no input for 60s and Paused, slow down loop
                if time.time() - getattr(self, 'last_input_time', 0) > 60 and self.is_paused:
                     self.stdscr.timeout(1000)
                else:
                     self.stdscr.timeout(200)

            except Exception as e:
                # v1.8.4 - Global resilience: Catch and log loop errors instead of crashing
                try: 
                    with open("/tmp/mytunes_error.log", "a") as f:
                        f.write(f"[{time.ctime()}] Loop Error: {str(e)}\n")
                except: pass
                # Small sleep to prevent infinite tight loop on persistent error
                time.sleep(0.1)
        
        # Cleanup Mouse (Prevent terminal artifacts)
        try: curses.mousemask(0)
        except: pass

        if self.stop_on_exit:
            self.player.stop()
            self.player.cleanup_orphaned_mpv()

def main(stdscr):
    app = MyTunesApp(stdscr)
    app.run()

def cli():
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        # Don't show technical curses errors to user if box/win fails
        if "addstr() returned ERR" in str(e):
            print("Error: Terminal window is too small.")
        else:
            print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    cli()
