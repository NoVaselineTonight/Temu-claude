import sys

p = sys.argv[1] + '/tests/test_money.py'
s = open(p, encoding='utf-8').read()
add = '''

class SafeToSpendFixTests(unittest.TestCase):
    """MAJ-1 and MAJ-2 on a hand-built account: moves are capped by safe to spend, so it must not be generous."""

    def account(self, rows):
        import sqlite3
        conn = sqlite3.connect(":memory:")
        conn.execute("CREATE TABLE tx (d TEXT, ts TEXT, amount REAL, balance REAL, type TEXT, category TEXT, "
                     "mcc TEXT, merchant TEXT, label TEXT, basket TEXT, context TEXT, id INTEGER)")
        bal = 0.0
        for i, (d, amt, typ, label, basket) in enumerate(sorted(rows)):
            bal += amt
            conn.execute("INSERT INTO tx VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                         (d, d + " 12:00:00", amt, round(bal, 2), typ, label, None, None, label, basket, None, i + 1))
        return conn

    def months(self, n=6, end=(2026, 9)):
        y, m = end
        out = []
        for _ in range(n):
            out.append((y, m))
            m -= 1
            if m == 0:
                y, m = y - 1, 12
        return list(reversed(out))

    def test_MAJ1_a_late_unpaid_rent_still_counts(self):
        from app import insights
        rows = []
        for y, m in self.months(end=(2026, 8)):
            rows.append(("%04d-%02d-01" % (y, m), 2500.0, "salary", "Salary", "income"))
            rows.append(("%04d-%02d-05" % (y, m), -800.0, "housing_payment", "Housing", "regular"))
        rows.append(("2026-09-01", 2500.0, "salary", "Salary", "income"))      # September rent not paid yet
        conn = self.account(rows)
        s = insights.safe_to_spend(conn, "2026-09-10")
        self.assertIn(800.0, [b["expected"] for b in s["upcoming_bills"]], "the late rent was dropped")

    def test_MAJ2_paid_this_month_means_next_payday_is_next_month(self):
        from app import insights
        rows = []
        for i, (y, m) in enumerate(self.months(end=(2026, 8))):
            day = 15 if i % 2 else 28                                            # alternating salary day
            rows.append(("%04d-%02d-%02d" % (y, m, day), 2500.0, "salary", "Salary", "income"))
        rows.append(("2026-09-12", 2500.0, "salary", "Salary", "income"))     # September already paid
        conn = self.account(rows)
        s = insights.safe_to_spend(conn, "2026-09-14")
        self.assertGreaterEqual(s["next_payday"], "2026-10-01")
'''
marker = '\n\nif __name__ == "__main__":'
assert s.count(marker) == 1
s = s.replace(marker, add + marker)
open(p, 'w', encoding='utf-8').write(s)
print("tests appended")
