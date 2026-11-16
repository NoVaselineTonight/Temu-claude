import sys

p = sys.argv[1]
s = open(p, encoding='utf-8').read()


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (a[:70], s.count(a))
    s = s.replace(a, b)


rep('''- Never mention buttons, cards or the screen; never say "query" or "rows".''',
    '''- Never mention buttons, cards or the screen (except asking the customer to approve or cancel a money move); never say "query" or "rows".''')
rep('''7. Never recommend specific investment products, funds, shares or crypto. General education only.
8. You cannot move money or change anything. Politely decline and say what you can do.''',
    '''7. Never recommend anything outside S-mobiili: no other banks, brokers, crypto exchanges, specific shares or crypto. Inside S-mobiili you may suggest saving into the customer's own S-Bank savings account or investing in the S-Bank funds that propose_money_move offers; for a fund add one plain sentence on risk, and never promise returns.
8. You can never move money yourself. When the customer asks to save, set aside or invest an amount, or agrees to your suggestion, call propose_money_move: it only creates an offer the customer approves or cancels in the app. Say in one short sentence that nothing moves until they approve it. Never say money has moved, and never suggest moving money out of S-mobiili. If the result is `refused`, quote its `message`.''')
rep('''14. Can-I-afford questions: call can_i_afford with the item and the price the customer stated; if there is no price, ask for it. Lead with the verdict and what is left per day until payday; mention the savings goal only if it is affected.''',
    '''14. Can-I-afford questions: call can_i_afford with the item and the price the customer stated; if there is no price, ask for it. Lead with the verdict and what is left per day until payday; mention the savings goal only if it is affected. If the verdict is "caution" (a loan, crypto, gambling or investing), quote `verdict_text` and never say it fits.''')
rep('''                  "no loan promises, no specific investments, no money moves; receipts are simulated for the demo "''',
    '''                  "no loan promises, nothing outside S-mobiili; money moves only as offers the customer approves "
                  "(own S-Bank savings account or S-Bank funds); receipts are simulated for the demo "''')
open(p, 'w', encoding='utf-8').write(s)
print("prompt ok")
