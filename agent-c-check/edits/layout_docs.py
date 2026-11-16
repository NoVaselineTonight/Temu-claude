import sys

root = sys.argv[1]


def rep(path, a, b):
    p = root + '/' + path
    s = open(p, encoding='utf-8').read()
    assert s.count(a) == 1, (path, a[:70], s.count(a))
    open(p, 'w', encoding='utf-8').write(s.replace(a, b))


rep('DEMO.md', '''Say: "This is his account as the bank sees it; everything below works from these numbers."''',
    '''Say: "This is his account as the bank sees it; everything below works from these numbers." Below the ask box are eight quick actions (Where it went, Safe to spend, Can I afford it?, What if..., Save & invest, Savings goal, Money leaks, Receipts), and "For you" lists the check-in, this week's quiz and anything worth a look as collapsed rows; tap one to open it.''')
rep('DEMO.md', '''13. **Save it, with permission.** Back on the front page, the check-in card says''',
    '''13. **Save it, with permission.** Back on the front page, open the check-in row under "For you": it says''')
rep('README.md', '''- Monthly check-in, this week's quiz and "Worth a look" right on the start page.''',
    '''- Start page: the account card, the ask box, eight quick actions for the main features, and "For you" with the monthly check-in, this week's quiz and "Worth a look" as collapsed rows.''')
rep('HANDOFF.md', '''  tap for transactions and "Move money"), then the check-in, the weekly quiz and "Worth a look" as cards.''',
    '''  tap for transactions and "Move money"), the ask box, eight quick-action tiles, then "For you" with the
  check-in, the weekly quiz and "Worth a look" as collapsed rows. "Your things" only shows when it has items.''')
print("docs ok")
