// DC Go-Go Music Festival - 2026 campaign renderer.
// Rebuilds the 2019-2021 visual system as code so pieces are repeatable:
// giant numeral hero, label tucked into its counter, corner year tag,
// black/white/DC-red palette, heavy condensed caps.
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const OUT = __dirname;
const RED = '#E8252B';

// The Foundation's own mark, embedded so page rendering needs no base URL.
const LOGO = 'data:image/png;base64,' +
  fs.readFileSync(path.join(__dirname, 'logo_transparent.png')).toString('base64');

const FONTS = `
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Anton&family=Barlow+Condensed:wght@600;700;800&display=swap" rel="stylesheet">
`;

const BASE = (w, h) => `
  *{margin:0;padding:0;box-sizing:border-box}
  html,body{width:${w}px;height:${h}px;overflow:hidden;background:#000}
  body{font-family:'Barlow Condensed',sans-serif;-webkit-font-smoothing:antialiased}
  .stage{position:relative;width:${w}px;height:${h}px;overflow:hidden}
  .bg{position:absolute;inset:0}
  .veil{position:absolute;inset:0}
  .content{position:absolute;inset:0;display:flex;flex-direction:column}
  .anton{font-family:'Anton',sans-serif;font-weight:400}

  /* Corner year tag - white rule above, boxed year below */
  .tag{position:absolute;top:${h*0.042}px;left:${w*0.045}px;z-index:5}
  .tag .site{font-weight:800;letter-spacing:.04em;font-size:${w*0.026}px;
    color:#fff;text-transform:uppercase;margin-bottom:${w*0.008}px;
    text-shadow:0 2px 12px rgba(0,0,0,.6)}
  .tag .yr{display:inline-block;background:#fff;color:#000;font-weight:800;
    font-size:${w*0.045}px;line-height:1;padding:${w*0.012}px ${w*0.022}px;
    letter-spacing:.02em;text-transform:uppercase}
  .tag .yr.red{background:${RED};color:#fff}

  /* Logo lockup slot at the foot */
  .lockup{position:absolute;bottom:${h*0.045}px;left:0;right:0;z-index:5;
    display:flex;align-items:center;justify-content:center;gap:${w*0.02}px}
  .logoslot{width:${w*0.095}px;height:${w*0.095}px;
    background-image:url('${LOGO}');background-size:contain;
    background-repeat:no-repeat;background-position:center}
  .wordmark{font-family:'Anton',sans-serif;font-size:${w*0.058}px;color:#fff;
    letter-spacing:-.01em;text-transform:uppercase;
    text-shadow:0 2px 16px rgba(0,0,0,.7)}
`;

// Giant numeral with the label riding its baseline, right-aligned.
// The label sits below the glyph body, not across it, so neither is obscured.
const numeral = (w, fig, label, sub, outline) => `
  <div class="numwrap">
    <div class="num anton${outline ? ' out' : ''}">${fig}</div>
    <div class="numlabel">
      <div class="l1 anton">${label}</div>
      ${sub ? `<div class="l2 anton">${sub}</div>` : ''}
    </div>
  </div>
  <style>
    .numwrap{position:relative;display:inline-block;
      padding-bottom:${w*0.055}px}
    .num{font-size:${w*0.44}px;line-height:.82;color:#000;letter-spacing:-.03em}
    .num.out{color:#000;-webkit-text-stroke:${w*0.0085}px ${RED}}
    .numlabel{position:absolute;right:0;bottom:0;text-align:right}
    .l1{background:${RED};color:#fff;font-size:${w*0.038}px;line-height:1;
      padding:${w*0.007}px ${w*0.014}px;display:inline-block;letter-spacing:.01em}
    .l2{color:${RED};font-size:${w*0.028}px;line-height:1.05;
      margin-top:${w*0.005}px;letter-spacing:.01em}
  </style>
`;

const pieces = [

// 1. Announce. "26" is the year, not a claimed statistic.
{
  name: '2026_announce_2000',
  w: 2000, h: 2000,
  html: (w, h) => `
    <div class="stage">
      <div class="bg" style="background:
        linear-gradient(180deg,#9fc3e8 0%,#c9d9e8 38%,#e8e2d6 62%,#4a4136 100%)"></div>
      <div class="veil" style="background:
        radial-gradient(900px 600px at 50% 95%, rgba(0,0,0,.42), transparent 70%)"></div>
      <div class="photoslot">Skyline / crowd photo<br>drops in here</div>
      <div class="content" style="align-items:center;justify-content:center;
           padding-top:${h*0.05}px">
        <div class="kicker anton">THE OFFICIAL MUSIC OF WASHINGTON, D.C.</div>
        ${numeral(w, '26', 'BIGGEST', 'SHOW ON EARTH', true)}
        <div class="tagline anton">THE FESTIVAL RETURNS</div>
      </div>
      <div class="tag"><div class="site">DCGOGOFEST.ORG</div>
        <div class="yr red">IN 2026</div></div>
      <div class="lockup">
        <div class="logoslot"></div>
        <div class="wordmark">DC GO-GO MUSIC FESTIVAL</div>
      </div>
    </div>
    <style>
      .photoslot{position:absolute;inset:${h*0.16}px ${w*0.06}px ${h*0.16}px;
        border:3px dashed rgba(232,37,43,.5);border-radius:14px;
        display:flex;align-items:flex-start;justify-content:flex-end;
        padding:${w*0.018}px;color:rgba(232,37,43,.85);font-weight:800;
        font-size:${w*0.018}px;text-transform:uppercase;text-align:right;
        letter-spacing:.06em;line-height:1.3}
      .kicker{font-size:${w*0.052}px;color:#111;text-transform:uppercase;
        letter-spacing:-.005em;margin-bottom:${h*0.035}px;text-align:center}
      .tagline{font-size:${w*0.062}px;color:#111;text-transform:uppercase;
        margin-top:${h*0.02}px;letter-spacing:-.01em}
    </style>`
},

// 2. The 3D rebuild. Venue names are the sourced historical ones.
{
  name: '2026_venues_2000',
  w: 2000, h: 2000,
  html: (w, h) => `
    <div class="stage">
      <div class="bg" style="background:#0a0a0c"></div>
      <div class="veil" style="background:
        radial-gradient(760px 520px at 22% 8%, rgba(232,37,43,.30), transparent 68%),
        radial-gradient(640px 460px at 86% 22%, rgba(255,255,255,.10), transparent 70%)"></div>
      <div class="slash"></div>
      <div class="content" style="padding:${h*0.19}px ${w*0.065}px ${h*0.235}px">
        <h1 class="anton">EVERY<br>STAGE<br><span class="r">REBUILT</span></h1>
        <p class="dek">The rooms go-go was born in, rebuilt in 3D.</p>
        <div class="venues">
          <div class="v"><span class="anton n">01</span>
            <span class="anton vn">LINCOLN THEATRE</span>
            <span class="va">1215 U St NW</span></div>
          <div class="v"><span class="anton n">02</span>
            <span class="anton vn">HOWARD THEATRE</span>
            <span class="va">620 T St NW</span></div>
          <div class="v"><span class="anton n">03</span>
            <span class="anton vn">THE MAVERICK ROOM</span>
            <span class="va">4th St NE</span></div>
        </div>
      </div>
      <div class="tag"><div class="site">DCGOGOFEST.ORG</div>
        <div class="yr red">IN 2026</div></div>
      <div class="lockup">
        <div class="logoslot"></div>
        <div class="wordmark">DC GO-GO MUSIC FESTIVAL</div>
      </div>
    </div>
    <style>
      .slash{position:absolute;top:-16%;left:-14%;width:148%;height:${h*0.115}px;
        background:${RED};transform:rotate(-26deg);transform-origin:0 0;opacity:.95}
      h1{font-size:${w*0.105}px;line-height:1.0;color:#fff;text-transform:uppercase;
        letter-spacing:-.025em}
      h1 .r{color:${RED}}
      .dek{margin-top:${h*0.025}px;font-size:${w*0.030}px;font-weight:700;
        color:#b9b4ad;text-transform:uppercase;letter-spacing:.02em}
      .venues{margin-top:auto;display:flex;flex-direction:column;gap:${h*0.014}px}
      .v{display:flex;align-items:baseline;gap:${w*0.022}px;
        border-top:2px solid #26262e;padding-top:${h*0.014}px}
      .n{font-size:${w*0.038}px;color:${RED};min-width:${w*0.07}px}
      .vn{font-size:${w*0.046}px;color:#fff;text-transform:uppercase;
        letter-spacing:-.01em}
      .va{margin-left:auto;font-size:${w*0.027}px;font-weight:700;color:#8b857e;
        text-transform:uppercase;letter-spacing:.05em}
    </style>`
},

// 3. Story format, continuing the 2020 chapter.
{
  name: '2026_story_1080x1920',
  w: 1080, h: 1920,
  html: (w, h) => `
    <div class="stage">
      <div class="bg" style="background:#111114"></div>
      <div class="veil" style="background:
        radial-gradient(520px 620px at 50% 30%, rgba(232,37,43,.22), transparent 72%)"></div>
      <div class="photoslot">Crowd photo<br>drops in here</div>
      <div class="content" style="align-items:center;justify-content:center;
           padding:${h*0.1}px ${w*0.08}px">
        <p class="pre anton">IN 2020 COVID TOOK THE STAGE AWAY.</p>
        ${numeral(w, '26', 'WE BUILT', 'A NEW ONE', true)}
        <p class="post anton">THE BIGGEST SHOW ON EARTH</p>
      </div>
      <div class="tag"><div class="site">DCGOGOFEST.ORG</div>
        <div class="yr red">IN 2026</div></div>
      <div class="lockup">
        <div class="logoslot"></div>
        <div class="wordmark" style="font-size:${w*0.062}px">DC GO-GO MUSIC FESTIVAL</div>
      </div>
    </div>
    <style>
      .photoslot{position:absolute;inset:${h*0.13}px ${w*0.06}px ${h*0.13}px;
        border:3px dashed rgba(232,37,43,.45);border-radius:14px;
        display:flex;align-items:flex-start;justify-content:flex-end;
        padding:${w*0.03}px;color:rgba(232,37,43,.8);font-weight:800;
        font-size:${w*0.026}px;text-transform:uppercase;text-align:right;
        letter-spacing:.05em;line-height:1.3}
      .pre{font-size:${w*0.058}px;color:#fff;text-transform:uppercase;
        text-align:center;line-height:1.1;margin-bottom:${h*0.03}px;max-width:16ch}
      .post{font-size:${w*0.062}px;color:${RED};text-transform:uppercase;
        text-align:center;margin-top:${h*0.025}px;letter-spacing:-.01em}
    </style>`
},
];

(async () => {
  const browser = await chromium.launch({ args: ['--no-sandbox'] });
  for (const p of pieces) {
    const page = await browser.newPage({
      viewport: { width: p.w, height: p.h },
      deviceScaleFactor: 1,
    });
    const doc = `<!doctype html><html><head><meta charset="utf-8">${FONTS}
      <style>${BASE(p.w, p.h)}</style></head><body>${p.html(p.w, p.h)}</body></html>`;
    await page.setContent(doc, { waitUntil: 'networkidle' });
    await page.evaluate(() => document.fonts.ready);
    await page.waitForTimeout(400);
    const file = path.join(OUT, `${p.name}.png`);
    await page.screenshot({ path: file });
    console.log(`${p.name}.png  ${p.w}x${p.h}`);
    await page.close();
  }
  await browser.close();
})();
