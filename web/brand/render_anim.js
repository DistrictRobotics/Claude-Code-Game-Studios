// Renders the animated mark to a frame sequence by stepping the CSS
// animation clock, so output is deterministic rather than wall-clock timed.
const { chromium } = require('playwright');
const fs = require('fs');

const LOOP_MS = 2400, FPS = 30;
const frames = Math.round(LOOP_MS / 1000 * FPS);

(async () => {
  fs.rmSync('frames', { recursive: true, force: true });
  fs.mkdirSync('frames');
  const b = await chromium.launch({ args: ['--no-sandbox'] });
  const p = await b.newPage({ viewport: { width: 1600, height: 600 },
                              deviceScaleFactor: 1 });
  await p.goto('file://' + process.cwd() + '/logo_animated.html',
               { waitUntil: 'networkidle' });
  await p.evaluate(() => document.fonts.ready);
  await p.evaluate(() => document.getAnimations().forEach(a => a.pause()));

  for (let i = 0; i < frames; i++) {
    const t = i * (LOOP_MS / frames);
    await p.evaluate(ms => {
      document.getAnimations().forEach(a => { a.currentTime = ms; });
    }, t);
    await p.screenshot({ path: `frames/${String(i).padStart(3, '0')}.png` });
  }
  console.log(`${frames} frames`);
  await b.close();
})();
