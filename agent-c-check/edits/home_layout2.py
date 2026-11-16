import sys

root = sys.argv[1]
p = root + '/web/app.js'
s = open(p, encoding='utf-8').read()


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (a[:80], s.count(a))
    s = s.replace(a, b)


# the goal tile opens a form even when there is no goal yet
rep('''      var g = (res && res.goal) || null;
      if (!g) {
        body.appendChild(h('p', { class: 'muted' }, 'You have no savings goal right now. Tell me about one in a conversation, for example "I am saving for Japan in 2027".'));
        return;
      }
      var box = h('div', { class: 'thing-body' });
      var tg = num(g.target), sv = num(g.saved);
      keyFig(box, euros(sv) + ' of ' + euros(tg), 'saved so far');
      var fill = h('div', { class: 'prog-fill' });
      fill.style.width = (tg > 0 ? Math.min(100, sv / tg * 100) : 0) + '%';
      box.appendChild(h('div', { class: 'prog-track', role: 'img', 'aria-label': pct(tg > 0 ? sv / tg * 100 : 0) + ' of the goal' }, fill));''',
    '''      var g = (res && res.goal) || null;
      var isNew = !g;
      g = g || { name: '', target: '', saved: 0 };
      var box = h('div', { class: 'thing-body' });
      var tg = num(g.target), sv = num(g.saved);
      if (isNew) {
        box.appendChild(h('p', { class: 'small' }, 'What are you saving for? Svinkki uses it to show what a purchase does to your goal.'));
      } else {
        keyFig(box, euros(sv) + ' of ' + euros(tg), 'saved so far');
        var fill = h('div', { class: 'prog-fill' });
        fill.style.width = (tg > 0 ? Math.min(100, sv / tg * 100) : 0) + '%';
        box.appendChild(h('div', { class: 'prog-track', role: 'img', 'aria-label': pct(tg > 0 ? sv / tg * 100 : 0) + ' of the goal' }, fill));
      }''')
rep('''      name.value = g.name || ''; target.value = String(tg); saved.value = String(sv);''',
    '''      name.value = g.name || ''; target.value = isNew ? '' : String(tg); saved.value = String(sv);
      if (isNew) { name.placeholder = 'A trip to Japan'; target.placeholder = '3000'; }''')
rep('''      var save = h('button', { type: 'button', class: 'btn block' }, 'Save changes');''',
    '''      var save = h('button', { type: 'button', class: 'btn block' }, isNew ? 'Create goal' : 'Save changes');''')
rep('''      box.appendChild(save);
      box.appendChild(msg);
      box.appendChild(clear);''', '''      box.appendChild(save);
      box.appendChild(msg);
      if (!isNew) box.appendChild(clear);''')

# grammar
rep('''plural(list.length, 'thing', 'things') + ' stand out',''',
    '''plural(list.length, 'thing', 'things') + (list.length === 1 ? ' stands out' : ' stand out'),''')
open(p, 'w', encoding='utf-8').write(s)

c = root + '/web/styles.css'
css = open(c, encoding='utf-8').read()
css += '''.fold-body > .card > .card-head .card-titles { display: none; }   /* the row above already names it */
'''
open(c, 'w', encoding='utf-8').write(css)
print("layout2 ok")
