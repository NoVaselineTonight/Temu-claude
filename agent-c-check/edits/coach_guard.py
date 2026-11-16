import sys
p = sys.argv[1]
s = open(p, encoding='utf-8').read()
def rep(a, b):
    global s
    assert s.count(a) == 1, a[:60]
    s = s.replace(a, b)
rep('''REFUSAL_MONEY = "I can't move money, only look at it. Want to see what's safe to spend this week?"''',
    '''REFUSAL_MONEY = ("I can only move money inside S-mobiili, to your S-Bank savings account or an S-Bank fund, and only "
                 "after you approve it. Payments and transfers out of S-mobiili are not something I do.")''')
rep('''_QUESTION_START = re.compile(''', '''# In-app moves (own savings account, S-Bank funds) go on to an approval card; everything that would take
# money out of S-mobiili, pay someone or pay a bill is still refused.
_INAPP_RE = re.compile(r"savings? account|\b(to|into|in) (my )?savings\b|\bbuffer\b|\bfunds?\b|\binvest\w*|"
                       r"säästötil\w*|säästöön\b|rahasto\w*|sijoit\w*", re.I)
_EXTERNAL_RE = re.compile(r"\b(pay|paying|wire|send|withdraw|top up|payment|rent|bills?|invoice|iban|another bank|other bank|"
                          r"someone|friend|account number|mobilepay|paypal|revolut|nordea|op\b|danske)\b|"
                          r"\b[A-Z]{2}\d{2}(?:\s?[A-Z0-9]{4}){2,}|\bmaksa\w*|\blähetä\w*|\bnosta\b|\blasku\w*|"
                          r"\bvuokra\w*|\bkaveri\w*", re.I)
_QUESTION_START = re.compile(''')
rep('''    if _MOVE_RE.search(message) and not _QUESTION_START.match(message):
        return REFUSAL_MONEY
    if _MOVE_FI_RE.search(message):
        return REFUSAL_MONEY''', '''    inapp = bool(_INAPP_RE.search(message)) and not _EXTERNAL_RE.search(message)
    if _MOVE_RE.search(message) and not _QUESTION_START.match(message) and not inapp:
        return REFUSAL_MONEY
    if _MOVE_FI_RE.search(message) and not inapp:
        return REFUSAL_MONEY''')
open(p, 'w', encoding='utf-8').write(s)
print("guard ok")
