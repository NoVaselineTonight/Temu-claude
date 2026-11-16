import sys

p = sys.argv[1]
s = open(p, encoding='utf-8').read()


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (a[:70], s.count(a))
    s = s.replace(a, b)


rep('''def afford(conn, today, item, price, goal=None, monthly_saving_target=0.0):''', '''# MAJ-5: some "purchases" are not purchases. Borrowing, crypto and gambling get a plain warning instead of
# "it fits"; investing is pointed at the in-app S-Bank funds (moved only after the customer approves).
_RISK_KINDS = (
    ("loan", re.compile(r"\\b(payday|quick|instant|short[- ]term|sms|fast)\\s*loans?\\b|\\bpikavip\\w*|\\bvip(p)?i\\w*|"
                        r"\\bpikalain\\w*|\\bloan\\b|\\blaina\\w*|\\bcredit\\b|\\bluotto\\w*|\\bbnpl\\b|buy now,? pay later", re.I)),
    ("crypto", re.compile(r"\\bbitcoins?\\b|\\bbtc\\b|\\bcrypto\\w*|\\bkrypto\\w*|\\bethereum\\b|\\beth\\b|\\bdogecoin\\b|"
                          r"\\bsolana\\b|\\bnfts?\\b|\\bmeme ?coins?\\b|\\btokens?\\b", re.I)),
    ("gambling", re.compile(r"\\bcasino\\w*|\\bkasino\\w*|\\bgambl\\w*|\\bbet(s|ting)?\\b|\\bpoker\\b|\\blotter(y|ies)\\b|"
                            r"\\blotto\\b|\\bslots?\\b|\\bveikkaus\\w*|\\brahapel\\w*|\\bvedonly\\w*", re.I)),
    ("invest", re.compile(r"\\bfunds?\\b|\\brahasto\\w*|\\bshares?\\b|\\bstocks?\\b|\\bosake\\w*|\\betfs?\\b|"
                          r"\\bindex\\b|\\bbonds?\\b|\\binvest\\w*|\\bsijoitu\\w*", re.I)),
)


def risk_kind(item):
    """'loan', 'crypto', 'gambling', 'invest' or None for an ordinary purchase."""
    text = str(item or "")
    for kind, rx in _RISK_KINDS:
        if rx.search(text):
            return kind
    return None


def afford(conn, today, item, price, goal=None, monthly_saving_target=0.0):''')

rep('''    goal_effect = None
    if isinstance(goal, dict) and goal.get("name"):''', '''    risk = risk_kind(item)
    if risk:
        verdict = "caution"
        room = ("about %s a day would be left %s" % (_eur0(max(0.0, per_day_after)), until)) if after >= 0 else \\
            ("that is %s more than the %s you can safely spend %s" % (_eur0(-after), _eur0(max(0.0, safe_total)), until))
        if risk == "loan":
            text = ("A %s is borrowing, not a purchase: you pay it back with interest and fees, often much more than "
                    "you borrowed. I would not take it. If money is short before payday, let's look at what is "
                    "safe to spend instead." % item)
        elif risk == "crypto":
            text = ("You could pay %s (%s), but %s can lose much of its value in days. Only put in money you could "
                    "lose completely. For investing, an S-Bank fund in S-mobiili spreads the risk; I can set one up "
                    "for you to approve." % (_eur(price), room, item))
        elif risk == "gambling":
            text = ("I would not plan money for %s: on average you get back less than you put in. %s is money you "
                    "could keep instead." % (item, _eur(price)))
        else:
            text = ("Investing is not spending, so the question is whether you can leave the money alone: %s. "
                    "Inside S-mobiili you can put money into an S-Bank fund; I will show you the move and ask you "
                    "to approve it first." % room)

    goal_effect = None
    if isinstance(goal, dict) and goal.get("name"):''')
rep('''        "goal_effect": goal_effect, "alternatives": alternatives,''',
    '''        "goal_effect": goal_effect, "alternatives": alternatives if not risk else [], "risk": risk,''')
open(p, 'w', encoding='utf-8').write(s)
print("features ok")
