import sys

root = sys.argv[1]


def rep(path, a, b):
    p = root + '/' + path
    s = open(p, encoding='utf-8').read()
    assert s.count(a) == 1, (path, a[:70], s.count(a))
    open(p, 'w', encoding='utf-8').write(s.replace(a, b))


rep('README.md', 'Python 3.13, standard library only. Nothing is installed. Nothing moves money.',
    'Python 3.13, standard library only. Nothing is installed. Money moves only inside S-mobiili (your own '
    'savings account or an S-Bank fund) and only after you approve that exact move.')
rep('README.md', '- Monthly check-in with opt-in suggestions. Accepting one records the intent and never moves money.',
    '- Monthly check-in, this week\'s quiz and "Worth a look" right on the start page.\n'
    '- Save and invest inside S-mobiili: the coach or a check-in suggestion offers a move to your own S-Bank '
    'savings account or an S-Bank fund; an approval card shows the amount, from, to and the balance after, and '
    'nothing moves until you tap "Approve". A move never takes money needed for bills before payday, and nothing '
    'can go outside S-mobiili (`app/money.py`).')
rep('README.md', '## Privacy and security\n', '''## Privacy and security

- Moving money (owner decision, 14 Nov 2026, for the demo): the AI model and the built-in rules can only
  *propose* a move. Money moves only when the customer approves that one proposal in the app, naming its
  amount and destination, within 15 minutes, once. Destinations are a fixed list inside S-mobiili; payments,
  rent, IBANs and transfers to other people or banks are refused. Moves are recorded in the demo state, not at
  a bank, and "Reset demo" undoes them.
''')

rep('DEMO.md', '''For a two-minute slot do steps 1, 3, 4, 5, 8 and 9.''',
    '''13. **Save it, with permission.** Back on the front page, the check-in card says what was left over and offers "Move €307 to savings" (the amount never exceeds what is safe before payday). Tap it: an approval card shows €307, from the current account to the S-Bank savings account, and the balance after. Tap "Approve and move". Say: "It can move money, but only inside S-mobiili and only after I approve the exact move." The savings account now shows under "Your things". Or ask: "Invest 50 euros in the index fund"; the card adds a plain risk note.
14. **Think twice.** Ask "Can I afford a 300 euro payday loan?" Reply: it is borrowing, not a purchase, and Svinkki would not take it.

For a two-minute slot do steps 1, 3, 4, 5, 8, 9 and 13.''')

rep('docs/SECURITY_PLAN.md', '''- **SR-6. All tools are read-only.** The database connection used by tools cannot write, create or
  drop anything.''', '''- **SR-6. All tools are read-only.** The database connection used by tools cannot write, create or
  drop anything. *Changed for the demo on 14 Nov 2026 (owner decision):* one tool,
  `propose_money_move`, may create a pending offer to move money from the customer's current account to
  their own S-Bank savings account or an S-Bank fund. It cannot move money. Money moves only through
  `POST /api/money/confirm`, which the customer triggers by approving the offer on screen; the request
  must name the offer, its amount and its destination, arrive within 15 minutes and is accepted once. The
  amount is capped at what is safe to spend before payday. There is no destination outside S-mobiili.''')
rep('docs/SECURITY_PLAN.md', '''  - move money or change anything;''',
    '''  - make payments or move money out of S-mobiili (in-app saving and investing are offered for approval
    only, see SR-6);''')
rep('docs/SECURITY_PLAN.md', '''| V12 | Ask the coach to transfer money | Refusal. It states it is read-only. | SR-6 |''',
    '''| V12 | Ask the coach to pay a bill or send money to someone | Refusal. In-app saving gives an offer that moves nothing until approved (`tests/test_money.py`). | SR-6 |''')

rep('HANDOFF.md', '''## Where things stand
''', '''## Where things stand

Updated 14 Nov 2026, about 01:00, by agent-c (main coding agent after agent-a):

- **Money can move in the demo, with permission.** The coach or a check-in suggestion offers a move to the
  customer's own S-Bank savings account or an S-Bank fund; an approval card must be tapped before anything
  moves (`app/money.py`, `/api/money/*`, `tests/test_money.py`). Payments and transfers out are still refused.
- **Start page:** the check-in, the weekly quiz and "Worth a look" are cards on the front page.
- **Evaluation fixes (agent-b's `.devloop/eval-1.md`):** MAJ-1 (late unpaid bills dropped from safe to spend),
  MAJ-2 (payday guessed too early), MAJ-3 (unclear period or category answered silently), MAJ-4 (spending more
  reported as saving), MAJ-5 ("yes, it fits" for payday loans, crypto, gambling), MAJ-6 (check-in suggesting
  more than is safe), MAJ-8 (income questions) are fixed. MAJ-7 and MAJ-9 were fixed earlier (D5, D4).
  MAJ-10 (safe to spend vs. forecast) now shares the payday rule with the forecast; not re-evaluated.
- Tests: 650 pass.
''')
print("docs ok")
