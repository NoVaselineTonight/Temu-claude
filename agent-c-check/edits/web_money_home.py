import sys

root = sys.argv[1]
p = root + '/web/app.js'
s = open(p, encoding='utf-8').read()


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (a[:80], s.count(a))
    s = s.replace(a, b)


# ---- the approval card: the only way money moves
rep('''  // --- Can I afford this? ---
  var VERDICT_WORDS = { yes: 'Yes', tight: 'Tight', no: 'Not right now' };''',
    '''  // --- Moving money inside S-mobiili: always an explicit approval of one exact move ---
  function moneyProposalCard(pr) {
    var c = cardShell('Approve this move?', 'Inside S-mobiili', 'money-card');
    keyFig(c, money(pr.amount), 'to your ' + (pr.to || 'savings'));
    c.appendChild(rowsNode([['From', pr.from || 'Your current account'], ['To', pr.to || ''],
      pr.balance_after != null ? ['Balance after', money(pr.balance_after)] : null].filter(Boolean)));
    if (pr.about) c.appendChild(h('p', { class: 'small' }, ht(pr.about)));
    if (pr.risk) c.appendChild(h('p', { class: 'notice' }, ht(pr.risk)));
    c.appendChild(h('p', { class: 'tiny' }, ht(pr.note || 'Nothing moves until you approve.')));
    var msg = h('div', { 'aria-live': 'polite' });
    var row = h('div', { class: 'btn-row' });
    var yes = h('button', { type: 'button', class: 'btn' }, 'Approve and move ' + money(pr.amount));
    var no = h('button', { type: 'button', class: 'btn secondary' }, 'Cancel');
    function answer(approve) {
      yes.disabled = true; no.disabled = true;
      msg.replaceChildren(loadingNode(approve ? 'Moving...' : 'Cancelling...'));
      api('/api/money/confirm', { method: 'POST', body: { proposal_id: pr.id, approve: approve, amount: pr.amount, dest: pr.dest } }).then(function (r) {
        row.hidden = true;
        var ok = r && r.ok !== false;
        msg.replaceChildren(h('p', { class: 'notice ' + (ok && r.moved ? 'ok' : (ok ? '' : 'err')) }, ht((r && r.message) || (approve ? 'Done.' : 'Nothing was moved.'))));
        if (r && r.moved) thingsChanged();
      }, function (e) {
        yes.disabled = false; no.disabled = false;
        if (!e.handled) msg.replaceChildren(errorNode(e));
      });
    }
    yes.addEventListener('click', function () { answer(true); });
    no.addEventListener('click', function () { answer(false); });
    row.appendChild(yes); row.appendChild(no);
    c.appendChild(row); c.appendChild(msg);
    return c;
  }

  // A small form for moving money yourself: pick where, pick how much, then approve on the next card.
  function moneyMoveForm(out, dests, available) {
    var uid = 'mv-' + Math.random().toString(36).slice(2, 7);
    var sel = h('select', { class: 'input', id: uid + '-d' });
    (dests || []).forEach(function (d) { sel.appendChild(h('option', { value: d.id }, d.name)); });
    var amt = h('input', { type: 'number', class: 'input', id: uid + '-a', min: '5', step: '1', inputmode: 'decimal', placeholder: '50' });
    var btn = h('button', { type: 'button', class: 'btn block' }, 'Show the move');
    btn.addEventListener('click', function () {
      var v = Number(amt.value);
      if (!isFinite(v) || v <= 0) { out.replaceChildren(h('p', { class: 'notice' }, 'Enter an amount above zero.')); return; }
      btn.disabled = true;
      api('/api/money/propose', { method: 'POST', body: { dest: sel.value, amount: v } }).then(function (r) {
        btn.disabled = false;
        if (r && r.proposal) out.replaceChildren(moneyProposalCard(r.proposal));
        else out.replaceChildren(h('p', { class: 'notice' }, ht((r && r.message) || 'That move is not possible.')));
      }, function (e) { btn.disabled = false; if (!e.handled) out.replaceChildren(errorNode(e)); });
    });
    return h('div', { class: 'form' },
      available != null ? h('p', { class: 'small' }, 'You can move up to ' + money(Math.floor(num(available))) + ' now without touching money for bills.') : null,
      h('div', { class: 'form-grid' },
        h('div', null, h('label', { for: uid + '-d' }, 'Where to'), sel),
        h('div', null, h('label', { for: uid + '-a' }, 'Amount in euros'), amt)),
      btn);
  }

  // --- Can I afford this? ---
  var VERDICT_WORDS = { yes: 'Yes', tight: 'Tight', no: 'Not right now', caution: 'Think twice' };''')

rep('''  function affordInto(c, d) {
    var v = VERDICT_WORDS[d.verdict] ? d.verdict : 'tight';
    c.appendChild(h('div', { class: 'verdict v-' + v }, VERDICT_WORDS[v]));''',
    '''  function affordInto(c, d) {
    var v = VERDICT_WORDS[d.verdict] ? d.verdict : 'tight';
    c.appendChild(h('div', { class: 'verdict v-' + v }, VERDICT_WORDS[v]));
    if (v === 'caution' && d.verdict_text) c.appendChild(h('p', { class: 'small' }, ht(d.verdict_text)));''')

# accepting a set-aside suggestion opens the approval card
rep('''      api('/api/suggestions/action', { method: 'POST', body: { id: s.id, action: action } }).then(function (r) {
        row.hidden = true;
        msg.replaceChildren(h('p', { class: 'notice ok' }, (r && r.message) ? ht(r.message) : (action === 'accept' ? 'Noted. No money was moved.' : 'Okay, we will leave it for now.')));''',
    '''      api('/api/suggestions/action', { method: 'POST', body: { id: s.id, action: action } }).then(function (r) {
        row.hidden = true;
        if (r && r.proposal) { msg.replaceChildren(moneyProposalCard(r.proposal)); return; }
        msg.replaceChildren(h('p', { class: 'notice ' + (r && r.ok === false ? '' : 'ok') }, (r && r.message) ? ht(r.message) : (action === 'accept' ? 'Noted.' : 'Okay, we will leave it for now.')));''')

# chat cards for the two money tools
rep('''    alerts: function (d) {
      var c = cardShell('Worth a look');''', '''    money_proposal: function (d) {
      if (d.refused || !d.proposal) {
        var c0 = cardShell('Move money');
        c0.appendChild(h('p', { class: 'notice' }, ht(d.message || 'That move is not possible.')));
        return c0;
      }
      return moneyProposalCard(d.proposal);
    },
    money_holdings: function (d) {
      var c = cardShell('Savings and investments', 'In S-mobiili');
      var held = d.holdings || [];
      if (held.length) addRows(c, held.map(function (x) { return [x.name, money(x.amount)]; }));
      else c.appendChild(h('p', { class: 'small muted' }, 'Nothing moved yet.'));
      var out = h('div', { 'aria-live': 'polite' });
      more(c, [moneyMoveForm(out, d.destinations, d.available_to_move), out]);
      return c;
    },
    alerts: function (d) {
      var c = cardShell('Worth a look');''')

# what-if: an increase is a cost, not a saving (MAJ-4)
rep('''    what_if: function (d) {
      var months = num(d.months) || 12;
      var c = cardShell('If you spent less');''', '''    what_if: function (d) {
      var months = num(d.months) || 12;
      if (d.direction === 'increase' || num(d.saved_monthly) < 0) {
        var ci = cardShell('If you spent more');
        keyFig(ci, euros(-num(d.saved_monthly) * 12), 'extra a year');
        addRows(ci, [['A month', money(-num(d.saved_monthly)) + ' more'], ['Spending a month', euros(d.baseline_monthly) + ' to ' + euros(d.new_monthly)]]);
        more(ci, [rowsNode((d.lines || []).map(function (l) { return [targetName(l.target), euros(l.baseline) + ' to ' + euros(l.new) + ' a month']; }))], d);
        return ci;
      }
      var c = cardShell('If you spent less');''')

# "Your things": savings and funds
rep('''    quiz: { name: 'Quiz score', icon: 'help' },
    pin: { name: 'Kept answer', icon: 'pin' }''', '''    quiz: { name: 'Quiz score', icon: 'help' },
    money: { name: 'Savings and investments', icon: 'coin' },
    pin: { name: 'Kept answer', icon: 'pin' }''')
rep('''    } else if (kind === 'target') targetThing(body, done);''', '''    } else if (kind === 'money') {
      load(body, t, function () { return api('/api/money'); }, function (m) {
        var box = h('div', { class: 'thing-body' });
        var held = m.holdings || [];
        box.appendChild(rowsNode(held.map(function (x) { return [x.name, money(x.amount)]; })) || h('p', { class: 'muted' }, 'Nothing moved yet.'));
        box.appendChild(h('p', { class: 'tiny' }, 'Demo: fund values do not change here. Money only moves after you approve it, and it stays in S-mobiili.'));
        var out = h('div', { 'aria-live': 'polite' });
        box.appendChild(eyebrow('Move more'));
        box.appendChild(moneyMoveForm(out, m.destinations, m.available));
        box.appendChild(out);
        body.appendChild(box);
      });
    } else if (kind === 'target') targetThing(body, done);''')

# ---- start page: check-in, quiz and worth-a-look as cards, not chips
rep('''    var forYou = h('div', { class: 'chips for-you', role: 'group', 'aria-label': 'Ready for you' });''',
    '''    var forYou = h('div', { class: 'for-you-cards', role: 'group', 'aria-label': 'Ready for you' });''')
rep('''    // Things that are ready: the check-in, the quiz, anything worth a look.
    function ready(text, ic, onTap) {
      forYou.appendChild(h('button', { type: 'button', class: 'chip ready' }, icon(ic, 16), text));
      forYou.lastChild.addEventListener('click', onTap);
    }
    api('/api/checkin').then(function (r) {
      if (alive(t) && r && r.due && r.checkin) ready('Your check-in is ready', 'calendar', function () { openConversation({ insert: 'checkin', pre: r }); });
    }, function () {});
    api('/api/quiz').then(function (q) {
      if (alive(t) && q && q.quiz_id) ready('This week\\'s quiz', 'help', function () { openConversation({ insert: 'quiz', pre: q }); });
    }, function () {});
    api('/api/alerts').then(function (d) {
      var list = (d && Array.isArray(d.alerts)) ? d.alerts : [];
      if (alive(t) && list.length) ready(list.length === 1 ? '1 thing worth a look' : list.length + ' things worth a look', 'flag',
        function () { openConversation({ insert: 'alerts', pre: { alerts: list, explain: d.explain } }); });
    }, function () {});''',
    '''    // Ready for you, right on the start page: the check-in, this week's quiz and anything worth a look.
    var slots = { checkin: h('div'), quiz: h('div'), alerts: h('div') };
    forYou.appendChild(slots.checkin); forYou.appendChild(slots.quiz); forYou.appendChild(slots.alerts);
    function place(key, node) {
      if (!alive(t) || !node) return;
      slots[key].replaceChildren(node);
      if (!forYou.querySelector('.sec-head')) forYou.insertBefore(sectionHead('For you'), forYou.firstChild);
    }
    api('/api/checkin').then(function (r) {
      if (r && r.due && r.checkin) place('checkin', checkinCard(r.checkin));
    }, function () {});
    api('/api/quiz').then(function (q) {
      if (q && q.quiz_id) place('quiz', quizCard(q));
    }, function () {});
    api('/api/alerts').then(function (d) {
      var list = (d && Array.isArray(d.alerts)) ? d.alerts : [];
      if (list.length) place('alerts', CARDS.alerts({ alerts: list, explain: d.explain }));
    }, function () {});''')
open(p, 'w', encoding='utf-8').write(s)

c = root + '/web/styles.css'
css = open(c, encoding='utf-8').read()
css += '''
/* Approving an in-app money move; "Think twice" for loans, crypto, gambling and investing */
.verdict.v-caution { color: var(--warning); background: var(--warning-bg); }
.money-card { border: 2px solid var(--green-medium); }
.money-card .btn-row { margin-top: 12px; }
.for-you-cards { display: grid; gap: 12px; margin-top: 20px; }
.for-you-cards:empty { display: none; }
.for-you-cards > div:empty { display: none; }
'''
open(c, 'w', encoding='utf-8').write(css)
print("web ok")
