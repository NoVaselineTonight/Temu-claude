import sys

root = sys.argv[1]


def rep(path, a, b, n=1):
    p = root + '/' + path
    s = open(p, encoding='utf-8').read()
    assert s.count(a) == n, (path, a[:70], s.count(a))
    open(p, 'w', encoding='utf-8').write(s.replace(a, b))


# MAJ-2: salary day alternates between mid-month and month end in this data: when the history is mixed,
# expect the later one (a longer window holds back more bills, never fewer).
rep('app/insights.py', '''    eom = sum(1 for x in ds if x.day >= _last_day(x.year, x.month) - 3)
    if eom * 2 > len(ds):
        return "eom"''', '''    eom = sum(1 for x in ds if x.day >= _last_day(x.year, x.month) - 3)
    if eom * 2 > len(ds) or (eom * 3 >= len(ds) and (len(ds) - eom) * 3 >= len(ds)):
        return "eom"''')
# ...and once this month's salary has arrived, the next one is next month.
rep('app/insights.py', '''def _next_payday(t, pay):
    cand = _payday_on(t.year, t.month, pay)
    if cand <= t:''', '''def _next_payday(t, pay, conn=None):
    """Next payday after t. With `conn`, a salary already received this month moves it to next month."""
    cand = _payday_on(t.year, t.month, pay)
    paid = conn is not None and _scalar(conn, "SELECT COUNT(*) FROM tx WHERE type='salary' AND d>=? AND d<=?",
                                        (_month_start(t).isoformat(), t.isoformat()), default=0) > 0
    if cand <= t or paid:''')
rep('app/insights.py', '''        nxt = _next_payday(t, pay)
        win_end = nxt''', '''        nxt = _next_payday(t, pay, conn)
        win_end = nxt''')
rep('app/features.py', '''        return (ins._next_payday(t, pay) if pay is not None else None), t + timedelta(days=n), False''',
    '''        return (ins._next_payday(t, pay, conn) if pay is not None else None), t + timedelta(days=n), False''')
rep('app/features.py', '''    nxt = ins._next_payday(t, pay)''', '''    nxt = ins._next_payday(t, pay, conn)''')
rep('app/features.py', '''    nxt = ins._next_payday(t, pay) if pay is not None else None''',
    '''    nxt = ins._next_payday(t, pay, conn) if pay is not None else None''')

# MAJ-1: this month's bill that is late but not paid yet is still expected (as due today), not dropped.
rep('app/insights.py', '''            if cur == _month_start(t) and k < paid_now:
                continue
            if due < t or due >= win_end:
                continue''', '''            if cur == _month_start(t) and k < paid_now:
                continue
            if due < t:
                if cur != _month_start(t):
                    continue
                due = t          # late this month and not paid yet: still expected (MAJ-1)
            if due >= win_end:
                continue''')
print("payday ok")
