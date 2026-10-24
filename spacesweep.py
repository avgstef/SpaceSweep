import os
import sys
import shutil
import string
import tempfile
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from datetime import datetime

APP_NAME = "SpaceSweep"
VERSION = "1.3.0"
BG = "#090909"
SIDEBAR = "#101010"
SURFACE = "#151515"
SURFACE_2 = "#202020"
SURFACE_3 = "#2b2b2b"
BORDER = "#38302a"
TEXT = "#f8f5f1"
MUTED = "#a59b92"
MINT = "#ff8a24"       # Primary orange accent
MINT_DARK = "#3b2110"
BLUE = "#ffad61"
AMBER = "#ff8a24"
RED = "#ff5f45"
FONT = "Segoe UI"

def fmt_size(size):
    value = float(size)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if value < 1024 or unit == "TB":
            return f"{value:.1f} {unit}"
        value /= 1024
    return f"{value:.1f} TB"

def get_drives():
    found = []
    if os.name == "nt":
        for letter in string.ascii_uppercase:
            path = f"{letter}:\\"
            if os.path.exists(path):
                try:
                    total, used, free = shutil.disk_usage(path)
                    found.append({"path": path, "total": total, "used": used, "free": free})
                except OSError:
                    pass
    else:
        total, used, free = shutil.disk_usage("/")
        found.append({"path": "/", "total": total, "used": used, "free": free})
    return found

def safe_walk(root):
    for current, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in ("System Volume Information", "$Recycle.Bin", "Recovery")]
        yield current, files

class SpaceSweep(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"{APP_NAME} — Storage Intelligence")
        self.geometry("1240x800")
        self._set_app_icon()
        self.attributes("-alpha", 0.0)
        self.minsize(1000, 680)
        self.configure(bg=BG)
        self.drives = []
        self.large_results = []
        self.temp_results = []
        self.scan_busy = False
        self.current_page = "Overview"
        self._setup_style()
        self._build_shell()
        self.refresh_dashboard()
        self.after(15, self._fade_in)

    def _set_app_icon(self):
        try:
            base = Path(getattr(sys, "_MEIPASS", Path(__file__).parent))
            icon_path = base / "spacesweep.ico"
            if icon_path.exists():
                self.iconbitmap(str(icon_path))
        except (tk.TclError, OSError):
            pass

    def _fade_in(self, alpha=0.0):
        try:
            alpha = min(1.0, alpha + 0.08)
            self.attributes("-alpha", alpha)
            if alpha < 1.0:
                self.after(12, lambda: self._fade_in(alpha))
        except tk.TclError:
            pass

    def _animate_in(self, widgets, index=0):
        # Gentle staggered reveal; avoids abrupt page changes without blocking scans.
        if index >= len(widgets):
            return
        try:
            widget = widgets[index]
            widget.place_configure(y=widget.winfo_y() + 1) if widget.winfo_manager() == "place" else None
            self.after(24, lambda: self._animate_in(widgets, index + 1))
        except tk.TclError:
            pass

    def _setup_style(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Treeview",
            background=SURFACE, foreground=TEXT, fieldbackground=SURFACE,
            rowheight=34, borderwidth=0, font=(FONT, 10))
        style.configure("Treeview.Heading",
            background=SURFACE_2, foreground=MUTED,
            font=(FONT, 9, "bold"), relief="flat", padding=(10, 10))
        style.map("Treeview",
            background=[("selected", "#593016")],
            foreground=[("selected", TEXT)])
        style.configure("TProgressbar",
            troughcolor=SURFACE_3, background=MINT, bordercolor=SURFACE_3,
            lightcolor=MINT, darkcolor=MINT, thickness=9)
        style.configure("Orange.Horizontal.TProgressbar",
            troughcolor=SURFACE_3, background=MINT, bordercolor=SURFACE_3,
            lightcolor=MINT, darkcolor=MINT, thickness=9)
        style.configure("Vertical.TScrollbar",
            background=SURFACE_2, troughcolor=SURFACE, bordercolor=SURFACE,
            arrowcolor=MUTED)

    def _label(self, parent, text, size=10, color=TEXT, weight="normal", **kwargs):
        return tk.Label(parent, text=text, bg=kwargs.pop("bg", parent.cget("bg")),
                        fg=color, font=(FONT, size, weight), **kwargs)

    def _button(self, parent, text, command, primary=False, compact=False):
        bg = MINT if primary else SURFACE_2
        fg = "#1a0d04" if primary else TEXT
        button = tk.Button(parent, text=text, command=command, bg=bg, fg=fg,
                           activebackground=(MINT if primary else SURFACE_3),
                           activeforeground=fg, relief="flat", bd=0, cursor="hand2",
                           font=(FONT, 9, "bold" if primary else "normal"),
                           padx=14 if compact else 18, pady=8 if compact else 10)
        button.bind("<Enter>", lambda _e: button.configure(bg=(MINT if primary else SURFACE_3)))
        button.bind("<Leave>", lambda _e: button.configure(bg=bg))
        return button

    def _build_shell(self):
        self.sidebar = tk.Frame(self, bg=SIDEBAR, width=226)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        brand = tk.Frame(self.sidebar, bg=SIDEBAR)
        brand.pack(fill="x", padx=22, pady=(26, 32))
        logo = tk.Canvas(brand, width=38, height=38, bg=SIDEBAR, highlightthickness=0)
        logo.pack(side="left")
        logo.create_rounded_rectangle = None
        logo.create_rectangle(2, 2, 36, 36, fill="#27160c", outline="#5b3218", width=1)
        logo.create_arc(7, 7, 31, 31, start=28, extent=300, style="arc", outline=MINT, width=3)
        logo.create_line(19, 11, 19, 20, fill="#fff0df", width=2)
        logo.create_line(19, 20, 26, 24, fill=MINT, width=2)
        logo.create_oval(16, 16, 22, 22, fill=MINT, outline="")
        namebox = tk.Frame(brand, bg=SIDEBAR)
        namebox.pack(side="left", padx=10)
        self._label(namebox, "SpaceSweep", 15, TEXT, "bold").pack(anchor="w")
        self._label(namebox, "STORAGE INTELLIGENCE", 7, MUTED, "bold").pack(anchor="w", pady=(2, 0))

        self._label(self.sidebar, "WORKSPACE", 8, "#75665b", "bold").pack(anchor="w", padx=24, pady=(0, 10))
        self.nav_buttons = {}
        nav_items = [
            ("Overview", "◫"),
            ("Large files", "⌕"),
            ("Cleanup", "✳"),
            ("Duplicates", "▦"),
        ]
        for label, glyph in nav_items:
            btn = tk.Button(self.sidebar, text=f"   {glyph}     {label}", anchor="w",
                            command=lambda page=label: self.show_page(page),
                            bg=SIDEBAR, fg=MUTED, activebackground=SURFACE_2,
                            activeforeground=TEXT, relief="flat", bd=0,
                            font=(FONT, 10), padx=16, pady=12, cursor="hand2")
            btn.pack(fill="x", padx=12, pady=2)
            self.nav_buttons[label] = btn

        tk.Frame(self.sidebar, bg="#30251e", height=1).pack(fill="x", padx=20, pady=22)
        self._label(self.sidebar, "PREFERENCES", 8, "#75665b", "bold").pack(anchor="w", padx=24, pady=(0, 10))
        btn = tk.Button(self.sidebar, text="   ⚙     Settings", anchor="w",
                        command=lambda: self.show_page("Settings"), bg=SIDEBAR, fg=MUTED,
                        activebackground=SURFACE_2, activeforeground=TEXT,
                        relief="flat", bd=0, font=(FONT, 10), padx=16, pady=12, cursor="hand2")
        btn.pack(fill="x", padx=12, pady=2)
        self.nav_buttons["Settings"] = btn

        bottom = tk.Frame(self.sidebar, bg="#19130f", padx=14, pady=14)
        bottom.pack(side="bottom", fill="x", padx=12, pady=14)
        self._label(bottom, "◉  PROTECTION ACTIVE", 8, MINT, "bold", bg="#19130f").pack(anchor="w")
        self._label(bottom, "Nothing is removed without review.", 8, MUTED, bg="#19130f",
                    wraplength=175, justify="left").pack(anchor="w", pady=(7, 0))

        self.main = tk.Frame(self, bg=BG)
        self.main.pack(side="left", fill="both", expand=True)
        # Decorative orange glow bands create a gradient-wallpaper feel using native Tk.
        self.glow = tk.Canvas(self.main, height=5, bg=BG, highlightthickness=0, bd=0)
        self.glow.pack(side="top", fill="x")
        glow_colors = ["#ff8a24", "#d86a18", "#8a3d12", "#46200c", BG, BG, BG, BG]
        self.glow.bind("<Configure>", lambda _e: self._paint_glow(glow_colors))
        self.topbar = tk.Frame(self.main, bg=BG, height=76)
        self.topbar.pack(fill="x", padx=30, pady=(18, 4))
        self.topbar.pack_propagate(False)
        self.page_title = self._label(self.topbar, "Overview", 23, TEXT, "bold", bg=BG)
        self.page_title.pack(side="left", anchor="center")
        right = tk.Frame(self.topbar, bg=BG)
        right.pack(side="right", anchor="center")
        self.status_dot = tk.Canvas(right, width=9, height=9, bg=BG, highlightthickness=0)
        self.status_dot.pack(side="left", padx=(0, 7))
        self.status_dot.create_oval(1, 1, 8, 8, fill=MINT, outline="")
        self.status_label = self._label(right, "SYSTEM READY", 8, MUTED, "bold", bg=BG)
        self.status_label.pack(side="left", padx=(0, 16))
        self._button(right, "↻  Refresh", self.refresh_dashboard, compact=True).pack(side="left")
        self.content = tk.Frame(self.main, bg=BG)
        self.content.pack(fill="both", expand=True, padx=30, pady=(4, 24))
        self.show_page("Overview")

    def _paint_glow(self, colors):
        try:
            self.glow.delete("all")
            width = max(1, self.glow.winfo_width())
            segments = len(colors)
            for i, color in enumerate(colors):
                x1 = int(width * i / segments)
                x2 = int(width * (i + 1) / segments) + 1
                self.glow.create_rectangle(x1, 0, x2, 5, fill=color, outline=color)
        except tk.TclError:
            pass

    def _clear_content(self):
        for child in self.content.winfo_children():
            child.destroy()

    def show_page(self, page):
        self.current_page = page
        self.page_title.configure(text=page)
        for name, btn in self.nav_buttons.items():
            active = name == page
            btn.configure(bg=(MINT_DARK if active else SIDEBAR),
                          fg=(MINT if active else MUTED),
                          font=(FONT, 10, "bold" if active else "normal"))
        self._clear_content()
        if page == "Overview":
            self._build_overview()
        elif page == "Large files":
            self._build_large_page()
        elif page == "Cleanup":
            self._build_cleanup_page()
        elif page == "Duplicates":
            self._build_duplicates_page()
        else:
            self._build_settings_page()

    def _panel(self, parent, padx=18, pady=16):
        return tk.Frame(parent, bg=SURFACE, padx=padx, pady=pady,
                        highlightbackground=BORDER, highlightthickness=1)

    def _build_overview(self):
        intro = tk.Frame(self.content, bg=BG)
        intro.pack(fill="x", pady=(0, 18))
        textblock = tk.Frame(intro, bg=BG)
        textblock.pack(side="left", fill="x", expand=True)
        self._label(textblock, "A clearer view of your storage.", 12, MUTED).pack(anchor="w")
        self._label(textblock, "Your PC, minus the clutter.", 10, "#647995").pack(anchor="w", pady=(4, 0))
        self._button(intro, "＋  Scan a folder", lambda: self.show_page("Large files"), primary=True).pack(side="right", pady=3)

        stats = tk.Frame(self.content, bg=BG)
        stats.pack(fill="x", pady=(0, 16))
        total = sum(d["total"] for d in self.drives)
        free = sum(d["free"] for d in self.drives)
        used = total - free
        count = len(self.drives)
        self._stat_card(stats, "TOTAL CAPACITY", fmt_size(total), "Across detected drives", "▤", BLUE).pack(side="left", fill="both", expand=True, padx=(0, 10))
        self._stat_card(stats, "SPACE IN USE", fmt_size(used), f"{(used/total*100 if total else 0):.0f}% of total capacity", "◉", AMBER).pack(side="left", fill="both", expand=True, padx=5)
        self._stat_card(stats, "SPACE AVAILABLE", fmt_size(free), "Ready for new files", "↗", MINT).pack(side="left", fill="both", expand=True, padx=(10, 0))

        row = tk.Frame(self.content, bg=BG)
        row.pack(fill="both", expand=True)
        drive_panel = self._panel(row, 20, 18)
        drive_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))
        header = tk.Frame(drive_panel, bg=SURFACE)
        header.pack(fill="x", pady=(0, 16))
        self._label(header, "Storage overview", 13, TEXT, "bold", bg=SURFACE).pack(side="left")
        self._label(header, f"{count} drive{'s' if count != 1 else ''} detected", 9, MUTED, bg=SURFACE).pack(side="right")
        for drive in self.drives:
            self._drive_row(drive_panel, drive)

        quick = self._panel(row, 20, 18)
        quick.configure(width=280)
        quick.pack(side="left", fill="y", padx=(10, 0))
        self._label(quick, "Quick actions", 13, TEXT, "bold", bg=SURFACE).pack(anchor="w")
        self._label(quick, "A few tools to get you started.", 9, MUTED, bg=SURFACE).pack(anchor="w", pady=(5, 16))
        self._action_card(quick, "⌕", "Find large files", "See what's using your space", lambda: self.show_page("Large files"), BLUE)
        self._action_card(quick, "✳", "Review temp files", "Choose what you want removed", lambda: self.show_page("Cleanup"), MINT)
        self._action_card(quick, "▦", "Find duplicates", "Identify repeated files", lambda: self.show_page("Duplicates"), AMBER)
        foot = tk.Frame(self.content, bg=BG)
        foot.pack(fill="x", pady=(13, 0))
        self._label(foot, "SPACE SWEEP  /  LOCAL-FIRST UTILITIES", 8, "#76675b", "bold", bg=BG).pack(side="left")
        self._label(foot, f"VERSION {VERSION}", 8, "#76675b", "bold", bg=BG).pack(side="right")

    def _stat_card(self, parent, title, value, sub, glyph, color):
        frame = self._panel(parent, 17, 15)
        top = tk.Frame(frame, bg=SURFACE)
        top.pack(fill="x")
        self._label(top, title, 8, MUTED, "bold", bg=SURFACE).pack(side="left")
        self._label(top, glyph, 15, color, "bold", bg=SURFACE).pack(side="right")
        self._label(frame, value, 21, TEXT, "bold", bg=SURFACE).pack(anchor="w", pady=(10, 4))
        self._label(frame, sub, 9, MUTED, bg=SURFACE).pack(anchor="w")
        return frame

    def _drive_row(self, parent, drive):
        total, used, free = drive["total"], drive["used"], drive["free"]
        pct = used / total * 100 if total else 0
        block = tk.Frame(parent, bg=SURFACE)
        block.pack(fill="x", pady=8)
        line = tk.Frame(block, bg=SURFACE)
        line.pack(fill="x")
        self._label(line, "▣", 13, MINT, "bold", bg=SURFACE).pack(side="left", padx=(0, 9))
        self._label(line, drive["path"], 11, TEXT, "bold", bg=SURFACE).pack(side="left")
        self._label(line, f"{pct:.0f}% used", 9, MUTED, bg=SURFACE).pack(side="right")
        bar = ttk.Progressbar(block, maximum=100, value=pct)
        bar.pack(fill="x", pady=(10, 7))
        self._label(block, f"{fmt_size(used)} used  ·  {fmt_size(free)} free", 9, MUTED, bg=SURFACE).pack(anchor="w")

    def _action_card(self, parent, glyph, title, desc, command, color):
        card = tk.Frame(parent, bg=SURFACE_2, padx=12, pady=12,
                        highlightbackground=BORDER, highlightthickness=1, cursor="hand2")
        card.pack(fill="x", pady=5)
        self._label(card, glyph, 17, color, "bold", bg=SURFACE_2).pack(side="left", padx=(0, 11))
        texts = tk.Frame(card, bg=SURFACE_2)
        texts.pack(side="left", fill="x", expand=True)
        self._label(texts, title, 10, TEXT, "bold", bg=SURFACE_2).pack(anchor="w")
        self._label(texts, desc, 8, MUTED, bg=SURFACE_2, wraplength=180, justify="left").pack(anchor="w", pady=(3, 0))
        for widget in (card, *card.winfo_children(), *texts.winfo_children()):
            widget.bind("<Button-1>", lambda _e, cmd=command: cmd())

    def _build_large_page(self):
        self._label(self.content, "Find the files taking up the most room.", 11, MUTED).pack(anchor="w", pady=(0, 16))
        panel = self._panel(self.content, 18, 16)
        panel.pack(fill="x", pady=(0, 12))
        self._label(panel, "SCAN LOCATION", 8, MUTED, "bold", bg=SURFACE).pack(anchor="w", pady=(0, 8))
        controls = tk.Frame(panel, bg=SURFACE)
        controls.pack(fill="x")
        self.large_path = tk.StringVar(value=str(Path.home()))
        entry = tk.Entry(controls, textvariable=self.large_path, bg=SURFACE_2, fg=TEXT,
                         insertbackground=TEXT, relief="flat", font=(FONT, 10))
        entry.pack(side="left", fill="x", expand=True, ipady=10, padx=(0, 8))
        self._button(controls, "Browse", self.browse_large, compact=True).pack(side="left", padx=(0, 8))
        self.large_scan_btn = self._button(controls, "Scan folder  →", self.start_large_scan, primary=True, compact=True)
        self.large_scan_btn.pack(side="left")
        progress_row = tk.Frame(self.content, bg=BG)
        progress_row.pack(fill="x", pady=(0, 10))
        self.large_progress = ttk.Progressbar(progress_row, mode="determinate", maximum=100, style="Orange.Horizontal.TProgressbar")
        self.large_progress.pack(side="left", fill="x", expand=True)
        self.large_percent = self._label(progress_row, "0%", 9, MINT, "bold", bg=BG, width=5, anchor="e")
        self.large_percent.pack(side="right", padx=(12, 0))
        results_panel = self._panel(self.content, 12, 12)
        results_panel.pack(fill="both", expand=True)
        header = tk.Frame(results_panel, bg=SURFACE)
        header.pack(fill="x", padx=4, pady=(0, 10))
        self._label(header, "Largest files", 12, TEXT, "bold", bg=SURFACE).pack(side="left")
        self.large_count = tk.StringVar(value="Scan a folder to see results.")
        self._label(header, "", 9, MUTED, bg=SURFACE).pack(side="right")
        self.large_tree = ttk.Treeview(results_panel, columns=("size", "modified", "path"), show="headings")
        self.large_tree.heading("size", text="FILE SIZE")
        self.large_tree.heading("modified", text="LAST MODIFIED")
        self.large_tree.heading("path", text="LOCATION")
        self.large_tree.column("size", width=115, anchor="e")
        self.large_tree.column("modified", width=155)
        self.large_tree.column("path", width=650)
        self.large_tree.pack(fill="both", expand=True)
        self._label(results_panel, "", 8, MUTED, bg=SURFACE).pack(anchor="w")
        tk.Label(results_panel, textvariable=self.large_count, bg=SURFACE, fg=MUTED, font=(FONT, 9)).pack(anchor="w", pady=(10, 0))

    def browse_large(self):
        path = filedialog.askdirectory(title="Choose a folder to scan")
        if path:
            self.large_path.set(path)

    def start_large_scan(self):
        root = self.large_path.get().strip()
        if not os.path.isdir(root):
            messagebox.showerror("Invalid folder", "Choose an existing folder to scan.")
            return
        self.large_tree.delete(*self.large_tree.get_children())
        self.large_count.set("Scanning files…")
        self.status_label.configure(text="SCANNING FILES", fg=AMBER)
        self.large_progress.configure(value=0)
        self.large_percent.configure(text="0%")
        self.large_scan_btn.configure(state="disabled")
        threading.Thread(target=self._scan_large_worker, args=(root,), daemon=True).start()

    def _scan_large_worker(self, root):
        # Pass one counts candidates so the UI can show a real percentage during the scan.
        total_files = 0
        for current, names in safe_walk(root):
            total_files += len(names)
            self.after(0, lambda n=total_files: self._update_large_progress(0, n, "Preparing scan…"))
        results, count = [], 0
        for current, names in safe_walk(root):
            for name in names:
                try:
                    path = os.path.join(current, name)
                    stat = os.stat(path, follow_symlinks=False)
                    if os.path.isfile(path):
                        results.append((stat.st_size, stat.st_mtime, path))
                    count += 1
                except OSError:
                    count += 1
                if count % 20 == 0 or count == total_files:
                    pct = min(100, int(count * 100 / max(1, total_files)))
                    self.after(0, lambda p=pct, n=count, t=total_files: self._update_large_progress(p, n, "Scanning files…"))
        results.sort(key=lambda x: x[0], reverse=True)
        self.after(0, lambda: self._show_large_results(results[:1500], count))

    def _update_large_progress(self, pct, count, phase):
        if not self.winfo_exists():
            return
        self.large_progress.configure(value=pct)
        self.large_percent.configure(text=f"{pct}%")
        self.large_count.set(f"{phase} {count:,} files counted")

    def _show_large_results(self, results, count):
        self.large_progress.configure(value=100)
        self.large_percent.configure(text="100%")
        self.large_scan_btn.configure(state="normal")
        self.large_results = results
        for size, modified, path in results:
            date = datetime.fromtimestamp(modified).strftime("%d %b %Y, %H:%M")
            self.large_tree.insert("", "end", values=(fmt_size(size), date, path))
        self.large_count.set(f"{count:,} files scanned  ·  Showing the {len(results):,} largest")
        self.status_label.configure(text="SCAN COMPLETE", fg=MINT)

    def _build_cleanup_page(self):
        self._label(self.content, "Review temporary files before reclaiming space.", 11, MUTED).pack(anchor="w", pady=(0, 16))
        notice = tk.Frame(self.content, bg="#25170e", padx=16, pady=12,
                          highlightbackground="#6a3a19", highlightthickness=1)
        notice.pack(fill="x", pady=(0, 12))
        self._label(notice, "✓  REVIEW FIRST. DELETE ONLY WHAT YOU SELECT.", 9, MINT, "bold", bg="#25170e").pack(anchor="w")
        self._label(notice, "Cleanup is limited to your user temp folder. Files in use or inaccessible files will be skipped.", 9, "#d7b69b", bg="#25170e").pack(anchor="w", pady=(5, 0))
        controls = tk.Frame(self.content, bg=BG)
        controls.pack(fill="x", pady=(0, 12))
        self._button(controls, "Scan temp folder", self.start_temp_scan, primary=True).pack(side="left")
        self._button(controls, "Select all", self.select_all_temp, compact=True).pack(side="left", padx=8)
        self._button(controls, "Delete selected  →", self.delete_selected_temp, compact=True).pack(side="left")
        temp_progress_row = tk.Frame(self.content, bg=BG)
        temp_progress_row.pack(fill="x", pady=(0, 10))
        self.temp_progress = ttk.Progressbar(temp_progress_row, mode="determinate", maximum=100, style="Orange.Horizontal.TProgressbar")
        self.temp_progress.pack(side="left", fill="x", expand=True)
        self.temp_percent = self._label(temp_progress_row, "0%", 9, MINT, "bold", bg=BG, width=5, anchor="e")
        self.temp_percent.pack(side="right", padx=(12, 0))
        panel = self._panel(self.content, 12, 12)
        panel.pack(fill="both", expand=True)
        self.temp_tree = ttk.Treeview(panel, columns=("size", "path"), show="headings", selectmode="extended")
        self.temp_tree.heading("size", text="SIZE")
        self.temp_tree.heading("path", text="TEMPORARY FILE PATH")
        self.temp_tree.column("size", width=120, anchor="e")
        self.temp_tree.column("path", width=780)
        self.temp_tree.pack(fill="both", expand=True)
        self.temp_count = tk.StringVar(value="No scan yet.")
        tk.Label(panel, textvariable=self.temp_count, bg=SURFACE, fg=MUTED, font=(FONT, 9)).pack(anchor="w", pady=(10, 0))

    def start_temp_scan(self):
        root = tempfile.gettempdir()
        self.temp_tree.delete(*self.temp_tree.get_children())
        self.temp_count.set("Scanning temporary files…")
        self.status_label.configure(text="SCANNING TEMP FILES", fg=AMBER)
        self.temp_progress.configure(value=0)
        self.temp_percent.configure(text="0%")
        threading.Thread(target=self._scan_temp_worker, args=(root,), daemon=True).start()

    def _scan_temp_worker(self, root):
        total_files = 0
        for current, names in safe_walk(root):
            total_files += len(names)
        results, total = [], 0
        scanned = 0
        for current, names in safe_walk(root):
            for name in names:
                try:
                    path = os.path.join(current, name)
                    if os.path.isfile(path) and not os.path.islink(path):
                        size = os.path.getsize(path)
                        results.append((size, path))
                        total += size
                except OSError:
                    pass
                scanned += 1
                if scanned % 20 == 0 or scanned == total_files:
                    pct = min(100, int(scanned * 100 / max(1, total_files)))
                    self.after(0, lambda p=pct, n=scanned, t=total_files: self._update_temp_progress(p, n, t))
        results.sort(reverse=True)
        self.after(0, lambda: self._show_temp_results(results, total))

    def _update_temp_progress(self, pct, scanned, total):
        if not self.winfo_exists():
            return
        self.temp_progress.configure(value=pct)
        self.temp_percent.configure(text=f"{pct}%")
        self.temp_count.set(f"Scanning temporary files… {scanned:,} / {total:,}")

    def _show_temp_results(self, results, total):
        self.temp_progress.configure(value=100)
        self.temp_percent.configure(text="100%")
        self.temp_results = results
        for size, path in results:
            self.temp_tree.insert("", "end", values=(fmt_size(size), path))
        self.temp_count.set(f"{len(results):,} files found  ·  {fmt_size(total)} potentially reclaimable; some may be in use")
        self.status_label.configure(text="SCAN COMPLETE", fg=MINT)

    def select_all_temp(self):
        if self.temp_tree.get_children():
            self.temp_tree.selection_set(self.temp_tree.get_children())

    def delete_selected_temp(self):
        selected = self.temp_tree.selection()
        if not selected:
            messagebox.showinfo("Nothing selected", "Select the files you want to remove first.")
            return
        paths = [self.temp_tree.item(item, "values")[1] for item in selected]
        if not messagebox.askyesno("Confirm permanent deletion",
                f"Attempt to permanently delete {len(paths)} selected files?\n\n"
                "This does not use the Recycle Bin. Review the paths before continuing."):
            return
        deleted = reclaimed = skipped = 0
        temp_root = os.path.abspath(tempfile.gettempdir())
        for path in paths:
            try:
                absolute = os.path.abspath(path)
                if os.path.commonpath([temp_root, absolute]) != temp_root:
                    skipped += 1
                    continue
                if os.path.islink(absolute) or not os.path.isfile(absolute):
                    skipped += 1
                    continue
                size = os.path.getsize(absolute)
                os.remove(absolute)
                deleted += 1
                reclaimed += size
            except (OSError, ValueError):
                skipped += 1
        messagebox.showinfo("Cleanup complete", f"Deleted: {deleted}\nSkipped: {skipped}\nSpace reclaimed: {fmt_size(reclaimed)}")
        self.start_temp_scan()

    def _build_duplicates_page(self):
        panel = self._panel(self.content, 24, 22)
        panel.pack(fill="both", expand=True)
        self._label(panel, "Duplicate detection", 19, TEXT, "bold", bg=SURFACE).pack(anchor="w")
        self._label(panel, "Find repeated files without risking automatic deletion.", 10, MUTED, bg=SURFACE).pack(anchor="w", pady=(7, 18))
        pill = tk.Frame(panel, bg="#2c1b0d", padx=12, pady=10)
        pill.pack(fill="x", pady=(0, 18))
        self._label(pill, "COMING IN THE NEXT BUILD", 9, AMBER, "bold", bg="#2c1b0d").pack(anchor="w")
        self._label(panel, "Planned workflow", 11, TEXT, "bold", bg=SURFACE).pack(anchor="w", pady=(0, 10))
        for number, title, desc in [
            ("01", "Choose a folder", "Limit the scan to a location you control."),
            ("02", "Compare file fingerprints", "Group files with matching sizes and cryptographic hashes."),
            ("03", "Review before acting", "Show every duplicate group and let you decide what stays."),
        ]:
            line = tk.Frame(panel, bg=SURFACE)
            line.pack(fill="x", pady=8)
            self._label(line, number, 10, MINT, "bold", bg=SURFACE).pack(side="left", padx=(0, 15))
            block = tk.Frame(line, bg=SURFACE)
            block.pack(side="left", fill="x", expand=True)
            self._label(block, title, 10, TEXT, "bold", bg=SURFACE).pack(anchor="w")
            self._label(block, desc, 9, MUTED, bg=SURFACE).pack(anchor="w", pady=(3, 0))

    def _build_settings_page(self):
        panel = self._panel(self.content, 24, 22)
        panel.pack(fill="x", anchor="n")
        self._label(panel, "Application settings", 17, TEXT, "bold", bg=SURFACE).pack(anchor="w")
        self._label(panel, "SpaceSweep keeps its scanning local to your PC.", 10, MUTED, bg=SURFACE).pack(anchor="w", pady=(5, 18))
        for title, desc in [
            ("Local-first by design", "No accounts, analytics, or cloud uploads are used by this starter build."),
            ("Deletion safety", "Cleanup is manual and requires confirmation. There is no automatic scheduled deletion."),
            ("Scan boundaries", "Large-file scans cover only the folder you choose. Temporary cleanup uses your user temp folder."),
            ("Build information", f"SpaceSweep {VERSION}  ·  Python desktop application  ·  MIT license"),
        ]:
            section = tk.Frame(panel, bg=SURFACE_2, padx=15, pady=13)
            section.pack(fill="x", pady=5)
            self._label(section, title, 10, TEXT, "bold", bg=SURFACE_2).pack(anchor="w")
            self._label(section, desc, 9, MUTED, bg=SURFACE_2, wraplength=820, justify="left").pack(anchor="w", pady=(4, 0))

    def refresh_dashboard(self):
        self.drives = get_drives()
        if hasattr(self, "content"):
            self.show_page(self.current_page)

if __name__ == "__main__":
    app = SpaceSweep()
    app.mainloop()
