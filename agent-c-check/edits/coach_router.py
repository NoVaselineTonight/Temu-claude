import sys

p = sys.argv[1]
s = open(p, encoding='utf-8').read()


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (a[:80], s.count(a))
    s = s.replace(a, b)


# ---- MAJ-3: "last 10 days", "past 2 weeks"
rep('''    m = re.search(r"\\b(?:on|last|this|since)\\s+(mon|tue|tues|wed|thu|thur|thurs|fri|sat|sun)(?:day|sday|nesday|rsday|urday)?\\b", s)''',
    '''    n_words = {"two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "ten": 10, "fourteen": 14}
    m = re.search(r"\\b(?:last|past|previous)\\s+(\\d{1,3}|two|three|four|five|six|seven|ten|fourteen)\\s+(days?|weeks?)\\b", s)
    if m:
        n = int(m.group(1)) if m.group(1).isdigit() else n_words[m.group(1)]
        days = n * (7 if m.group(2).startswith("week") else 1)
        if 1 <= days <= 366:
            try:
                t = _dt.date.fromisoformat(today[:10])
            except ValueError:
                return None
            return "dates", ((t - _dt.timedelta(days=days - 1)).isoformat(), t.isoformat())
    m = re.search(r"\\b(?:on|last|this|since)\\s+(mon|tue|tues|wed|thu|thur|thurs|fri|sat|sun)(?:day|sday|nesday|rsday|urday)?\\b", s)''')

# ---- MAJ-8: income, also in the past tense and for one month
rep('''    if re.search(r"\\bhow much (money )?do i (earn|make|get paid)\\b|\\bwhat do i (earn|make)\\b|"
                 r"\\bwhat('?s| is) my (monthly )?(income|salary|pay)\\b|\\bhow much (money )?comes in\\b|"
                 r"^\\s*(my )?(monthly )?income\\s*[?.!]*$", s):
        return "check_mortgage", {}, {"view": "income"}''',
    '''    if re.search(r"\\bhow much (money )?(do|did) i (earn|make|get paid|receive|get)\\b(?! back)|\\bwhat (do|did) i (earn|make)\\b|"
                 r"\\bwhat('?s| is| was) my (monthly )?(income|salary|pay|earnings)\\b|\\bhow much (money )?(comes|came) in\\b|"
                 r"\\bmy (income|salary|earnings|pay) (last|this|in)\\b|\\bhow much (salary|income|pay) did i\\b|"
                 r"^\\s*(my )?(monthly )?income\\s*[?.!]*$", s) and not re.search(r"\\bspen[dt]\\b|\\bafford\\b", s):
        mon = month_of_period(period, today) if period else None
        if mon:
            return "get_overview", {"month": mon}, {"view": "income"}
        return "check_mortgage", {}, {"view": "income"}''')

# ---- MAJ-4: increases in the what-if
rep('''    target = label or basket_t
    if (target and (pct is not None or _CUT_VERB.search(s)) and not re.search(r"\\bhow much did i\\b|\\bwhat did i\\b", s)) \\
            or (pct is not None and re.search(r"\\bif i\\b|what if|\\bcut\\b|reduc|lower|spend less", s)):
        assumed = target is None
        p = pct if pct is not None else 20.0''',
    '''    target = label or basket_t
    inc = (not _CUT_VERB.search(s) and not re.search(r"\\bsave more\\b", s)
           and re.search(r"\\b(spend|spending|use|using|pay|paying|buy|buying|eat|eating|go|going|take|taking)\\w*\\b"
                         r"[^?.]{0,25}\\b(more|extra)\\b|\\bmore\\b[^?.]{0,15}\\b(on|for)\\b|"
                         r"\\b(increas\\w*|rais\\w*|doubl\\w*|tripl\\w*|went up|go up|goes up)\\b", s))
    if target and inc and (pct is not None or re.search(r"\\bif i\\b|what if|\\bwould\\b|doubl|tripl", s)) \\
            and not re.search(r"\\bhow much did i\\b|\\bwhat did i\\b", s):
        p = pct if pct is not None else (200.0 if re.search(r"tripl", s) else 100.0 if re.search(r"doubl", s) else 20.0)
        return "simulate_what_if", {"changes": [{"target": target, "pct": -p}], "months": 12}, \\
            {"assumed_pct": pct is None and not re.search(r"doubl|tripl", s), "increase": True}
    if (target and (pct is not None or _CUT_VERB.search(s)) and not re.search(r"\\bhow much did i\\b|\\bwhat did i\\b", s)) \\
            or (pct is not None and re.search(r"\\bif i\\b|what if|\\bcut\\b|reduc|lower|spend less", s)):
        assumed = target is None
        p = pct if pct is not None else 20.0''')

# ---- money moves inside S-mobiili (offer only; the customer approves in the app)
rep('''    # savings goal
    if re.search(r"\\b(save|saving|savings goal|goal|reach|put aside|set aside)\\b", s) and amts and pct is None \\''',
    '''    # in-app money moves: an offer to approve, never a move
    hypothetical = re.search(r"\\bif i\\b|what if|\\bwould i\\b|\\bshould i\\b|\\bcould i\\b|\\bcan i afford\\b", s)
    dest_words = re.search(r"savings? account|\\b(to|into|in) (my )?savings\\b|\\bbuffer\\b|"
                           r"\\b(in|into|to) (my |a |an |the )?(s-bank )?([\\w-]+ )?fund\\b", s)
    verb = re.search(r"\\b(move|put|transfer|set aside|put aside|save|deposit|invest)\\b", s)
    if amts and verb and not hypothetical and (dest_words or verb.group(1) == "invest"):
        dest = _money_dest(s if dest_words else "fund")
        if dest:
            return "propose_money_move", {"destination": dest, "amount": amts[0][0], "reason": "You asked in the chat"}, {}
    if re.search(r"\\b(how much|what)\\b[^?]{0,30}\\b(in|on) my (savings( account)?|investments?|funds?)\\b|"
                 r"\\bmy (savings account|investments|funds)\\b\\s*[?.!]*$|\\bshow (me )?my (savings|investments|funds)\\b", s):
        return "get_savings_and_investments", {}, {}

    # savings goal
    if re.search(r"\\b(save|saving|savings goal|goal|reach|put aside|set aside)\\b", s) and amts and pct is None \\''')

# ---- MAJ-3: say when the period or the category was not understood
rep('''        if label:
            args["label"] = label
        return "get_spend", args, {"period_given": period is not None or bool(day_dates)}''',
    '''        if label:
            args["label"] = label
        hints = {"period_given": period is not None or bool(day_dates)}
        if day_dates and day_dates[0] != day_dates[1]:
            hints["pw"] = "from %s to %s" % (_day(day_dates[0]), _day(day_dates[1]))
        if period is None and not day_dates and re.search(
                r"\\b(days?|weeks?|months?|years?|since|between|quarter|weekends?|spring|summer|autumn|fall|winter|"
                r"christmas|holidays?|easter|midsummer|lately|recently)\\b", s) \\
                and not re.search(r"\\b(a|per|each|every) (day|week|month|year)\\b|\\b(daily|weekly|monthly|yearly)\\b", s):
            hints["period_unclear"] = True
        if not label:
            um = re.search(r"\\bon (?:my |the )?([a-zåäö][\\w' -]{1,30}?)(?=\\s+(?:last|this|in|during|over|yesterday|"
                           r"today|since|the past|past)\\b|\\s*[?.!]*$)", s)
            if um and um.group(1).strip() not in ("it", "that", "this", "everything", "stuff", "things", "average",
                                                    "the weekend", "weekends", "my card", "card", "me"):
                hints["unknown_target"] = um.group(1).strip()
        return "get_spend", args, hints''')

# ---- renderers
rep('''        pw = period_words(args.get("period", "last_month"))
        if args.get("from_date"):
            pw = "on " + _day(args["from_date"])
        n = _g(res, "count", 0) or 0''',
    '''        pw = period_words(args.get("period", "last_month"))
        if args.get("from_date"):
            pw = "on " + _day(args["from_date"])
        if hints.get("pw"):
            pw = hints["pw"]
        lead = ""
        if hints.get("period_unclear"):
            lead = "I couldn't read that time span, so this is %s. " % pw
        if hints.get("unknown_target") and not lab and tool == "get_spend":
            lead += "I don't have a category for \\"%s\\", so this is all your spending. " % hints["unknown_target"][:30]
        if lead:
            return lead + _render(tool, res, args, {k: v for k, v in hints.items()
                                                     if k not in ("period_unclear", "unknown_target")})
        n = _g(res, "count", 0) or 0''')

rep('''    if tool == "get_overview":
        b = _g(res, "baskets", {})
        mon = "in " + _month(res.get("month"))''',
    '''    if tool == "get_overview" and hints.get("view") == "income":
        return "In %s, %s came in." % (_month(res.get("month")), _eur_x(res.get("income")))

    if tool == "get_overview":
        b = _g(res, "baskets", {})
        mon = "in " + _month(res.get("month"))''')

rep('''            return "You haven't spent anything on %s lately, so there is nothing to save." % what
''', '''            return "You haven't spent anything on %s lately, so there is nothing to save." % what
        if res.get("direction") == "increase" or p < 0:
            more = abs(p)
            how = "Doubling" if more == 100 else "Tripling" if more == 200 else "Spending %g%% more on" % more
            obj = "" if more in (100, 200) else ""
            yr_inc = ("about %s a year" % _eur(abs(res.get("saved_total") or 0))) if res.get("months") == 12 else \\
                "%s over %s months" % (_eur(abs(res.get("saved_total") or 0)), res.get("months"))
            if more in (100, 200):
                return "%s your spending on %s would cost about %s more a month, %s." % (
                    how, what, _eur(abs(res.get("saved_monthly") or 0)), yr_inc)
            return "%s %s%s would cost about %s more a month, %s." % (
                how, what, obj, _eur(abs(res.get("saved_monthly") or 0)), yr_inc)
''')

rep('''def _render2(tool, res, args, hints):
    if tool == "can_i_afford":
        v = res.get("verdict")
''', '''def _render2(tool, res, args, hints):
    if tool == "can_i_afford" and res.get("verdict") == "caution" and res.get("verdict_text"):
        return str(res["verdict_text"])   # a loan, crypto, gambling or investing: never "it fits" (MAJ-5)
    if tool == "can_i_afford":
        v = res.get("verdict")
''')

rep('''    if tool in ("get_spend", "_food"):
        lab = "food" if tool == "_food" else args.get("label")''',
    '''    if tool == "propose_money_move":
        if res.get("refused"):
            return str(res.get("message") or "I can't set up that move.")
        pr = _g(res, "proposal", {}) or {}
        risk = (" " + str(pr["risk"])) if pr.get("risk") else ""
        return ("Here's the move: %s from your current account to your %s. Nothing moves until you approve it.%s" % (
            _eur_x(pr.get("amount")), pr.get("to") or "savings", risk))
    if tool == "get_savings_and_investments":
        held = [h for h in (res.get("holdings") or []) if isinstance(h, dict)]
        can = _eur(int(res.get("available_to_move") or 0))
        if not held:
            return ("You haven't moved anything to savings or funds in S-mobiili yet. You could move up to %s now "
                    "without touching money for bills." % can)
        return "You have %s. You could move up to %s more now." % (
            _join(["%s in your %s" % (_eur_x(h.get("amount")), h.get("name")) for h in held]), can)

    if tool in ("get_spend", "_food"):
        lab = "food" if tool == "_food" else args.get("label")''')

# ---- helper for destinations
rep('''def _route_en(message, ctx):''', '''def _money_dest(text):
    try:
        from app import money as _money
    except ImportError:   # pragma: no cover
        return None
    return _money.dest_from_text(text)


def _route_en(message, ctx):''')

# ---- Finnish: move and invest
rep('''    (r"\\bsijoit\\w*|\\bosake\\w*|\\brahasto\\w*|\\bkryptovaluutt\\w*", "invest"),''',
    '''    (r"\\bsiirrä\\b|\\bsiirtäisitkö\\b", "move"),
    (r"\\bsäästä\\b|\\blaita säästöön\\b", "save"),
    (r"\\bsäästötilille\\w*|\\bsäästötilil\\w*", "to my savings account"),
    (r"\\bkorkorahastoon\\b", "in the interest fund"),
    (r"\\bindeksirahastoon\\b|\\brahastoon\\b", "in the index fund"),
    (r"\\bsijoit\\w*|\\bosake\\w*|\\brahasto\\w*|\\bkryptovaluutt\\w*", "invest"),''')
open(p, 'w', encoding='utf-8').write(s)
print("coach ok")
