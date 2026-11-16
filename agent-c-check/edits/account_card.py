import sys

root = sys.argv[1]


def rep(path, a, b, n=1):
    p = root + '/' + path
    s = open(p, encoding='utf-8').read()
    assert s.count(a) == n, (path, a[:70], s.count(a))
    open(p, 'w', encoding='utf-8').write(s.replace(a, b))


# ---------------------------------------------------------------- server: GET /api/account
rep('app/server.py', '''def ep_money(req):''', '''def ep_account(req):
    """The customer's simulated S-Bank accounts for the start page: current account balance, savings and
    investments, and what is safe to spend until payday. Figures come from the per-customer data copy, so an
    approved in-app move shows at once. The account number is made up (a hash), never a real or customer id."""
    cap, s = money.available(req.conn, req.today)
    row = req.conn.execute("SELECT COALESCE(-SUM(CASE WHEN type='investment_deposit' THEN amount END), 0), "
                           "COALESCE(SUM(CASE WHEN type='investment_withdrawal' THEN amount END), 0) FROM tx").fetchone()
    saved_total = max(0.0, float(row[0] or 0) - float(row[1] or 0))
    held = money.holdings(req.cid)
    in_app = sum(h["amount"] for h in held)
    digits = int(hashlib.sha256(("acct:" + req.cid).encode()).hexdigest()[:8], 16) % 10000
    parts = [{"name": h["name"], "amount": h["amount"], "kind": h["kind"]} for h in held]
    if saved_total - in_app > 0.005:
        parts.insert(0, {"name": "Earlier savings and investments", "amount": round(saved_total - in_app, 2),
                         "kind": "earlier"})
    return {
        "simulated": True,
        "current": {"name": "S-Bank current account", "number": "FI** **** **** %04d" % digits,
                    "balance": s.get("balance")},
        "savings": {"name": "Savings and investments", "balance": round(saved_total, 2), "parts": parts},
        "safe_to_spend": s.get("safe_total"), "next_payday": s.get("next_payday"),
        "can_move": round(cap, 2), "destinations": money.destinations(),
        "note": "A demo account built from synthetic data. Money only moves inside S-mobiili, after you approve it.",
    }


def ep_money(req):''')
rep('app/server.py', '''    "/api/money": ("GET", ep_money),''', '''    "/api/account": ("GET", ep_account),
    "/api/money": ("GET", ep_money),''')

# ---------------------------------------------------------------- web: the account card at the top
rep('web/app.js', '''    viewEl.appendChild(h('div', { class: 'home' },
      h('div', { class: 'greet' }, h('h1', null, first ? 'Hi ' + first + '!' : 'Hi!'), h('p', { class: 'muted' }, 'What would you like to know about your money?')),
      comp.el, askLink, forYou, starters, thingsBox, convBox));''', '''    var acctBox = h('div', { class: 'acct-slot' });
    viewEl.appendChild(h('div', { class: 'home' },
      acctBox,
      h('div', { class: 'greet' }, h('h1', null, first ? 'Hi ' + first + '!' : 'Hi!'), h('p', { class: 'muted' }, 'What would you like to know about your money?')),
      comp.el, askLink, forYou, starters, thingsBox, convBox));
    api('/api/account').then(function (a) { if (alive(t) && a && a.current) acctBox.replaceChildren(accountCard(a)); }, function () {});''')

rep('web/app.js', '''  // --- Moving money inside S-mobiili: always an explicit approval of one exact move ---''', '''  // --- The simulated bank account at the top of the start page ---
  function accountCard(a) {
    var cur = a.current || {}, sav = a.savings || {};
    var btn = h('button', { type: 'button', class: 'acct-card', 'aria-label': 'Your accounts: current account balance ' + money(cur.balance, { exact: true }) },
      h('span', { class: 'acct-top' }, h('span', { class: 'acct-name' }, cur.name || 'Current account'), h('span', { class: 'acct-num' }, cur.number || '')),
      h('span', { class: 'acct-bal' }, money(cur.balance, { exact: true })),
      h('span', { class: 'acct-rows' },
        h('span', { class: 'acct-row' }, h('span', null, sav.name || 'Savings and investments'), h('b', null, money(sav.balance, { exact: true }))),
        a.safe_to_spend != null ? h('span', { class: 'acct-row' }, h('span', null, 'Safe to spend' + (a.next_payday ? ' until ' + fmtDate(a.next_payday) : '')),
          h('b', null, num(a.safe_to_spend) > 0 ? money(a.safe_to_spend) : 'Nothing')) : null),
      h('span', { class: 'acct-demo' }, 'Demo account · synthetic data'));
    btn.addEventListener('click', function () { openAccount(); });
    return btn;
  }

  function openAccount() {
    var body = openSheet('Your accounts');
    var t = token;
    load(body, t, function () { return api('/api/account'); }, function (a) {
      var cur = a.current || {}, sav = a.savings || {};
      var box = h('div', { class: 'thing-body' });
      box.appendChild(rowsNode([[cur.name + ' ' + (cur.number || ''), money(cur.balance, { exact: true })],
        [sav.name, money(sav.balance, { exact: true })]].concat((sav.parts || []).map(function (p) { return ['  ' + p.name, money(p.amount, { exact: true })]; }))));
      if (a.safe_to_spend != null) box.appendChild(h('p', { class: 'small' }, 'Safe to spend' + (a.next_payday ? ' until payday on ' + fmtDate(a.next_payday) : '') + ': ' + (num(a.safe_to_spend) > 0 ? money(a.safe_to_spend) : 'nothing') + '.'));
      box.appendChild(eyebrow('Latest transactions'));
      var txBox = h('div', null, loadingNode('Loading...'));
      box.appendChild(txBox);
      api('/api/transactions?limit=5').then(function (r) { if (alive(t)) txBox.replaceChildren(txList(r || {}, { bare: true })); },
        function (e) { if (!e.handled) txBox.replaceChildren(errorNode(e)); });
      box.appendChild(eyebrow('Move money'));
      var out = h('div', { 'aria-live': 'polite' });
      box.appendChild(moneyMoveForm(out, a.destinations, a.can_move));
      box.appendChild(out);
      box.appendChild(h('p', { class: 'tiny' }, ht(a.note || '')));
      body.appendChild(box);
    });
  }

  // --- Moving money inside S-mobiili: always an explicit approval of one exact move ---''')

c = root + '/web/styles.css'
css = open(c, encoding='utf-8').read()
css += '''
/* The simulated bank account at the top of the start page */
.acct-slot:empty { display: none; }
.acct-card { display: grid; gap: 6px; width: 100%; text-align: left; border: 0; cursor: pointer;
  background: var(--green-strongest); color: #fff; border-radius: var(--radius, 16px); padding: 16px 18px; margin-bottom: 18px; }
.acct-card:focus-visible { outline: 3px solid var(--green-bright); outline-offset: 2px; }
.acct-top { display: flex; justify-content: space-between; gap: 8px; font-size: 13px; opacity: .9; }
.acct-num { font-variant-numeric: tabular-nums; letter-spacing: .04em; }
.acct-bal { font-size: 34px; font-weight: 800; letter-spacing: -.02em; line-height: 1.1; }
.acct-rows { display: grid; gap: 2px; font-size: 14px; }
.acct-row { display: flex; justify-content: space-between; gap: 8px; }
.acct-row b { font-weight: 700; }
.acct-demo { font-size: 11px; opacity: .7; }
'''
open(c, 'w', encoding='utf-8').write(css)
print("account ok")
