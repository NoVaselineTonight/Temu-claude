import sys

p = sys.argv[1]
s = open(p, encoding='utf-8').read()


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (a[:70], s.count(a))
    s = s.replace(a, b)


rep('''def _norm_pct(p):
    """A percentage is a percentage: 0.5 means half a percent. Outside 0..100 is an error."""
    try:
        p = float(p)
    except (TypeError, ValueError):
        return 0.0
    if p != p or p < 0 or p > 100:
        raise ValueError("pct must be between 0 and 100")
    return p''', '''def _norm_pct(p):
    """A percentage is a percentage: 0.5 means half a percent. A cut is 0..100; an increase is negative
    (-20 = spend 20% more, -100 = double), down to -1000. Anything else is an error."""
    try:
        p = float(p)
    except (TypeError, ValueError):
        return 0.0
    if p != p or p < -1000 or p > 100:
        raise ValueError("pct must be between -1000 and 100")
    return p''')

# explain text: an increase costs, a cut saves (MAJ-4)
rep('''        desc = ", ".join("%s by %s%%" % (" and ".join(names), "%g" % pct) for pct, names in groups)
        over = "a year" if months == 12 else "over %d months" % months
        explain = ("Based on your last %d full months (%s), cutting %s would save about %s a month, %s %s." % (
            n, months_span(frm, to, today), desc, _eur0(saved_monthly), _eur0(us * months), over))''',
    '''        desc = ", ".join("%s by %s%%" % (" and ".join(names), "%g" % abs(pct)) for pct, names in groups)
        over = "a year" if months == 12 else "over %d months" % months
        if us < 0:
            explain = ("Based on your last %d full months (%s), spending more on %s would cost about %s more a "
                       "month, %s %s." % (n, months_span(frm, to, today), desc, _eur0(-saved_monthly),
                                          _eur0(-us * months), over))
        else:
            explain = ("Based on your last %d full months (%s), cutting %s would save about %s a month, %s %s." % (
                n, months_span(frm, to, today), desc, _eur0(saved_monthly), _eur0(us * months), over))''')
rep('''    return {"baseline_monthly": _r(ub), "new_monthly": _r(ub - us), "saved_monthly": saved_monthly,
            "saved_total": _r(us * months), "months": months, "lines": lines,''',
    '''    return {"baseline_monthly": _r(ub), "new_monthly": _r(ub - us), "saved_monthly": saved_monthly,
            "saved_total": _r(us * months), "months": months, "lines": lines,
            "direction": "increase" if us < 0 else "cut",''')
open(p, 'w', encoding='utf-8').write(s)
print("insights ok")
