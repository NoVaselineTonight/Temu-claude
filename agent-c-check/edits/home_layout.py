import sys

root = sys.argv[1]
p = root + '/web/app.js'
s = open(p, encoding='utf-8').read()


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (a[:80], s.count(a))
    s = s.replace(a, b)


# ------------------------------------------------------------------ the start page, top to bottom:
# account, greeting + ask, quick actions, "For you" (collapsed rows), Your things, Conversations.
rep('''    var comp = composer('Ask Svinkki', 'Ask Svinkki a question', function (text) { openConversation({ message: text }); });
    var askLink = h('button', { type: 'button', class: 'link-btn ask-link', 'aria-haspopup': 'dialog', onclick: function () { openAsk(); } }, icon('help', 18), 'What can I ask?');
    var forYou = h('div', { class: 'for-you-cards', role: 'group', 'aria-label': 'Ready for you' });
    var starters = h('div', { class: 'starters', hidden: true });
    var thingsBox = h('div', { class: 'home-sec' }, sectionHead('Your things'), loadingNode('Loading...'));
    var convBox = h('div', { class: 'home-sec' });
    var acctBox = h('div', { class: 'acct-slot' });
    viewEl.appendChild(h('div', { class: 'home' },
      acctBox,
      h('div', { class: 'greet' }, h('h1', null, first ? 'Hi ' + first + '!' : 'Hi!'), h('p', { class: 'muted' }, 'What would you like to know about your money?')),
      comp.el, askLink, forYou, starters, thingsBox, convBox));
    api('/api/account').then(function (a) { if (alive(t) && a && a.current) acctBox.replaceChildren(accountCard(a)); }, function () {});

    // Ready for you, right on the start page: the check-in, this week's quiz and anything worth a look.
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
    }, function () {});''',
    '''    var comp = composer('Ask about your money', 'Ask Svinkki a question', function (text) { openConversation({ message: text }); });
    var askLink = h('button', { type: 'button', class: 'link-btn ask-link', 'aria-haspopup': 'dialog', onclick: function () { openAsk(); } }, icon('help', 18), 'What can I ask?');
    var forYou = h('div', { class: 'home-sec', hidden: true });
    var fyList = h('div', { class: 'list-card fy-list', role: 'group', 'aria-label': 'Ready for you' });
    forYou.appendChild(sectionHead('For you'));
    forYou.appendChild(fyList);
    var starters = h('div', { class: 'starters', hidden: true });
    var thingsBox = h('div', { class: 'home-sec', hidden: true });
    var convBox = h('div', { class: 'home-sec' });
    var acctBox = h('div', { class: 'acct-slot' });
    viewEl.appendChild(h('div', { class: 'home' },
      acctBox,
      h('div', { class: 'greet' }, h('h1', null, first ? 'Hi ' + first + '!' : 'Hi!')),
      comp.el, askLink, quickActions(), forYou, thingsBox, convBox, starters));
    api('/api/account').then(function (a) { if (alive(t) && a && a.current) acctBox.replaceChildren(accountCard(a)); }, function () {});

    // "For you": the check-in, this week's quiz and anything worth a look, each one line, collapsed until tapped.
    var slots = { checkin: h('div'), quiz: h('div'), alerts: h('div') };
    fyList.appendChild(slots.checkin); fyList.appendChild(slots.quiz); fyList.appendChild(slots.alerts);
    function place(key, ic, title, summary, build) {
      if (!alive(t)) return;
      slots[key].replaceChildren(foldRow(ic, title, summary, build));
      forYou.hidden = false;
    }
    api('/api/checkin').then(function (r) {
      if (!(r && r.due && r.checkin)) return;
      var c = r.checkin, sur = num(c.surplus);
      place('checkin', 'calendar', 'Your check-in' + (c.period && c.period.from ? ', ' + fmtMonthOf(c.period.from) : ''),
        sur >= 0 ? money(sur) + ' left over' : money(-sur) + ' more out than in', function () { return checkinCard(c); });
    }, function () {});
    api('/api/quiz').then(function (q) {
      if (q && q.quiz_id) place('quiz', 'help', 'This week\\'s quiz', 'Guess, then see the real figure', function () { return quizCard(q); });
    }, function () {});
    api('/api/alerts').then(function (d) {
      var list = (d && Array.isArray(d.alerts)) ? d.alerts : [];
      if (list.length) place('alerts', 'flag', 'Worth a look', plural(list.length, 'thing', 'things') + ' stand out',
        function () { return CARDS.alerts({ alerts: list, explain: d.explain }); });
    }, function () {});''')

# Your things: only shown when there is something in it
rep('''      thingsBox.replaceChildren(sectionHead('Your things'));
      if (!things.length) {
        thingsBox.appendChild(h('p', { class: 'quiet-line' }, 'Things you set up in a conversation, such as a savings goal, show up here.'));
      } else {''', '''      thingsBox.replaceChildren(sectionHead('Your things'));
      thingsBox.hidden = !things.length;
      if (things.length) {''')
# the "Try one" chips are replaced by the quick actions
rep('''      // A few starter questions until the first conversation exists.
      starters.hidden = !!convs.length;
      if (!convs.length) {''', '''      // The quick actions replace the old "Try one" starter chips.
      starters.hidden = true;
      if (false) {''')

# ------------------------------------------------------------------ helpers
rep('''  function convRow(cv) {''', '''  // One-tap shortcuts to the things that used to sit behind the chat or "What can I ask?".
  function quickActions() {
    var acts = [
      ['list', 'Where it went', function () { openConversation({ message: 'Where did my money go last month?' }); }],
      ['wallet', 'Safe to spend', function () { openConversation({ message: 'What can I safely spend this week?' }); }],
      ['tag', 'Can I afford it?', function () { openConversation({ insert: 'afford' }); }],
      ['sliders', 'What if...', function () { openConversation({ insert: 'whatif' }); }],
      ['coin', 'Save & invest', function () { openAccount(); }],
      ['flag', 'Savings goal', function () { openThing({ id: 'goal', kind: 'goal', title: 'Savings goal' }); }],
      ['target', 'Money leaks', function () { openConversation({ message: 'Where is my money leaking?' }); }],
      ['receipt', 'Receipts', function () { openConversation({ message: 'Show my receipts' }); }]
    ];
    return h('div', { class: 'qa-grid', role: 'group', 'aria-label': 'Quick actions' }, acts.map(function (a) {
      return h('button', { type: 'button', class: 'qa', onclick: a[2] }, h('span', { class: 'qa-ico' }, icon(a[0], 20)), h('span', { class: 'qa-label' }, a[1]));
    }));
  }

  // A collapsed row that builds its card the first time it is opened.
  function foldRow(ic, title, summary, build) {
    var body = h('div', { class: 'fold-body' });
    var d = h('details', { class: 'fold' },
      h('summary', { class: 'thing-row fold-sum' }, h('span', { class: 'thing-ico' }, icon(ic, 20)),
        h('span', { class: 'thing-text' }, h('b', null, title), h('span', { class: 'tiny' }, summary)),
        h('span', { class: 'chev' }, icon('chev', 18))),
      body);
    d.addEventListener('toggle', function () {
      if (d.open && !body.firstChild) { try { body.appendChild(build()); } catch (e) { body.appendChild(errorNode(e)); } }
    });
    return d;
  }

  function fmtMonthOf(iso) {
    var m = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
    var k = Number(String(iso || '').slice(5, 7));
    return k >= 1 && k <= 12 ? m[k - 1] : '';
  }

  function convRow(cv) {''')
open(p, 'w', encoding='utf-8').write(s)

c = root + '/web/styles.css'
css = open(c, encoding='utf-8').read()
css += '''
/* Start page: quick actions and collapsed "For you" rows */
.home .greet h1 { font-size: 24px; }
.qa-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; margin-top: 18px; }
.qa { display: flex; flex-direction: column; align-items: center; gap: 6px; padding: 10px 2px; min-height: 76px;
  background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); cursor: pointer;
  color: var(--green-strongest); font: inherit; font-size: 12px; font-weight: 600; line-height: 1.2; text-align: center; }
.qa:hover { background: var(--surface-soft); }
.qa:focus-visible { outline: 3px solid var(--green-medium); outline-offset: 2px; }
.qa-ico { width: 36px; height: 36px; border-radius: 50%; background: var(--mint-soft); display: inline-flex; align-items: center; justify-content: center; }
.fy-list > div:empty { display: none; }
.fold > summary { list-style: none; cursor: pointer; }
.fold > summary::-webkit-details-marker { display: none; }
.fold .chev { transition: transform .15s; }
.fold[open] .chev { transform: rotate(90deg); }
.fold-body { padding: 0 12px 12px; }
.fold-body > .card { box-shadow: none; border: 0; padding: 0; }
'''
open(c, 'w', encoding='utf-8').write(css)
print("layout ok")
