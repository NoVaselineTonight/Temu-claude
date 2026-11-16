import sys

root = sys.argv[1]
p = root + '/tests/test_coach.py'
s = open(p, encoding='utf-8').read()
a = '''    def test_declared_tools_match_the_registry_and_a_system_prompt_is_sent(self):
        _, fake = self.run_gemini([fx.gem_text("Hello")], message="hi")
        body = fake.requests[0]
        decls = [d["name"] for t in body["tools"] for d in t["functionDeclarations"]]
        self.assertEqual(sorted(decls), sorted(t["name"] for t in self.tools.TOOLS))'''
b = '''    def test_declared_tools_match_the_registry_and_a_system_prompt_is_sent(self):
        # Comparison tools are offered to the model only when the customer asks for a comparison (owner, 14 Nov).
        cmp_tools = {"get_benchmarks", "get_averages", "get_area_context"}
        _, fake = self.run_gemini([fx.gem_text("Hello")], message="hi")
        body = fake.requests[0]
        decls = [d["name"] for t in body["tools"] for d in t["functionDeclarations"]]
        self.assertEqual(sorted(decls), sorted(t["name"] for t in self.tools.TOOLS if t["name"] not in cmp_tools))
        _, fake2 = self.run_gemini([fx.gem_text("Hello")], message="How do I compare with people my age?")
        decls2 = [d["name"] for t in fake2.requests[0]["tools"] for d in t["functionDeclarations"]]
        self.assertEqual(sorted(decls2), sorted(t["name"] for t in self.tools.TOOLS))'''
assert s.count(a) == 1
s = s.replace(a, b)
open(p, 'w', encoding='utf-8').write(s)

# new tests: no comparison unless asked
p = root + '/tests/test_money.py'
s = open(p, encoding='utf-8').read()
add = '''

class NoUnaskedComparisonTests(MoneyBase):
    """Owner, 14 Nov 2026: comparisons with other people only when the customer asks for one."""

    def chat(self, msg):
        r = self.a.post("/api/chat", {"message": msg})
        self.assertEqual(r.status, 200, r.text[:300])
        return r.json

    PEER = r"people your age|most people|most customers|people like you|compar|turn on comparisons"

    def test_own_questions_get_no_comparison(self):
        for q in ("How much do I earn?", "How much did I earn last month?", "How much did I spend on taxis last month?",
                  "How much did I spend on groceries last month?", "What is my balance?"):
            with self.subTest(q=q):
                r = self.chat(q)
                self.assertNotRegex(r["reply"].lower(), self.PEER)
                for c in r["cards"]:
                    self.assertNotIn("peer", c.get("data") or {}, q)

    def test_a_comparison_is_given_when_asked(self):
        r = self.chat("How do I compare with people my age?")
        self.assertIn(r["tools_used"], (["get_benchmarks"], ["get_averages"]))

    def test_alerts_and_quiz_do_not_compare_with_others(self):
        for a in (self.a.get("/api/alerts").json.get("alerts") or []):
            self.assertNotRegex(str(a).lower(), r"people your age|most people|people of your age")
        q = self.a.get("/api/quiz").json
        if q.get("quiz_id"):
            r = self.a.post("/api/quiz/answer", {"quiz_id": q["quiz_id"], "guess": 10}).json
            self.assertNotIn("peer", r)
'''
marker = '\n\nif __name__ == "__main__":'
assert s.count(marker) == 1
s = s.replace(marker, add + marker)
open(p, 'w', encoding='utf-8').write(s)
print("tests ok")
