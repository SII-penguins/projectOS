#!/usr/bin/env python3
"""Read-only lifecycle audit for a ProjectOS-managed project."""
from __future__ import annotations
import argparse, datetime as dt, json, re, sys
from pathlib import Path

ACTIVE={"pending","ready","in progress","in-progress","blocked","review"}
TERMINAL={"done","completed","cancelled","canceled","superseded","rejected"}
TASK_RE=re.compile(r"(?<![\w-])([\w]+(?:-[\w]+)+)(?![\w-])")
DATE_RE=re.compile(r"\b(20\d{2}-\d{2}-\d{2})\b")
META=("Status","Canonical For","Last Reconciled","Freshness Rule","Archive Rule")
SEV={"INFO":0,"WARN":1,"ERROR":2}
DEFAULTS={"progress":"PROGRESS.md","todo":"TODO.md","plan":"doc/IMPLEMENTATION_PLAN.md","run":"doc/RUN_REGISTRY.md","prd":"doc/PRD.md","frontend":"doc/FRONTEND_GUIDELINES.md","backend":"doc/BACKEND_STRUCTURE.md","flow":"doc/APP_FLOW.md","team":"doc/TEAM.md","lessons":"lessons.md"}

def markdown_text(text):
    """Blank fenced examples while preserving source line numbers."""
    lines=[]; fence=None
    for line in text.splitlines():
        match=re.match(r"^\s{0,3}(`{3,}|~{3,})(.*)$",line)
        if fence:
            if match and match[1][0]==fence[0] and len(match[1])>=len(fence) and not match[2].strip():
                fence=None
            lines.append("")
        elif match:
            fence=match[1]; lines.append("")
        else:lines.append(line)
    return "\n".join(lines)

def norm(s): return re.sub(r"\s+"," ",(s or "").strip().strip("`*_ ")).lower()
def rel(p,r):
    try:return p.relative_to(r).as_posix()
    except ValueError:return p.as_posix()
def finding(sev,code,path,msg,line=None,suggestion=None):
    return {"severity":sev,"code":code,"path":path,"message":msg,"line":line,"suggestion":suggestion}
def field(text,name):
    pat=re.compile(rf"^\s*(?:[-*]\s*)?{re.escape(name)}\s*:\s*(.*?)\s*$",re.I)
    for i,line in enumerate(markdown_text(text).splitlines(),1):
        m=pat.match(line)
        if m:return m.group(1).strip(),i
    return None,None
def date_of(value):
    m=DATE_RE.search(value or "")
    try:return dt.date.fromisoformat(m.group(1)) if m else None
    except ValueError:return None
def tables(text):
    lines=markdown_text(text).splitlines(); i=0
    while i+1<len(lines):
        if "|" not in lines[i] or not re.match(r"^\s*\|?\s*:?-{3,}",lines[i+1]): i+=1; continue
        heads=[x.strip() for x in lines[i].strip().strip("|").split("|")]; rows=[]; j=i+2
        while j<len(lines) and "|" in lines[j] and lines[j].strip() and not lines[j].lstrip().startswith("#"):
            cells=[x.strip() for x in lines[j].strip().strip("|").split("|")]
            if len(cells)!=len(heads):raise ValueError(f"Unsupported or malformed Markdown table at line {j+1}; inspect manually")
            rows.append((j+1,cells))
            j+=1
        yield heads,rows; i=max(j,i+1)
def idx(heads,*names):
    hs=[norm(x) for x in heads]
    for n in names:
        if norm(n) in hs:return hs.index(norm(n))
    return None
def task_tables(text):
    for h,r in tables(text):
        if idx(h,"ID") is not None and idx(h,"Status","Final Status") is not None:yield h,r
def task_ids(text,statuses=None):
    out=set()
    for h,rows in task_tables(text):
        ii=idx(h,"ID"); si=idx(h,"Status","Final Status")
        for _,c in rows:
            if statuses is None or norm(c[si]) in statuses:
                if c[ii].strip("` "):out.add(c[ii].strip("` "))
    return out
def phase(text):
    text=markdown_text(text)
    for n in ("Current Phase","Current Stage","Phase","Stage"):
        v,l=field(text,n)
        if v:return v,l
    m=re.search(r"^#+\s+.*current.*(?:phase|stage).*?\n+([^#\n]+)",text,re.I|re.M)
    return (m.group(1).strip(),text[:m.start(1)].count("\n")+1) if m else (None,None)
def active_stages(text):
    out=[]
    for h,rows in tables(text):
        si=idx(h,"Stage","Phase"); ti=idx(h,"Status")
        if si is None or ti is None:continue
        for line,c in rows:
            if norm(c[ti]) in {"active","current","in progress","in-progress"}:out.append((c[si].strip("` "),line))
    return out
def metadata(path,text,root):
    out=[]
    for n in META:
        if field(text,n)[0] is None:out.append(finding("WARN","META_MISSING",rel(path,root),f"Missing `{n}:`."))
    return out
def freshness(path,text,root,today,names,days,code):
    for n in names:
        v,l=field(text,n); d=date_of(v)
        if not d:continue
        age=(today-d).days
        if age<0:return [finding("WARN","FUTURE_DATE",rel(path,root),f"`{n}` is in the future.",l)]
        if age>days:return [finding("WARN",code,rel(path,root),f"`{n}` is {age} days old; treat as unverified, not deletable.",l)]
        return []
    return [finding("WARN","FRESHNESS_DATE_MISSING",rel(path,root),"No parseable reconciliation date.")]
def config(root,arg):
    p=inside(root,arg or "projectos.audit.json")
    if not p.is_file():
        if arg:raise ValueError(f"Explicit audit config does not exist: {p}")
        return {},None
    try:data=json.loads(p.read_text(encoding="utf-8"))
    except (ValueError,OSError) as e:raise ValueError(f"Invalid audit config: {e}") from e
    validate_config(data)
    return data,p
def inside(root,s):
    p=(root/s).resolve()
    if not p.is_relative_to(root.resolve()):raise ValueError(f"Path escapes project root: {s}")
    return p

def validate_config(cfg):
    if not isinstance(cfg,dict):raise ValueError("Audit config must be an object")
    allowed={"documents","diagnostics_globs","task_archive_globs","active_task_statuses","terminal_task_statuses","thresholds"}
    if set(cfg)-allowed:raise ValueError(f"Unknown audit config keys: {sorted(set(cfg)-allowed)}")
    docs=cfg.get("documents",{})
    if not isinstance(docs,dict):raise ValueError("documents must be an object")
    unknown=set(docs)-set(DEFAULTS)-{"entrypoint","run_registry"}
    if unknown:raise ValueError(f"Unknown document roles: {sorted(unknown)}")
    for key,value in docs.items():
        if value is not None and (not isinstance(value,str) or not value.strip()):raise ValueError(f"documents.{key} must be a path or null")
    if "run" in docs and "run_registry" in docs and docs["run"]!=docs["run_registry"]:
        raise ValueError("run and run_registry map to conflicting paths")
    for key in ("diagnostics_globs","task_archive_globs","active_task_statuses","terminal_task_statuses"):
        values=cfg.get(key,[])
        if not isinstance(values,list) or any(not isinstance(x,str) or not x.strip() for x in values):
            raise ValueError(f"{key} must be a list of nonempty strings")
        if key.endswith("_globs"):
            for value in values:
                if Path(value).is_absolute() or ".." in value.replace("\\","/").split("/"):
                    raise ValueError(f"Glob escapes project root: {value}")
    active=ACTIVE|{norm(x) for x in cfg.get("active_task_statuses",[])}
    terminal=TERMINAL|{norm(x) for x in cfg.get("terminal_task_statuses",[])}
    if active&terminal:raise ValueError(f"Status cannot be active and terminal: {sorted(active&terminal)}")
    thresholds=cfg.get("thresholds",{})
    if not isinstance(thresholds,dict):raise ValueError("thresholds must be an object")
    for key,value in thresholds.items():
        if key not in {"progress_stale_days","todo_stale_days","plan_stale_days","max_progress_lines"}:
            raise ValueError(f"Unknown threshold: {key}")
        if type(value) is not int or value<1:raise ValueError(f"{key} must be a positive integer")

def discover(root,cfg):
    validate_config(cfg)
    d=dict(cfg.get("documents",{}))
    if "run_registry" in d:d["run"]=d.pop("run_registry")
    docs={}
    entrypoint="AGENTS.md" if (root/"AGENTS.md").is_file() else "CLAUDE.md"
    for key,default in {"entrypoint":entrypoint,**DEFAULTS}.items():
        value=d.get(key,default)
        if value is None:continue
        q=inside(root,value)
        if key in d and not q.is_file():raise ValueError(f"Configured document does not exist: {value}")
        if q.is_file():docs[key]=(q,q.read_text(encoding="utf-8"))
    for pat in ["doc/diagnostics/*.md",*cfg.get("diagnostics_globs",[])]:
        for q in root.glob(pat):
            q=inside(root,q)
            if q.is_file():docs[f"diag:{q}"]=(q,q.read_text(encoding="utf-8"))
    for pat in ["doc/archive/TASKS.md","doc/archive/tasks/**/*.md",*cfg.get("task_archive_globs",[])]:
        for q in root.glob(pat):
            q=inside(root,q)
            if q.is_file():docs[f"archive:{q}"]=(q,q.read_text(encoding="utf-8"))
    return docs

def next_task(value,known):
    candidates=[]
    for tid in known:
        match=re.search(r"(?<![\w-])"+re.escape(tid)+r"(?![\w-])",value)
        if match:candidates.append((match.start(),tid))
    for match in TASK_RE.finditer(value):
        if match[1][0].isupper() or match[1][0].isdigit() or ord(match[1][0])>127:
            candidates.append((match.start(),match[1]))
    return min(candidates)[1] if candidates else None

def stage_identity(value):
    value=norm(value)
    match=re.match(r"([a-z][\w-]*\d[\w-]*)(?=$|\s|[:：—])",value)
    return match[1] if match else value

def validate_output(root,output):
    if output.is_relative_to(root):
        raise ValueError("--output must be outside the audited project; project inputs are read-only")
    if output.exists():
        for path in root.rglob("*"):
            if path.is_file() and output.samefile(path):
                raise ValueError("--output aliases a project file; project inputs are read-only")

def audit(root,today,cfg):
    docs=discover(root,cfg); out=[]; active=ACTIVE|{norm(x) for x in cfg.get("active_task_statuses",[])}; terminal=TERMINAL|{norm(x) for x in cfg.get("terminal_task_statuses",[])}
    th=cfg.get("thresholds",{}) if isinstance(cfg.get("thresholds",{}),dict) else {}
    pd=int(th.get("progress_stale_days",7)); td=int(th.get("todo_stale_days",14)); ld=int(th.get("plan_stale_days",45)); maxp=int(th.get("max_progress_lines",250))
    if "entrypoint" not in docs:out.append(finding("WARN","ENTRYPOINT_MISSING",".","No canonical agent entrypoint found."))
    if (root/"AGENTS.md").is_file() and (root/"CLAUDE.md").is_file() and not cfg.get("documents",{}).get("entrypoint"):
        out.append(finding("WARN","ENTRYPOINT_SELECTION",".","Both client entrypoints exist; map the authoritative entrypoint and inspect compatibility routing."))
    for key,(p,text) in docs.items():
        text=markdown_text(text)
        out+=metadata(p,text,root)
        if key=="progress":
            out+=freshness(p,text,root,today,("As Of","Last Reconciled","Last Updated"),pd,"PROGRESS_STALE")
            if field(text,"As Of")[0] is None:out.append(finding("WARN","LIVE_METADATA_MISSING",rel(p,root),"Missing `As Of:`."))
            if not phase(text)[0]:out.append(finding("ERROR","CURRENT_PHASE_MISSING",rel(p,root),"No current phase/stage."))
            if len(text.splitlines())>maxp:out.append(finding("WARN","PROGRESS_TOO_LARGE",rel(p,root),f"PROGRESS has {len(text.splitlines())} lines (limit {maxp}); review for compaction."))
        elif key=="todo":
            out+=freshness(p,text,root,today,("Last Reconciled","Last Updated"),td,"TODO_STALE")
            task_groups=list(task_tables(text))
            if not task_groups:out.append(finding("ERROR","TASK_TABLE_MISSING",rel(p,root),"No ID/Status task table.")); continue
            seen=set()
            for h,rows in task_groups:
                ii=idx(h,"ID"); si=idx(h,"Status","Final Status")
                required={"Owner":idx(h,"Owner"),"Dependencies":idx(h,"Dependencies","Dependency"),"Next Action":idx(h,"Next Action","Next"),"Acceptance Gate":idx(h,"Acceptance Gate","Acceptance"),"Evidence":idx(h,"Evidence","Artifact"),"Last Touched":idx(h,"Last Touched","Last Updated","Updated")}
                for n,x in required.items():
                    if x is None:out.append(finding("WARN","TASK_COLUMN_MISSING",rel(p,root),f"Missing `{n}` task column."))
                for line,c in rows:
                    tid=c[ii].strip("` "); st=norm(c[si])
                    if not tid:out.append(finding("ERROR","TASK_ID_MISSING",rel(p,root),"Task row has no ID.",line))
                    elif tid in seen:out.append(finding("ERROR","TASK_ID_DUPLICATE",rel(p,root),f"Duplicate task `{tid}`.",line))
                    seen.add(tid)
                    if st in terminal:out.append(finding("WARN","TERMINAL_TASK_ACTIVE",rel(p,root),f"Terminal task `{tid}` remains active.",line))
                    elif st not in active:out.append(finding("WARN","TASK_STATUS_UNKNOWN",rel(p,root),f"Unknown task status `{c[si]}` for `{tid}`.",line))
        elif key=="plan":
            out+=freshness(p,text,root,today,("Last Reconciled","Last Updated"),ld,"PLAN_STALE")
            if field(text,"Plan Version")[0] is None:out.append(finding("WARN","PLAN_VERSION_MISSING",rel(p,root),"Missing `Plan Version:`."))
            stages=active_stages(text)
            if len(stages)>1:out.append(finding("ERROR","MULTIPLE_ACTIVE_STAGES",rel(p,root),"Multiple active roadmap stages."))
        elif key=="run":
            if not any(idx(h,"Trust","Trust Level") is not None for h,_ in tables(text)):out.append(finding("ERROR","RUN_TRUST_MISSING",rel(p,root),"No run table with trust classification."))
        elif key.startswith("diag:") and field(text,"Diagnostic Status")[0] is None:out.append(finding("WARN","DIAGNOSTIC_STATUS_MISSING",rel(p,root),"Missing `Diagnostic Status:`."))
        elif key in {"prd","frontend","backend","flow"}:
            if field(text,"Contract Version")[0] is None:out.append(finding("WARN","CONTRACT_VERSION_MISSING",rel(p,root),"Missing `Contract Version:`."))
            if field(text,"Last Verified Against")[0] is None:out.append(finding("WARN","CONTRACT_VERIFICATION_MISSING",rel(p,root),"Missing `Last Verified Against:`."))
            if any(x in text.lower() for x in ("current blocker","active task queue")):out.append(finding("WARN","CONTRACT_LIVE_POLLUTION",rel(p,root),"Stable contract contains live-state language."))
        elif key=="team" and re.search(r"current(?:ly)?\s+(?:assigned|assignee|task owner)",text,re.I):out.append(finding("WARN","TEAM_ROSTER_POLLUTION",rel(p,root),"TEAM contains current assignment state."))
        elif key=="lessons":
            entries=len(re.findall(r"^##\s+20\d\d-\d\d-\d\d",text,re.M)); states=len(re.findall(r"^\s*Rule Status\s*:",text,re.I|re.M))
            if entries>states:out.append(finding("INFO","LESSON_RULE_STATUS_PARTIAL",rel(p,root),"Some lesson rules lack active/superseded/retired state."))
        elif key.startswith("archive:"):
            task_groups=list(task_tables(text))
            if not task_groups:out.append(finding("WARN","ARCHIVE_TABLE_MISSING",rel(p,root),"No supported terminal task table; inspect archive manually."))
            for h,rows in task_groups:
                ii=idx(h,"ID"); si=idx(h,"Status","Final Status")
                for line,c in rows:
                    if norm(c[si]) in active:out.append(finding("ERROR","ARCHIVE_ACTIVE_TASK",rel(p,root),f"Active task `{c[ii].strip('` ')}` is in a terminal archive.",line))
                    elif norm(c[si]) not in terminal:out.append(finding("ERROR","ARCHIVE_STATUS_UNKNOWN",rel(p,root),f"Task `{c[ii]}` has unverified terminal status `{c[si]}`.",line))
    todo=docs.get("todo"); progress=docs.get("progress"); plan=docs.get("plan")
    active_ids=task_ids(todo[1],active) if todo else set()
    if progress and todo:
        v,l=field(progress[1],"Next Action")
        if not v:
            sec=re.search(r"^#+\s+.*next.*action.*?\n+([^#]*?)(?=\n#|\Z)",markdown_text(progress[1]),re.I|re.M)
            v=sec.group(1) if sec else ""
        tid=next_task(v,task_ids(todo[1]))
        if tid and tid not in active_ids:out.append(finding("ERROR","NEXT_TASK_NOT_ACTIVE",rel(progress[0],root),f"Next task `{tid}` is not active.",l))
        elif not tid and active_ids:out.append(finding("WARN","NEXT_TASK_ID_MISSING",rel(progress[0],root),"Active tasks exist but next action has no task ID."))
    if progress and plan:
        ph,pl=phase(progress[1]); stages=active_stages(plan[1])
        if ph and len(stages)==1 and stage_identity(ph)!=stage_identity(stages[0][0]):out.append(finding("ERROR","PHASE_PLAN_MISMATCH",rel(progress[0],root),f"Progress phase `{ph}` != plan stage `{stages[0][0]}`.",pl))
    archived={}
    for k,(p,text) in docs.items():
        if k.startswith("archive:"):
            for tid in task_ids(text):archived[tid]=rel(p,root)
    for tid in active_ids & set(archived):out.append(finding("ERROR","TASK_ACTIVE_AND_ARCHIVED",archived[tid],f"Task `{tid}` is both active and archived."))
    return sorted(out,key=lambda x:(-SEV[x["severity"]],x["path"],x.get("line") or 0,x["code"]))

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("project_root",nargs="?",default="."); ap.add_argument("--config"); ap.add_argument("--today"); ap.add_argument("--format",choices=("markdown","json"),default="markdown"); ap.add_argument("--output"); ap.add_argument("--fail-on",choices=("none","error","warn"),default="error"); a=ap.parse_args()
    root=Path(a.project_root).resolve()
    if not root.is_dir():return 2
    try:
        output=Path(a.output).resolve() if a.output else None
        if output:validate_output(root,output)
        cfg,cp=config(root,a.config)
        today=dt.date.fromisoformat(a.today) if a.today else dt.date.today()
        findings=audit(root,today,cfg)
    except Exception as e:print(e,file=sys.stderr); return 2
    if a.format=="json":report=json.dumps({"project_root":str(root),"audit_date":str(today),"config":str(cp) if cp else None,"read_only":True,"findings":findings},indent=2,ensure_ascii=False)+"\n"
    else:
        counts={s:sum(x["severity"]==s for x in findings) for s in SEV}; lines=["# ProjectOS Documentation Audit","",f"- Project root: `{root}`",f"- Audit date: `{today}`",f"- Findings: **{counts['ERROR']} errors**, **{counts['WARN']} warnings**, **{counts['INFO']} informational**","- Mode: read-only; no files were changed.",""]
        for s in ("ERROR","WARN","INFO"):
            group=[x for x in findings if x["severity"]==s]
            if group:
                lines += [f"## {s}",""]+[f"- **{x['code']}** `{x['path']}`{':' + str(x['line']) if x.get('line') else ''}: {x['message']}" for x in group]+[""]
        report="\n".join(lines)
    if output:
        validate_output(root,output)
        output.write_text(report,encoding="utf-8"); print(f"Wrote audit report: {output}")
    else:print(report,end="")
    has_e=any(x["severity"]=="ERROR" for x in findings); has_w=any(x["severity"]=="WARN" for x in findings)
    return 1 if (a.fail_on=="error" and has_e) or (a.fail_on=="warn" and (has_e or has_w)) else 0
if __name__=="__main__":raise SystemExit(main())
