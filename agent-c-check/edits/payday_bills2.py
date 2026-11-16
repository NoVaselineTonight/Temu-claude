import sys

root = sys.argv[1]


def rep(path, a, b, n=1):
    p = root + '/' + path
    s = open(p, encoding='utf-8').read()
    assert s.count(a) == n, (path, a[:70], s.count(a))
    open(p, 'w', encoding='utf-8').write(s.replace(a, b))


rep('app/features.py', '''    nxt = ins._next_payday(t, pay) if pay is not None else None''',
    '''    nxt = ins._next_payday(t, pay, conn) if pay is not None else None''')
rep('app/features.py', '''    nxt = ins._next_payday(t, pay)\n''', '''    nxt = ins._next_payday(t, pay, conn)\n''')
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
print("payday2 ok")
