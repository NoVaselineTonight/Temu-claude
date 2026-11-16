import sys

p = sys.argv[1]
s = open(p, encoding='utf-8').read()


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (a[:70], s.count(a))
    s = s.replace(a, b)


rep('''NO_MONEY_MESSAGES = {
    "accept": "Noted. I saved your intention. No money was moved: Svinkki cannot move money, "
              "so you decide when and how to set it aside.",''', '''NO_MONEY_MESSAGES = {
    "accept": "Noted. I saved your choice.",''')

rep('''                req.conn = db.sandbox(req.cid, req.today,
                                      state.list_overrides(req.cid))  # SR-2''', '''                req.conn = db.sandbox(req.cid, req.today, state.list_overrides(req.cid),
                                      state.list_moves(req.cid))  # SR-2''')
rep('''        conn = db.sandbox(req.cid, req.today, state.list_overrides(req.cid))
    try:
        result["used"]''', '''        conn = db.sandbox(req.cid, req.today, state.list_overrides(req.cid), state.list_moves(req.cid))
    try:
        result["used"]''')
rep('''    conn = db.sandbox(req.cid, req.today, state.list_overrides(req.cid))
    try:
        return {"override"''', '''    conn = db.sandbox(req.cid, req.today, state.list_overrides(req.cid), state.list_moves(req.cid))
    try:
        return {"override"''')

rep('''    def save_goal(name, target, deadline=None, monthly_needed=None):''', '''    def propose_money(dest, amount, reason=""):
        """The coach can only create a proposal; the customer approves it in the app (POST /api/money/confirm)."""
        return money.propose(req.conn, req.today, req.cid, dest, amount, reason, "chat")

    def save_goal(name, target, deadline=None, monthly_needed=None):''')
rep('''                          explain=explain, save_goal=save_goal, memory=memory)''', '''                          explain=explain, save_goal=save_goal, memory=memory,
                          propose_money=propose_money, holdings=money.holdings(req.cid))''')

rep('''    checkin["suggestions"] = suggestions
    return {"due": True, "checkin": checkin}''', '''    checkin["suggestions"] = _money_suggestions(req, suggestions)
    return {"due": True, "checkin": checkin}


_MONEY_KINDS = ("save_surplus", "build_buffer")


def _money_suggestions(req, suggestions):
    """MAJ-6: a set-aside suggestion never offers more than is safe to move before payday, and says how the
    move works. Below 20 euros it is dropped."""
    out = []
    cap = None
    for s in suggestions:
        if s.get("kind") in _MONEY_KINDS:
            if cap is None:
                cap = money.available(req.conn, req.today)[0]
            amt = float(int(min(float(s.get("amount") or 0), cap)))
            if amt < 20:
                continue
            s = dict(s)
            word = "buffer" if s["kind"] == "build_buffer" else "savings"
            first = str(s.get("detail") or "").split(". You could")[0].split(". Would you")[0].rstrip(".")
            s.update({"amount": amt, "dest": "savings",
                      "title": "Move %s to your S-Bank savings account?" % _money_text(amt),
                      "detail": ("%s. You can move up to %s now without touching money needed for bills before "
                                 "payday. I will show you the move and ask you to approve it first; the money "
                                 "stays in S-mobiili." % (first, _money_text(int(cap)))),
                      "action_label": "Move %s to %s" % (_money_text(amt), word)})
        out.append(s)
    return out''')

rep('''    if not req.consent.get("suggestions"):
        raise ApiError(403, "consent_required")
    state.record_intent(req.cid, sid, action)
    return {"ok": True, "message": NO_MONEY_MESSAGES[action]}''', '''    if not req.consent.get("suggestions"):
        raise ApiError(403, "consent_required")
    if action == "accept" and sid.split(":", 1)[0] in _MONEY_KINDS:
        # Accepting a set-aside suggestion does not move money: it opens an approval for that exact move.
        current = ep_checkin(req).get("checkin") or {}
        sug = next((x for x in (current.get("suggestions") or []) if x.get("id") == sid), None)
        if sug is None:
            return {"ok": False, "message": "This suggestion is no longer available."}
        try:
            prop = money.propose(req.conn, req.today, req.cid, "savings", sug["amount"],
                                 sug.get("title", ""), "checkin:" + sid)
        except money.MoneyError as e:
            return {"ok": False, "message": str(e)}
        return {"ok": True, "proposal": prop,
                "message": "Here is the move. Nothing happens until you approve it."}
    state.record_intent(req.cid, sid, action)
    return {"ok": True, "message": NO_MONEY_MESSAGES[action]}


# ---------------------------------------------------------------------------
# In-app money moves: propose (anyone in the app, including the coach), confirm (only the customer)
# ---------------------------------------------------------------------------

def ep_money(req):
    cap, s = money.available(req.conn, req.today)
    return {"holdings": money.holdings(req.cid), "destinations": money.destinations(),
            "available": round(cap, 2), "balance": s.get("balance"), "next_payday": s.get("next_payday")}


def ep_money_propose(req):
    b = req.body
    dest = b.get("dest")
    if not isinstance(dest, str) or dest not in money.DEST_IDS:
        raise ApiError(400, "invalid_destination")   # no free-form destination exists
    amount = b.get("amount")
    if isinstance(amount, bool) or not isinstance(amount, (int, float)):
        raise ApiError(400, "invalid_amount")
    reason = b.get("reason")
    reason = reason[:200] if isinstance(reason, str) else ""
    try:
        prop = money.propose(req.conn, req.today, req.cid, dest, amount, reason, "app")
    except money.MoneyError as e:
        return {"ok": False, "message": str(e)}
    return {"ok": True, "proposal": prop}


def ep_money_confirm(req):
    """The only way money moves: the customer approves one proposal, naming its amount and destination."""
    b = req.body
    pid, approve = b.get("proposal_id"), b.get("approve")
    if not isinstance(pid, str) or not isinstance(approve, bool):
        raise ApiError(400, "invalid_request")
    got = state.get_proposal(req.cid, pid) if 0 < len(pid) <= 64 else None
    try:
        res = money.confirm(req.conn, req.today, req.cid, pid, approve, b.get("amount"), b.get("dest"))
    except money.MoneyError as e:
        return {"ok": False, "moved": False, "message": str(e)}
    src = str(((got or {}).get("data") or {}).get("source") or "")
    if res.get("moved") and src.startswith("checkin:"):
        state.record_intent(req.cid, src[len("checkin:"):], "accept")
    return res''')

rep('''    for p in state.list_pins(cid):''', '''    for hd in money.holdings(cid):
        things.append({"id": "money:" + hd["id"], "kind": "money", "title": hd["name"],
                       "summary": "%s %s in S-mobiili" % (_money_text(hd["amount"]),
                                                          "saved" if hd["kind"] == "savings" else "invested")})
    for p in state.list_pins(cid):''')

rep('''    "/api/home": ("GET", ep_home),''', '''    "/api/home": ("GET", ep_home),
    "/api/money": ("GET", ep_money),
    "/api/money/propose": ("POST", ep_money_propose),
    "/api/money/confirm": ("POST", ep_money_confirm),''')
open(p, 'w', encoding='utf-8').write(s)
print("server ok")
