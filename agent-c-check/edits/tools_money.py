import sys

p = sys.argv[1]
s = open(p, encoding='utf-8').read()


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (a[:70], s.count(a))
    s = s.replace(a, b)


# what-if: increases as well as cuts (MAJ-4)
rep('''        "description": "What-if: how much would be saved by cutting spending in some labels or baskets "
                       "by a percentage. Targets: a label, 'Dining out', 'Night out' or a basket name.",''',
    '''        "description": "What-if: how much would be saved by cutting spending in some labels or baskets "
                       "by a percentage, or how much more it would cost to spend more (a negative pct: -20 means "
                       "20% more, -100 means double). Targets: a label, 'Dining out', 'Night out' or a basket name. "
                       "A negative `saved_monthly` in the result is extra cost.",''')
rep('''                    "pct": {"type": "number", "description": "Percent to cut, 0 to 100."},''',
    '''                    "pct": {"type": "number", "description": "Percent to cut, 0 to 100; negative for an "
                                                                 "increase (-20 = spend 20% more, -100 = double)."},''')

# the money tools go at the end of TOOLS (the list closes at the first top-level "]" after "TOOLS = [")
i = s.index("TOOLS = [")
j = s.index("\n]\n", i)
s = s[:j] + '''
    {
        "name": "propose_money_move",
        "description": "Offer to move money inside S-mobiili: from the customer's current account to their own "
                       "S-Bank savings account or an S-Bank fund. This only creates an offer the customer must "
                       "approve in the app; it never moves money by itself, and nothing can go outside S-mobiili. "
                       "Use it when the customer asks to save, set aside or invest an amount, or agrees to your "
                       "suggestion to do so. The amount is capped at what is safe to spend until payday; if it is "
                       "too much the result says the most that can be moved. Tell the customer to approve or "
                       "cancel the move on the card. Destinations: savings (S-Bank savings account), fund_index "
                       "(S-Bank global index fund, for five years or more), fund_interest (S-Bank short-term "
                       "interest fund, low risk).",
        "parameters": {"type": "object", "properties": {
            "destination": {"type": "string", "enum": ["savings", "fund_index", "fund_interest"]},
            "amount": {"type": "number", "description": "Euros to move, as the customer said or agreed."},
            "reason": {"type": "string", "description": "A few words on why, shown on the approval card."},
        }, "required": ["destination", "amount"]},
    },
    {
        "name": "get_savings_and_investments",
        "description": "What the customer has moved into their S-Bank savings account and S-Bank funds in this "
                       "app, how much can be moved now without touching money needed for bills, and the "
                       "destinations available. Read-only.",
        "parameters": {"type": "object", "properties": {}},
    },''' + s[j:]

rep('''_DISPATCH = {''', '''def _t_propose_money(args, ctx, ins):
    fn = getattr(ctx, "propose_money", None)
    if not callable(fn):
        raise _Unavailable("moving money is not available here")
    dest = args.get("destination")
    if dest not in ("savings", "fund_index", "fund_interest"):
        raise ValueError("destination must be savings, fund_index or fund_interest")
    amount = _num(args.get("amount"), 0, 50_000_000, "amount")
    reason = re.sub(r"[\\x00-\\x1f]", " ", str(args.get("reason") or "")).strip()[:200]
    from app import money
    try:
        prop = fn(dest, amount, reason)
    except money.MoneyError as e:
        return {"refused": True, "message": str(e), "requested": _r2(amount), "destination": dest}, "money_proposal"
    return {"proposal": prop, "requested": _r2(amount), "destination": dest}, "money_proposal"


def _t_money_holdings(args, ctx, ins):
    from app import money
    cap, s = money.available(ctx.conn, ctx.today)
    held = getattr(ctx, "holdings", None)
    return {"holdings": held if isinstance(held, list) else [], "available_to_move": _r2(cap),
            "destinations": money.destinations(), "next_payday": s.get("next_payday")}, "money_holdings"


def _r2(v):
    return round(float(v), 2)


_DISPATCH = {''')
rep('''    "get_quiz_stats": _t_quiz_stats, "get_area_context": _t_area, "remember_category": _t_remember,
}''', '''    "get_quiz_stats": _t_quiz_stats, "get_area_context": _t_area, "remember_category": _t_remember,
    "propose_money_move": _t_propose_money, "get_savings_and_investments": _t_money_holdings,
}''')
open(p, 'w', encoding='utf-8').write(s)
print("tools ok")
