#!/usr/bin/env python3
"""
MyTunes Pro - Professional TUI Edition v1.0
Premium CLI Music Player with Curses Interface
Enhanced with Context7-researched MPV IPC & Resize Handling
"""
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
# Suppress urllib3 warning about LibreSSL compatibility
warnings.filterwarnings("ignore", message=".*urllib3 v2 only supports OpenSSL 1.1.1+.*")
import webbrowser
import tempfile
import shutil
import pusher
import requests


# Ensure Unicode support
# locale.setlocale(locale.LC_ALL, '')

# === [Configuration] ===
DATA_FILE = os.path.expanduser("~/.pymusic_data.json")
MPV_SOCKET = "/tmp/mpv_socket"
LOG_FILE = "/tmp/mytunes_mpv.log"
PID_FILE = "/tmp/mytunes_mpv.pid"
APP_NAME = "MyTunes Pro"
APP_VERSION = "1.8.1"

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
        "header_r2": "[F7]유튜브 [F8]라이브 [F9]라이브공유 [SPC]Play/Stop [+/-]볼륨 [<>]빨리감기",
        "help_guide": "[j/k]이동 [En]선택 [h/q]뒤로 [S/1]검색 [F/2]즐겨찾기 [R/3]기록 [M/4]메인 [F7]유튜브 [F8]라이브 [F9]라이브공유",
        "menu_main": "☰ 메인 메뉴",
        "menu_search_results": "⌕ YouTube 음악 검색",
        "menu_favorites": "★ 나의 즐겨찾기",
        "menu_history": "◷ 재생 기록",
        "menu_bg_play": "⧉ 백그라운드 재생 (나가기)",
        "lang_toggle": "⚙ 언어 변경 (English)",
        "favorites_info": "즐겨찾기 저장 위치: {}",
        "hist_info": "최근 재생 기록 (최대 100곡)",
        "time_fmt": "{}/{}",
        "vol_fmt": "볼륨: {}%"
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
        "header_r2": "[F7]YT [F8]Live [F9]LiveShare [SPC]Play/Stop [+/-]Vol [<>]Seek",
        "help_guide": "[j/k]Move [En]Select [h/q]Back [S/1]Srch [F/2]Fav [R/3]Hist [M/4]Main [F7]YT [F8]Live [F9]Share",
        "menu_main": "☰ Main Menu",
        "menu_search_results": "⌕ Search YouTube Music",
        "menu_favorites": "★ My Favorites",
        "menu_history": "◷ History",
        "menu_bg_play": "⧉ Background Play (Leave)",
        "lang_toggle": "⚙ Switch Language (한국어)",
        "favorites_info": "Favorites stored at: {}",
        "hist_info": "Recent Playback History (Max 100)",
        "time_fmt": "{}/{}",
        "vol_fmt": "Vol: {}%"
    }
}

# === [Data Management] ===
class DataManager:
    def __init__(self):
        self.data = self.load_data()
        self.favorites_set = {f['url'] for f in self.data.get('favorites', []) if 'url' in f}
        
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
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

    def get_progress(self, url):
        return self.data.get("resume", {}).get(url, 0)

    def set_progress(self, url, time_pos):
        if "resume" not in self.data: self.data["resume"] = {}
        self.data["resume"][url] = time_pos

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

# === [Player Logic with Advanced IPC] ===
class Player:
    def __init__(self):
        self.current_proc = None
        self.loading = False
        
        self.current_proc = None
        self.loading = False
        
        
        self.loading_ts = 0
        
        # Cleanup pre-existing instance if any
        # self.cleanup_orphaned_mpv() # Moved to play() per user request
        
    def cleanup_orphaned_mpv(self):
        # User requested revert to aggressive pkill for reliability
        # This ensures any previous background instances are killed
        try:
            subprocess.run(["pkill", "-f", "mpv"], stderr=subprocess.DEVNULL)
        except: pass
        
    def play(self, url, start_pos=0):
        # 1. Try to reuse existing instance via IPC (Graceful)
        if os.path.exists(MPV_SOCKET):
            try:
                # "loadfile" <url> "replace" stops current and plays new
                resp = self.send_cmd(["loadfile", url, "replace"])
                if resp and not resp.get("error"):
                    if start_pos > 0:
                        self.send_cmd(["seek", str(start_pos), "absolute"])
                    self.loading = True
                    self.loading_ts = time.time()
                    return # Success! No need to restart
            except:
                pass # Fallback to restart if IPC fails

        # 2. Fallback: Clean up and start fresh (Aggressive)
        self.cleanup_orphaned_mpv()
        
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
            "--idle=yes", 
            url
        ]
        
        # B. macOS Specific UI Optimizations
        if sys.platform == "darwin":
            # 'accessory' hides Dock but allows system resources
            cmd.append("--macos-app-activation-policy=accessory")
            
        # C. YouTube 403 Forbidden Bypass (Cross-platform robustness)
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
        """Send raw command list to MPV via JSON IPC."""
        try:
            client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            client.settimeout(0.1) # Fast timeout
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
            return json.loads(response.decode('utf-8'))
        except:
            return None

    def get_property(self, prop):
        res = self.send_cmd(["get_property", prop])
        if res and "data" in res:
            return res["data"]
        return None
        
    def set_property(self, prop, value):
        self.send_cmd(["set_property", prop, value])

    def toggle_pause(self):
        self.send_cmd(["cycle", "pause"])

    def seek(self, seconds):
        """Seek relative to current position."""
        self.send_cmd(["seek", seconds, "relative"])

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
        
        # Search State
        self.current_search_query = None
        self.search_page = 1
        self.is_loading_more = False
        
        # Playback State
        self.playback_time = 0
        self.playback_duration = 0
        self.is_paused = False
        self.last_save_time = time.time()
        self.status_blink = False
        
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
        
        # Register Signal for Terminal Disconnect (Window Close)
        try:
            signal.signal(signal.SIGHUP, self.handle_disconnect)
        except: pass

        # Pusher Client
        try:
            self.pusher = pusher.Pusher(
                app_id='2106370',
                key='44e3d7e4957944c867ec',
                secret='0be8e65a287bbccc7369',
                cluster='ap3',
                ssl=True
            )
        except: self.pusher = None
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
            # 1. Mandatory every loop: Current time (for progress bar)
            t = self.player.get_property("time-pos")
            if t is not None: 
                self.playback_time = float(t)
                if self.player.loading and self.playback_time >= 0:
                    self.player.loading = False
                
                # Update Resume Data (Memory) - Throttle save logic
                if self.current_track and self.playback_duration > 30:
                    if self.playback_time / self.playback_duration > 0.99:
                        self.dm.set_progress(self.current_track['url'], 0)
                    elif self.playback_time > 10:
                        self.dm.set_progress(self.current_track['url'], self.playback_time)

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

            # Timeout fallback for loading state (remains every loop logic)
            if self.player.loading and (time.time() - getattr(self.player, 'loading_ts', 0) > 8):
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

    def handle_input(self):
        try:
            # Use get_wch for Unicode support (captures Korean shortcuts)
            key = self.stdscr.get_wch()
        except curses.error:
            return
        except:
            return

        if key == -1: return

        # Handle formatting: invalid key might be int -1
        
        # Resize Info
        if key == curses.KEY_RESIZE:
            self.stdscr.clear()
            self.stdscr.refresh()
            return

        # GLOBAL ESC: Background Play (Exit but keep music)
        # get_wch returns int 27 or str '\x1b' depending on system/lib
        if key == 27 or key == '\x1b':
            self.stop_on_exit = False
            self.running = False
            return

        # Helper to normalize input for checking
        k_char = str(key).lower() if isinstance(key, str) else ""
        
        current_list = self.get_current_list()

        # Navigation logic
        # Back: Q, Left Arrow, Backspace, Korean 'ㅂ' (q), h, 6
        if key == curses.KEY_LEFT or key == curses.KEY_BACKSPACE or key == 127 or \
           k_char in ['q', 'ㅂ', '6', 'h', 'ㅗ']:
            if len(self.view_stack) > 1:
                # Pop current view and push to forward stack
                current_view = self.view_stack.pop()
                self.forward_stack.append(current_view)
                
                self.selection_idx = 0; self.scroll_offset = 0
                self.status_msg = "" 
            # Else: Do nothing (Prevent Quit on Q)
            return

        # Forward: L, Right Arrow (Browser Style)
        # Re-visit the view we just popped from
        if k_char in ['l', 'L', 'ㅣ'] or key == curses.KEY_RIGHT:
            if self.forward_stack:
                next_view = self.forward_stack.pop()
                self.view_stack.append(next_view)
                self.selection_idx = 0; self.scroll_offset = 0
                self.status_msg = ""
            return

        if key == curses.KEY_UP or k_char in ['k', 'ㅏ']:
            if self.selection_idx > 0:
                self.selection_idx -= 1
                if self.selection_idx < self.scroll_offset: self.scroll_offset = self.selection_idx
        elif key == curses.KEY_DOWN or k_char in ['j', 'ㅓ']:
            if self.selection_idx < len(current_list) - 1:
                self.selection_idx += 1
                h, _ = self.stdscr.getmaxyx()
                # Use h - 10 to match inner_h in draw() (h - footer_h(5) - header_top(3) - borders(2))
                list_area_height = h - 10
                if self.selection_idx >= self.scroll_offset + list_area_height:
                    self.scroll_offset = self.selection_idx - list_area_height + 1

        # Enter / Select: Enter Only (L moved to Forward)
        elif key == '\n' or key == 10 or key == 13:
            self.activate_selection(current_list)
        
        # Shortcuts with Korean support AND Number keys (for instant reaction)
        # Search: S, ㄴ, 1, /
        elif k_char in ['s', 'S', 'ㄴ', '1', '/']: 
            self.forward_stack = [] # Clear forward history on new navigation
            self.prompt_search()
        
        # Favorites: F, ㄹ, 2
        elif k_char in ['f', 'F', 'ㄹ', '2']:
            if self.view_stack[-1] != "favorites":
                self.forward_stack = [] 
                self.view_stack.append("favorites")
                self.selection_idx = 0
            self.status_msg = self.t("favorites_info", DATA_FILE)
            
        # History: R, ㄱ, 3 (Changed from H to avoid Back conflict)
        elif k_char in ['r', 'R', 'ㄱ', '3']:
            if self.view_stack[-1] != "history":
                self.forward_stack = []
                self.cached_history = list(self.dm.data['history']) # Snapshot
                self.view_stack.append("history")
                self.selection_idx = 0
            self.status_msg = self.t("hist_info")
            
        # Main Menu: M, ㅡ, 4
        elif k_char in ['m', 'M', 'ㅡ', '4']:
            self.forward_stack = [] # Clear forward history
            self.view_stack = ["main"]; self.selection_idx = 0; self.scroll_offset = 0; self.status_msg = ""
            
        # Play/Pause: Space
        elif k_char == ' ': 
            self.player.toggle_pause()

        # Volume: 9/0 or [/] or -/+
        elif k_char in ['-','_']:
            self.player.change_volume(-5)
            self.status_msg = "Volume -5"
        elif k_char in ['+','=']:
            self.player.change_volume(5)
            self.status_msg = "Volume +5"

        # Seek: ,/. (10s), </> (30s)
        elif k_char == ',':
            self.player.seek(-10)
        elif k_char == '.':
            self.player.seek(10)
        elif k_char == '<':
            self.player.seek(-30)
            self.status_msg = "Rewind 30s"
        elif k_char == '>':
            self.player.seek(30)
            self.status_msg = "Forward 30s"
            
        elif key == 27:
            self.stop_on_exit = False
            self.running = False
            
        # Share Track (F9): Real-time Publish
        elif key == curses.KEY_F9:
            if current_list and 0 <= self.selection_idx < len(current_list):
                target_item = current_list[self.selection_idx]
                url = target_item.get('url')
                title = target_item.get('title', 'Unknown Title')
                
                if url:
                    # If it's US, try to re-fetch country info one more time (maybe misdetected)
                    if self.dm.get_country() == 'US':
                        threading.Thread(target=self.dm.fetch_country, daemon=True).start()

                    # Dedup Check: Using a time-based cooldown (e.g. 5 seconds) for same URL
                    last_sent_time = self.sent_history.get(url, 0)
                    if time.time() - last_sent_time < 5:
                        self.status_msg = "⚠️  Already Shared Recently!"
                    else:
                        try:
                            # Send to Pusher
                            payload = {
                                "title": title,
                                "url": url,
                                "duration": target_item.get('duration', '--:--'),
                                "country": self.dm.get_country(),
                                "timestamp": time.time()
                            }
                            if self.pusher:
                                self.pusher.trigger('mytunes-global', 'share-track', payload)
                                self.sent_history[url] = time.time()
                                safe_title = self.truncate(title, 50)
                                self.status_msg = f"🚀 Shared: {safe_title}..."
                            else:
                                self.status_msg = "❌ Pusher Error"
                        except Exception as e:
                            self.status_msg = f"❌ Share Failed: {str(e)}"

            
        # Add to Favorites: A, ㅁ, 5
        elif k_char in ['a', 'A', 'ㅁ', '5']:
            if current_list and 0 <= self.selection_idx < len(current_list):
                target_item = current_list[self.selection_idx]
                # Ensure it's a valid track item (has url)
                if "url" in target_item:
                    is_added = self.dm.toggle_favorite(target_item)
                    self.status_msg = self.t("fav_added") if is_added else self.t("fav_removed")

        # Open in Browser (YouTube): F7
        elif key == curses.KEY_F7:
            if current_list and 0 <= self.selection_idx < len(current_list):
                target_item = current_list[self.selection_idx]
                url = target_item.get('url')
                if url:
                    if self.is_remote():
                        self.show_copy_dialog("YouTube", url)
                    else:
                        try:
                            # Robust multi-platform open
                            if sys.platform == 'darwin':
                                subprocess.Popen(["open", url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                            elif sys.platform == 'win32':
                                os.startfile(url)
                            elif self.is_wsl():
                                # In WSL, call the Windows shell to open the URL in Windows browser
                                subprocess.Popen(["cmd.exe", "/c", "start", url.replace("&", "^&")], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                            else:
                                webbrowser.open(url)
                            self.status_msg = "🌐 Opening YouTube in Browser..."
                        except:
                            webbrowser.open(url)
                            self.status_msg = "🌐 Opening YouTube..."

        # Open Live Station: F8
        elif key == curses.KEY_F8:
            live_url = "https://mytunes.postgresql.co.kr/live/"
            if self.is_remote():
                self.show_copy_dialog("Live Station", live_url)
                return

            # Add timestamp to user-data-dir to force size/position flags to be respected (prevents "remembering")
            # Using int(time.time() / 3600) to keep it stable within the same hour but fresh enough for new versions
            temp_user_data = os.path.join(tempfile.gettempdir(), f"mytunes_v174_{int(time.time() / 10)}")
            
            # Universal flags
            flags = [
                f"--app={live_url}", 
                "--window-size=712,800", 
                "--window-position=100,100",
                f"--user-data-dir={temp_user_data}", 
                "--no-first-run",
                "--disable-extensions",
                "--disable-default-apps",
                "--disable-features=Translation",
                "--disable-save-password-bubble",
                "--disable-translate"
            ]
            
            launched = False
            # 1. macOS (Avoid AppleScript to prevent permission prompts)
            if sys.platform == 'darwin':
                browsers = [
                    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                    "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"
                ]
                for b_path in browsers:
                    if os.path.exists(b_path):
                        try:
                            # Use 'open -na' but without AppleScript to stay 'standard' and avoid prompts
                            subprocess.Popen(["open", "-na", b_path, "--args"] + flags, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                            launched = True; break
                        except: pass
            
            # 2. Windows Native
            elif sys.platform == 'win32':
                win_paths = [
                    os.path.join(os.environ.get('PROGRAMFILES', 'C:\\Program Files'), 'Google\\Chrome\\Application\\chrome.exe'),
                    os.path.join(os.environ.get('PROGRAMFILES(X86)', 'C:\\Program Files (x86)'), 'Google\\Chrome\\Application\\chrome.exe'),
                    os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Google\\Chrome\\Application\\chrome.exe'),
                    os.path.join(os.environ.get('PROGRAMFILES', 'C:\\Program Files'), 'BraveSoftware\\Brave-Browser\\Application\\brave.exe'),
                    os.path.join(os.environ.get('PROGRAMFILES(X86)', 'C:\\Program Files (x86)'), 'Microsoft\\Edge\\Application\\msedge.exe'),
                    os.path.join(os.environ.get('PROGRAMFILES', 'C:\\Program Files'), 'Microsoft\\Edge\\Application\\msedge.exe'),
                ]
                # v1.8.1 - Precise: No internal quotes around URL to avoid misparsing as literal parts of URI
                win_flags = [
                    f'--app={live_url}',
                    '--window-size=712,800',
                    '--window-position=100,100',
                    '--new-window',
                    '--no-first-run',
                    '--disable-extensions'
                ]
                for p in win_paths:
                    if os.path.exists(p):
                        try:
                            # Use list-based Popen for native Windows
                            subprocess.Popen([p] + win_flags, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                            launched = True; break
                        except: pass
            
            # 3. WSL (Run Windows Chrome via cmd.exe)
            elif self.is_wsl():
                try:
                    # v1.8.1 - Pure and Precise for WSL->CMD
                    # 1. No internal quotes for the URL (prevents "Empty URL" / navigation failure)
                    # 2. Use start "" chrome (Prevents 'start' from hijacking the first flag as a title)
                    # 3. Combined flags for maximum compatibility
                    c_args = [
                        f'--app={live_url}',
                        '--window-size=712,800',
                        '--window-position=100,100',
                        '--new-window',
                        '--no-first-run',
                        '--disable-extensions'
                    ]
                    # Direct call to chrome via cmd start
                    full_cmd = f'start "" chrome {" ".join(c_args)}'
                    subprocess.Popen(["cmd.exe", "/c", full_cmd], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    launched = True
                except:
                    # Fallback to general start
                    try:
                        subprocess.Popen(["cmd.exe", "/c", "start", live_url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        launched = True
                    except: pass

            # 4. Native Linux
            else:
                for b in ['google-chrome', 'google-chrome-stable', 'brave-browser', 'chromium-browser', 'chromium']:
                    p = shutil.which(b)
                    if p:
                        try:
                            subprocess.Popen([p] + flags, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); launched = True; break
                        except: pass

            if launched:
                self.status_msg = "📡 Opening Live Popup (712x800)..."
            else:
                webbrowser.open(live_url)
                self.status_msg = "📡 Opening Live Station (Browser)..."

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
                k = win.getch()
                if k == -1: continue
                
                # ESC -> Background Play (Exit app)
                if k == 27:
                    self.stop_on_exit = False
                    self.running = False
                    res = False # Or irrelevant since we quit
                    break
                
                if k in [10, 13, curses.KEY_ENTER, ord(' ')]: 
                    res = True
                    break
                if k in [ord('0'), ord('r'), ord('R')]: 
                    res = False
                    break
                    
        except: res = True # Default to Resume on error
        
        # Cleanup
        self.stdscr.timeout(200) # Ensure timeout is restored, NOT nodelay(True)
        self.stdscr.touchwin()
        self.stdscr.refresh()
        return res

    def is_remote(self):
        return 'SSH_CONNECTION' in os.environ or 'SSH_CLIENT' in os.environ

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
                k = win.getch()
                if k in [10, 13, curses.KEY_ENTER, 27, ord(' ')]: 
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
            # Check for Load More Button
            if item.get("id") == "load_more_btn":
                self.load_more_results()
                return

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
            self.perform_search(query)
        else:
            # Revert if no query and we were just previewing history
            # But requirement 2: "If Enter with no query, preserve previous search results"
            # This is tricky because ESC and empty Enter currently both return "".
            # I will assume "" means "keep current view (history)".
            # If the user wants to CANCEL and go back to Main, they might need ESC.
            pass

    def perform_search(self, query, page=1):
        try:
            self.is_loading_more = True
            if page == 1:
                self.current_search_query = query
                self.search_page = 1
                self.status_msg = self.t("searching")
            else:
                self.status_msg = "Loading next 50..."
            self.draw() # Force redraw to show status

            # Resolve yt-dlp path: checks dirname of current python (venv/bin) first
            yt_dlp_cmd = "yt-dlp"
            venv_bin = os.path.dirname(sys.executable)
            venv_yt_dlp = os.path.join(venv_bin, "yt-dlp")
            if os.path.exists(venv_yt_dlp) and os.access(venv_yt_dlp, os.X_OK):
                yt_dlp_cmd = venv_yt_dlp

            # Optimize search for music/audio
            limit = 50
            # yt-dlp logic: ytsearchN asks for N results total.
            # to get page 2 (51-100), we ask for 100, checking playlist-items indices?
            # actually ytsearchN with --playlist-start START works.
            # We ask for (page * limit) because 'ytsearch' usually returns 'up to N'.
            # If we just ask for 50 with start 51, it might fail depending on yt-dlp version.
            # Safest is: ytsearch(page*limit) with --playlist-start ((page-1)*limit + 1)
            
            total_fetch = page * limit
            start_index = (page - 1) * limit + 1
            
            search_query = f"{query} music"
            cmd = [
                yt_dlp_cmd, 
                f"ytsearch{total_fetch}:{search_query}", 
                "--dump-json", "--flat-playlist", "--no-playlist", "--skip-download",
                "--playlist-start", str(start_index)
            ]
            
            try:
                result = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode('utf-8')
            except subprocess.CalledProcessError:
                result = "" # Handle error or empty
                
            new = []
            for line in result.strip().split("\n"):
                if line:
                    try:
                        d = json.loads(line)
                        url = d.get("url")
                        if not url or "http" not in url: url = f"https://www.youtube.com/watch?v={d.get('id')}"
                        dur = d.get("duration", 0)
                        dur_str = f"{int(dur)//60}:{int(dur)%60:02d}" if dur else ""
                        new.append({"title": d.get("title", "Unknown"), "url": url, "duration": dur_str})
                    except: pass
            
            if new:
                # Remove previous 'Load More' button if exists
                if self.search_results and self.search_results[-1].get("id") == "load_more_btn":
                    self.search_results.pop()
                    
                # Append Load More Button if we got full batch (likely more exists)
                # Or just always add it if we got results.
                # Adding it at the end of new list
                load_more_item = {
                    "title": "[ Next 50 Results... ]" if self.lang == 'en' else "[ 다음 50개 더 보기... ]",
                    "id": "load_more_btn",
                    "url": "", # Dummy
                    "duration": ""
                }
                new.append(load_more_item)

                if page == 1:
                    self.search_results = new
                    if self.view_stack[-1] != "search":
                        self.view_stack.append("search")
                    self.selection_idx = 0; self.scroll_offset = 0
                    
                    # SAVE to History (Exclude load_more_btn)
                    items_to_save = [x for x in new if x.get('id') != 'load_more_btn']
                    self.dm.add_search_results(items_to_save)
                    
                else:
                    self.search_results.extend(new)
                    # Also save subsequent pages to history
                    items_to_save = [x for x in new if x.get('id') != 'load_more_btn']
                    self.dm.add_search_results(items_to_save)
                
                self.search_page = page
                self.status_msg = f"Search Done. ({len(self.search_results)-1})" # -1 for button
            else:
                if page == 1: self.status_msg = self.t("no_results")
                else: 
                     self.status_msg = "No more results."
                     # Remove button if no more
                     if self.search_results and self.search_results[-1].get("id") == "load_more_btn":
                        self.search_results.pop()
        except Exception as e: self.status_msg = f"Error: {e}"
        finally:
            self.is_loading_more = False

    def load_more_results(self):
        if self.current_search_query and not self.is_loading_more:
            self.perform_search(self.current_search_query, self.search_page + 1)

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
             song_title = self.truncate(self.current_track['title'], w - 10)
             self.stdscr.addstr(h - 3, 2, f"{status_icon} {song_title}", curses.color_pair(2))
        else:
             self.stdscr.addstr(h - 3, 2, self.t("stopped"), curses.color_pair(1))

        # Footer Line 3: System Message & Branding
        branding = "postgresql.co.kr/debate300.com"
        branding_x = w - 2 - len(branding)
        
        # Draw Branding always - Bright/Bold White
        self.stdscr.addstr(h - 2, branding_x, branding, curses.color_pair(1) | curses.A_BOLD)
        
        # Draw Status Msg
        if self.player.loading:
            self.stdscr.addstr(h - 2, 2, f"⏳ Loading...", curses.color_pair(6) | curses.A_BLINK)
        elif self.status_msg:
             avail_w = branding_x - 4
             if avail_w > 5:
                msg = self.truncate(self.status_msg, avail_w)
                attr = curses.color_pair(6)
                if self.status_blink: attr |= curses.A_BLINK | curses.A_BOLD
                self.stdscr.addstr(h - 2, 2, f"📢 {msg}", attr)

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
                    # If selected, base_style is Blue/White. If playing(unselected), Green.
                    self.stdscr.addstr(y_pos, curr_x, prefix, base_style)
                    curr_x += len(prefix)
                    
                    # 2. Play Icon (Green if not selected)
                    # base_style already covers Green if playing and not selected.
                    if chk_icon:
                         self.stdscr.addstr(y_pos, curr_x, chk_icon, base_style)
                         curr_x += len(chk_icon)
                         
                    # 3. Fav Icon (Yellow if not selected)
                    f_style = base_style
                    if fav_icon and not is_sel: f_style = curses.color_pair(3) | curses.A_BOLD
                    if fav_icon:
                         self.stdscr.addstr(y_pos, curr_x, fav_icon, f_style)
                         curr_x += len(fav_icon)
                         
                    # 4. Title
                    self.stdscr.addstr(y_pos, curr_x, title_txt, base_style)
                    curr_x += self.get_display_width(title_txt)
                    
                    # 5. Fill Padding
                    remain = w - 2 - curr_x - len(dur_txt)
                    if remain > 0:
                        self.stdscr.addstr(y_pos, curr_x, " "*remain, base_style)
                        curr_x += remain
                        
                    # 6. Duration
                    if dur_txt:
                        self.stdscr.addstr(y_pos, curr_x, dur_txt, base_style)
                        
                except: pass
        
        self.stdscr.refresh()

    def check_autoplay(self):
        # Auto-play next track from Global Queue
        try:
            is_idle = self.player.get_property("idle-active")
            if is_idle and self.current_track and self.queue:
                if self.queue_idx + 1 < len(self.queue):
                     self.queue_idx += 1
                     next_item = self.queue[self.queue_idx]
                     
                     if next_item.get('id') == 'load_more_btn':
                         # TODO: Auto-trigger load more? For now just stop.
                         self.current_track = None 
                         return
                     
                     try: self.play_music(next_item, interactive=False, preserve_queue=True)
                     except: pass
                else:
                    self.current_track = None 
        except: pass

    def run(self):
        while self.running:
            self.loop_count = (self.loop_count + 1) % 1000
            self.update_playback_state()
            self.check_autoplay()
            self.draw()
            self.handle_input()
        
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
