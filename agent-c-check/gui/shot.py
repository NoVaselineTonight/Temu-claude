"""Drive headless Chrome over CDP: run a list of steps, take phone-width screenshots.

usage: python shot.py steps.json outdir
steps: [{"go": url} | {"js": code} | {"wait": ms} | {"shot": name, "full": bool}]
"""
import base64, json, os, subprocess, sys, time, urllib.request
import websocket

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PORT = 9333
steps = json.load(open(sys.argv[1], encoding="utf-8"))
out = sys.argv[2]
os.makedirs(out, exist_ok=True)
prof = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chrome-profile")
proc = subprocess.Popen([CHROME, "--headless=new", f"--remote-debugging-port={PORT}", f"--user-data-dir={prof}",
                         "--no-first-run", "--hide-scrollbars", "about:blank"],
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
try:
    for _ in range(50):
        try:
            tabs = json.load(urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json"))
            page = [t for t in tabs if t["type"] == "page"][0]
            break
        except Exception:
            time.sleep(0.2)
    ws = websocket.create_connection(page["webSocketDebuggerUrl"], timeout=60)
    n = [0]
    logs = []

    def cmd(method, **params):
        n[0] += 1
        ws.send(json.dumps({"id": n[0], "method": method, "params": params}))
        while True:
            m = json.loads(ws.recv())
            if m.get("method") == "Runtime.exceptionThrown":
                logs.append("EXC " + json.dumps(m["params"]["exceptionDetails"])[:400])
            if m.get("method") == "Runtime.consoleAPICalled" and m["params"]["type"] in ("error", "warning"):
                logs.append("CONSOLE " + json.dumps(m["params"]["args"])[:300])
            if m.get("id") == n[0]:
                return m.get("result", m)

    cmd("Runtime.enable")
    cmd("Page.enable")
    cmd("Network.enable")
    cmd("Network.setCacheDisabled", cacheDisabled=True)
    cmd("Emulation.setDeviceMetricsOverride", width=390, height=844, deviceScaleFactor=float(os.environ.get("SCALE","1")), mobile=True)
    for s in steps:
        if "go" in s:
            cmd("Page.navigate", url=s["go"]); time.sleep(s.get("after", 1.5))
        elif "js" in s:
            r = cmd("Runtime.evaluate", expression=s["js"], awaitPromise=True, returnByValue=True)
            v = r.get("result", {}).get("value")
            if v is not None:
                print("JS:", json.dumps(v)[:3000])
            if r.get("exceptionDetails"):
                print("JS ERR:", json.dumps(r["exceptionDetails"])[:500])
            time.sleep(s.get("after", 0.8))
        elif "wait" in s:
            time.sleep(s["wait"] / 1000)
        elif "shot" in s:
            params = {"format": "png"}
            if s.get("full"):
                m = cmd("Page.getLayoutMetrics")["cssContentSize"]
                params["clip"] = {"x": 0, "y": 0, "width": 390, "height": min(m["height"], 6000), "scale": 1}
                params["captureBeyondViewport"] = True
            data = cmd("Page.captureScreenshot", **params)["data"]
            p = os.path.join(out, s["shot"] + ".png")
            open(p, "wb").write(base64.b64decode(data))
            print("saved", p)
    for l in logs:
        print(l)
finally:
    proc.kill()
