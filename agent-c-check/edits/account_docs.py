import sys

root = sys.argv[1]


def rep(path, a, b):
    p = root + '/' + path
    s = open(p, encoding='utf-8').read()
    assert s.count(a) == 1, (path, a[:70], s.count(a))
    open(p, 'w', encoding='utf-8').write(s.replace(a, b))


rep('DEMO.md', '''7. **Ask: "Can I afford a 300 euro jacket?"** Reply: yes, and about €35 a day is still left until payday on 15 October.''',
    '''7. **Ask: "Can I afford a 300 euro jacket?"** Reply: yes, with about €16 a day left until payday on 31 October. (Veeti's salary day alternates between the 15th and month end, so Svinkki plans for the later one.)''')
rep('DEMO.md', '''3. **The front page.**''', '''3. **The front page.** At the top is his simulated S-Bank account: the current account balance (€2,227.52), savings and investments, and what is safe to spend until payday. Tap it for the latest transactions and "Move money". Say: "This is his account as the bank sees it; everything below works from these numbers."''')
rep('submission/VIDEO_SCRIPT.md', '''"Yes, and about €35 a day is still left until payday.''', '''"Yes, and about €16 a day is still left until payday.''')
rep('README.md', '''- Monthly check-in, this week's quiz and "Worth a look" right on the start page.''',
    '''- A simulated S-Bank account at the top of the start page: current account balance, savings and investments, and what is safe to spend until payday; tap it for the latest transactions and "Move money" (`GET /api/account`).
- Monthly check-in, this week's quiz and "Worth a look" right on the start page.''')
rep('HANDOFF.md', '''- **Start page:** the check-in, the weekly quiz and "Worth a look" are cards on the front page.''',
    '''- **Start page:** a simulated S-Bank account card at the top (balance, savings and investments, safe to spend;
  tap for transactions and "Move money"), then the check-in, the weekly quiz and "Worth a look" as cards.''')
rep('HANDOFF.md', '''printed `Ran 653 tests ... OK` at the last run (14 Nov, about 01:30).''',
    '''printed `Ran 655 tests ... OK` at the last run (14 Nov, about 02:00).''')
rep('README.md', '''The last run printed `Ran 653 tests in 54.2s` and `OK`.''', '''The last run printed `Ran 655 tests in 54.1s` and `OK`.''')
print("docs ok")
