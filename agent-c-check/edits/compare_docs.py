import sys

root = sys.argv[1]


def rep(path, a, b):
    p = root + '/' + path
    s = open(p, encoding='utf-8').read()
    assert s.count(a) == 1, (path, a[:70], s.count(a))
    open(p, 'w', encoding='utf-8').write(s.replace(a, b))


rep('DEMO.md', '''Reply: "You spent €92.85 on taxis in August (2 payments). That is €76 more than most people your age nearby spend in a month." Open "Transactions used (2)". Say: "The number comes with the two rides it was added from."''',
    '''Reply: "You spent €92.85 on taxis in August (2 payments)." Open "Transactions used (2)". Say: "The number comes with the two rides it was added from. It only compares me with other people when I ask: try 'How does that compare with people my age?'"''')
rep('HANDOFF.md', '''- **Start page:** the check-in, the weekly quiz and "Worth a look" are cards on the front page.''',
    '''- **Start page:** the check-in, the weekly quiz and "Worth a look" are cards on the front page.
- **No unasked comparisons (owner, 14 Nov):** answers about the customer's own money never compare with other
  people unless the message asks for it (`coach.compare_requested`). The model only sees the comparison tools
  then; alerts and the quiz compare with the customer's own usual spending only.''')
rep('HANDOFF.md', '''printed `Ran 650 tests ... OK` at the last run (14 Nov, about 01:00).''',
    '''printed `Ran 653 tests ... OK` at the last run (14 Nov, about 01:30).''')
rep('README.md', '''The last run printed `Ran 650 tests in 42.6s` and `OK`.''', '''The last run printed `Ran 653 tests in 54.2s` and `OK`.''')
rep('README.md', '''- Benchmarks against groups of similar customers''', '''- Benchmarks against groups of similar customers, only when the customer asks for a comparison''')
print("docs ok")
