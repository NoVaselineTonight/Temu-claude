import sys

p = sys.argv[1] + '/tests/test_wave4.py'
s = open(p, encoding='utf-8').read()
a = '''    def test_F_transfer_is_refused(self):
        for m in ("Transfer 500 euros to my savings", "Send 200 euros to my landlord", "Move 100 euros to my savings account",
                  "Pay my rent for me"):
            with self.subTest(m):
                r = self.ask(m)
                self.assertEqual(r["tools_used"], [])
                self.assertRegex(r["reply"].lower(), r"can't|cannot|not able|unable|don't|only read")
                self.assertRegex(r["reply"].lower(), r"mov|transfer|payment|pay")'''
b = '''    def test_F_transfer_is_refused(self):
        # Payments and transfers out of S-mobiili are refused before any tool runs.
        for m in ("Send 200 euros to my landlord", "Pay my rent for me", "Transfer 500 euros to my friend"):
            with self.subTest(m):
                r = self.ask(m)
                self.assertEqual(r["tools_used"], [])
                self.assertRegex(r["reply"].lower(), r"can't|cannot|not able|unable|don't|only read")
                self.assertRegex(r["reply"].lower(), r"mov|transfer|payment|pay")
        # Owner decision 14 Nov 2026: saving inside S-mobiili becomes an offer the customer approves, nothing more.
        for m in ("Transfer 500 euros to my savings", "Move 100 euros to my savings account"):
            with self.subTest(m):
                r = self.ask(m)
                self.assertIn(r["tools_used"], ([], ["propose_money_move"]))
                self.assertNotRegex(r["reply"].lower(), r"\\b(moved|done)\\b")'''
assert s.count(a) == 1
open(p, 'w', encoding='utf-8').write(s.replace(a, b))
print("ok")
