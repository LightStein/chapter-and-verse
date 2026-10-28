import importlib.util, sys, re, os
spec = importlib.util.spec_from_file_location("ask", "engine/ask.py")
ask = importlib.util.module_from_spec(spec); sys.argv = ["ask.py"]
spec.loader.exec_module(ask)
metas = ask.load_meta_index()

# question -> regex matching a chunk that actually contains the answer
CASES = [
 ("какого цвета провод защитного заземления?", r"(зелено-желт|желто-зелен)\w*[\s\S]{0,60}защитн"),
 ("какого цвета нулевой рабочий проводник?",    r"голуб\w*[\s\S]{0,80}нулев|нулев\w*[\s\S]{0,80}голуб"),
 ("на какой высоте от пола ставить выключатель?", r"выключател[\s\S]{0,80}(0,8|1,7|1,8)\s*м|(0,8|1,7|1,8)\s*м[\s\S]{0,60}выключател"),
 ("нужно ли УЗО в ванной комнате?",             r"30\s*мА"),
 ("какая степень защиты IP нужна для светильника в душевой?", r"IP\s?[2-6][0-9]"),
 ("как обозначается нулевой рабочий проводник?", r"\bN\b[\s\S]{0,60}нулев|нулев[\s\S]{0,60}\bN\b"),
]

def variant(full, mode):
    if mode == "current":   return full
    if mode == "q-only":    return {k: v for k, v in full.items() if v >= 3.0}
    if mode == "exp-0.3":   return {k: (v if v >= 3.0 else 0.3) for k, v in full.items()}
    if mode == "exp-cap6":  # question terms + the 6 shortest expanded terms
        q = {k: v for k, v in full.items() if v >= 3.0}
        e = sorted([k for k, v in full.items() if v < 3.0], key=len)[:6]
        q.update({k: 1.0 for k in e}); return q
    if mode == "cap6+0.3":
        q = {k: v for k, v in full.items() if v >= 3.0}
        e = sorted([k for k, v in full.items() if v < 3.0], key=len)[:6]
        q.update({k: 0.3 for k in e}); return q

MODES = ["current", "q-only", "exp-0.3", "exp-cap6", "cap6+0.3"]
print("%-10s %s" % ("mode", "  ".join("Q%d" % (i+1) for i in range(len(CASES)))), " recall")
for mode in MODES:
    hits, marks = 0, []
    for q, pat in CASES:
        full, docs = ask.route_lexical(q, metas)
        chunks = ask.retrieve(docs, variant(full, mode))
        rx = re.compile(pat, re.I)
        found = any(rx.search(c) for _, c in chunks)
        hits += found
        marks.append(" Y" if found else " .")
    print("%-10s %s   %d/%d" % (mode, "  ".join(marks), hits, len(CASES)))
