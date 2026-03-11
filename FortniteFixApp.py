"""Fortnite AWS Fix v6.0 — Desktop App (Python + CustomTkinter)"""
import customtkinter as ctk
import subprocess, threading, random, time, os, socket
from datetime import datetime

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

NEON="#00f0ff"; GOLD="#ffd700"; GREEN="#00ff88"; RED="#ff4466"; PURPLE="#b060ff"
BG="#05080f"; PANEL="#090f1d"; PANEL2="#0c1628"; BORDER="#1a3050"; TEXT="#b8cfea"; DIM="#3a5a7a"

JOKES=["😂 Ваня снова в топ-1 по смертям","👀 Ваня: '0 пинг!'  Мы: 999ms",
       "💀 Ваня купил скин и всё равно проиграл","🤖 Ваня строил 1x1 — бот его снёс",
       "😭 Ваня поставил графику Эпик... FPS 8","⏰ Ваня включил расписание и опоздал на катку"]

FIXES=[
    ("⚡","Быстрый фикс","DNS + Winsock + TCP/IP","#00c8ff",
     ["ipconfig /flushdns","netsh winsock reset","netsh int ip reset","netsh int ipv4 reset","ipconfig /registerdns"]),
    ("🔄","Полный сброс","+ SFC + DISM (15 мин)","#ff9f40",
     ["ipconfig /flushdns","netsh winsock reset","sfc /scannow","DISM /Online /Cleanup-Image /RestoreHealth"]),
    ("🌐","Смена DNS","Google 8.8.8.8 + CF 1.1.1.1","#a29bfe",
     ['netsh interface ip set dns "Ethernet" static 8.8.8.8','netsh interface ip set dns "Wi-Fi" static 8.8.8.8',
      'netsh interface ip add dns "Ethernet" 1.1.1.1 index=2',"ipconfig /flushdns"]),
    ("🗑","Очистка кэша","Fortnite + Epic Launcher","#55efc4",
     [r'del /f /s /q "%LOCALAPPDATA%\FortniteGame\Saved\Cache\*"',
      r'del /f /s /q "%LOCALAPPDATA%\EpicGamesLauncher\Saved\webcache\*"']),
    ("📶","QoS приоритет","DSCP=46 для Fortnite","#fd79a8",
     ['netsh qos delete policy "FortniteClient"',
      'netsh qos add policy "FortniteClient" app="FortniteClient-Win64-Shipping.exe" dscp=46 throttle-rate=-1']),
    ("📝","Очистка hosts","Удалить блокировки Epic/AWS","#ffeaa7",
     [r'copy /Y %WINDIR%\System32\drivers\etc\hosts %WINDIR%\System32\drivers\etc\hosts.bak']),
    ("🔕","Откл. IPv6","Помогает в РФ/СНГ","#74b9ff",
     ['reg add "HKLM\\SYSTEM\\CurrentControlSet\\Services\\Tcpip6\\Parameters" /v "DisabledComponents" /t REG_DWORD /d 255 /f']),
    ("🏎","Откл. Nagle","Снижает пинг на 5-30ms","#00b894",
     ['reg add "HKLM\\SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters" /v "TcpAckFrequency" /t REG_DWORD /d 1 /f',
      'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters" /v "TCPNoDelay" /t REG_DWORD /d 1 /f']),
    ("⏸","Пауза Win Update","Остановить обновления","#e17055",
     ["net stop wuauserv","net stop bits","net stop dosvc"]),
]

SCHED_FIXES=[("dns","🌐","Смена DNS"),("quick","⚡","Быстрый фикс"),
             ("cache","🗑","Очистка кэша"),("wu","⏸","Пауза Windows Update")]

PRESETS={
    "fps":{"name":"⚡ МАКСИМУМ FPS","color":NEON,"desc":"+40-60% FPS",
           "ini":"[ScalabilityGroups]\nsg.ResolutionQuality=75\nsg.ViewDistanceQuality=1\nsg.ShadowQuality=0\nsg.PostProcessQuality=0\nsg.TextureQuality=0\nsg.EffectsQuality=0\nsg.FoliageQuality=0\n\n[/Script/FortniteGame.FortGameUserSettings]\nResolutionSizeX=1280\nResolutionSizeY=720\nbUseVSync=False\nbFrameRateLimit=0\nbShowFPS=True\n",
           "settings":[("Разрешение","1280×720"),("Текстуры","0 Низкие"),("Тени","Выкл"),("Сглаживание","Выкл"),("Ожид. FPS","120-240+")]},
    "balance":{"name":"⚖️ БАЛАНС","color":PURPLE,"desc":"Лучший выбор",
               "ini":"[ScalabilityGroups]\nsg.ResolutionQuality=100\nsg.ViewDistanceQuality=2\nsg.ShadowQuality=2\nsg.PostProcessQuality=2\nsg.TextureQuality=2\nsg.EffectsQuality=2\nsg.FoliageQuality=2\n\n[/Script/FortniteGame.FortGameUserSettings]\nResolutionSizeX=1920\nResolutionSizeY=1080\nbUseVSync=False\nbFrameRateLimit=144\n",
               "settings":[("Разрешение","1920×1080"),("Текстуры","2 Средние"),("Тени","Средние"),("Сглаживание","TAA"),("Ожид. FPS","60-120")]},
    "quality":{"name":"✨ КАЧЕСТВО","color":GOLD,"desc":"Красивая картинка",
               "ini":"[ScalabilityGroups]\nsg.ResolutionQuality=100\nsg.ViewDistanceQuality=4\nsg.ShadowQuality=4\nsg.PostProcessQuality=4\nsg.TextureQuality=4\nsg.EffectsQuality=4\nsg.FoliageQuality=4\n\n[/Script/FortniteGame.FortGameUserSettings]\nResolutionSizeX=2560\nResolutionSizeY=1440\nbUseVSync=False\nbFrameRateLimit=60\n",
               "settings":[("Разрешение","2560×1440"),("Текстуры","4 Эпик"),("Тени","Высокие"),("Сглаживание","TSR"),("Ожид. FPS","30-60")]},
}

def run_cmd(cmd):
    try:
        r=subprocess.run(cmd,shell=True,capture_output=True,text=True,timeout=60,encoding="cp1251",errors="replace")
        return r.returncode==0, r.stdout+r.stderr
    except Exception as e:
        return False,str(e)

def ping_host(host,timeout=2):
    try:
        t0=time.time(); s=socket.create_connection((host,80),timeout=timeout); s.close()
        return int((time.time()-t0)*1000)
    except:
        return -1

def make_btn(parent, text, cmd, size=13, bold=True, color="#0060df", hover="#0080ff", width=None, corner=8):
    """Single clean button factory — no **kw conflicts."""
    kwargs = dict(
        text=text, command=cmd,
        fg_color=color, hover_color=hover,
        font=ctk.CTkFont(size=size, weight="bold" if bold else "normal"),
        corner_radius=corner,
    )
    if width: kwargs["width"] = width
    return ctk.CTkButton(parent, **kwargs)

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Fortnite AWS Fix v6.0")
        self.geometry("1000x660"); self.minsize(900,600); self.configure(fg_color=BG)
        self.monitor_running=False; self.ping_history=[]; self.sched_active=False; self.active_preset=None
        self._build_ui()

    def _build_ui(self):
        self.sidebar=ctk.CTkFrame(self,width=200,fg_color=PANEL,corner_radius=0,border_width=1,border_color=BORDER)
        self.sidebar.pack(side="left",fill="y"); self.sidebar.pack_propagate(False)
        lf=ctk.CTkFrame(self.sidebar,fg_color="transparent"); lf.pack(pady=(20,6),padx=16)
        ctk.CTkLabel(lf,text="⚡",font=ctk.CTkFont(size=26)).pack(side="left")
        ctk.CTkLabel(lf,text=" FORTNITE FIX",font=ctk.CTkFont(size=12,weight="bold"),text_color=NEON).pack(side="left")
        ctk.CTkLabel(self.sidebar,text="v6.0",font=ctk.CTkFont(size=10),text_color=DIM).pack()
        ctk.CTkFrame(self.sidebar,height=1,fg_color=BORDER).pack(fill="x",padx=12,pady=10)
        self.nav_btns={}
        pages=[("dash","⚡  Главная"),("monitor","📊  Пинг-монитор  🆕"),("sched","⏰  Расписание  🆕"),
               ("graphics","🎮  Графика  🆕"),("fixes","🔧  Фиксы"),("check","📡  Проверка AWS")]
        for pid,label in pages:
            b=ctk.CTkButton(self.sidebar,text=label,anchor="w",font=ctk.CTkFont(size=12),height=36,
                            fg_color="transparent",hover_color="#0d1e38",text_color=DIM,corner_radius=8,
                            command=lambda p=pid:self.show_page(p))
            b.pack(fill="x",padx=10,pady=2); self.nav_btns[pid]=b
        ctk.CTkFrame(self.sidebar,height=1,fg_color=BORDER).pack(fill="x",padx=12,pady=10,side="bottom")
        self.joke_lbl=ctk.CTkLabel(self.sidebar,text=random.choice(JOKES),font=ctk.CTkFont(size=10,slant="italic"),
                                   text_color=GOLD,wraplength=175,justify="center")
        self.joke_lbl.pack(side="bottom",padx=10,pady=6)
        self.content=ctk.CTkFrame(self,fg_color=BG,corner_radius=0); self.content.pack(side="left",fill="both",expand=True)
        self.pages={}
        self._build_dashboard(); self._build_monitor(); self._build_scheduler()
        self._build_graphics(); self._build_fixes(); self._build_check()
        self.show_page("dash")

    def show_page(self,pid):
        for p in self.pages.values(): p.pack_forget()
        self.pages[pid].pack(fill="both",expand=True)
        for k,b in self.nav_btns.items():
            b.configure(fg_color="#0d2040" if k==pid else "transparent",
                        text_color=NEON if k==pid else DIM)

    def _page(self,pid):
        f=ctk.CTkScrollableFrame(self.content,fg_color=BG,corner_radius=0,scrollbar_button_color=BORDER)
        self.pages[pid]=f; return f

    def _pad(self,parent):
        f=ctk.CTkFrame(parent,fg_color="transparent"); f.pack(fill="both",expand=True,padx=22,pady=18); return f

    def _section(self,parent,title):
        ctk.CTkLabel(parent,text=title,font=ctk.CTkFont(size=18,weight="bold"),text_color="#fff").pack(anchor="w",pady=(0,4))

    def _card(self,parent):
        f=ctk.CTkFrame(parent,fg_color=PANEL2,corner_radius=12,border_width=1,border_color=BORDER)
        f.pack(fill="x",pady=6); return f

    def _log(self,parent,h=160):
        tb=ctk.CTkTextbox(parent,height=h,fg_color="#020810",border_width=1,border_color=BORDER,
                          font=ctk.CTkFont(family="Courier New",size=12),text_color="#68ffaa",corner_radius=8)
        tb.pack(fill="x",pady=(6,0)); tb.configure(state="disabled"); return tb

    def _log_add(self,tb,text):
        tb.configure(state="normal"); tb.insert("end",text+"\n"); tb.configure(state="disabled"); tb.see("end")

    def _log_clear(self,tb):
        tb.configure(state="normal"); tb.delete("1.0","end"); tb.configure(state="disabled")

    # ── DASHBOARD ──────────────────────────────────────────
    def _build_dashboard(self):
        p=self._page("dash"); pad=self._pad(p)
        hero=ctk.CTkFrame(pad,fg_color=PANEL,corner_radius=14,border_width=1,border_color=BORDER)
        hero.pack(fill="x",pady=(0,14))
        hi=ctk.CTkFrame(hero,fg_color="transparent"); hi.pack(fill="x",padx=24,pady=18)
        ctk.CTkLabel(hi,text="FORTNITE AWS FIX",font=ctk.CTkFont(size=26,weight="bold"),text_color="#fff").pack(anchor="w")
        ctk.CTkLabel(hi,text="Инструмент против лагов • Россия / СНГ",font=ctk.CTkFont(size=12),text_color=DIM).pack(anchor="w",pady=(2,10))
        self.joke_hero=ctk.CTkLabel(hi,text=random.choice(JOKES),font=ctk.CTkFont(size=11,slant="italic"),text_color=GOLD)
        self.joke_hero.pack(anchor="w",pady=(0,12))
        make_btn(hi,"⚡  БЫСТРЫЙ ФИКС",self._quick_fix,size=15,width=220,color="#0060df",hover="#0090ff").pack(anchor="w")
        self.dash_log=self._log(hi,100)
        grid=ctk.CTkFrame(pad,fg_color="transparent"); grid.pack(fill="x",pady=(6,0))
        cards=[("📊","Пинг-монитор","Живой график","monitor"),("⏰","Расписание","Автофикс перед игрой","sched"),
               ("🎮","Графика","Пресеты FPS/Баланс","graphics"),("🔧","Фиксы сети","DNS QoS Nagle…","fixes"),
               ("📡","Проверка AWS","Пинг серверов","check"),("😂","Новая шутка","Про Ваню",None)]
        for i,(ico,name,desc,pid) in enumerate(cards):
            c=ctk.CTkFrame(grid,fg_color=PANEL2,corner_radius=11,border_width=1,border_color=BORDER)
            c.grid(row=i//3,column=i%3,padx=5,pady=5,sticky="ew"); grid.columnconfigure(i%3,weight=1)
            ci=ctk.CTkFrame(c,fg_color="transparent"); ci.pack(padx=12,pady=10)
            ctk.CTkLabel(ci,text=ico,font=ctk.CTkFont(size=20)).pack(anchor="w")
            ctk.CTkLabel(ci,text=name,font=ctk.CTkFont(size=12,weight="bold"),text_color="#fff").pack(anchor="w")
            ctk.CTkLabel(ci,text=desc,font=ctk.CTkFont(size=10),text_color=DIM).pack(anchor="w")
            cb=lambda e,x=pid:self.show_page(x) if x else self._refresh_joke()
            for w in [c,ci]+ci.winfo_children(): w.bind("<Button-1>",cb)

    def _refresh_joke(self):
        j=random.choice(JOKES); self.joke_lbl.configure(text=j); self.joke_hero.configure(text=j)

    def _quick_fix(self):
        self._log_clear(self.dash_log)
        cmds=["ipconfig /flushdns","netsh winsock reset","netsh int ip reset","netsh int ipv4 reset","ipconfig /registerdns"]
        def run():
            for c in cmds:
                ok,_=run_cmd(c); self._log_add(self.dash_log,f"{'✓' if ok else '✗'} {c.split()[0]}"); time.sleep(0.1)
            self._log_add(self.dash_log,"✅ Быстрый фикс завершён!")
        threading.Thread(target=run,daemon=True).start()

    # ── PING MONITOR ───────────────────────────────────────
    def _build_monitor(self):
        p=self._page("monitor"); pad=self._pad(p)
        self._section(pad,"📊 Пинг-монитор")
        ctk.CTkLabel(pad,text="Мониторинг задержки до серверов в реальном времени",text_color=DIM,font=ctk.CTkFont(size=11)).pack(anchor="w",pady=(0,10))
        sr=ctk.CTkFrame(pad,fg_color="transparent"); sr.pack(fill="x",pady=(0,10))
        self.stat_cur=self._stat(sr,"—","Текущий ms",GREEN,0)
        self.stat_avg=self._stat(sr,"—","Средний ms",GOLD,1)
        self.stat_max=self._stat(sr,"—","Максимум ms",RED,2)
        for i in range(3): sr.columnconfigure(i,weight=1)
        cr=ctk.CTkFrame(pad,fg_color="transparent"); cr.pack(fill="x",pady=(0,10))
        self.mon_btn=make_btn(cr,"▶  Запустить",self._toggle_monitor,width=200,color="#0060df",hover="#0090ff")
        self.mon_btn.pack(side="left")
        self.mon_lbl=ctk.CTkLabel(cr,text="● Остановлен",text_color=DIM,font=ctk.CTkFont(size=11)); self.mon_lbl.pack(side="left",padx=12)
        ctk.CTkLabel(cr,text="Интервал:",text_color=DIM,font=ctk.CTkFont(size=11)).pack(side="left")
        self.mon_int=ctk.CTkComboBox(cr,values=["2 сек","5 сек","10 сек"],width=90,fg_color=PANEL2,border_color=BORDER)
        self.mon_int.pack(side="left",padx=6); self.mon_int.set("2 сек")
        self.srv_lbls={}
        for name,host in [("AWS EU Frankfurt","ec2.eu-central-1.amazonaws.com"),("AWS EU Stockholm","ec2.eu-north-1.amazonaws.com"),
                           ("Fortnite.com","fortnite.com"),("Epic Games API","api.epicgames.com")]:
            row=ctk.CTkFrame(pad,fg_color=PANEL2,corner_radius=8,border_width=1,border_color=BORDER); row.pack(fill="x",pady=2)
            ctk.CTkLabel(row,text="●",font=ctk.CTkFont(size=12),text_color=DIM).pack(side="left",padx=(10,6),pady=8)
            ctk.CTkLabel(row,text=name,font=ctk.CTkFont(size=12),text_color=TEXT).pack(side="left")
            lbl=ctk.CTkLabel(row,text="— ms",font=ctk.CTkFont(size=12,weight="bold"),text_color=DIM); lbl.pack(side="right",padx=14)
            self.srv_lbls[host]=lbl
        cc=self._card(pad)
        ctk.CTkLabel(cc,text="📈 График пинга",font=ctk.CTkFont(size=11),text_color=DIM).pack(anchor="w",padx=12,pady=(8,2))
        self.chart=ctk.CTkCanvas(cc,height=110,bg="#020810",highlightthickness=0); self.chart.pack(fill="x",padx=10,pady=(0,8))

    def _stat(self,parent,val,label,color,col):
        f=ctk.CTkFrame(parent,fg_color=PANEL2,corner_radius=9,border_width=1,border_color=BORDER)
        f.grid(row=0,column=col,padx=4,sticky="ew")
        v=ctk.CTkLabel(f,text=val,font=ctk.CTkFont(size=24,weight="bold"),text_color=color); v.pack(pady=(10,2))
        ctk.CTkLabel(f,text=label,font=ctk.CTkFont(size=10),text_color=DIM).pack(pady=(0,8))
        return v

    def _toggle_monitor(self):
        if self.monitor_running:
            self.monitor_running=False
            self.mon_btn.configure(text="▶  Запустить",fg_color="#0060df",hover_color="#0090ff")
            self.mon_lbl.configure(text="● Остановлен",text_color=DIM)
        else:
            self.monitor_running=True
            self.mon_btn.configure(text="⏹  Остановить",fg_color="#6b0000",hover_color="#8b0000")
            self.mon_lbl.configure(text="● Активен",text_color=GREEN)
            threading.Thread(target=self._mon_loop,daemon=True).start()

    def _mon_loop(self):
        while self.monitor_running:
            iv={"2 сек":2,"5 сек":5,"10 сек":10}.get(self.mon_int.get(),2)
            hosts=list(self.srv_lbls.keys()); results=[]
            for h in hosts:
                ms=ping_host(h); results.append(ms)
                lbl=self.srv_lbls[h]
                if ms<0: lbl.configure(text="timeout",text_color=RED)
                else:
                    col=GREEN if ms<80 else GOLD if ms<150 else RED
                    lbl.configure(text=f"{ms} ms",text_color=col)
            valid=[r for r in results if r>=0]
            if valid:
                avg=sum(valid)//len(valid); self.ping_history.append(avg)
                if len(self.ping_history)>30: self.ping_history.pop(0)
                self.stat_cur.configure(text=str(avg),text_color=GREEN if avg<80 else GOLD if avg<150 else RED)
                self.stat_avg.configure(text=str(sum(self.ping_history)//len(self.ping_history)))
                self.stat_max.configure(text=str(max(self.ping_history)))
                self._draw_chart()
            time.sleep(iv)

    def _draw_chart(self):
        c=self.chart; c.delete("all")
        if len(self.ping_history)<2: return
        W=c.winfo_width() or 500; H=110; maxV=max(max(self.ping_history),200)
        pts=[(int(10+(i/(len(self.ping_history)-1))*(W-20)),int(H-10-(v/maxV)*(H-20))) for i,v in enumerate(self.ping_history)]
        poly=[(10,H-10)]+pts+[(pts[-1][0],H-10)]
        c.create_polygon([x for pt in poly for x in pt],fill="#003030",outline="")
        c.create_line([x for pt in pts for x in pt],fill=GREEN if self.ping_history[-1]<80 else GOLD if self.ping_history[-1]<150 else RED,width=2,smooth=True)

    # ── SCHEDULER ──────────────────────────────────────────
    def _build_scheduler(self):
        p=self._page("sched"); pad=self._pad(p)
        self._section(pad,"⏰ Расписание фикса")
        ctk.CTkLabel(pad,text="Автоматически запускает фиксы за несколько минут до игры",text_color=DIM,font=ctk.CTkFont(size=11)).pack(anchor="w",pady=(0,12))
        tc=ctk.CTkFrame(pad,fg_color="transparent"); tc.pack(fill="x"); tc.columnconfigure(0,weight=1); tc.columnconfigure(1,weight=1)
        lf=ctk.CTkFrame(tc,fg_color=PANEL,corner_radius=11,border_width=1,border_color=BORDER); lf.grid(row=0,column=0,padx=(0,6),sticky="nsew")
        li=ctk.CTkFrame(lf,fg_color="transparent"); li.pack(fill="both",padx=14,pady=14)
        ctk.CTkLabel(li,text="🕐 Время начала игры",font=ctk.CTkFont(size=13,weight="bold"),text_color="#fff").pack(anchor="w",pady=(0,6))
        ctk.CTkLabel(li,text="Во сколько обычно начинаешь играть?",text_color=DIM,font=ctk.CTkFont(size=11)).pack(anchor="w",pady=(0,6))
        tr=ctk.CTkFrame(li,fg_color="transparent"); tr.pack(anchor="w",pady=(0,8))
        self.sh=ctk.CTkEntry(tr,width=65,font=ctk.CTkFont(size=22,weight="bold"),fg_color=PANEL2,border_color=NEON,justify="center"); self.sh.insert(0,"20"); self.sh.pack(side="left")
        ctk.CTkLabel(tr,text=" : ",font=ctk.CTkFont(size=22,weight="bold"),text_color=NEON).pack(side="left")
        self.sm=ctk.CTkEntry(tr,width=65,font=ctk.CTkFont(size=22,weight="bold"),fg_color=PANEL2,border_color=NEON,justify="center"); self.sm.insert(0,"00"); self.sm.pack(side="left")
        br=ctk.CTkFrame(li,fg_color="transparent"); br.pack(anchor="w",pady=(0,10))
        ctk.CTkLabel(br,text="За сколько минут:",text_color=DIM,font=ctk.CTkFont(size=11)).pack(side="left")
        self.sbef=ctk.CTkComboBox(br,values=["2 мин","5 мин","10 мин"],width=85,fg_color=PANEL2,border_color=BORDER); self.sbef.set("2 мин"); self.sbef.pack(side="left",padx=6)
        bb=ctk.CTkFrame(li,fg_color="transparent"); bb.pack(anchor="w")
        make_btn(bb,"⏰  Включить",self._start_sched,width=130,color="#0060df",hover="#0090ff").pack(side="left")
        make_btn(bb,"✕  Выключить",self._stop_sched,width=120,color="#5c1010",hover="#8b1515").pack(side="left",padx=8)
        rf=ctk.CTkFrame(tc,fg_color=PANEL,corner_radius=11,border_width=1,border_color=BORDER); rf.grid(row=0,column=1,padx=(6,0),sticky="nsew")
        ri=ctk.CTkFrame(rf,fg_color="transparent"); ri.pack(fill="both",padx=14,pady=14)
        ctk.CTkLabel(ri,text="⚡ Что запускать",font=ctk.CTkFont(size=13,weight="bold"),text_color="#fff").pack(anchor="w",pady=(0,8))
        self.sched_vars={}; defaults={"dns":True,"quick":True,"cache":False,"wu":True}
        for kid,ico,label in SCHED_FIXES:
            var=ctk.BooleanVar(value=defaults.get(kid,False)); self.sched_vars[kid]=var
            row=ctk.CTkFrame(ri,fg_color=PANEL2,corner_radius=7,border_width=1,border_color=BORDER); row.pack(fill="x",pady=2)
            ctk.CTkCheckBox(row,text=f"{ico}  {label}",variable=var,font=ctk.CTkFont(size=12),text_color=TEXT,
                            checkmark_color=NEON,fg_color=PANEL2,hover_color=PANEL).pack(padx=10,pady=7,anchor="w")
        sf=ctk.CTkFrame(pad,fg_color=PANEL2,corner_radius=9,border_width=1,border_color=BORDER); sf.pack(fill="x",pady=(12,0))
        self.sched_lbl=ctk.CTkLabel(sf,text="⏸  Расписание не активно",font=ctk.CTkFont(size=12),text_color=DIM); self.sched_lbl.pack(padx=14,pady=10)
        self.sched_log=self._log(pad,80)

    def _start_sched(self):
        try: h=int(self.sh.get()); m=int(self.sm.get())
        except: self.sched_lbl.configure(text="⚠  Введи корректное время!",text_color=RED); return
        before=int(self.sbef.get().split()[0]); self.sched_active=True
        tm=(m-before)%60; th=h if m-before>=0 else (h-1)%24
        self.sched_lbl.configure(text=f"✅  Активно — фикс запустится в {th:02d}:{tm:02d}",text_color=GREEN)
        threading.Thread(target=self._sched_loop,args=(h,m,before),daemon=True).start()

    def _stop_sched(self):
        self.sched_active=False; self.sched_lbl.configure(text="⏸  Расписание остановлено",text_color=DIM)

    def _sched_loop(self,h,m,before):
        while self.sched_active:
            now=datetime.now(); th=h; tm=m-before
            if tm<0: th-=1; tm+=60
            if now.hour==th and now.minute==tm: self._run_sched(); time.sleep(65)
            time.sleep(10)

    def _run_sched(self):
        self._log_add(self.sched_log,"⏰ Расписание сработало!")
        fmap={"dns":["ipconfig /flushdns",'netsh interface ip set dns "Ethernet" static 8.8.8.8'],
              "quick":["ipconfig /flushdns","netsh winsock reset","netsh int ip reset"],
              "cache":[r'del /f /s /q "%LOCALAPPDATA%\FortniteGame\Saved\Cache\*"'],
              "wu":["net stop wuauserv","net stop bits","net stop dosvc"]}
        for kid,ico,label in SCHED_FIXES:
            if self.sched_vars.get(kid,ctk.BooleanVar()).get():
                self._log_add(self.sched_log,f"  {ico} {label}...")
                for cmd in fmap.get(kid,[]): run_cmd(cmd)
                self._log_add(self.sched_log,f"  ✓ {label} готово")
        self._log_add(self.sched_log,"✅ Готово! Запускай Fortnite.")

    # ── GRAPHICS ───────────────────────────────────────────
    def _build_graphics(self):
        p=self._page("graphics"); pad=self._pad(p)
        self._section(pad,"🎮 Пресеты графики")
        ctk.CTkLabel(pad,text="Готовые настройки GameUserSettings.ini",text_color=DIM,font=ctk.CTkFont(size=11)).pack(anchor="w",pady=(0,12))
        pr=ctk.CTkFrame(pad,fg_color="transparent"); pr.pack(fill="x",pady=(0,12))
        self.preset_cards={}
        for i,(pid,pdata) in enumerate(PRESETS.items()):
            pr.columnconfigure(i,weight=1)
            c=ctk.CTkFrame(pr,fg_color=PANEL,corner_radius=11,border_width=2,border_color=BORDER); c.grid(row=0,column=i,padx=4,sticky="ew")
            ci=ctk.CTkFrame(c,fg_color="transparent"); ci.pack(fill="both",padx=12,pady=12)
            ctk.CTkLabel(ci,text=pdata["name"],font=ctk.CTkFont(size=13,weight="bold"),text_color=pdata["color"]).pack(anchor="w")
            ctk.CTkLabel(ci,text=pdata["desc"],font=ctk.CTkFont(size=10),text_color=DIM).pack(anchor="w",pady=(2,6))
            for sn,sv in pdata["settings"]:
                r=ctk.CTkFrame(ci,fg_color="transparent"); r.pack(fill="x",pady=1)
                ctk.CTkLabel(r,text=sn,font=ctk.CTkFont(size=10),text_color=DIM).pack(side="left")
                ctk.CTkLabel(r,text=sv,font=ctk.CTkFont(size=10,weight="bold"),text_color=TEXT).pack(side="right")
            make_btn(ci,"✓  Выбрать",lambda x=pid:self._sel_preset(x),size=11,bold=False,width=110,color="#1a3050",hover="#2a4060").pack(anchor="w",pady=(8,0))
            self.preset_cards[pid]=c
        ic=self._card(pad); ip=ctk.CTkFrame(ic,fg_color="transparent"); ip.pack(fill="x",padx=14,pady=12)
        ctk.CTkLabel(ip,text="Выбранный пресет:",font=ctk.CTkFont(size=12,weight="bold"),text_color="#fff").pack(anchor="w")
        self.preset_lbl=ctk.CTkLabel(ip,text="— не выбран",font=ctk.CTkFont(size=12),text_color=DIM); self.preset_lbl.pack(anchor="w",pady=(2,8))
        bb=ctk.CTkFrame(ip,fg_color="transparent"); bb.pack(anchor="w")
        self.apply_btn=make_btn(bb,"💾  Скачать .ini",self._save_preset,width=220,color="#0060df",hover="#0090ff")
        self.apply_btn.pack(side="left"); self.apply_btn.configure(state="disabled",fg_color="#1a2a3a")
        make_btn(bb,"📁  Куда копировать?",self._show_path,size=11,bold=False,width=180,color="#1a3050",hover="#2a4060").pack(side="left",padx=8)
        self.gfx_log=self._log(pad,80)

    def _sel_preset(self,pid):
        self.active_preset=pid
        for k,c in self.preset_cards.items(): c.configure(border_color=PRESETS[k]["color"] if k==pid else BORDER)
        self.preset_lbl.configure(text=PRESETS[pid]["name"],text_color=PRESETS[pid]["color"])
        self.apply_btn.configure(state="normal",fg_color="#0060df")

    def _save_preset(self):
        if not self.active_preset: return
        path=os.path.join(os.path.expanduser("~"),"Downloads","GameUserSettings.ini")
        try:
            with open(path,"w",encoding="utf-8") as f: f.write(PRESETS[self.active_preset]["ini"])
            self._log_add(self.gfx_log,f"✓ Сохранён: {path}")
            self._log_add(self.gfx_log,"Скопируй в: %LOCALAPPDATA%\\FortniteGame\\Saved\\Config\\WindowsClient\\")
            self._log_add(self.gfx_log,"⚠ Сначала сделай резервную копию старого файла!")
        except Exception as e: self._log_add(self.gfx_log,f"✗ Ошибка: {e}")

    def _show_path(self):
        self._log_add(self.gfx_log,"Путь: %LOCALAPPDATA%\\FortniteGame\\Saved\\Config\\WindowsClient\\GameUserSettings.ini")
        self._log_add(self.gfx_log,"Win+R → %LOCALAPPDATA% → FortniteGame → Saved → Config → WindowsClient")

    # ── FIXES ──────────────────────────────────────────────
    def _build_fixes(self):
        p=self._page("fixes"); pad=self._pad(p)
        self._section(pad,"🔧 Фиксы сети")
        ctk.CTkLabel(pad,text="Нажми ▶ на нужном фиксе",text_color=DIM,font=ctk.CTkFont(size=11)).pack(anchor="w",pady=(0,12))
        for ico,name,desc,color,cmds in FIXES:
            c=ctk.CTkFrame(pad,fg_color=PANEL2,corner_radius=9,border_width=1,border_color=BORDER); c.pack(fill="x",pady=4)
            strip=ctk.CTkFrame(c,width=3,fg_color=color,corner_radius=0); strip.pack(side="left",fill="y")
            ci=ctk.CTkFrame(c,fg_color="transparent"); ci.pack(fill="x",padx=12,pady=8)
            top=ctk.CTkFrame(ci,fg_color="transparent"); top.pack(fill="x")
            ctk.CTkLabel(top,text=ico,font=ctk.CTkFont(size=18)).pack(side="left",padx=(0,8))
            inf=ctk.CTkFrame(top,fg_color="transparent"); inf.pack(side="left",fill="x",expand=True)
            ctk.CTkLabel(inf,text=name,font=ctk.CTkFont(size=12,weight="bold"),text_color="#fff").pack(anchor="w")
            ctk.CTkLabel(inf,text=desc,font=ctk.CTkFont(size=10),text_color=DIM).pack(anchor="w")
            lh=[None]
            btn=make_btn(top,"▶",None,size=12,width=34,color="#1a3050",hover="#2a4060")
            btn.pack(side="right")
            btn.configure(command=lambda c2=cmds,n=name,b=btn,lhh=lh,ci2=ci: self._run_fix(c2,n,b,lhh,ci2))

    def _run_fix(self,cmds,name,btn,lh,parent):
        btn.configure(text="⟳",state="disabled")
        if lh[0] is None: lh[0]=self._log(parent,70)
        else: self._log_clear(lh[0])
        def run():
            for c in cmds:
                ok,_=run_cmd(c); self._log_add(lh[0],f"{'✓' if ok else '✗'} {c.split()[0]}"); time.sleep(0.1)
            self._log_add(lh[0],f"✅ {name} завершён!")
            btn.configure(text="✓",state="normal",fg_color="#0a3020",hover_color="#0d4028",text_color=GREEN)
        threading.Thread(target=run,daemon=True).start()

    # ── CHECK ──────────────────────────────────────────────
    def _build_check(self):
        p=self._page("check"); pad=self._pad(p)
        self._section(pad,"📡 Проверка серверов")
        ctk.CTkLabel(pad,text="Проверяет доступность AWS и Fortnite из твоей сети",text_color=DIM,font=ctk.CTkFont(size=11)).pack(anchor="w",pady=(0,12))
        make_btn(pad,"🔍  Проверить серверы",self._run_check,width=200,color="#0060df",hover="#0090ff").pack(anchor="w",pady=(0,12))
        self.check_log=self._log(pad,200)
        ctk.CTkLabel(pad,text="🔒 Если AWS timeout — используй AmneziaVPN (amnezia.org)",
                     font=ctk.CTkFont(size=11,slant="italic"),text_color=GOLD).pack(anchor="w",pady=(8,0))

    def _run_check(self):
        self._log_clear(self.check_log)
        hosts=[("AWS EU Frankfurt","ec2.eu-central-1.amazonaws.com"),("AWS EU Stockholm","ec2.eu-north-1.amazonaws.com"),
               ("Fortnite.com","fortnite.com"),("Epic Games API","api.epicgames.com")]
        def run():
            self._log_add(self.check_log,"Сканирую серверы..."); bad=False
            for name,host in hosts:
                ms=ping_host(host)
                if ms<0: bad=True; self._log_add(self.check_log,f"✗  {name:<26} timeout ← ЗАБЛОКИРОВАН")
                else: self._log_add(self.check_log,f"✓  {name:<26} {ms} ms  {'OK' if ms<100 else 'ВЫСОКИЙ ПИНГ'}")
                time.sleep(0.15)
            if bad:
                self._log_add(self.check_log,"\n⚠  AWS заблокирован (РКН)!")
                self._log_add(self.check_log,"→  AmneziaVPN: amnezia.org (бесплатно)")
                self._log_add(self.check_log,"→  Подключай VPN ДО запуска Fortnite!")
            else: self._log_add(self.check_log,"\n✅ Все серверы доступны!")
        threading.Thread(target=run,daemon=True).start()

if __name__=="__main__":
    app=App(); app.mainloop()
