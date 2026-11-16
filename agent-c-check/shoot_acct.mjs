// Start page with the simulated account card, then the account sheet. No AI calls.
import { spawn } from 'node:child_process';
import { writeFileSync, mkdirSync, rmSync } from 'node:fs';

const OUT = process.argv[2], APP = process.argv[3], PORT = 9335;
rmSync(OUT, { recursive: true, force: true }); mkdirSync(OUT, { recursive: true });
const chrome = spawn('C:/Program Files/Google/Chrome/Application/chrome.exe', ['--headless=new', `--remote-debugging-port=${PORT}`,
  `--user-data-dir=${OUT}/profile`, '--no-first-run', '--no-default-browser-check', 'about:blank'], { stdio: 'ignore' });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
let page;
for (let i = 0; i < 50 && !page; i++) {
  try { page = (await (await fetch(`http://127.0.0.1:${PORT}/json/list`)).json()).find((t) => t.type === 'page'); } catch { await sleep(200); }
}
const ws = new WebSocket(page.webSocketDebuggerUrl);
await new Promise((r) => ws.addEventListener('open', r, { once: true }));
let id = 0; const pending = new Map(); const errors = [];
ws.addEventListener('message', (ev) => {
  const m = JSON.parse(ev.data);
  if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); }
  if (m.method === 'Runtime.exceptionThrown') errors.push(m.params.exceptionDetails.exception?.description || m.params.exceptionDetails.text);
});
const send = (method, params = {}) => new Promise((r) => { const i = ++id; pending.set(i, r); ws.send(JSON.stringify({ id: i, method, params })); });
const js = async (expr) => (await send('Runtime.evaluate', { expression: expr, awaitPromise: true, returnByValue: true })).result?.result?.value;
const shot = async (name, h) => {
  await send('Emulation.setDeviceMetricsOverride', { width: 390, height: h, deviceScaleFactor: 1, mobile: true }); await sleep(700);
  writeFileSync(`${OUT}/${name}.png`, Buffer.from((await send('Page.captureScreenshot', { format: 'png' })).result.data, 'base64'));
};
await send('Runtime.enable'); await send('Page.enable');
await send('Emulation.setDeviceMetricsOverride', { width: 390, height: 900, deviceScaleFactor: 1, mobile: true });
await send('Page.navigate', { url: APP }); await sleep(1500);
await js(`(async () => {
  const p = await (await fetch('/api/demo/personas')).json(); const v = p.find(x => x.name.startsWith('Veeti'));
  const post = (u, b) => fetch(u, { method: 'POST', credentials: 'same-origin', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(b) });
  await post('/api/demo/login', { id: v.id });
  await post('/api/consent', { analysis: true, ai: true, benchmarks: true, suggestions: true }); return true; })()`);
await send('Page.navigate', { url: APP }); await sleep(2500);
for (let i = 0; i < 3 && !(await js(`!!document.querySelector('.home')`)); i++) {
  await js(`(() => { const b = [...document.querySelectorAll('button')].find(x => /start|continue|got it|ok/i.test(x.textContent)); b && b.click(); })()`); await sleep(1500);
}
await sleep(2500);
console.log('card:', (await js(`(document.querySelector('.acct-card')||{}).innerText`) || 'MISSING').replace(/\n+/g, ' | '));
await shot('1-start-top', 900);
await js(`document.querySelector('.acct-card').click()`); await sleep(2500);
console.log('sheet:', (await js(`(document.querySelector('.sheet')||{}).innerText`) || 'MISSING').replace(/\n+/g, ' | ').slice(0, 600));
await shot('2-account-sheet', 1100);
console.log('page errors:', errors.length, errors.slice(0, 2));
ws.close(); chrome.kill(); process.exit(0);
