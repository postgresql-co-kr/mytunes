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

# Ensure Unicode support
locale.setlocale(locale.LC_ALL, '')

# === [Configuration] ===
DATA_FILE = os.path.expanduser("~/.pymusic_data.json")
MPV_SOCKET = "/tmp/mpv_socket"
LOG_FILE = "/tmp/mytunes_mpv.log"
APP_NAME = "MyTunes Pro"
APP_VERSION = "1.0.0"

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
        "header_help": "[S/1]검색 [F/2]즐겨찾기 [H/3]기록 [M/4]메인 [A/5]추가/삭제 [SPC]재생/중지 [Q/0]이전",
        "help_guide": "[↑/↓]이동 [Enter]선택 [S/1]검색 [F/2]즐겨찾기 [H/3]기록 [M/4]메인 [A/5]추가/삭제 [SPACE]재생/중지 [Q/0]이전",
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
        "header_help": "[S/1]Search [F/2]Favs [H/3]Hist [M/4]Main [A/5]Add/Del [SPC]Play/Pause [Q/0]Back",
        "help_guide": "[↑/↓]Move [Enter]Select [S/1]Search [F/2]Favs [H/3]Hist [M/4]Main [A/5]Add/Del [SPACE]Play/Pause [Q/0]Back",
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
        
    def load_data(self):
        if not os.path.exists(DATA_FILE):
            return {"history": [], "favorites": [], "language": "ko", "resume": {}}
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if "resume" not in data: data["resume"] = {}
                return data
        except Exception:
            return {"history": [], "favorites": [], "language": "ko", "resume": {}}

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
        is_fav = any(f['url'] == item['url'] for f in self.data['favorites'])
        if is_fav:
            self.data['favorites'] = [f for f in self.data['favorites'] if f['url'] != item['url']]
            status = False
        else:
            self.data['favorites'].insert(0, item)
            status = True
        self.save_data()
        return status

    def is_favorite(self, url):
        return any(f['url'] == url for f in self.data['favorites'])

# === [Player Logic with Advanced IPC] ===
class Player:
    def __init__(self):
        self.current_proc = None
        self.loading = False
        
    def play(self, url, start_pos=0):
        self.stop()
        self.loading = True
        if os.path.exists(MPV_SOCKET):
            try: os.remove(MPV_SOCKET)
            except OSError: pass
        
        # Start mpv with IPC server
        cmd = [
            "mpv", "--no-video", "--vo=null", "--no-terminal", "--force-window=no",
            f"--input-ipc-server={MPV_SOCKET}", 
            "--idle=yes", # Keep running even after track ends (optional, usually better to restart per track for stability herein)
            url
        ]
        
        if start_pos > 0:
            cmd.append(f"--start={start_pos}")
        
        # Remove --idle=yes if we want it to close after song, 
        # but for consistent IPC let's stick to simple playback.
        # Actually without --idle=yes, it exits after song.
        
        try: log = open(LOG_FILE, "a")
        except: log = subprocess.DEVNULL
            
        kwargs = {"stdout": subprocess.DEVNULL, "stderr": log}
        if os.name != "nt": kwargs["preexec_fn"] = os.setpgrp
            
        self.current_proc = subprocess.Popen(cmd, **kwargs)

    def stop(self):
        subprocess.run(["pkill", "-f", "mpv"], stderr=subprocess.DEVNULL)
        self.current_proc = None

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
        self.search_results = []
        self.selection_idx = 0
        self.scroll_offset = 0
        self.current_track = None
        self.cached_history = [] # Snapshot for stable history view
        self.status_msg = ""
        
        # Playback State
        self.playback_time = 0
        self.playback_duration = 0
        self.is_paused = False
        self.last_save_time = time.time()
        self.status_blink = False
        
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
        # Poll MPV for true state
        try:
            t = self.player.get_property("time-pos")
            d = self.player.get_property("duration")
            p = self.player.get_property("pause")
            title = self.player.get_property("media-title")
            
            if t is not None: 
                self.playback_time = float(t)
                # Clear loading state once we get valid time
                if self.player.loading and self.playback_time > 0:
                    self.player.loading = False
                
                # Update Resume Data (Memory)
                if self.current_track and self.playback_duration > 30:
                    # Clear if > 99% played
                    if self.playback_time / self.playback_duration > 0.99:
                        self.dm.set_progress(self.current_track['url'], 0)
                    elif self.playback_time > 10:
                        self.dm.set_progress(self.current_track['url'], self.playback_time)
            
            if d is not None: self.playback_duration = float(d)
            if p is not None: self.is_paused = p
            
            # Sync title/url if missing (Background Play persistence)
            if self.current_track is None and title:
                # Try to fetch URL as well to ensure list highlighting works
                url_path = self.player.get_property("path")
                if not url_path: url_path = ""
                self.current_track = {"title": title, "url": url_path}
                
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
        k_char = key if isinstance(key, str) else ""
        
        # Navigation logic
        # Back: Q, Left Arrow, Backspace + Korean 'ㅂ' (q), 0
        if key == curses.KEY_LEFT or key == curses.KEY_BACKSPACE or key == 127 or \
           k_char in ['q', 'Q', 'ㅂ', '0']:
            if len(self.view_stack) > 1:
                self.view_stack.pop(); self.selection_idx = 0; self.scroll_offset = 0
                self.status_msg = "" 
            # Else: Do nothing (Prevent Quit on Q)
            return

        current_list = self.get_current_list()

        if key == curses.KEY_UP:
            if self.selection_idx > 0:
                self.selection_idx -= 1
                if self.selection_idx < self.scroll_offset: self.scroll_offset = self.selection_idx
        elif key == curses.KEY_DOWN:
            if self.selection_idx < len(current_list) - 1:
                self.selection_idx += 1
                h, _ = self.stdscr.getmaxyx()
                list_area_height = h - 7 - 5
                if self.selection_idx >= self.scroll_offset + list_area_height:
                    self.scroll_offset = self.selection_idx - list_area_height + 1
        
        # Enter
        elif key == '\n' or key == 10 or key == 13:
            self.activate_selection(current_list)
        
        # Shortcuts with Korean support AND Number keys (for instant reaction)
        # Search: S, ㄴ, 1
        elif k_char in ['s', 'S', 'ㄴ', '1']: 
            self.prompt_search()
        
        # Favorites: F, ㄹ, 2
        elif k_char in ['f', 'F', 'ㄹ', '2']:
            self.view_stack.append("favorites"); self.selection_idx = 0
            self.status_msg = self.t("favorites_info", DATA_FILE)
            
        # History: H, ㅗ, 3
        elif k_char in ['h', 'H', 'ㅗ', '3']:
            self.cached_history = list(self.dm.data['history']) # Snapshot
            self.view_stack.append("history"); self.selection_idx = 0; self.status_msg = self.t("hist_info")
            
        # Main Menu: M, ㅡ, 4
        elif k_char in ['m', 'M', 'ㅡ', '4']:
            self.view_stack = ["main"]; self.selection_idx = 0; self.scroll_offset = 0; self.status_msg = ""
            
        # Play/Pause: Space
        elif k_char == ' ': 
            self.player.toggle_pause()

        # Seek: < (Rewind 10s), > (Forward 10s)
        # Also support , and . for convenience
        elif k_char in [',', '<']:
            self.player.seek(-10)
        elif k_char in ['.', '>']:
            self.player.seek(10)
            
        # ESC: Background Play (Exit but keep music)
        elif key == 27:
            self.stop_on_exit = False
            self.running = False
            
        # Add to Favorites: A, ㅁ, 5
        elif k_char in ['a', 'A', 'ㅁ', '5']:
            if current_list and 0 <= self.selection_idx < len(current_list):
                target_item = current_list[self.selection_idx]
                # Ensure it's a valid track item (has url)
                if "url" in target_item:
                    is_added = self.dm.toggle_favorite(target_item)
                    self.status_msg = self.t("fav_added") if is_added else self.t("fav_removed")

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
        self.stdscr.nodelay(True)
        self.stdscr.touchwin()
        self.stdscr.refresh()
        return res

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
            self.current_track = item
            self.dm.add_history(item)
            
            start_pos = 0
            if 'url' in item:
                saved = self.dm.get_progress(item['url'])
                if saved > 10: 
                    if self.ask_resume(saved, item.get('title', 'Unknown')): start_pos = saved
            
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
        self.stdscr.nodelay(True)
        self.stdscr.touchwin(); self.stdscr.refresh()
        
        return "".join(chars).strip()

    def prompt_search(self):
        curses.flushinp() # Clear any buffered keys
        query = self.input_dialog(self.t("search_label"), self.t("search_prompt"))
        if query:
            self.status_msg = self.t("searching")
            self.draw()
            self.perform_search(query)

    def perform_search(self, query):
        try:
            # Resolve yt-dlp path: checks dirname of current python (venv/bin) first
            yt_dlp_cmd = "yt-dlp"
            venv_bin = os.path.dirname(sys.executable)
            venv_yt_dlp = os.path.join(venv_bin, "yt-dlp")
            if os.path.exists(venv_yt_dlp) and os.access(venv_yt_dlp, os.X_OK):
                yt_dlp_cmd = venv_yt_dlp

            # Optimize search for music/audio
            search_query = f"{query} music"
            cmd = [yt_dlp_cmd, f"ytsearch40:{search_query}", "--dump-json", "--flat-playlist", "--no-playlist", "--skip-download"]
            result = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode('utf-8')
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
                self.search_results = new
                self.view_stack.append("search")
                self.selection_idx = 0; self.scroll_offset = 0
                self.status_msg = "Search Done."
            else: self.status_msg = self.t("no_results")
        except Exception as e: self.status_msg = f"Error: {e}"

    def draw(self):
        self.stdscr.erase()
        h, w = self.stdscr.getmaxyx()
        
        if h < 15 or w < 40:
            self.stdscr.addstr(0, 0, "Window too small!")
            return

        # Header (3 lines)
        self.draw_box(self.stdscr, 0, 0, 3, w, APP_NAME)
        title = self.t("title", APP_VERSION)
        help_txt = self.t("header_help")
        gap = w - 4 - self.get_display_width(title) - self.get_display_width(help_txt)
        if gap < 2: gap = 2
        hdr_txt = f"{title}{' '*gap}{help_txt}"
        self.stdscr.addstr(1, 2, self.truncate(hdr_txt, w-4), curses.color_pair(1) | curses.A_BOLD)

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
        list_top = 3
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
        # Auto-play next track if player is idle (song finished)
        try:
            is_idle = self.player.get_property("idle-active")
            if is_idle and self.current_track:
                # Find current track in current list
                items = self.get_current_list()
                curr_url = self.current_track.get('url')
                
                found_idx = -1
                for i, item in enumerate(items):
                    if item.get('url') == curr_url:
                        found_idx = i
                        break
                
                # If found and next item exists
                if found_idx != -1 and found_idx + 1 < len(items):
                     next_item = items[found_idx + 1]
                     self.selection_idx = found_idx + 1 # Move cursor
                     
                     # Check if we need to scroll
                     inner_h = self.stdscr.getmaxyx()[0] - 5 - 3 - 2
                     if self.selection_idx >= self.scroll_offset + inner_h:
                         self.scroll_offset = self.selection_idx - inner_h + 1
                     
                     self.play_music(next_item)
                else:
                    # End of list or track not in list -> Stop
                    self.current_track = None 
        except: pass

    def run(self):
        while self.running:
            self.update_playback_state()
            self.check_autoplay()
            self.draw()
            self.handle_input()
        
        if self.stop_on_exit:
            self.player.stop()

def main(stdscr):
    app = MyTunesApp(stdscr)
    app.run()

if __name__ == "__main__":
    try: curses.wrapper(main)
    except KeyboardInterrupt: sys.exit(0)
