from __future__ import annotations
import csv, json, re, threading, tkinter as tk
from tkinter import filedialog, messagebox, ttk
from collections import Counter
from dataclasses import asdict
from pathlib import Path
from logscope import read_log, LEVELS, normalized_message

class App(tk.Tk):
    def __init__(self):
        super().__init__();self.title("LogScope");self.geometry("1100x680");self.minsize(850,520);self.build()
    def build(self):
        top=ttk.Frame(self,padding=12);top.pack(fill="x");ttk.Label(top,text="LogScope",font=("Segoe UI",16,"bold")).pack(anchor="w");ttk.Label(top,text="Search, filter, group and export plain-text logs.").pack(anchor="w",pady=(2,8))
        row=ttk.Frame(top);row.pack(fill="x");self.path=tk.StringVar();ttk.Entry(row,textvariable=self.path).pack(side="left",fill="x",expand=True);ttk.Button(row,text="Open log",command=self.choose).pack(side="left",padx=6)
        ttk.Label(row,text="Level").pack(side="left");self.level=tk.StringVar(value="ALL");ttk.Combobox(row,textvariable=self.level,values=["ALL"]+sorted(LEVELS),state="readonly",width=10).pack(side="left",padx=5)
        ttk.Label(row,text="Contains").pack(side="left");self.contains=tk.StringVar();ttk.Entry(row,textvariable=self.contains,width=20).pack(side="left",padx=5);self.go=ttk.Button(row,text="Filter",command=self.run);self.go.pack(side="left")
        body=ttk.Frame(self,padding=12);body.pack(fill="both",expand=True);self.tree=ttk.Treeview(body,columns=("line","time","level","source","message"),show="headings")
        for c,w in (("line",60),("time",190),("level",90),("source",140),("message",560)):self.tree.heading(c,text=c.title());self.tree.column(c,width=w,anchor="w")
        self.tree.pack(side="left",fill="both",expand=True);sb=ttk.Scrollbar(body,command=self.tree.yview);sb.pack(side="right",fill="y");self.tree.configure(yscrollcommand=sb.set)
        bottom=ttk.Frame(self,padding=12);bottom.pack(fill="x");self.summary=tk.StringVar(value="No log loaded.");ttk.Label(bottom,textvariable=self.summary).pack(side="left");ttk.Button(bottom,text="Export CSV",command=self.csv).pack(side="right");ttk.Button(bottom,text="Export JSON",command=self.json_export).pack(side="right",padx=6)
    def choose(self):
        p=filedialog.askopenfilename(filetypes=[("Logs","*.log *.txt"),("All files","*.*")])
        if p:self.path.set(p);self.run()
    def run(self):
        p=Path(self.path.get())
        if not p.is_file():messagebox.showerror("LogScope","Choose a log file.");return
        self.go.configure(state="disabled");self.summary.set("Reading log...")
        def work():
            try:records=list(read_log(p));err=None
            except Exception as e:records=None;err=str(e)
            self.after(0,lambda:self.finish(records,err))
        threading.Thread(target=work,daemon=True).start()
    def finish(self,records,err):
        self.go.configure(state="normal")
        if err:messagebox.showerror("Read failed",err);return
        level=self.level.get();needle=self.contains.get().lower()
        records=[r for r in records if (level=="ALL" or r.level==level) and (not needle or needle in r.message.lower())]
        for i in self.tree.get_children():self.tree.delete(i)
        for r in records:self.tree.insert("", "end",values=(r.line,r.timestamp,r.level,r.source,r.message))
        self.last=records;counts=Counter(r.level for r in records);self.summary.set(f"{len(records)} records • "+" • ".join(f"{k}={v}" for k,v in counts.most_common()));self.status="Ready"
    def csv(self):
        if not hasattr(self,"last"):return
        p=filedialog.asksaveasfilename(defaultextension=".csv",filetypes=[("CSV","*.csv")])
        if p:
            rows=[asdict(r) for r in self.last]
            with open(p,"w",newline="",encoding="utf-8") as f:w=csv.DictWriter(f,fieldnames=rows[0].keys() if rows else ["line"]);w.writeheader();w.writerows(rows)
    def json_export(self):
        if not hasattr(self,"last"):return
        p=filedialog.asksaveasfilename(defaultextension=".json",filetypes=[("JSON","*.json")])
        if p:Path(p).write_text(json.dumps([asdict(r) for r in self.last],indent=2),encoding="utf-8")

if __name__=="__main__":App().mainloop()
