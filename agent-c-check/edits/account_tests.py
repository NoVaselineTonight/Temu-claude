import sys

p = sys.argv[1] + '/tests/test_money.py'
s = open(p, encoding='utf-8').read()
add = '''

class AccountCardTests(MoneyBase):
    """The simulated bank account shown at the top of the start page."""

    def test_account_shows_the_balance_and_follows_an_approved_move(self):
        a = self.a.get("/api/account").json
        self.assertTrue(a["simulated"])
        self.assertAlmostEqual(a["current"]["balance"], self.balance(), places=2)
        self.assertRegex(a["current"]["number"], r"^FI\\*\\* \\*{4} \\*{4} \\d{4}$")
        saved0 = a["savings"]["balance"]
        prop = self.propose()["proposal"]
        self.assertAlmostEqual(self.a.get("/api/account").json["current"]["balance"], a["current"]["balance"],
                               places=2, msg="a proposal alone changes nothing")
        self.assertTrue(self.confirm(prop).json["moved"])
        b = self.a.get("/api/account").json
        self.assertAlmostEqual(b["current"]["balance"], a["current"]["balance"] - prop["amount"], places=2)
        self.assertAlmostEqual(b["savings"]["balance"], saved0 + prop["amount"], places=2)
        self.assertIn("S-Bank savings account", [x["name"] for x in b["savings"]["parts"]])

    def test_account_reveals_no_ids_and_needs_a_session(self):
        text = self.a.get("/api/account").text
        self.assertNotRegex(text, r"CUST\\d{5}|MX\\d{5}")
        b = fx.session(self.server, "B")
        self.assertNotEqual(b.get("/api/account").json["current"]["number"],
                            self.a.get("/api/account").json["current"]["number"])
        self.assertIn(self.server.client().get("/api/account").status, (401, 403))
'''
marker = '\n\nif __name__ == "__main__":'
assert s.count(marker) == 1
open(p, 'w', encoding='utf-8').write(s.replace(marker, add + marker))
print("account tests ok")
