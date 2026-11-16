"""Probe the open evaluation majors against a running key-less Svinkki server (built-in rules only)."""
import http.cookiejar
import json
import sys
import urllib.request

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8012"


def session(persona):
    jar = http.cookiejar.CookieJar()
    op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))

    def call(path, body=None):
        data = None if body is None else json.dumps(body).encode()
        req = urllib.request.Request(BASE + path, data=data, headers={"Content-Type": "application/json"})
        try:
            with op.open(req, timeout=60) as r:
                return json.loads(r.read() or b"null")
        except urllib.error.HTTPError as e:
            return {"_status": e.code, "_body": e.read().decode()[:200]}

    pid = [p for p in call("/api/demo/personas") if p["name"].startswith(persona)][0]["id"]
    call("/api/demo/login", {"id": pid})
    call("/api/consent", {"analysis": True, "ai": True, "benchmarks": True, "suggestions": True})
    return call


QUESTIONS = {
    "MAJ-4 what-if increase": ["What if I spend 20% more on restaurants?", "How much more would I spend if I doubled my taxi use?"],
    "MAJ-5 afford investments/loans": ["Can I afford 500 euros of bitcoin?", "Can I afford a 300 euro payday loan?", "Can I afford to buy 1000 euros of index fund units?"],
    "MAJ-3 unknown period/category": ["How much did I spend on taxis in March?", "How much did I spend on coffee last month?", "How much did I spend on taxis in the last 10 days?"],
    "MAJ-8 basic money questions": ["What is my balance?", "How much did I earn last month?", "When is my next payday?", "How much do I spend on rent?"],
}

call = session(sys.argv[2] if len(sys.argv) > 2 else "Veeti")
for group, qs in QUESTIONS.items():
    print("=" * 8, group)
    for q in qs:
        r = call("/api/chat", {"message": q})
        reply = (r or {}).get("reply") or r
        tools = (r or {}).get("tools_used")
        print("Q:", q)
        print("A:", str(reply).replace("\n", " ")[:300], "| tools:", tools)
