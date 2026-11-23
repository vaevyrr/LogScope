#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, json, re
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path

LEVELS={"TRACE","DEBUG","INFO","NOTICE","WARN","WARNING","ERROR","CRITICAL","FATAL"}
LINE_RE=re.compile(r"^(?:(?P<timestamp>\d{4}-\d{2}-\d{2}[T ][0-9:.+\-Z]+)\s+)?(?:(?:\[(?P<bracket>[A-Za-z]+)\])|(?P<level>[A-Za-z]+))(?:\s+\[(?P<source>[^\]]+)\])?\s*[:|-]?\s*(?P<message>.*)$")

@dataclass
class Record:
    line:int
    timestamp:str
    level:str
    source:str
    message:str

def parse_line(number,line):
    m=LINE_RE.match(line.strip())
    if not m:
        return Record(number,"","UNKNOWN","",line.strip())
    raw=(m.group("bracket") or m.group("level") or "UNKNOWN").upper()
    level=raw if raw in LEVELS else "UNKNOWN"
    return Record(number,m.group("timestamp") or "",level,m.group("source") or "",m.group("message").strip())

def read_log(path):
    with path.open("r",encoding="utf-8",errors="replace") as f:
        for n,line in enumerate(f,1):
            if line.strip():
                yield parse_line(n,line)

def normalized_message(message):
    return re.sub(r"\b\d+(?:\.\d+)?\b","<n>",message).lower().strip()

def main():
    p=argparse.ArgumentParser(description="Explore a plain-text log without modifying it.")
    p.add_argument("log",type=Path)
    p.add_argument("--level",choices=sorted(LEVELS),type=str.upper)
    p.add_argument("--contains")
    p.add_argument("--source")
    p.add_argument("--limit",type=int,default=100)
    p.add_argument("--group",action="store_true")
    p.add_argument("--json",dest="json_path",type=Path)
    p.add_argument("--csv",dest="csv_path",type=Path)
    a=p.parse_args()
    if a.limit<1: p.error("--limit must be at least 1")
    try: records=list(read_log(a.log))
    except OSError as e: p.exit(2,f"logscope: {e}\n")
    records=[r for r in records if (not a.level or r.level==a.level) and
             (not a.contains or a.contains.lower() in r.message.lower()) and
             (not a.source or r.source.lower()==a.source.lower())]
    print(f"Records: {len(records)}")
    counts=Counter(r.level for r in records)
    print("Levels: "+(", ".join(f"{k}={v}" for k,v in counts.most_common()) or "none"))
    print("\nTimeline:")
    for r in records[:a.limit]:
        stamp=f"{r.timestamp} " if r.timestamp else ""
        source=f" [{r.source}]" if r.source else ""
        print(f"{r.line:>6} {stamp}{r.level:<8}{source} {r.message}")
    if a.group:
        print("\nRepeated messages:")
        for msg,count in Counter(normalized_message(r.message) for r in records).most_common(10):
            if count>1: print(f"  {count:>4}x {msg}")
    payload=[asdict(r) for r in records]
    if a.json_path: a.json_path.write_text(json.dumps(payload,indent=2),encoding="utf-8")
    if a.csv_path:
        with a.csv_path.open("w",newline="",encoding="utf-8") as f:
            w=csv.DictWriter(f,fieldnames=Record.__dataclass_fields__.keys()); w.writeheader(); w.writerows(payload)

if __name__=="__main__":
    main()
