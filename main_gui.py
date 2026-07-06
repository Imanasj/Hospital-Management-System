import tkinter as tk
from tkinter import ttk, messagebox
import re
from datetime import datetime, date

from database_module import (
    add_patient, get_all_patients, search_patients, health_card_exists,
    add_appointment, get_all_appointments, get_appointments_by_patient,
    update_appointment_status, cancel_appointment, check_double_booking,
    add_medical_record, get_records_by_patient,
    add_to_queue, get_queue, remove_from_queue, get_queue_count
)
from analytics_module import (
    get_daily_patient_count, calculate_avg_wait_time, get_total_appointments_today,
    check_department_overload, get_all_department_loads,
    get_hourly_stats, get_urgency_breakdown
)
from appointment_module import Appointment

# ── DATA ──────────────────────────────────────────────────────────────────────
DEPARTMENTS    = ["Cardiology","Emergency","General Practice","Neurology","Orthopedics","Pediatrics"]
URGENCY_LEVELS = ["Critical","High","Medium","Low"]
DOCTORS = {
    "Cardiology":       ["Dr. Patel","Dr. Chen"],
    "Emergency":        ["Dr. Martinez","Dr. Thompson"],
    "General Practice": ["Dr. Smith","Dr. Lee"],
    "Neurology":        ["Dr. Johnson","Dr. Kim"],
    "Orthopedics":      ["Dr. Williams","Dr. Davis"],
    "Pediatrics":       ["Dr. Wilson","Dr. Garcia"],
}
ALL_DOCTORS = [d for dl in DOCTORS.values() for d in dl]

# ── PALETTE ───────────────────────────────────────────────────────────────────
BG       = "#060910"
SB       = "#0a0e1a"   # sidebar
PANEL    = "#0f1623"
CARD     = "#141c2e"
CARD2    = "#1a2235"
BORDER   = "#1e2d47"
BORDER2  = "#243354"

BLUE  = "#3b82f6"; BLUE2 = "#60a5fa"; BLUE3 = "#1d4ed8"
CYAN  = "#06b6d4"
GREEN = "#10b981"; GREEN2 = "#059669"
AMBER = "#f59e0b"; AMBER2 = "#d97706"
RED   = "#ef4444"; RED2   = "#dc2626"
PURP  = "#8b5cf6"
PINK  = "#ec4899"

TEXT  = "#f1f5f9"; TSUB = "#94a3b8"; TMUT = "#475569"

UC = {"Critical":RED,"High":AMBER,"Medium":BLUE,"Low":GREEN}
DC = {"Cardiology":RED,"Emergency":AMBER,"General Practice":GREEN,
      "Neurology":PURP,"Orthopedics":CYAN,"Pediatrics":PINK}

FT  = ("Segoe UI Semibold",21)
FH2 = ("Segoe UI Semibold",13)
FH3 = ("Segoe UI",11,"bold")
FB  = ("Segoe UI",10)
FS  = ("Segoe UI",9)
FTY = ("Segoe UI",8)
FM  = ("Cascadia Code",9)
FN  = ("Segoe UI Semibold",28)
FNS = ("Segoe UI Semibold",17)

# ── VALIDATORS ────────────────────────────────────────────────────────────────
def vd(s):
    try: datetime.strptime(s,"%Y-%m-%d"); return True
    except: return False
def vt(s):
    try: datetime.strptime(s,"%H:%M"); return True
    except: return False
def ve(s): return bool(re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$',s)) if s else True
def vp(s): return bool(re.match(r'^[\d\s\-\+\(\)]{7,20}$',s)) if s else True

# ── WIDGET HELPERS ────────────────────────────────────────────────────────────
def L(p,text,font=FB,fg=TEXT,bg=None,**kw):
    return tk.Label(p,text=text,font=font,fg=fg,bg=bg or p.cget("bg"),**kw)

def E(p,w=30,**kw):
    e=tk.Entry(p,font=FB,bg=CARD2,fg=TEXT,insertbackground=BLUE2,
               relief="flat",highlightthickness=1,highlightbackground=BORDER2,
               highlightcolor=BLUE,width=w,selectbackground=BLUE3,
               selectforeground=TEXT,**kw)
    e.bind("<FocusIn>", lambda ev:e.config(highlightbackground=BLUE))
    e.bind("<FocusOut>",lambda ev:e.config(highlightbackground=BORDER2))
    return e

def _hl(c):
    m={BLUE:BLUE2,RED:"#f87171",GREEN:"#34d399",AMBER:"#fbbf24",
       PURP:"#a78bfa",CYAN:"#22d3ee",CARD:CARD2,CARD2:BORDER,
       PANEL:CARD,SB:CARD,BORDER:BORDER2}
    return m.get(c,c)

def tint(fg,bg=CARD,alpha=0.2):
    """Blend two #rrggbb colors because Tkinter does not support #rrggbbaa."""
    fg=fg.lstrip("#"); bg=bg.lstrip("#")
    fr,fgreen,fb=[int(fg[i:i+2],16) for i in (0,2,4)]
    br,bg2,bb=[int(bg[i:i+2],16) for i in (0,2,4)]
    return "#{:02x}{:02x}{:02x}".format(
        int(fr*alpha+br*(1-alpha)),
        int(fgreen*alpha+bg2*(1-alpha)),
        int(fb*alpha+bb*(1-alpha)),
    )

def B(p,text,cmd,bg=BLUE,fg="white",px=16,py=7,w=None,**kw):
    b=tk.Button(p,text=text,command=cmd,bg=bg,fg=fg,font=FB,
                relief="flat",cursor="hand2",activebackground=BLUE2,
                activeforeground="white",padx=px,pady=py,bd=0,**kw)
    if w: b.config(width=w)
    b.bind("<Enter>",lambda e:b.config(bg=_hl(bg)))
    b.bind("<Leave>",lambda e:b.config(bg=bg))
    return b

def CB(p,vals,var,w=27):
    s=ttk.Style(); s.theme_use("clam")
    s.configure("H.TCombobox",fieldbackground=CARD2,background=CARD2,
                foreground=TEXT,selectbackground=BLUE3,bordercolor=BORDER2,
                arrowcolor=TSUB,insertcolor=TEXT,lightcolor=CARD2,darkcolor=CARD2)
    s.map("H.TCombobox",fieldbackground=[("readonly",CARD2)],foreground=[("readonly",TEXT)])
    return ttk.Combobox(p,textvariable=var,values=vals,font=FB,
                        width=w,state="readonly",style="H.TCombobox")

def TV(p,cols,h=10,ws=None):
    s=ttk.Style()
    s.configure("H.Treeview",background=CARD,foreground=TEXT,
                fieldbackground=CARD,rowheight=30,font=FB,borderwidth=0,relief="flat")
    s.configure("H.Treeview.Heading",background=PANEL,foreground=TSUB,
                font=("Segoe UI",9,"bold"),relief="flat",borderwidth=0)
    s.map("H.Treeview",background=[("selected",BLUE3)],foreground=[("selected",TEXT)])
    f=tk.Frame(p,bg=CARD,highlightthickness=1,highlightbackground=BORDER)
    t=ttk.Treeview(f,columns=cols,show="headings",height=h,style="H.Treeview")
    sb=ttk.Scrollbar(f,orient="vertical",command=t.yview)
    t.configure(yscrollcommand=sb.set)
    t.pack(side="left",fill="both",expand=True)
    sb.pack(side="right",fill="y")
    for i,c in enumerate(cols):
        ww=ws[i] if ws else 110
        t.heading(c,text=c); t.column(c,width=ww,anchor="w",minwidth=30)
    return f,t

def CF(p,**kw):
    return tk.Frame(p,bg=CARD,highlightthickness=1,highlightbackground=BORDER,**kw)

def scr(p):
    cv=tk.Canvas(p,bg=BG,highlightthickness=0)
    sb=ttk.Scrollbar(p,orient="vertical",command=cv.yview)
    cv.configure(yscrollcommand=sb.set)
    sb.pack(side="right",fill="y"); cv.pack(side="left",fill="both",expand=True)
    inn=tk.Frame(cv,bg=BG)
    wid=cv.create_window((0,0),window=inn,anchor="nw")
    cv.bind("<Configure>",lambda e:cv.itemconfig(wid,width=e.width))
    inn.bind("<Configure>",lambda e:cv.configure(scrollregion=cv.bbox("all")))
    cv.bind_all("<MouseWheel>",lambda e:cv.yview_scroll(int(-1*(e.delta/120)),"units"))
    return inn

def div(p,c=BORDER,py=0):
    tk.Frame(p,bg=c,height=1).pack(fill="x",pady=py)

def donut(cv,cx,cy,r,data,colors,bg=CARD):
    total=sum(data) or 1; start=-90
    for val,color in zip(data,colors):
        ext=360*val/total
        if ext>0:
            cv.create_arc(cx-r,cy-r,cx+r,cy+r,start=start,extent=ext,
                          fill=color,outline=bg,width=2,style="pieslice")
        start+=ext
    cv.create_oval(cx-r*.55,cy-r*.55,cx+r*.55,cy+r*.55,fill=bg,outline=bg)

def sparkline(cv,w,h,vals,color=BLUE):
    if not vals or max(vals)==0: return
    mx=max(vals); mn=min(vals); rng=mx-mn or 1; pad=6
    sx=lambda i: pad+i*(w-2*pad)/(len(vals)-1)
    sy=lambda v: h-pad-(v-mn)/rng*(h-2*pad)
    pts=[(sx(i),sy(v)) for i,v in enumerate(vals)]
    poly=[pad,h]+[c for p in pts for c in p]+[w-pad,h]
    cv.create_polygon(poly,fill=tint(color,BG,0.13),outline="",smooth=True)
    for i in range(len(pts)-1):
        cv.create_line(pts[i][0],pts[i][1],pts[i+1][0],pts[i+1][1],
                       fill=color,width=2,smooth=True)
    cv.create_oval(pts[-1][0]-4,pts[-1][1]-4,pts[-1][0]+4,pts[-1][1]+4,
                   fill=color,outline=BG,width=2)


# ── APP ───────────────────────────────────────────────────────────────────────
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("MediCore HMS")
        self.geometry("1280x800")
        self.minsize(1100,680)
        self.configure(bg=BG)
        self._clk=None
        self._navb={}
        self._shell()
        self._go("dashboard")
        self._tick()

    # ── SHELL ─────────────────────────────────────────────────────────────────
    def _shell(self):
        # ── Top bar
        tb=tk.Frame(self,bg=SB,height=52); tb.pack(fill="x"); tb.pack_propagate(False)

        logo=tk.Frame(tb,bg=SB,width=230); logo.pack(side="left",fill="y"); logo.pack_propagate(False)
        tk.Label(logo,text="  ✚ MediCore",font=("Segoe UI Semibold",14),bg=SB,fg=BLUE2).pack(side="left",pady=14)
        tk.Label(logo,text="HMS",font=("Segoe UI",10),bg=SB,fg=TSUB).pack(side="left")

        # Search
        sf=tk.Frame(tb,bg=CARD2,highlightthickness=1,highlightbackground=BORDER2)
        sf.pack(side="left",padx=16,pady=9,fill="y")
        tk.Label(sf,text="⌕",font=("Segoe UI",12),bg=CARD2,fg=TMUT).pack(side="left",padx=8)
        self._se=tk.Entry(sf,font=FB,bg=CARD2,fg=TMUT,insertbackground=TEXT,
                          relief="flat",width=28)
        self._se.insert(0,"Search patients, appointments…")
        self._se.bind("<FocusIn>",lambda e:(self._se.delete(0,tk.END),self._se.config(fg=TEXT))
                      if self._se.get()=="Search patients, appointments…" else None)
        self._se.pack(side="left",pady=5,padx=(0,10))

        # Right
        rr=tk.Frame(tb,bg=SB); rr.pack(side="right",padx=16,fill="y")
        self._clk=tk.Label(rr,text="",font=FS,bg=SB,fg=TSUB); self._clk.pack(side="right",padx=(12,0))
        uc=tk.Frame(rr,bg=CARD2,highlightthickness=1,highlightbackground=BORDER2)
        uc.pack(side="right",pady=10)
        tk.Label(uc,text=" DR ",font=("Segoe UI Semibold",9),bg=BLUE3,fg=TEXT,pady=5).pack(side="left")
        tk.Label(uc,text=" Dr. Sarah Johnson  ",font=FS,bg=CARD2,fg=TEXT).pack(side="left")

        div(self,BORDER)

        # ── Body
        body=tk.Frame(self,bg=BG); body.pack(fill="both",expand=True)
        self._sb=tk.Frame(body,bg=SB,width=228); self._sb.pack(side="left",fill="y"); self._sb.pack_propagate(False)
        tk.Frame(body,bg=BORDER,width=1).pack(side="left",fill="y")
        self.content=tk.Frame(body,bg=BG); self.content.pack(side="left",fill="both",expand=True)
        self._build_sidebar()

    def _build_sidebar(self):
        tk.Frame(self._sb,bg=SB,height=10).pack()
        L(self._sb,"  NAVIGATION",font=FTY,fg=TMUT,bg=SB).pack(anchor="w",padx=16,pady=(8,4))

        pages = [
            ("dashboard", "", "Dashboard"),
            ("register", "", "Patients"),
            ("appointments", "", "Appointments"),
            ("records", "", "Medical Records"),
            ("queue", "", "Wait Queue"),
            ("analytics", "", "Analytics"),
        ]
        for key,icon,label in pages:
            row=tk.Frame(self._sb,bg=SB,cursor="hand2"); row.pack(fill="x",padx=6,pady=1)
            ind=tk.Frame(row,bg=SB,width=3); ind.pack(side="left",fill="y")
            inn=tk.Frame(row,bg=SB,pady=9); inn.pack(side="left",fill="both",expand=True,padx=4)
            tk.Label(inn,text=icon,font=("Segoe UI",11),bg=SB,fg=TSUB,width=2).pack(side="left")
            tk.Label(inn,text=label,font=("Segoe UI",10),bg=SB,fg=TSUB).pack(side="left",padx=8)
            self._navb[key]=(row,ind,inn)
            for w in [row,ind,inn]+list(inn.winfo_children()):
                try: w.bind("<Button-1>",lambda e,k=key:self._go(k))
                except: pass

        div(self._sb,BORDER,py=10)
        L(self._sb,"  SYSTEM",font=FTY,fg=TMUT,bg=SB).pack(anchor="w",padx=16,pady=(0,4))
        for lab in ["⚙  Settings","?  Help & Support"]:
            r=tk.Frame(self._sb,bg=SB); r.pack(fill="x",padx=10,pady=1)
            tk.Frame(r,bg=SB,width=3).pack(side="left",fill="y")
            tk.Label(r,text=lab,font=("Segoe UI",10),bg=SB,fg=TMUT,padx=12,pady=8).pack(side="left")

        tk.Frame(self._sb,bg=SB).pack(expand=True,fill="both")
        div(self._sb,BORDER)
        bot=tk.Frame(self._sb,bg=SB,pady=10,padx=12); bot.pack(fill="x")
        tk.Label(bot,text=" DR ",font=("Segoe UI Semibold",9),bg=BLUE3,fg=TEXT,pady=5).pack(side="left")
        inf=tk.Frame(bot,bg=SB); inf.pack(side="left",padx=8)
        L(inf,"Dr. Sarah Johnson",font=("Segoe UI",9,"bold"),fg=TEXT,bg=SB).pack(anchor="w")
        L(inf,"Administrator",font=FTY,fg=TSUB,bg=SB).pack(anchor="w")

    def _go(self,key):
        for k,(row,ind,inn) in self._navb.items():
            row.config(bg=SB); ind.config(bg=SB); inn.config(bg=SB)
            for w in inn.winfo_children():
                try: w.config(bg=SB,fg=TSUB)
                except: pass
        if key in self._navb:
            row,ind,inn=self._navb[key]
            row.config(bg=CARD); ind.config(bg=BLUE); inn.config(bg=CARD)
            for w in inn.winfo_children():
                try: w.config(bg=CARD,fg=TEXT)
                except: pass
        self._clear()
        getattr(self,f"_p_{key}")()

    def _clear(self):
        for w in self.content.winfo_children(): w.destroy()

    def _hdr(self,p,title,sub=""):
        h=tk.Frame(p,bg=BG); h.pack(fill="x",padx=32,pady=(22,0))
        L(h,title,font=FT,fg=TEXT).pack(side="left",anchor="s")
        if sub:
            s=tk.Frame(h,bg=BG); s.pack(side="left",anchor="s",padx=(10,0),pady=(0,3))
            L(s,sub,font=FS,fg=TMUT,bg=BG).pack()
        div(p,BORDER,py=(10,0))

    def _tick(self):
        if self._clk:
            self._clk.config(text=datetime.now().strftime("%I:%M %p  |  %a %b %d"))
        self.after(1000,self._tick)

    def toast(self,msg,kind="ok"):
        cmap={"ok":(GREEN,"✓"),"warn":(AMBER,"⚠"),"err":(RED,"✕")}
        color,icon=cmap.get(kind,(BLUE,"●"))
        t=tk.Toplevel(self); t.overrideredirect(True); t.attributes("-topmost",True); t.configure(bg=CARD)
        f=tk.Frame(t,bg=CARD,highlightthickness=1,highlightbackground=color); f.pack()
        tk.Frame(f,bg=color,width=4).pack(side="left",fill="y")
        tk.Label(f,text=icon,font=("Segoe UI",12),bg=CARD,fg=color,padx=10,pady=12).pack(side="left")
        tk.Label(f,text=msg,font=FB,bg=CARD,fg=TEXT,padx=4,pady=12).pack(side="left")
        tk.Label(f,text="  ",bg=CARD).pack(side="left")
        self.update_idletasks()
        t.geometry(f"+{self.winfo_x()+self.winfo_width()-340}+{self.winfo_y()+self.winfo_height()-80}")
        t.after(3500,t.destroy)

    def _stat(self,p,label,val,color,sub="",icon=""):
        f=CF(p,padx=20,pady=16)
        top=tk.Frame(f,bg=CARD); top.pack(fill="x")
        L(top,label,font=FS,fg=TSUB,bg=CARD).pack(side="left")
        if icon: tk.Label(top,text=icon,font=("Segoe UI",14),bg=CARD,fg=color).pack(side="right")
        L(f,str(val),font=FN,fg=color,bg=CARD).pack(anchor="w",pady=(4,0))
        if sub: L(f,sub,font=FTY,fg=TMUT,bg=CARD).pack(anchor="w")
        tk.Frame(f,bg=color,height=2).pack(fill="x",pady=(10,0))
        return f

    def _frow(self,p,label,widget,row):
        L(p,label,font=FS,fg=TSUB,bg=CARD).grid(row=row,column=0,sticky="w",padx=(0,16),pady=6)
        widget.grid(row=row,column=1,sticky="w",pady=6)

    # ─────────────────────────────────────────────────────────────────────────
    # DASHBOARD
    # ─────────────────────────────────────────────────────────────────────────
    def _p_dashboard(self):
        inn=scr(self.content)
        self._hdr(inn,f"Welcome back, Dr. Johnson!",
                  f"Here's what's happening at your hospital — {date.today().strftime('%A, %B %d, %Y')}")

        # Stat cards
        r1=tk.Frame(inn,bg=BG); r1.pack(fill="x",padx=32,pady=18)
        for lbl2,val,color,sub,icon in [
            ("Total Patients",      get_daily_patient_count(),      BLUE, "Registered today","👥"),
            ("Appointments Today",  get_total_appointments_today(), CYAN, "Scheduled",       "📅"),
            ("In Queue",            get_queue_count(),              AMBER,"Waiting now",     "⏳"),
            ("Avg Wait Time",       f"{calculate_avg_wait_time()}m",GREEN,"Minutes average", "⏱"),
        ]:
            self._stat(r1,lbl2,val,color,sub,icon).pack(side="left",fill="both",expand=True,padx=(0,12))

        # Charts
        cr=tk.Frame(inn,bg=BG); cr.pack(fill="x",padx=32,pady=(0,16))

        # Sparkline
        lc=CF(cr,padx=20,pady=18); lc.pack(side="left",fill="both",expand=True,padx=(0,12))
        L(lc,"Patient Flow",font=FH2,fg=TEXT,bg=CARD).pack(anchor="w")
        L(lc,"Hourly registrations today",font=FS,fg=TMUT,bg=CARD).pack(anchor="w",pady=(2,10))
        hourly=get_hourly_stats(); hours=list(range(7,20)); counts=[hourly.get(h,0) for h in hours]
        cw,ch=460,150
        cv=tk.Canvas(lc,width=cw,height=ch+28,bg=CARD,highlightthickness=0); cv.pack()
        for i in range(5):
            y=ch-i*ch//4; cv.create_line(0,y,cw,y,fill=BORDER,width=1)
        sparkline(cv,cw,ch,counts,BLUE)
        for i,hr in enumerate(hours[::2]):
            x=6+(i*2)*(cw-12)/(len(hours)-1)
            cv.create_text(x,ch+14,text=f"{hr}:00",fill=TMUT,font=("Segoe UI",7))
        if any(counts):
            ph=hours[counts.index(max(counts))]
            L(lc,f"🔺 Peak: {ph}:00 — {max(counts)} patients",font=FTY,fg=BLUE2,bg=CARD).pack(anchor="w",pady=(6,0))

        # Donut
        rc=CF(cr,padx=18,pady=18,width=270); rc.pack(side="left",fill="y"); rc.pack_propagate(False)
        L(rc,"Department Distribution",font=FH2,fg=TEXT,bg=CARD).pack(anchor="w")
        L(rc,"Queue load by department",font=FS,fg=TMUT,bg=CARD).pack(anchor="w",pady=(2,8))
        dl=get_all_department_loads()
        dv=[dl.get(d,0) for d in DEPARTMENTS]; dc_=[DC[d] for d in DEPARTMENTS]
        dcv=tk.Canvas(rc,width=190,height=190,bg=CARD,highlightthickness=0); dcv.pack()
        donut(dcv,95,95,76,dv or [1]*6,dc_ if any(dv) else [BORDER]*6,bg=CARD)
        for dept,color in zip(DEPARTMENTS,dc_):
            pct=int(dl.get(dept,0)/max(sum(dv),1)*100)
            rr=tk.Frame(rc,bg=CARD); rr.pack(fill="x",pady=1)
            tk.Label(rr,text="●",fg=color,bg=CARD,font=("Segoe UI",10)).pack(side="left")
            L(rr,dept[:13],font=FTY,fg=TSUB,bg=CARD).pack(side="left",padx=4)
            L(rr,f"{pct}%",font=("Segoe UI Semibold",9),fg=TEXT,bg=CARD).pack(side="right")

        # Queue preview
        L(inn,"Live Queue — Top Priority Patients",font=FH2,fg=TEXT,bg=BG).pack(anchor="w",padx=32,pady=(6,8))
        qrows=get_queue()[:5]
        if qrows:
            qf=tk.Frame(inn,bg=BG); qf.pack(fill="x",padx=32)
            hf=tk.Frame(qf,bg=PANEL,padx=14,pady=6); hf.pack(fill="x",pady=(0,3))
            for txt,w2 in [("#",3),("Patient",20),("Department",18),("Urgency",10),("Wait",10),("Time",14)]:
                L(hf,txt,font=("Segoe UI",8,"bold"),fg=TMUT,bg=PANEL,width=w2,anchor="w").pack(side="left")
            for i,q in enumerate(qrows):
                qid,name,pid,dept,urg,checkin,wait=q; color=UC.get(urg,BLUE)
                rf=CF(qf); rf.pack(fill="x",pady=2)
                tk.Frame(rf,bg=color,width=3).pack(side="left",fill="y")
                ir=tk.Frame(rf,bg=CARD,padx=12,pady=10); ir.pack(side="left",fill="both",expand=True)
                L(ir,str(i+1),font=("Segoe UI Semibold",10),fg=color,bg=CARD,width=3).pack(side="left")
                L(ir,name,font=("Segoe UI",10,"bold"),fg=TEXT,bg=CARD,width=20).pack(side="left")
                L(ir,dept,font=FB,fg=TSUB,bg=CARD,width=18).pack(side="left")
                tk.Label(ir,text=f"  {urg}  ",bg=tint(color,CARD,0.2),fg=color,font=("Segoe UI Semibold",8),padx=4,pady=2).pack(side="left",padx=(0,12))
                L(ir,f"~{wait} min",font=("Segoe UI Semibold",10),fg=color,bg=CARD,width=10).pack(side="left")
                L(ir,str(checkin)[11:16] if checkin else "—",font=FS,fg=TMUT,bg=CARD).pack(side="left")
        else:
            ef=CF(inn,pady=24); ef.pack(fill="x",padx=32)
            L(ef,"  Queue is empty.",font=FH2,fg=GREEN,bg=CARD).pack()

        # Overload alerts
        alerts=[(d,n) for d,n in get_all_department_loads().items() if n>=10]
        if alerts:
            L(inn,"⚠  Overload Alerts",font=FH2,fg=RED,bg=BG).pack(anchor="w",padx=32,pady=(14,6))
            for dept,count in alerts:
                alert_bg=tint(RED,BG,0.13)
                af=tk.Frame(inn,bg=alert_bg,highlightthickness=1,highlightbackground=RED,padx=16,pady=10)
                af.pack(fill="x",padx=32,pady=3)
                L(af,f"🚨  {dept}",font=FH3,fg=RED,bg=alert_bg).pack(side="left")
                L(af,f"{count} patients — OVERLOADED",fg=RED,bg=alert_bg).pack(side="right")

        B(inn,"↺  Refresh",self._p_dashboard,bg=CARD,px=16,py=8).pack(anchor="w",padx=32,pady=16)

    # ─────────────────────────────────────────────────────────────────────────
    # REGISTER PATIENT
    # ─────────────────────────────────────────────────────────────────────────
    def _p_register(self):
        inn=scr(self.content)
        self._hdr(inn,"Patient Registration","Add new patients to the system")
        body=tk.Frame(inn,bg=BG); body.pack(fill="both",padx=32,pady=18,expand=True)

        fc=CF(body,padx=26,pady=22); fc.pack(side="left",fill="y",padx=(0,14))
        L(fc,"New Patient",font=FH2,bg=CARD).grid(row=0,column=0,columnspan=2,sticky="w",pady=(0,14))
        ents={}
        for i,(lab,key) in enumerate([
            ("Full Name *","name"),("Date of Birth (YYYY-MM-DD) *","dob"),
            ("Health Card Number *","hc"),("Phone Number","phone"),
            ("Email Address","email"),("Emergency Contact","emerg")
        ],start=1):
            e=E(fc,w=32); self._frow(fc,lab,e,i); ents[key]=e

        err=L(fc,"",fg=RED,bg=CARD,wraplength=340); err.grid(row=8,column=0,columnspan=2,sticky="w",pady=4)

        def save():
            err.config(text="")
            n,d,h=ents["name"].get().strip(),ents["dob"].get().strip(),ents["hc"].get().strip()
            ph,em,eg=ents["phone"].get().strip(),ents["email"].get().strip(),ents["emerg"].get().strip()
            if not n: err.config(text="Full name is required."); return
            if not vd(d): err.config(text="Date must be YYYY-MM-DD"); return
            if not h: err.config(text="Health card is required."); return
            if not ve(em): err.config(text="Invalid email address."); return
            if not vp(ph): err.config(text="Invalid phone number."); return
            if health_card_exists(h): err.config(text="Health card already registered."); return
            try:
                pid=add_patient(n,d,h,ph,em,eg)
                for e2 in ents.values(): e2.delete(0,tk.END)
                self.toast(f"Patient registered — ID: {pid}"); reload()
            except Exception as ex: err.config(text=str(ex))

        bf=tk.Frame(fc,bg=CARD); bf.grid(row=9,column=0,columnspan=2,sticky="w",pady=(10,0))
        B(bf,"Save Patient",save,bg=GREEN,px=14,py=7).pack(side="left",padx=(0,8))
        B(bf,"Clear",lambda:[e2.delete(0,tk.END) for e2 in ents.values()],bg=CARD,px=14,py=7).pack(side="left")

        lc=CF(body,padx=14,pady=16); lc.pack(side="left",fill="both",expand=True)
        tr=tk.Frame(lc,bg=CARD); tr.pack(fill="x",pady=(0,10))
        L(tr,"All Patients",font=FH2,bg=CARD).pack(side="left")
        sf2=tk.Frame(tr,bg=CARD2,highlightthickness=1,highlightbackground=BORDER2); sf2.pack(side="right")
        tk.Label(sf2,text="⌕",bg=CARD2,fg=TMUT,font=("Segoe UI",11)).pack(side="left",padx=6)
        se=E(sf2,w=20); se.pack(side="left",pady=4,padx=(0,8))
        tf,tree=TV(lc,("ID","Name","DOB","Health Card","Phone","Email"),h=14,ws=[45,155,92,118,108,155])
        tf.pack(fill="both",expand=True)
        def reload(data=None):
            tree.delete(*tree.get_children())
            for p in (data or get_all_patients()): tree.insert("","end",values=(p[0],p[1],p[2],p[3],p[4],p[5]))
        se.bind("<KeyRelease>",lambda e:reload(search_patients(se.get()) if se.get() else None))
        reload()

    # ─────────────────────────────────────────────────────────────────────────
    # APPOINTMENTS
    # ─────────────────────────────────────────────────────────────────────────
    def _p_appointments(self):
        inn=scr(self.content)
        self._hdr(inn,"Appointment Scheduler","Book & manage with double-booking prevention")
        body=tk.Frame(inn,bg=BG); body.pack(fill="both",padx=32,pady=18,expand=True)

        fc=CF(body,padx=26,pady=22); fc.pack(side="left",fill="y",padx=(0,14))
        L(fc,"New Appointment",font=FH2,bg=CARD).grid(row=0,column=0,columnspan=2,sticky="w",pady=(0,12))
        ents={}; dv=tk.StringVar(value=DEPARTMENTS[0]); drv=tk.StringVar(); uv=tk.StringVar(value="Medium")

        pe=E(fc,w=30); self._frow(fc,"Patient ID *",pe,1); ents["pid"]=pe
        dcb=CB(fc,DEPARTMENTS,dv,w=28); self._frow(fc,"Department *",dcb,2)
        drcb=CB(fc,DOCTORS[DEPARTMENTS[0]],drv,w=28); self._frow(fc,"Doctor *",drcb,3)
        def upd(*_):
            docs=DOCTORS.get(dv.get(),ALL_DOCTORS); drv.set(docs[0]); drcb["values"]=docs
        dv.trace("w",upd); upd()
        de=E(fc,w=30); de.insert(0,date.today().strftime("%Y-%m-%d")); self._frow(fc,"Date (YYYY-MM-DD) *",de,4); ents["date"]=de
        te=E(fc,w=30); te.insert(0,"09:00"); self._frow(fc,"Time (HH:MM) *",te,5); ents["time"]=te
        self._frow(fc,"Urgency",CB(fc,URGENCY_LEVELS,uv,w=28),6)
        re2=E(fc,w=30); self._frow(fc,"Reason",re2,7); ents["reason"]=re2
        err=L(fc,"",fg=RED,bg=CARD,wraplength=300); err.grid(row=9,column=0,columnspan=2,sticky="w",pady=4)

        def book():
            err.config(text="")
            try: pid=int(ents["pid"].get().strip())
            except: err.config(text="Patient ID must be a number."); return
            d2,t2=ents["date"].get().strip(),ents["time"].get().strip()
            if not vd(d2): err.config(text="Date must be YYYY-MM-DD"); return
            if not vt(t2): err.config(text="Time must be HH:MM"); return
            try:
                add_appointment(pid,drv.get(),d2,t2,dv.get(),ents["reason"].get().strip(),uv.get())
                wait=Appointment(pid,drv.get(),d2,t2,dv.get(),uv.get()).calculateWaitTime(get_queue_count()+1)
                add_to_queue(pid,dv.get(),uv.get(),wait)
                self.toast(f"Booked! Est. wait: ~{wait} min")
                ents["pid"].delete(0,tk.END); ents["reason"].delete(0,tk.END); reload()
            except ValueError as ve2: err.config(text=str(ve2))
            except Exception as ex: err.config(text=str(ex))

        B(fc,"Book Appointment",book,bg=BLUE,px=14,py=8).grid(row=8,column=0,columnspan=2,sticky="w",pady=(10,0))

        lc=CF(body,padx=14,pady=16); lc.pack(side="left",fill="both",expand=True)
        L(lc,"All Appointments",font=FH2,bg=CARD).pack(anchor="w",pady=(0,10))
        tf,tree=TV(lc,("ID","Patient","Doctor","Date","Time","Dept","Urgency","Status"),h=16,ws=[38,125,108,86,60,115,70,82])
        tf.pack(fill="both",expand=True)
        for urg,color in UC.items(): tree.tag_configure(urg,foreground=color)
        tree.tag_configure("Cancelled",foreground=TMUT); tree.tag_configure("Completed",foreground=GREEN)

        def reload():
            tree.delete(*tree.get_children())
            for a in get_all_appointments():
                tag="Cancelled" if a[7]=="Cancelled" else "Completed" if a[7]=="Completed" else (a[6] if a[6] in URGENCY_LEVELS else "")
                tree.insert("","end",values=(a[0],a[1],a[2],a[3],a[4],a[5],a[6],a[7]),tags=(tag,))

        br=tk.Frame(lc,bg=CARD); br.pack(fill="x",pady=(8,0))
        def done():
            s=tree.selection()
            if not s: self.toast("Select an appointment first.","warn"); return
            update_appointment_status(tree.item(s[0])["values"][0],"Completed"); self.toast("Marked complete."); reload()
        def cancel():
            s=tree.selection()
            if not s: self.toast("Select an appointment first.","warn"); return
            if messagebox.askyesno("Confirm","Cancel this appointment?"):
                cancel_appointment(tree.item(s[0])["values"][0]); self.toast("Cancelled.","warn"); reload()
        B(br,"✓  Complete",done,bg=GREEN,px=12,py=5).pack(side="left",padx=(0,8))
        B(br,"✕  Cancel",cancel,bg=RED,px=12,py=5).pack(side="left",padx=(0,8))
        B(br,"↺  Refresh",reload,bg=CARD,px=12,py=5).pack(side="left")
        reload()

    # ─────────────────────────────────────────────────────────────────────────
    # MEDICAL RECORDS
    # ─────────────────────────────────────────────────────────────────────────
    def _p_records(self):
        inn=scr(self.content)
        self._hdr(inn,"Medical Records","View and manage patient medical history")
        body=tk.Frame(inn,bg=BG); body.pack(fill="both",padx=32,pady=18,expand=True)

        fc=CF(body,padx=26,pady=22); fc.pack(side="left",fill="y",padx=(0,14))
        L(fc,"Add Medical Record",font=FH2,bg=CARD).grid(row=0,column=0,columnspan=2,sticky="w",pady=(0,12))
        rec={}
        for i,(lab,key) in enumerate([("Patient ID *","pid"),("Diagnosis *","diag"),("Medications","meds"),("Test Results","tests")],start=1):
            e=E(fc,w=32); self._frow(fc,lab,e,i); rec[key]=e
        L(fc,"Doctor Notes",font=FS,fg=TSUB,bg=CARD).grid(row=5,column=0,sticky="nw",padx=(0,16),pady=6)
        notes=tk.Text(fc,font=FB,bg=CARD2,fg=TEXT,insertbackground=BLUE2,relief="flat",
                      highlightthickness=1,highlightbackground=BORDER2,highlightcolor=BLUE,width=32,height=5,selectbackground=BLUE3)
        notes.grid(row=5,column=1,pady=6)
        err=L(fc,"",fg=RED,bg=CARD,wraplength=300); err.grid(row=7,column=0,columnspan=2,sticky="w",pady=4)

        def save():
            err.config(text="")
            try: pid=int(rec["pid"].get().strip())
            except: err.config(text="Patient ID must be a number."); return
            diag=rec["diag"].get().strip()
            if not diag: err.config(text="Diagnosis is required."); return
            try:
                add_medical_record(pid,diag,rec["meds"].get().strip(),rec["tests"].get().strip(),notes.get("1.0",tk.END).strip())
                for e2 in rec.values(): e2.delete(0,tk.END)
                notes.delete("1.0",tk.END); self.toast("Record saved!")
            except Exception as ex: err.config(text=str(ex))

        B(fc,"Save Record",save,bg=GREEN,px=14,py=7).grid(row=6,column=0,columnspan=2,sticky="w",pady=(10,0))

        vc=CF(body,padx=16,pady=18); vc.pack(side="left",fill="both",expand=True)
        L(vc,"Patient Record Lookup",font=FH2,bg=CARD).pack(anchor="w",pady=(0,10))
        sr=tk.Frame(vc,bg=CARD); sr.pack(fill="x",pady=(0,10))
        L(sr,"Patient ID:",font=FS,fg=TSUB,bg=CARD).pack(side="left",padx=(0,8))
        pe=E(sr,w=10); pe.pack(side="left",padx=(0,8))
        disp=tk.Text(vc,font=FM,bg=BG,fg=TEXT,relief="flat",padx=14,pady=12,height=22,
                     highlightthickness=1,highlightbackground=BORDER,selectbackground=BLUE3,
                     state="disabled",spacing1=2,spacing3=2)
        disp.pack(fill="both",expand=True)
        disp.tag_configure("hd",foreground=BLUE2,font=("Segoe UI Semibold",9))
        disp.tag_configure("vl",foreground=TEXT)
        disp.tag_configure("dv",foreground=TMUT)

        def load():
            try: pid=int(pe.get().strip())
            except: self.toast("Enter a valid Patient ID.","err"); return
            recs=get_records_by_patient(pid)
            disp.config(state="normal"); disp.delete("1.0",tk.END)
            if not recs: disp.insert(tk.END,"  No records found.\n")
            else:
                for r in recs:
                    disp.insert(tk.END,f"{'─'*52}\n","dv")
                    for lab,val in [("  Visit Date:   ",r[1]),("  Diagnosis:    ",r[2]),
                                    ("  Medications:  ",r[3]),("  Test Results: ",r[4]),("  Doctor Notes: ",r[5])]:
                        disp.insert(tk.END,lab,"hd"); disp.insert(tk.END,f"{val}\n","vl")
                disp.insert(tk.END,f"{'─'*52}\n","dv")
            disp.config(state="disabled")

        B(sr,"Load Records",load,bg=BLUE,px=12,py=6).pack(side="left")

    # ─────────────────────────────────────────────────────────────────────────
    # WAIT QUEUE
    # ─────────────────────────────────────────────────────────────────────────
    def _p_queue(self):
        inn=scr(self.content)
        self._hdr(inn,"Live Wait Queue","Sorted by urgency: Critical → High → Medium → Low")

        # Urgency summary strip
        strip=tk.Frame(inn,bg=BG); strip.pack(fill="x",padx=32,pady=(16,0))
        bd=get_urgency_breakdown()
        for urg in URGENCY_LEVELS:
            color=UC[urg]
            sf=CF(strip,padx=14,pady=10); sf.pack(side="left",padx=(0,10))
            tk.Label(sf,text="●",fg=color,bg=CARD,font=("Segoe UI",16)).pack(side="left")
            inf=tk.Frame(sf,bg=CARD); inf.pack(side="left",padx=8)
            L(inf,str(bd.get(urg,0)),font=FNS,fg=color,bg=CARD).pack(anchor="w")
            L(inf,urg,font=FTY,fg=TMUT,bg=CARD).pack(anchor="w")

        qf=tk.Frame(inn,bg=BG); qf.pack(fill="both",padx=32,pady=16,expand=True)

        def load_q():
            for w in qf.winfo_children(): w.destroy()
            rows=get_queue()
            if not rows:
                ef=CF(qf,padx=40,pady=40); ef.pack(fill="x")
                L(ef,"✓  Queue is empty — all patients have been seen",font=FH2,fg=GREEN,bg=CARD).pack()
                return
            hf=tk.Frame(qf,bg=PANEL,padx=12,pady=6); hf.pack(fill="x",pady=(0,4))
            for txt,w2 in [("POS",4),("PATIENT",18),("DEPARTMENT",16),("URGENCY",10),("CHECK-IN",13),("EST. WAIT",10),("",8)]:
                L(hf,txt,font=("Segoe UI",8,"bold"),fg=TMUT,bg=PANEL,width=w2,anchor="w").pack(side="left")
            for i,q in enumerate(rows,1):
                qid,name,pid,dept,urg,checkin,wait=q; color=UC.get(urg,BLUE)
                rf=CF(qf); rf.pack(fill="x",pady=2)
                tk.Frame(rf,bg=color,width=4).pack(side="left",fill="y")
                ir=tk.Frame(rf,bg=CARD,padx=12,pady=10); ir.pack(side="left",fill="both",expand=True)
                # Position badge
                badge_bg=tint(color,CARD,0.13)
                pf=tk.Frame(ir,bg=badge_bg,width=32,height=32); pf.pack(side="left",padx=(0,12)); pf.pack_propagate(False)
                tk.Label(pf,text=str(i),font=("Segoe UI Semibold",11),fg=color,bg=badge_bg).place(relx=.5,rely=.5,anchor="center")
                nb=tk.Frame(ir,bg=CARD,width=155); nb.pack(side="left"); nb.pack_propagate(False)
                L(nb,name,font=("Segoe UI",10,"bold"),fg=TEXT,bg=CARD).pack(anchor="w")
                L(nb,f"ID: {pid}",font=FTY,fg=TMUT,bg=CARD).pack(anchor="w")
                L(ir,dept,font=FB,fg=TSUB,bg=CARD,width=16).pack(side="left",padx=(8,0))
                tk.Label(ir,text=f"  {urg}  ",bg=badge_bg,fg=color,font=("Segoe UI Semibold",8),padx=4,pady=3).pack(side="left",padx=10)
                L(ir,str(checkin)[11:16] if checkin else "—",font=FS,fg=TSUB,bg=CARD,width=12).pack(side="left")
                L(ir,f"~{wait} min",font=("Segoe UI Semibold",10),fg=color,bg=CARD,width=10).pack(side="left")
                def dis(qid=qid):
                    remove_from_queue(qid); self.toast("Patient discharged.","warn"); load_q()
                B(rf,"Discharge",dis,bg=tint(RED,CARD,0.2),fg=RED,px=12,py=8).pack(side="right",padx=12)

        load_q()
        div(inn,BORDER,py=4)
        B(inn,"↺  Refresh Queue",load_q,bg=CARD,px=16,py=8).pack(anchor="w",padx=32,pady=8)

    # ─────────────────────────────────────────────────────────────────────────
    # ANALYTICS
    # ─────────────────────────────────────────────────────────────────────────
    def _p_analytics(self):
        inn=scr(self.content)
        self._hdr(inn,"Analytics Dashboard",f"Operational insights — {date.today().strftime('%B %d, %Y')}")

        r1=tk.Frame(inn,bg=BG); r1.pack(fill="x",padx=32,pady=18)
        for lbl2,val,color,sub,icon in [
            ("Patients Today",     get_daily_patient_count(),      BLUE, "Registered",    "👥"),
            ("Appointments Today", get_total_appointments_today(), CYAN, "Scheduled",     "📅"),
            ("In Queue Now",       get_queue_count(),              AMBER,"Waiting",       "⏳"),
            ("Avg Wait",           f"{calculate_avg_wait_time()}m",GREEN,"Minutes avg",  "⏱"),
        ]:
            self._stat(r1,lbl2,val,color,sub,icon).pack(side="left",fill="both",expand=True,padx=(0,12))

        cr=tk.Frame(inn,bg=BG); cr.pack(fill="x",padx=32,pady=(0,14))

        # Bar chart
        bc=CF(cr,padx=18,pady=16); bc.pack(side="left",fill="both",expand=True,padx=(0,12))
        L(bc,"Hourly Patient Arrivals",font=FH2,fg=TEXT,bg=CARD).pack(anchor="w")
        L(bc,"Registrations by hour today",font=FS,fg=TMUT,bg=CARD).pack(anchor="w",pady=(2,10))
        hourly=get_hourly_stats(); hours=list(range(7,20)); counts=[hourly.get(h,0) for h in hours]; mx=max(counts) if any(counts) else 1
        cw2,ch2=460,170
        cv2=tk.Canvas(bc,width=cw2,height=ch2+34,bg=CARD,highlightthickness=0); cv2.pack()
        bw2=26; gap2=(cw2-40-len(hours)*bw2)//len(hours); pad2=20
        for i in range(5):
            y=ch2-i*ch2//4; cv2.create_line(pad2,y,cw2-pad2,y,fill=BORDER,width=1,dash=(4,4))
            if i>0: cv2.create_text(pad2-4,y,text=str(int(mx*i//4)),fill=TMUT,font=("Segoe UI",7),anchor="e")
        for i,(hr,cnt) in enumerate(zip(hours,counts)):
            x1=pad2+i*(bw2+gap2); bh=int((cnt/mx)*ch2) if mx else 0; y1,y2=ch2-bh,ch2
            is_peak=cnt==mx and cnt>0; color=RED if is_peak else BLUE
            cv2.create_rectangle(x1,y1,x1+bw2,y2,fill=tint(color,CARD,0.33),outline="")
            if bh>4: cv2.create_rectangle(x1,y1,x1+bw2,y1+4,fill=color,outline="")
            cv2.create_text(x1+bw2//2,ch2+14,text=str(hr),fill=TMUT,font=("Segoe UI",7))
            if cnt>0: cv2.create_text(x1+bw2//2,y1-8,text=str(cnt),fill=color,font=("Segoe UI Semibold",8))
        if any(counts):
            ph=hours[counts.index(max(counts))]
            L(bc,f"🔴  Peak Hour: {ph}:00 — {max(counts)} registrations",font=FTY,fg=RED,bg=CARD).pack(anchor="w",pady=(6,0))

        # Urgency donut
        uc=CF(cr,padx=18,pady=16,width=255); uc.pack(side="left",fill="y"); uc.pack_propagate(False)
        L(uc,"Urgency Breakdown",font=FH2,fg=TEXT,bg=CARD).pack(anchor="w")
        L(uc,"Current queue",font=FS,fg=TMUT,bg=CARD).pack(anchor="w",pady=(2,8))
        bd2=get_urgency_breakdown(); uvals=[bd2.get(u,0) for u in URGENCY_LEVELS]; ucols=[UC[u] for u in URGENCY_LEVELS]
        dc2=tk.Canvas(uc,width=175,height=175,bg=CARD,highlightthickness=0); dc2.pack()
        donut(dc2,87,87,70,uvals or [1]*4,ucols if any(uvals) else [BORDER]*4,bg=CARD)
        for urg,color in zip(URGENCY_LEVELS,ucols):
            rr=tk.Frame(uc,bg=CARD); rr.pack(fill="x",pady=2)
            tk.Label(rr,text="●",fg=color,bg=CARD).pack(side="left")
            L(rr,urg,font=FS,fg=TSUB,bg=CARD).pack(side="left",padx=4)
            L(rr,str(bd2.get(urg,0)),font=("Segoe UI Semibold",9),fg=TEXT,bg=CARD).pack(side="right")

        # Department capacity bars
        L(inn,"Department Capacity Status",font=FH2,fg=TEXT,bg=BG).pack(anchor="w",padx=32,pady=(6,8))
        dl=get_all_department_loads()
        for dept in DEPARTMENTS:
            count=dl.get(dept,0); is_over,_=check_department_overload(dept)
            pct=min(int(count/10*100),100); color=RED if is_over else AMBER if pct>=60 else GREEN; dc_=DC[dept]
            df=CF(inn,padx=16,pady=12); df.pack(fill="x",padx=32,pady=3)
            top=tk.Frame(df,bg=CARD); top.pack(fill="x")
            tk.Label(top,text="●",fg=dc_,bg=CARD,font=("Segoe UI",12)).pack(side="left")
            L(top,dept,font=FH3,fg=TEXT,bg=CARD).pack(side="left",padx=6)
            L(top,f"{count} / 10 patients",font=FS,fg=TSUB,bg=CARD).pack(side="left",padx=8)
            if is_over:
                tk.Label(top,text=" ⚠ OVERLOADED ",bg=tint(RED,CARD,0.2),fg=RED,font=("Segoe UI Semibold",8),padx=6,pady=2).pack(side="right")
            pb=tk.Frame(df,bg=BORDER,height=6); pb.pack(fill="x",pady=(8,0))
            def fill_bar(pb=pb,c=color,p=pct):
                pb.update_idletasks()
                if p>0: tk.Frame(pb,bg=c,height=6).place(x=0,y=0,relheight=1,relwidth=p/100)
            df.after(60,fill_bar)

        B(inn,"↺  Refresh Analytics",self._p_analytics,bg=CARD,px=16,py=8).pack(anchor="w",padx=32,pady=18)


if __name__=="__main__":
    app=App(); app.mainloop()
