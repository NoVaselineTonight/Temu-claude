// Browser check of the start page cards and the in-app money move, against the key-less server (no AI cost).
import { spawn } from 'node:child_process';
import { writeFileSync, mkdirSync, rmSync } from 'node:fs';

const OUT = process.argv[2];
const APP = process.argv[3];
const PORT = 9334;
rmSync(OUT, { recursive: true, force: true });
mkdirSync(OUT, { recursive: true });
const chrome = spawn('C:/Program Files/Google/Chrome/Application/chrome.exe', [
  '--headless=new', `--remote-debugging-port=${PORT}`, `--user-data-dir=${OUT}/profile`,
  '--no-first-run', '--no-default-browser-check', '--disable-extensions', 'about:blank'], { stdio: 'ignore' });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
let page;
for (let i = 0; i < 50 && !page; i++) {
  try { page = (await (await fetch(`http://127.0.0.1:${PORT}/json/list`)).json()).find((t) => t.type === 'page'); }
  catch { await sleep(200); }
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
const js = async (expr) => {
  const r = await send('Runtime.evaluate', { expression: expr, awaitPromise: true, returnByValue: true });
  if (r.result?.exceptionDetails) throw new Error(expr.slice(0, 90) + ' -> ' + JSON.stringify(r.result.exceptionDetails.exception?.description));
  return r.result?.result?.value;
};
const shot = async (name, h = 1400) => {
  await send('Emulation.setDeviceMetricsOverride', { width: 390, height: h, deviceScaleFactor: 1, mobile: true });
  await sleep(700);
  const r = await send('Page.captureScreenshot', { format: 'png' });
  writeFileSync(`${OUT}/${name}.png`, Buffer.from(r.result.data, 'base64'));
  console.log('shot', name);
};
const clickText = (re) => js(`(() => { const b = [...document.querySelectorAll('button')].find(x => ${re}.test(x.textContent.trim()) && !x.disabled); if (b) { b.click(); return b.textContent.trim(); } return null; })()`);

await send('Runtime.enable'); await send('Page.enable');
await send('Emulation.setDeviceMetricsOverride', { width: 390, height: 1400, deviceScaleFactor: 1, mobile: true });
await send('Page.navigate', { url: APP }); await sleep(1500);
await js(`(async () => {
  const p = await (await fetch('/api/demo/personas')).json();
  const v = p.find(x => x.name.startsWith('Veeti'));
  const post = (u, b) => fetch(u, { method: 'POST', credentials: 'same-origin', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(b) });
  await post('/api/demo/login', { id: v.id });
  await post('/api/consent', { analysis: true, ai: true, benchmarks: true, suggestions: true });
  await post('/api/settings', { checkin_frequency: 'monthly', suggestion_level: 'normal', quiz: 'weekly' });
  return true; })()`);
await send('Page.navigate', { url: APP }); await sleep(2500);
for (let i = 0; i < 3 && !(await js(`!!document.querySelector('.home')`)); i++) {
  console.log('welcome step:', await clickText('/start|continue|let.s go|get started|begin|ok|got it/i')); await sleep(1500);
}
await sleep(2500);
console.log('for-you cards:', await js(`[...document.querySelectorAll('.for-you-cards .card-title')].map(e => e.textContent)`));
await shot('1-start-page', 2600);

console.log('page errors:', errors.length, errors.slice(0, 3));
ws.close(); chrome.kill(); process.exit(0);
