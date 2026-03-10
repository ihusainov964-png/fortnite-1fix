"""
Fortnite AWS Fix v6.0 — Desktop Application
Python + CustomTkinter
"""
import customtkinter as ctk
import subprocess, threading, random, time, os, sys, socket, struct
from datetime import datetime

# ── Theme ──────────────────────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

NEON   = "#00f0ff"
GOLD   = "#ffd700"
GREEN  = "#00ff88"
RED    = "#ff4466"
PURPLE = "#b060ff"
BG     = "#05080f"
PANEL  = "#090f1d"
PANEL2 = "#0c1628"
BORDER = "#1a3050"
TEXT   = "#b8cfea"
DIM    = "#3a5a7a"

JOKES = [
    "😂 Ваня снова в топ-1 по смертям",
    "👀 Ваня: '0 пинг!'  Мы: 999ms",
    "💀 Ваня купил скин и всё равно проиграл",
    "🤖 Ваня строил 1x1 — бот его снёс",
    "😭 Ваня поставил графику Эпик... FPS 8",
    "⏰ Ваня включил расписание и опоздал на катку",
    "🎯 У Вани 0 побед, но зато красивый скин",
]

FIXES = [
    ("⚡", "Быстрый фикс",      "DNS + Winsock + TCP/IP",           "#00c8ff",
     ["ipconfig /flushdns", "netsh winsock reset", "netsh int ip reset", "netsh int ipv4 reset", "ipconfig /registerdns"]),
    ("🔄", "Полный сброс",      "+ SFC + DISM (15 мин)",            "#ff9f40",
     ["ipconfig /flushdns", "netsh winsock reset", "sfc /scannow", "DISM /Online /Cleanup-Image /RestoreHealth"]),
    ("🌐", "Смена DNS",         "Google 8.8.8.8 + CF 1.1.1.1",     "#a29bfe",
     ['netsh interface ip set dns "Ethernet" static 8.8.8.8',
      'netsh interface ip set dns "Wi-Fi" static 8.8.8.8',
      'netsh interface ip add dns "Ethernet" 1.1.1.1 index=2',
      "ipconfig /flushdns"]),
    ("🗑", "Очистка кэша",      "Fortnite + Epic Launcher",         "#55efc4",
     [r'del /f /s /q "%LOCALAPPDATA%\FortniteGame\Saved\Cache\*"',
      r'del /f /s /q "%LOCALAPPDATA%\EpicGamesLauncher\Saved\webcache\*"']),
    ("📶", "QoS приоритет",     "DSCP=46 для Fortnite",             "#fd79a8",
     ['netsh qos delete policy "FortniteClient"',
      'netsh qos add policy "FortniteClient" app="FortniteClient-Win64-Shipping.exe" dscp=46 throttle-rate=-1']),
    ("📝", "Очистка hosts",     "Удалить блокировки Epic/AWS",      "#ffeaa7",
     [r'copy /Y %WINDIR%\System32\drivers\etc\hosts %WINDIR%\System32\drivers\etc\hosts.bak']),
    ("🔕", "Откл. IPv6",        "Помогает в РФ/СНГ",                "#74b9ff",
     ['reg add "HKLM\\SYSTEM\\CurrentControlSet\\Services\\Tcpip6\\Parameters" /v "DisabledComponents" /t REG_DWORD /d 255 /f']),
    ("🏎", "Откл. Nagle",       "Снижает пинг на 5-30ms",           "#00b894",
     ['reg add "HKLM\\SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters" /v "TcpAckFrequency" /t REG_DWORD /d 1 /f',
      'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters" /v "TCPNoDelay" /t REG_DWORD /d 1 /f']),
    ("⏸", "Пауза Win Update",  "Остановить обновления",            "#e17055",
     ["net stop wuauserv", "net stop bits", "net stop dosvc"]),
]

SCHED_FIXES = [
    ("dns",   "🌐", "Смена DNS"),
    ("quick", "⚡", "Быстрый фикс"),
    ("cache", "🗑", "Очистка кэша"),
    ("wu",    "⏸", "Пауза Windows Update"),
]

PRESETS = {
    "fps": {
        "name": "⚡ МАКСИМУМ FPS",
        "color": NEON,
        "desc": "+40-60% FPS, всё на минимум",
        "ini": "[ScalabilityGroups]\nsg.ResolutionQuality=75\nsg.ViewDistanceQuality=1\nsg.ShadowQuality=0\nsg.PostProcessQuality=0\nsg.TextureQuality=0\nsg.EffectsQuality=0\nsg.FoliageQuality=0\n\n[/Script/FortniteGame.FortGameUserSettings]\nResolutionSizeX=1280\nResolutionSizeY=720\nbUseVSync=False\nbFrameRateLimit=0\nbShowFPS=True\n",
        "settings": [("Разрешение","1280×720"),("Текстуры","0 Низкие"),("Тени","Выкл"),("Сглаживание","Выкл"),("Ожид. FPS","120-240+")],
    },
    "balance": {
        "name": "⚖️ БАЛАНС",
        "color": PURPLE,
        "desc": "Лучший выбор — FPS и картинка",
        "ini": "[ScalabilityGroups]\nsg.ResolutionQuality=100\nsg.ViewDistanceQuality=2\nsg.ShadowQuality=2\nsg.PostProcessQuality=2\nsg.TextureQuality=2\nsg.EffectsQuality=2\nsg.FoliageQuality=2\n\n[/Script/FortniteGame.FortGameUserSettings]\nResolutionSizeX=1920\nResolutionSizeY=1080\nbUseVSync=False\nbFrameRateLimit=144\n",
        "settings": [("Разрешение","1920×1080"),("Текстуры","2 Средние"),("Тени","Средние"),("Сглаживание","TAA"),("Ожид. FPS","60-120")],
    },
    "quality": {
        "name": "✨ КАЧЕСТВО",
        "color": GOLD,
        "desc": "Красивая картинка, нужен мощный ПК",
        "ini": "[ScalabilityGroups]\nsg.ResolutionQuality=100\nsg.ViewDistanceQuality=4\nsg.ShadowQuality=4\nsg.PostProcessQuality=4\nsg.TextureQuality=4\nsg.EffectsQuality=4\nsg.FoliageQuality=4\n\n[/Script/FortniteGame.FortGameUserSettings]\nResolutionSizeX=2560\nResolutionSizeY=1440\nbUseVSync=False\nbFrameRateLimit=60\n",
        "settings": [("Разрешение","2560×1440"),("Текстуры","4 Эпик"),("Тени","Высокие"),("Сглаживание","TSR"),("Ожид. FPS","30-60")],
    },
}


def run_cmd(cmd):
    """Run a shell command, return (success, output)."""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True,
            timeout=60, encoding="cp1251", errors="replace"
        )
        return result.returncode == 0, result.stdout + result.stderr
    except Exception as e:
        return False, str(e)


def ping_host(host, timeout=2):
    """Ping a host, return ms or -1 on fail."""
    try:
        t0 = time.time()
        s = socket.create_connection((host, 80), timeout=timeout)
        s.close()
        return int((time.time() - t0) * 1000)
    except:
        return -1


# ══════════════════════════════════════════════════════════════
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Fortnite AWS Fix v6.0")
        self.geometry("1000x660")
        self.minsize(900, 600)
        self.configure(fg_color=BG)

        # State
        self.monitor_running = False
        self.ping_history = []
        self.sched_active = False
        self.sched_thread = None
        self.active_preset = None
        self.sched_checks = {k: ctk.BooleanVar(value=d) for k, _, _ in SCHED_FIXES
                             for k, d in [(k, k in ("dns","quick","wu"))]}

        self._build_ui()

    # ─────────────────────────────────────────────────────────
    def _build_ui(self):
        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=200, fg_color=PANEL, corner_radius=0,
                                    border_width=1, border_color=BORDER)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Logo
        logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo_frame.pack(pady=(20,10), padx=16)
        ctk.CTkLabel(logo_frame, text="⚡", font=ctk.CTkFont(size=28)).pack(side="left")
        ctk.CTkLabel(logo_frame, text=" FORTNITE FIX", font=ctk.CTkFont(family="Arial", size=13, weight="bold"),
                     text_color=NEON).pack(side="left")

        ctk.CTkLabel(self.sidebar, text="v6.0", font=ctk.CTkFont(size=11), text_color=DIM).pack()

        ctk.CTkFrame(self.sidebar, height=1, fg_color=BORDER).pack(fill="x", padx=12, pady=12)

        # Nav buttons
        self.nav_btns = {}
        pages = [
            ("dash",     "⚡  Главная"),
            ("monitor",  "📊  Пинг-монитор"),
            ("sched",    "⏰  Расписание"),
            ("graphics", "🎮  Графика"),
            ("fixes",    "🔧  Фиксы"),
            ("check",    "📡  Проверка AWS"),
        ]
        for pid, label in pages:
            btn = ctk.CTkButton(
                self.sidebar, text=label, anchor="w",
                font=ctk.CTkFont(size=13), height=38,
                fg_color="transparent", hover_color="#0d1e38",
                text_color=DIM, corner_radius=8,
                command=lambda p=pid: self.show_page(p)
            )
            btn.pack(fill="x", padx=10, pady=2)
            self.nav_btns[pid] = btn

        # NEW badges
        for pid in ("monitor", "sched", "graphics"):
            self.nav_btns[pid].configure(text=self.nav_btns[pid].cget("text") + "  🆕")

        # Joke label at bottom
        ctk.CTkFrame(self.sidebar, height=1, fg_color=BORDER).pack(fill="x", padx=12, pady=12, side="bottom")
        self.joke_lbl = ctk.CTkLabel(
            self.sidebar, text=random.choice(JOKES),
            font=ctk.CTkFont(size=10, slant="italic"),
            text_color=GOLD, wraplength=175, justify="center"
        )
        self.joke_lbl.pack(side="bottom", padx=10, pady=8)

        # Main content area
        self.content = ctk.CTkFrame(self, fg_color=BG, corner_radius=0)
        self.content.pack(side="left", fill="both", expand=True)

        # Build all pages
        self.pages = {}
        self._build_dashboard()
        self._build_monitor()
        self._build_scheduler()
        self._build_graphics()
        self._build_fixes()
        self._build_check()

        self.show_page("dash")

    # ─────────────────────────────────────────────────────────
    def show_page(self, pid):
        for p in self.pages.values():
            p.pack_forget()
        self.pages[pid].pack(fill="both", expand=True)
        for k, btn in self.nav_btns.items():
            if k == pid:
                btn.configure(fg_color="#0d2040", text_color=NEON)
            else:
                btn.configure(fg_color="transparent", text_color=DIM)

    # ─────────────────────────────────────────────────────────
    # PAGE HELPERS
    def _page(self, pid):
        f = ctk.CTkScrollableFrame(self.content, fg_color=BG, corner_radius=0,
                                   scrollbar_button_color=BORDER)
        self.pages[pid] = f
        return f

    def _section(self, parent, title, pady=(0,12)):
        ctk.CTkLabel(parent, text=title, font=ctk.CTkFont(size=18, weight="bold"),
                     text_color="#ffffff").pack(anchor="w", pady=pady)

    def _card(self, parent, **kw):
        kw.setdefault("fg_color", PANEL2)
        kw.setdefault("corner_radius", 12)
        kw.setdefault("border_width", 1)
        kw.setdefault("border_color", BORDER)
        f = ctk.CTkFrame(parent, **kw)
        f.pack(fill="x", pady=6)
        return f

    def _log_box(self, parent, height=160):
        tb = ctk.CTkTextbox(parent, height=height, fg_color="#020810",
                            border_width=1, border_color=BORDER,
                            font=ctk.CTkFont(family="Courier New", size=12),
                            text_color="#68ffaa", corner_radius=8)
        tb.pack(fill="x", pady=(6,0))
        tb.configure(state="disabled")
        return tb

    def _log_append(self, tb, text, color=None):
        tb.configure(state="normal")
        tb.insert("end", text + "\n")
        tb.configure(state="disabled")
        tb.see("end")

    def _btn(self, parent, text, cmd, color=None, width=None, **kw):
        b = ctk.CTkButton(
            parent, text=text, command=cmd,
            fg_color=color or "#0060df",
            hover_color="#0080ff",
            font=ctk.CTkFont(size=13, weight="bold"),
            corner_radius=8,
            **({"width": width} if width else {}),
            **kw
        )
        return b

    # ─────────────────────────────────────────────────────────
    # DASHBOARD
    def _build_dashboard(self):
        p = self._page("dash")
        pad = ctk.CTkFrame(p, fg_color="transparent")
        pad.pack(fill="both", expand=True, padx=24, pady=20)

        # Hero
        hero = ctk.CTkFrame(pad, fg_color=PANEL, corner_radius=16,
                            border_width=1, border_color=BORDER)
        hero.pack(fill="x", pady=(0,16))
        inner = ctk.CTkFrame(hero, fg_color="transparent")
        inner.pack(fill="x", padx=26, pady=20)
        ctk.CTkLabel(inner, text="FORTNITE AWS FIX",
                     font=ctk.CTkFont(family="Arial", size=28, weight="bold"),
                     text_color="#ffffff").pack(anchor="w")
        ctk.CTkLabel(inner, text="Инструмент против лагов и блокировок • Россия / СНГ",
                     font=ctk.CTkFont(size=13), text_color=DIM).pack(anchor="w", pady=(2,12))
        self.joke_hero = ctk.CTkLabel(inner,
                     text=random.choice(JOKES),
                     font=ctk.CTkFont(size=12, slant="italic"),
                     text_color=GOLD)
        self.joke_hero.pack(anchor="w", pady=(0,14))
        self._btn(inner, "⚡  БЫСТРЫЙ ФИКС", self._quick_fix, width=220,
                  font=ctk.CTkFont(size=15, weight="bold")).pack(anchor="w")

        self.dash_log = self._log_box(inner, height=120)

        # Nav cards grid
        grid = ctk.CTkFrame(pad, fg_color="transparent")
        grid.pack(fill="x", pady=(8,0))
        cards = [
            ("📊", "Пинг-монитор",  "Живой график задержки",    "monitor"),
            ("⏰", "Расписание",     "Автофикс перед игрой",     "sched"),
            ("🎮", "Графика",        "Пресеты FPS / Баланс",     "graphics"),
            ("🔧", "Фиксы сети",    "DNS, QoS, Nagle, IPv6…",   "fixes"),
            ("📡", "Проверка AWS",  "Пинг серверов",             "check"),
            ("🔄", "Обновить шутку","Новая шутка про Ваню",      None),
        ]
        cols = 3
        for i, (ico, name, desc, pid) in enumerate(cards):
            col = i % cols
            row = i // cols
            c = ctk.CTkFrame(grid, fg_color=PANEL2, corner_radius=12,
                             border_width=1, border_color=BORDER)
            c.grid(row=row, column=col, padx=6, pady=6, sticky="ew")
            grid.columnconfigure(col, weight=1)
            inner2 = ctk.CTkFrame(c, fg_color="transparent")
            inner2.pack(padx=14, pady=12)
            ctk.CTkLabel(inner2, text=ico, font=ctk.CTkFont(size=22)).pack(anchor="w")
            ctk.CTkLabel(inner2, text=name, font=ctk.CTkFont(size=13, weight="bold"),
                         text_color="#fff").pack(anchor="w")
            ctk.CTkLabel(inner2, text=desc, font=ctk.CTkFont(size=11),
                         text_color=DIM).pack(anchor="w")
            if pid:
                c.bind("<Button-1>", lambda e, x=pid: self.show_page(x))
                for w in c.winfo_children() + inner2.winfo_children():
                    w.bind("<Button-1>", lambda e, x=pid: self.show_page(x))
            else:
                c.bind("<Button-1>", lambda e: self._refresh_joke())
                for w in c.winfo_children() + inner2.winfo_children():
                    w.bind("<Button-1>", lambda e: self._refresh_joke())

    def _refresh_joke(self):
        j = random.choice(JOKES)
        self.joke_lbl.configure(text=j)
        self.joke_hero.configure(text=j)

    def _quick_fix(self):
        cmds = ["ipconfig /flushdns","netsh winsock reset","netsh int ip reset",
                "netsh int ipv4 reset","ipconfig /registerdns"]
        self.dash_log.configure(state="normal")
        self.dash_log.delete("1.0","end")
        self.dash_log.configure(state="disabled")
        def run():
            for c in cmds:
                self._log_append(self.dash_log, f"► {c}")
                ok, out = run_cmd(c)
                self._log_append(self.dash_log, f"  {'✓' if ok else '✗'} {'OK' if ok else 'Ошибка (нужен администратор)'}")
                time.sleep(0.15)
            self._log_append(self.dash_log, "\n✅ Быстрый фикс завершён!")
        threading.Thread(target=run, daemon=True).start()

    # ─────────────────────────────────────────────────────────
    # PING MONITOR
    def _build_monitor(self):
        p = self._page("monitor")
        pad = ctk.CTkFrame(p, fg_color="transparent")
        pad.pack(fill="both", expand=True, padx=24, pady=20)

        self._section(pad, "📊 Пинг-монитор")
        ctk.CTkLabel(pad, text="Мониторинг задержки до серверов в реальном времени",
                     text_color=DIM, font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(0,12))

        # Stats row
        stats_row = ctk.CTkFrame(pad, fg_color="transparent")
        stats_row.pack(fill="x", pady=(0,12))
        self.stat_cur = self._stat_box(stats_row, "—", "Текущий ms", GREEN)
        self.stat_avg = self._stat_box(stats_row, "—", "Средний ms", GOLD)
        self.stat_max = self._stat_box(stats_row, "—", "Максимум ms", RED)
        for i in range(3): stats_row.columnconfigure(i, weight=1)

        # Controls
        ctrl = ctk.CTkFrame(pad, fg_color="transparent")
        ctrl.pack(fill="x", pady=(0,12))
        self.mon_btn = self._btn(ctrl, "▶  Запустить мониторинг", self._toggle_monitor, width=220)
        self.mon_btn.pack(side="left")
        self.mon_status = ctk.CTkLabel(ctrl, text="● Остановлен",
                                       text_color=DIM, font=ctk.CTkFont(size=12))
        self.mon_status.pack(side="left", padx=14)
        ctk.CTkLabel(ctrl, text="Интервал:", text_color=DIM, font=ctk.CTkFont(size=12)).pack(side="left")
        self.mon_interval = ctk.CTkComboBox(ctrl, values=["2 сек","5 сек","10 сек"],
                                            width=100, fg_color=PANEL2, border_color=BORDER)
        self.mon_interval.pack(side="left", padx=8)
        self.mon_interval.set("2 сек")

        # Server rows
        self.srv_labels = {}
        servers = ["AWS EU Frankfurt","AWS EU Stockholm","Fortnite.com","Epic Games API"]
        srv_hosts = ["ec2.eu-central-1.amazonaws.com","ec2.eu-north-1.amazonaws.com",
                     "fortnite.com","api.epicgames.com"]
        self.srv_hosts = srv_hosts
        for name, host in zip(servers, srv_hosts):
            row = ctk.CTkFrame(pad, fg_color=PANEL2, corner_radius=8,
                               border_width=1, border_color=BORDER)
            row.pack(fill="x", pady=3)
            ctk.CTkLabel(row, text="●", font=ctk.CTkFont(size=14),
                         text_color=DIM).pack(side="left", padx=(12,8), pady=8)
            ctk.CTkLabel(row, text=name, font=ctk.CTkFont(size=13),
                         text_color=TEXT).pack(side="left")
            lbl = ctk.CTkLabel(row, text="—  ms", font=ctk.CTkFont(size=13, weight="bold"),
                               text_color=DIM)
            lbl.pack(side="right", padx=16)
            self.srv_labels[host] = lbl

        # Chart placeholder
        chart_card = self._card(pad)
        ctk.CTkLabel(chart_card, text="📈 График пинга (последние 30 замеров)",
                     font=ctk.CTkFont(size=12), text_color=DIM).pack(anchor="w", padx=14, pady=(10,4))
        self.chart_canvas = ctk.CTkCanvas(chart_card, height=120, bg="#020810",
                                          highlightthickness=0)
        self.chart_canvas.pack(fill="x", padx=12, pady=(0,10))

    def _stat_box(self, parent, val, label, color):
        f = ctk.CTkFrame(parent, fg_color=PANEL2, corner_radius=10,
                         border_width=1, border_color=BORDER)
        f.grid(row=0, column=len(self.ping_history), padx=5, sticky="ew")
        # Use a dict trick to get column
        col = sum(1 for w in parent.winfo_children()) - 1
        f.grid(row=0, column=col, padx=5, sticky="ew")
        v = ctk.CTkLabel(f, text=val, font=ctk.CTkFont(size=26, weight="bold"), text_color=color)
        v.pack(pady=(12,2))
        ctk.CTkLabel(f, text=label, font=ctk.CTkFont(size=10), text_color=DIM).pack(pady=(0,10))
        return v

    def _toggle_monitor(self):
        if self.monitor_running:
            self.monitor_running = False
            self.mon_btn.configure(text="▶  Запустить мониторинг", fg_color="#0060df")
            self.mon_status.configure(text="● Остановлен", text_color=DIM)
        else:
            self.monitor_running = True
            self.mon_btn.configure(text="⏹  Остановить", fg_color="#8b0000")
            self.mon_status.configure(text="● Активен", text_color=GREEN)
            threading.Thread(target=self._monitor_loop, daemon=True).start()

    def _monitor_loop(self):
        while self.monitor_running:
            interval_map = {"2 сек": 2, "5 сек": 5, "10 сек": 10}
            interval = interval_map.get(self.mon_interval.get(), 2)
            results = []
            for host in self.srv_hosts:
                ms = ping_host(host)
                results.append(ms)
                lbl = self.srv_labels[host]
                if ms < 0:
                    lbl.configure(text="timeout", text_color=RED)
                else:
                    col = GREEN if ms < 80 else GOLD if ms < 150 else RED
                    lbl.configure(text=f"{ms} ms", text_color=col)
            valid = [r for r in results if r >= 0]
            if valid:
                avg = sum(valid)//len(valid)
                self.ping_history.append(avg)
                if len(self.ping_history) > 30: self.ping_history.pop(0)
                self.stat_cur.configure(text=str(avg))
                self.stat_avg.configure(text=str(sum(self.ping_history)//len(self.ping_history)))
                self.stat_max.configure(text=str(max(self.ping_history)))
                self._draw_chart()
            time.sleep(interval)

    def _draw_chart(self):
        c = self.chart_canvas
        c.delete("all")
        if len(self.ping_history) < 2: return
        W = c.winfo_width() or 600
        H = 120
        maxV = max(max(self.ping_history), 200)
        pts = []
        for i, v in enumerate(self.ping_history):
            x = int(20 + (i / (len(self.ping_history)-1)) * (W-40))
            y = int(H - 10 - (v/maxV)*(H-20))
            pts.append((x,y))
        # area fill
        poly = [(20, H-10)] + pts + [(pts[-1][0], H-10)]
        flat = [coord for pt in poly for coord in pt]
        c.create_polygon(flat, fill="#003030", outline="")
        # line
        flat_line = [coord for pt in pts for coord in pt]
        last = self.ping_history[-1]
        col = "#00ff88" if last < 80 else "#ffd700" if last < 150 else "#ff4466"
        c.create_line(flat_line, fill=col, width=2, smooth=True)
        # 100ms reference line
        ref_y = int(H - 10 - (100/maxV)*(H-20))
        c.create_line(20, ref_y, W-20, ref_y, fill="#333333", dash=(4,4))
        c.create_text(W-25, ref_y-6, text="100ms", fill="#444444", font=("Courier",8))

    # ─────────────────────────────────────────────────────────
    # SCHEDULER
    def _build_scheduler(self):
        p = self._page("sched")
        pad = ctk.CTkFrame(p, fg_color="transparent")
        pad.pack(fill="both", expand=True, padx=24, pady=20)

        self._section(pad, "⏰ Расписание фикса")
        ctk.CTkLabel(pad, text="Автоматически запускает фиксы за несколько минут до игры",
                     text_color=DIM, font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(0,14))

        two_col = ctk.CTkFrame(pad, fg_color="transparent")
        two_col.pack(fill="x")
        two_col.columnconfigure(0, weight=1)
        two_col.columnconfigure(1, weight=1)

        # Left: time picker
        left = ctk.CTkFrame(two_col, fg_color=PANEL, corner_radius=12,
                            border_width=1, border_color=BORDER)
        left.grid(row=0, column=0, padx=(0,8), sticky="nsew")
        lpad = ctk.CTkFrame(left, fg_color="transparent")
        lpad.pack(fill="both", padx=16, pady=16)
        ctk.CTkLabel(lpad, text="🕐 Время начала игры",
                     font=ctk.CTkFont(size=14, weight="bold"), text_color="#fff").pack(anchor="w", pady=(0,8))
        ctk.CTkLabel(lpad, text="Во сколько обычно начинаешь играть?",
                     text_color=DIM, font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(0,8))
        time_row = ctk.CTkFrame(lpad, fg_color="transparent")
        time_row.pack(anchor="w", pady=(0,10))
        self.sched_hour = ctk.CTkEntry(time_row, width=70, font=ctk.CTkFont(size=24, weight="bold"),
                                       fg_color=PANEL2, border_color=NEON, justify="center")
        self.sched_hour.insert(0, "20")
        self.sched_hour.pack(side="left")
        ctk.CTkLabel(time_row, text=" : ", font=ctk.CTkFont(size=24, weight="bold"),
                     text_color=NEON).pack(side="left")
        self.sched_min = ctk.CTkEntry(time_row, width=70, font=ctk.CTkFont(size=24, weight="bold"),
                                      fg_color=PANEL2, border_color=NEON, justify="center")
        self.sched_min.insert(0, "00")
        self.sched_min.pack(side="left")

        before_row = ctk.CTkFrame(lpad, fg_color="transparent")
        before_row.pack(anchor="w", pady=(0,14))
        ctk.CTkLabel(before_row, text="Запустить за:", text_color=DIM,
                     font=ctk.CTkFont(size=12)).pack(side="left")
        self.sched_before = ctk.CTkComboBox(before_row, values=["2 мин","5 мин","10 мин"],
                                            width=90, fg_color=PANEL2, border_color=BORDER)
        self.sched_before.set("2 мин")
        self.sched_before.pack(side="left", padx=8)

        btn_row = ctk.CTkFrame(lpad, fg_color="transparent")
        btn_row.pack(anchor="w")
        self._btn(btn_row, "⏰  Включить", self._start_schedule, width=140).pack(side="left")
        self._btn(btn_row, "✕  Выключить", self._stop_schedule,
                  color="#5c1010", width=120,
                  hover_color="#8b1515").pack(side="left", padx=8)

        # Right: checklist
        right = ctk.CTkFrame(two_col, fg_color=PANEL, corner_radius=12,
                             border_width=1, border_color=BORDER)
        right.grid(row=0, column=1, padx=(8,0), sticky="nsew")
        rpad = ctk.CTkFrame(right, fg_color="transparent")
        rpad.pack(fill="both", padx=16, pady=16)
        ctk.CTkLabel(rpad, text="⚡ Что запускать",
                     font=ctk.CTkFont(size=14, weight="bold"), text_color="#fff").pack(anchor="w", pady=(0,10))
        self.sched_vars = {}
        defaults = {"dns": True, "quick": True, "cache": False, "wu": True}
        for kid, ico, label in SCHED_FIXES:
            var = ctk.BooleanVar(value=defaults.get(kid, False))
            self.sched_vars[kid] = var
            row = ctk.CTkFrame(rpad, fg_color=PANEL2, corner_radius=8,
                               border_width=1, border_color=BORDER)
            row.pack(fill="x", pady=3)
            ctk.CTkCheckBox(row, text=f"{ico}  {label}", variable=var,
                            font=ctk.CTkFont(size=13), text_color=TEXT,
                            checkmark_color=NEON, fg_color=PANEL2,
                            hover_color=PANEL).pack(padx=12, pady=8, anchor="w")

        # Status
        self.sched_status_frame = ctk.CTkFrame(pad, fg_color=PANEL2, corner_radius=10,
                                               border_width=1, border_color=BORDER)
        self.sched_status_frame.pack(fill="x", pady=(14,0))
        self.sched_status_lbl = ctk.CTkLabel(
            self.sched_status_frame,
            text="⏸  Расписание не активно — настрой время и нажми «Включить»",
            font=ctk.CTkFont(size=13), text_color=DIM
        )
        self.sched_status_lbl.pack(padx=16, pady=12)

        self.sched_log = self._log_box(pad, height=100)

    def _start_schedule(self):
        try:
            h = int(self.sched_hour.get())
            m = int(self.sched_min.get())
        except:
            self.sched_status_lbl.configure(text="⚠  Введи корректное время!", text_color=RED)
            return
        before = int(self.sched_before.get().split()[0])
        self.sched_active = True
        self.sched_status_lbl.configure(
            text=f"✅  Активно — фикс запустится в {h:02d}:{(m-before)%60:02d} (за {before} мин до {h:02d}:{m:02d})",
            text_color=GREEN
        )
        self.sched_thread = threading.Thread(target=self._sched_loop,
                                             args=(h,m,before), daemon=True)
        self.sched_thread.start()

    def _stop_schedule(self):
        self.sched_active = False
        self.sched_status_lbl.configure(text="⏸  Расписание остановлено", text_color=DIM)

    def _sched_loop(self, h, m, before):
        while self.sched_active:
            now = datetime.now()
            target_m = m - before
            target_h = h if target_m >= 0 else h - 1
            target_m = target_m % 60
            if now.hour == target_h and now.minute == target_m:
                self._run_scheduled()
                time.sleep(65)  # avoid double-trigger
            time.sleep(10)

    def _run_scheduled(self):
        self._log_append(self.sched_log, "⏰ Расписание сработало! Запускаю фиксы...")
        fix_map = {
            "dns":   ["ipconfig /flushdns", 'netsh interface ip set dns "Ethernet" static 8.8.8.8'],
            "quick": ["ipconfig /flushdns","netsh winsock reset","netsh int ip reset","netsh int ipv4 reset"],
            "cache": [r'del /f /s /q "%LOCALAPPDATA%\FortniteGame\Saved\Cache\*"'],
            "wu":    ["net stop wuauserv","net stop bits","net stop dosvc"],
        }
        for kid, ico, label in SCHED_FIXES:
            if self.sched_vars.get(kid, ctk.BooleanVar()).get():
                self._log_append(self.sched_log, f"  {ico} {label}...")
                for cmd in fix_map.get(kid,[]):
                    run_cmd(cmd)
                self._log_append(self.sched_log, f"  ✓ {label} — готово")
        self._log_append(self.sched_log, "✅ Всё готово! Запускай Fortnite.")

    # ─────────────────────────────────────────────────────────
    # GRAPHICS
    def _build_graphics(self):
        p = self._page("graphics")
        pad = ctk.CTkFrame(p, fg_color="transparent")
        pad.pack(fill="both", expand=True, padx=24, pady=20)

        self._section(pad, "🎮 Пресеты графики Fortnite")
        ctk.CTkLabel(pad, text="Готовые настройки GameUserSettings.ini",
                     text_color=DIM, font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(0,14))

        preset_row = ctk.CTkFrame(pad, fg_color="transparent")
        preset_row.pack(fill="x", pady=(0,14))
        for i, (pid, pdata) in enumerate(PRESETS.items()):
            preset_row.columnconfigure(i, weight=1)
            c = ctk.CTkFrame(preset_row, fg_color=PANEL, corner_radius=12,
                             border_width=2, border_color=BORDER)
            c.grid(row=0, column=i, padx=5, sticky="ew")
            inner = ctk.CTkFrame(c, fg_color="transparent")
            inner.pack(fill="both", padx=14, pady=14)
            ctk.CTkLabel(inner, text=pdata["name"],
                         font=ctk.CTkFont(size=14, weight="bold"),
                         text_color=pdata["color"]).pack(anchor="w")
            ctk.CTkLabel(inner, text=pdata["desc"],
                         font=ctk.CTkFont(size=11), text_color=DIM).pack(anchor="w", pady=(2,8))
            for sname, sval in pdata["settings"]:
                r = ctk.CTkFrame(inner, fg_color="transparent")
                r.pack(fill="x", pady=1)
                ctk.CTkLabel(r, text=sname, font=ctk.CTkFont(size=11), text_color=DIM).pack(side="left")
                ctk.CTkLabel(r, text=sval, font=ctk.CTkFont(size=11, weight="bold"),
                             text_color=TEXT).pack(side="right")
            self._btn(inner, "✓  Выбрать", lambda x=pid, col=pdata["color"]: self._select_preset(x),
                      color="#1a3050", width=120,
                      font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(10,0))
            setattr(self, f"preset_card_{pid}", c)

        # Active preset info
        info_card = self._card(pad)
        info_pad = ctk.CTkFrame(info_card, fg_color="transparent")
        info_pad.pack(fill="x", padx=16, pady=14)
        ctk.CTkLabel(info_pad, text="Выбранный пресет:",
                     font=ctk.CTkFont(size=13, weight="bold"), text_color="#fff").pack(anchor="w")
        self.preset_name_lbl = ctk.CTkLabel(info_pad, text="— не выбран",
                                             font=ctk.CTkFont(size=13), text_color=DIM)
        self.preset_name_lbl.pack(anchor="w", pady=(2,10))

        btn_row2 = ctk.CTkFrame(info_pad, fg_color="transparent")
        btn_row2.pack(anchor="w")
        self.apply_preset_btn = self._btn(btn_row2, "💾  Скачать GameUserSettings.ini",
                                          self._save_preset, width=270,
                                          state="disabled")
        self.apply_preset_btn.pack(side="left")
        self._btn(btn_row2, "📁  Куда копировать?", self._show_ini_path,
                  color="#1a3050", width=180,
                  font=ctk.CTkFont(size=12)).pack(side="left", padx=10)

        self.graphics_log = self._log_box(pad, height=100)

    def _select_preset(self, pid):
        self.active_preset = pid
        # Reset borders
        for k in PRESETS:
            c = getattr(self, f"preset_card_{k}", None)
            if c: c.configure(border_color=BORDER)
        card = getattr(self, f"preset_card_{pid}", None)
        if card: card.configure(border_color=PRESETS[pid]["color"])
        self.preset_name_lbl.configure(
            text=PRESETS[pid]["name"],
            text_color=PRESETS[pid]["color"]
        )
        self.apply_preset_btn.configure(state="normal")

    def _save_preset(self):
        if not self.active_preset: return
        p = PRESETS[self.active_preset]
        ini_content = p["ini"]
        path = os.path.join(os.path.expanduser("~"), "Downloads", "GameUserSettings.ini")
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(ini_content)
            self._log_append(self.graphics_log, f"✓ Файл сохранён: {path}")
            self._log_append(self.graphics_log, "Скопируй его в:")
            self._log_append(self.graphics_log,
                r"%LOCALAPPDATA%\FortniteGame\Saved\Config\WindowsClient\")
            self._log_append(self.graphics_log, "⚠ Сначала сделай резервную копию старого файла!")
        except Exception as e:
            self._log_append(self.graphics_log, f"✗ Ошибка: {e}")

    def _show_ini_path(self):
        self._log_append(self.graphics_log, "Путь к настройкам Fortnite:")
        self._log_append(self.graphics_log,
            r"%LOCALAPPDATA%\FortniteGame\Saved\Config\WindowsClient\GameUserSettings.ini")
        self._log_append(self.graphics_log,
            "Открой: Win+R → %LOCALAPPDATA% → FortniteGame → Saved → Config → WindowsClient")

    # ─────────────────────────────────────────────────────────
    # FIXES
    def _build_fixes(self):
        p = self._page("fixes")
        pad = ctk.CTkFrame(p, fg_color="transparent")
        pad.pack(fill="both", expand=True, padx=24, pady=20)

        self._section(pad, "🔧 Фиксы сети")
        ctk.CTkLabel(pad, text="Нажми ▶ на нужном фиксе. Начинай сверху вниз.",
                     text_color=DIM, font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(0,14))

        for ico, name, desc, color, cmds in FIXES:
            card = ctk.CTkFrame(pad, fg_color=PANEL2, corner_radius=10,
                                border_width=1, border_color=BORDER)
            card.pack(fill="x", pady=5)
            # Left accent strip
            strip = ctk.CTkFrame(card, width=3, fg_color=color, corner_radius=0)
            strip.pack(side="left", fill="y")

            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(fill="x", padx=14, pady=10)

            top = ctk.CTkFrame(inner, fg_color="transparent")
            top.pack(fill="x")
            ctk.CTkLabel(top, text=ico, font=ctk.CTkFont(size=20)).pack(side="left", padx=(0,8))
            info = ctk.CTkFrame(top, fg_color="transparent")
            info.pack(side="left", fill="x", expand=True)
            ctk.CTkLabel(info, text=name, font=ctk.CTkFont(size=13, weight="bold"),
                         text_color="#fff").pack(anchor="w")
            ctk.CTkLabel(info, text=desc, font=ctk.CTkFont(size=11),
                         text_color=DIM).pack(anchor="w")

            log_holder = [None]
            btn = self._btn(top, "▶", None, color="#1a3050", width=36,
                            font=ctk.CTkFont(size=14))
            btn.pack(side="right", padx=(8,0))
            btn.configure(command=lambda c=cmds, n=name, b=btn, lh=log_holder, p2=inner:
                          self._run_fix(c, n, b, lh, p2))

    def _run_fix(self, cmds, name, btn, log_holder, parent):
        btn.configure(text="⟳", state="disabled")
        if log_holder[0] is None:
            log_holder[0] = self._log_box(parent, height=80)
        else:
            log_holder[0].configure(state="normal")
            log_holder[0].delete("1.0","end")
            log_holder[0].configure(state="disabled")

        def run():
            for c in cmds:
                ok, _ = run_cmd(c)
                self._log_append(log_holder[0], f"{'✓' if ok else '✗'} {c.split()[0]}...")
                time.sleep(0.1)
            self._log_append(log_holder[0], f"✅ {name} завершён!")
            btn.configure(text="✓", state="normal",
                          fg_color="#0a3020", text_color=GREEN)
        threading.Thread(target=run, daemon=True).start()

    # ─────────────────────────────────────────────────────────
    # CHECK
    def _build_check(self):
        p = self._page("check")
        pad = ctk.CTkFrame(p, fg_color="transparent")
        pad.pack(fill="both", expand=True, padx=24, pady=20)

        self._section(pad, "📡 Проверка серверов")
        ctk.CTkLabel(pad, text="Проверяет доступность AWS и Fortnite серверов из твоей сети",
                     text_color=DIM, font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(0,14))

        self._btn(pad, "🔍  Проверить серверы", self._run_check, width=200).pack(anchor="w", pady=(0,14))

        self.check_log = self._log_box(pad, height=220)

        ctk.CTkLabel(pad, text="🔒 Если AWS timeout — используй AmneziaVPN (amnezia.org)",
                     font=ctk.CTkFont(size=12, slant="italic"),
                     text_color=GOLD).pack(anchor="w", pady=(10,0))

    def _run_check(self):
        self.check_log.configure(state="normal")
        self.check_log.delete("1.0","end")
        self.check_log.configure(state="disabled")
        hosts = [
            ("AWS EU Frankfurt", "ec2.eu-central-1.amazonaws.com"),
            ("AWS EU Stockholm", "ec2.eu-north-1.amazonaws.com"),
            ("Fortnite.com",     "fortnite.com"),
            ("Epic Games API",   "api.epicgames.com"),
        ]
        def run():
            self._log_append(self.check_log, "Сканирую серверы...")
            any_bad = False
            for name, host in hosts:
                ms = ping_host(host)
                if ms < 0:
                    any_bad = True
                    self._log_append(self.check_log, f"✗  {name:<25} timeout  ← ЗАБЛОКИРОВАН")
                else:
                    status = "OK" if ms < 100 else "ВЫСОКИЙ ПИНГ"
                    self._log_append(self.check_log, f"✓  {name:<25} {ms} ms  {status}")
                time.sleep(0.2)
            if any_bad:
                self._log_append(self.check_log, "\n⚠  AWS заблокирован (РКН)!")
                self._log_append(self.check_log, "→  Решение: AmneziaVPN → amnezia.org (бесплатно)")
                self._log_append(self.check_log, "→  Подключай VPN ДО запуска Fortnite!")
            else:
                self._log_append(self.check_log, "\n✅ Все серверы доступны! Можно играть.")
        threading.Thread(target=run, daemon=True).start()


# ══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    app = App()
    app.mainloop()
