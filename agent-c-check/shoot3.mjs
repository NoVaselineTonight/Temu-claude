// Drives headless Chrome over the DevTools protocol (no installs) and screenshots Svinkki screens.
import { spawn } from 'node:child_process';
import { writeFileSync, mkdirSync } from 'node:fs';

const OUT = process.argv[2];
const APP = 'http://127.0.0.1:8011/';
const PORT = 9333;
mkdirSync(OUT, { recursive: true });

const chrome = spawn('C:/Program Files/Google/Chrome/Application/chrome.exe', [
  '--headless=new', `--remote-debugging-port=${PORT}`, `--user-data-dir=${OUT}/profile`,
  '--no-first-run', '--no-default-browser-check', '--disable-extensions', 'about:blank',
], { stdio: 'ignore' });

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
let page;
for (let i = 0; i < 50 && !page; i++) {
  try {
    const list = await (await fetch(`http://127.0.0.1:${PORT}/json/list`)).json();
    page = list.find((t) => t.type === 'page');
  } catch { await sleep(200); }
}
const ws = new WebSocket(page.webSocketDebuggerUrl);
await new Promise((r) => ws.addEventListener('open', r, { once: true }));
let id = 0; const pending = new Map(); const consoleErrors = [];
ws.addEventListener('message', (ev) => {
  const m = JSON.parse(ev.data);
  if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); }
  if (m.method === 'Runtime.exceptionThrown') consoleErrors.push(m.params.exceptionDetails.exception?.description || m.params.exceptionDetails.text);
  if (m.method === 'Runtime.consoleAPICalled' && m.params.type === 'error') consoleErrors.push(m.params.args.map((a) => a.value ?? a.description).join(' '));
});
const send = (method, params = {}) => new Promise((r) => { const i = ++id; pending.set(i, r); ws.send(JSON.stringify({ id: i, method, params })); });
const js = async (expr) => {
  const r = await send('Runtime.evaluate', { expression: expr, awaitPromise: true, returnByValue: true });
  if (r.result?.exceptionDetails) throw new Error(expr.slice(0, 80) + ' -> ' + JSON.stringify(r.result.exceptionDetails.exception?.description));
  return r.result?.result?.value;
};
const shot = async (name) => {
  await sleep(1500);
  const h = await js('Math.max(document.documentElement.scrollHeight, document.body.scrollHeight, ...[...document.querySelectorAll("main, #view, .view")].map(e => e.scrollHeight))');
  await send('Emulation.setDeviceMetricsOverride', { width: 390, height: Math.min(Math.max(h, 844), 8000), deviceScaleFactor: 1, mobile: true });
  await sleep(500);
  const r = await send('Page.captureScreenshot', { format: 'png' });
  writeFileSync(`${OUT}/${name}.png`, Buffer.from(r.result.data, 'base64'));
  await send('Emulation.setDeviceMetricsOverride', { width: 390, height: 844, deviceScaleFactor: 1, mobile: true });
  console.log('shot', name, 'height', h);
};
const text = (sel) => js(`(document.querySelector(${JSON.stringify(sel)})||{}).innerText||''`);

await send('Runtime.enable'); await send('Page.enable');
await send('Emulation.setDeviceMetricsOverride', { width: 390, height: 844, deviceScaleFactor: 1, mobile: true });
await send('Page.navigate', { url: APP }); await sleep(1500);
await js(`(async () => {
  const p = await (await fetch('/api/demo/personas')).json();
  const v = p.find(x => x.name.startsWith('Veeti'));
  const post = (u, b) => fetch(u, { method: 'POST', credentials: 'same-origin', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(b) });
  await post('/api/demo/login', { id: v.id });
  await post('/api/consent', { analysis: true, ai: true, benchmarks: true, suggestions: true });
  return true; })()`);
await send('Page.navigate', { url: APP }); await sleep(2500);

const tab = async (t) => { await js(`document.querySelector('.tab[data-tab="${t}"]').click()`); await sleep(3000); };
// Screenshot one card: the closest .card around a heading with this text.
const card = async (heading, name, pick = 'first') => {
  await send('Emulation.setDeviceMetricsOverride', { width: 390, height: 1800, deviceScaleFactor: 1, mobile: true });
  const r = await js(`(() => {
    const hs = [...document.querySelectorAll('h1,h2,h3,h4,.card-head,.eyebrow,b,strong,p')].filter(e => e.textContent.trim().startsWith(${JSON.stringify(heading)}));
    if (!hs.length) return null;
    const hEl = ${JSON.stringify(pick)} === 'last' ? hs[hs.length-1] : hs[0];
    const c = hEl.closest('.card, .msg, .sheet, section') || hEl.parentElement;
    c.scrollIntoView({ block: 'start' });
    const b = c.getBoundingClientRect();
    return { x: b.left, y: b.top, w: b.width, h: b.height, text: c.innerText.slice(0, 3000) };
  })()`);
  if (!r) { console.log('MISSING', heading); return; }
  await sleep(400);
  const r2 = await js(`(() => { const b = [...document.querySelectorAll('*')].length; return true; })()`);
  await send('Emulation.setDeviceMetricsOverride', { width: 390, height: Math.min(Math.ceil(r.h) + 90, 1800), deviceScaleFactor: 1, mobile: true }); await js(`(() => { const hs=[...document.querySelectorAll('h1,h2,h3,h4,.card-head,.eyebrow,b,strong,p')].filter(e => e.textContent.trim().startsWith(${JSON.stringify(heading)})); const c=(hs[0].closest('.card, .msg, .sheet, section')||hs[0].parentElement); c.scrollIntoView({block:'start'}); })()`); await sleep(600);
  const s = await send('Page.captureScreenshot', { format: 'png' });
  writeFileSync(`${OUT}/${name}.png`, Buffer.from(s.result.data, 'base64'));
  writeFileSync(`${OUT}/${name}.txt`, r.text);
  console.log('card', name, Math.round(r.h) + 'px');
};
const view = async (name) => {
  await send('Emulation.setDeviceMetricsOverride', { width: 390, height: 844, deviceScaleFactor: 1, mobile: true });
  await sleep(500);
  const s = await send('Page.captureScreenshot', { format: 'png' });
  writeFileSync(`${OUT}/${name}.png`, Buffer.from(s.result.data, 'base64'));
  console.log('view', name);
};

await tab('explore');
await card('Your payday plan', 'a-payday-plan');
await card('Leak finder', 'b-leak-finder');
await card('Patterns', 'c-patterns');
await card('Your area', 'd-area');
await tab('settings');
await card('Savings goal', 'e-goal-settings'); await card('Goal', 'e2-goal-settings');
await tab('chat');
const ask = async (q) => {
  await js(`(() => { const t = document.querySelector('textarea.chat-text'); t.value = ${JSON.stringify(q)}; t.dispatchEvent(new Event('input', { bubbles: true })); t.form.requestSubmit(); })()`);
  await sleep(5000);
};
await ask('I want to go to Japan in 2027');
await js(`(() => { const m = [...document.querySelectorAll('.msg')].pop(); m && m.scrollIntoView({block:'start'}); })()`);
await view('f-chat-goal-card');
writeFileSync(`${OUT}/f-chat-goal-card.txt`, await js(`([...document.querySelectorAll('.msg')].pop()||{}).innerText||''`));
await js(`document.querySelector('button[aria-label="Explain a text"]').click()`); await sleep(1000);
await view('g-explain-empty');
const loan = 'Consumer credit offer. Credit limit 5 000 EUR. Nominal interest rate 14.9 % per year plus a monthly account fee of 7.50 EUR and an opening fee of 50 EUR. The effective annual interest rate is 19.6 % with a 5 000 EUR loan repaid in 24 months. Minimum monthly payment 3 % of the balance, at least 30 EUR.';
await js(`(() => { const t = [...document.querySelectorAll('textarea')].find(x => !x.classList.contains('chat-text')); t.value = ${JSON.stringify(loan)}; t.dispatchEvent(new Event('input', { bubbles: true })); return true; })()`);
await js(`[...document.querySelectorAll('button')].find(b => b.textContent.trim() === 'Explain this text').click()`); await sleep(4000);
await view('h-explain-result');
await js(`(() => { const s = document.querySelector('.sheet-body, .sheet'); if (s) s.scrollTop = 99999; })()`); await sleep(400);
await view('i-explain-result-bottom');
writeFileSync(`${OUT}/h-explain-result.txt`, await js(`(document.querySelector('.sheet')||document.body).innerText.slice(0,4000)`));
writeFileSync(`${OUT}/errors.json`, JSON.stringify(consoleErrors, null, 1));
console.log('console errors:', consoleErrors.length);
ws.close(); chrome.kill();
process.exit(0);
