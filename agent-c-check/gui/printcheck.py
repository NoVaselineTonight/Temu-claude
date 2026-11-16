import base64, json, subprocess, sys, time, urllib.request, websocket
CH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
p = subprocess.Popen([CH, "--headless=new", "--remote-debugging-port=9334", "--user-data-dir=" + sys.argv[3], "about:blank"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
try:
    for _ in range(50):
        try:
            page = [t for t in json.load(urllib.request.urlopen("http://127.0.0.1:9334/json")) if t["type"] == "page"][0]; break
        except Exception: time.sleep(0.2)
    ws = websocket.create_connection(page["webSocketDebuggerUrl"]); n = [0]
    def cmd(m, **k):
        n[0] += 1; ws.send(json.dumps({"id": n[0], "method": m, "params": k}))
        while True:
            r = json.loads(ws.recv())
            if r.get("id") == n[0]: return r.get("result", r)
    cmd("Page.enable"); cmd("Emulation.setDeviceMetricsOverride", width=1920, height=1080, deviceScaleFactor=0.5, mobile=False)
    cmd("Emulation.setEmulatedMedia", media="print")
    cmd("Page.navigate", url=sys.argv[1]); time.sleep(2)
    h = cmd("Page.getLayoutMetrics")["cssContentSize"]["height"]
    print("height", h)
    d = cmd("Page.captureScreenshot", format="png", captureBeyondViewport=True, clip={"x": 0, "y": 0, "width": 1920, "height": h, "scale": 0.25})["data"]
    open(sys.argv[2], "wb").write(base64.b64decode(d))
finally:
    p.kill()
