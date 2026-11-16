import sys

root = sys.argv[1]


def rep(path, a, b, n=1):
    p = root + '/' + path
    s = open(p, encoding='utf-8').read()
    assert s.count(a) == n, (path, a[:70], s.count(a))
    open(p, 'w', encoding='utf-8').write(s.replace(a, b))


# --- the one place that decides whether a comparison was asked for
rep('app/coach.py', '''def chat(message, history, ctx):
    message = (message if isinstance(message, str) else "").strip()[:MAX_MESSAGE]
    if not message:
        return _package(EMPTY_REPLY, [], "offline")''', '''_COMPARE_RE = re.compile(
    r"compar\\w*|stack up|\\bversus\\b|\\bvs\\.?\\b|\\bpeers?\\b|people (my age|like me|around me|near me|nearby)|"
    r"\\bothers?\\b|other people|everyone else|most people|\\bmy age\\b|same age|similar (age|people)|"
    r"\\baverage\\b|\\btypical(ly)?\\b|\\bnormal\\b|\\bbenchmark\\w*|\\bfinns\\b|\\bstatistic\\w*|"
    r"\\b(my|the) (area|neighbou?rhood|postcode|district)\\b|\\bwhere i live\\b|"
    r"vertaa\\w*|verrattuna|muihin|muut ihmiset|ikäisi\\w*|keskimäär\\w*|tyypillise\\w*|normaali\\w*|alueeni|asuinalue\\w*",
    re.I)


def compare_requested(message):
    """True only when the customer asks to be compared with other people (or about their area).
    Comparisons are never added to an answer on the app's own initiative."""
    return bool(_COMPARE_RE.search(message or ""))


def _set_compare(ctx, message):
    flag = compare_requested(message)
    if isinstance(ctx, dict):
        ctx["compare_requested"] = flag
    else:
        try:
            setattr(ctx, "compare_requested", flag)
        except Exception:
            pass


def chat(message, history, ctx):
    message = (message if isinstance(message, str) else "").strip()[:MAX_MESSAGE]
    if not message:
        return _package(EMPTY_REPLY, [], "offline")
    _set_compare(ctx, message)''')

# --- Claude/Gemini only see the comparison tools when a comparison was asked for
rep('app/coach.py', '''def _declared_tools(ctx):
    """Tool declarations the model may see; the comparison tools only with benchmark consent."""
    bench_ok = bool((_ctx_get(ctx, "consent", {}) or {}).get("benchmarks"))''',
    '''def _declared_tools(ctx):
    """Tool declarations the model may see; the comparison tools only with benchmark consent and only when the
    customer asked for a comparison in this message."""
    bench_ok = bool((_ctx_get(ctx, "consent", {}) or {}).get("benchmarks")) and bool(_ctx_get(ctx, "compare_requested", False))''')

rep('app/coach.py', '''11. When a tool result contains a `peer` object you may quote its `sentence` word for word to compare the figure with people like the customer. Never invent a comparison, a peer figure or an average yourself; if there is no `peer`, do not compare.
12. When the customer asks what is normal, typical or average''',
    '''11. Never compare the customer with other people unless they ask for it in this message (how do I compare, is that normal, what do others spend). Do not add comparisons to answers about their own income, spending, balance or plans. When they do ask and a tool result contains a `peer` object, you may quote its `sentence` word for word. Never invent a comparison, a peer figure or an average yourself.
12. When the customer asks what is normal, typical or average''')

# --- spend tool: the peer figure (and the "turn on comparisons" hint) only when asked
rep('app/tools.py', '''    res = dict(res)
    if _period_days(res.get("period")) < 7:''', '''    res = dict(res)
    asked = ctx.get("compare_requested") if isinstance(ctx, dict) else getattr(ctx, "compare_requested", False)
    if not asked:
        return res          # no comparison with other people unless the customer asked for one
    if _period_days(res.get("period")) < 7:''')

# --- alerts: only against the customer's own usual spending, never against other people
rep('app/tools.py', '''def _t_alerts(args, ctx, ins):
    bench = None
    if (ctx.consent or {}).get("benchmarks"):
        bench = getattr(ctx, "bench_lookup", None)
    return _feat().alerts(ctx.conn, ctx.today, getattr(ctx, "profile", None), bench), "alerts"''',
    '''def _t_alerts(args, ctx, ins):
    # Alerts compare with the customer's own usual spending only; peer comparisons are given only on request.
    return _feat().alerts(ctx.conn, ctx.today, getattr(ctx, "profile", None), None), "alerts"''')
rep('app/server.py', '''    feat = _features()
    if req.consent.get("benchmarks"):
        res = feat.alerts(req.conn, req.today, db.profile(req.cid), db.bench)
    else:
        res = feat.alerts(req.conn, req.today)''', '''    feat = _features()
    res = feat.alerts(req.conn, req.today)    # own usual spending only; no comparison with others unasked''')

# --- quiz result: no comparison with others
rep('app/server.py', '''        if req.consent.get("benchmarks"):
            res = _insights().quiz_answer(req.conn, req.today, quiz_id, guess,
                                          profile=db.profile(req.cid), bench_lookup=db.bench)
        else:
            res = _insights().quiz_answer(req.conn, req.today, quiz_id, guess)''',
    '''        res = _insights().quiz_answer(req.conn, req.today, quiz_id, guess)   # no unasked comparison''')
print("compare edits ok")
