// Teste de fumaça da landing. Uso: npm run build && npm start (outra aba), depois npm run smoke
// BASE_URL padrão http://localhost:3000. Falha com exit 1 se algo estiver errado.
import { chromium } from 'playwright';

const BASE = process.env.BASE_URL ?? 'http://localhost:3000';
const GL = ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'];
const results = [];
const check = (name, ok, extra = '') => {
  results.push(ok);
  console.log(`${ok ? 'ok  ' : 'FAIL'} ${name}${extra ? ' · ' + extra : ''}`);
};

const browser = await chromium.launch({ args: GL });

// 1) WebGL ligado: canvas aparece e não está em branco
{
  const page = await browser.newPage({ viewport: { width: 1280, height: 800 } });
  await page.goto(BASE, { waitUntil: 'networkidle' });
  await page.waitForSelector('#L .mascot[data-mascot="ready"]', { timeout: 30000 }).catch(() => {});
  check('mascote 3D chega a "ready"', (await page.locator('#L .mascot').getAttribute('data-mascot')) === 'ready');
  await page.waitForTimeout(1200);
  // compara o palco com e sem o canvas: se o mascote desenha, os pixels mudam
  const withCanvas = await page.locator('#L .mascot').screenshot();
  await page.locator('#L .mascot canvas').evaluate((c) => (c.style.visibility = 'hidden'));
  const without = await page.locator('#L .mascot').screenshot();
  await page.locator('#L .mascot canvas').evaluate((c) => (c.style.visibility = 'visible'));
  const opaque = await page.evaluate(async ([a, b]) => {
    const load = async (b64) => {
      const img = new Image();
      img.src = 'data:image/png;base64,' + b64;
      await img.decode();
      const c = document.createElement('canvas');
      c.width = img.width;
      c.height = img.height;
      const g = c.getContext('2d');
      g.drawImage(img, 0, 0);
      return g.getImageData(0, 0, c.width, c.height).data;
    };
    const [x, y] = await Promise.all([load(a), load(b)]);
    let n = 0;
    for (let i = 0; i < x.length; i += 4) {
      if (Math.abs(x[i] - y[i]) + Math.abs(x[i + 1] - y[i + 1]) + Math.abs(x[i + 2] - y[i + 2]) > 24) n++;
    }
    return n / (x.length / 4);
  }, [withCanvas.toString('base64'), without.toString('base64')]);
  check('canvas não está em branco', opaque > 0.08, `${(opaque * 100).toFixed(1)}% dos pixels do palco mudam`);
  check('seção de vídeo existe', (await page.locator('#video video').count()) === 1);
  check('5 capítulos clicáveis', (await page.locator('#video .chapters button').count()) === 5);
  await page.getByRole('link', { name: 'Ver em ação' }).click();
  await page.waitForTimeout(600);
  check('"Ver em ação" rola até o vídeo sem sair da landing', (await page.locator('#L').isVisible()) && !(await page.evaluate(() => location.hash.startsWith('#/'))));
  await page.locator('#video .chapters button').nth(2).click();
  const t = await page.evaluate(() => document.querySelector('#video video').currentTime);
  check('capítulo leva ao tempo certo', Math.abs(t - 21.94) < 0.6, `t=${t.toFixed(2)}`);
  await page.close();
}

// 2) movimento reduzido: imagem oficial, sem canvas
{
  const ctx = await browser.newContext({ reducedMotion: 'reduce', viewport: { width: 1280, height: 800 } });
  const page = await ctx.newPage();
  await page.goto(BASE, { waitUntil: 'networkidle' });
  await page.waitForTimeout(800);
  check('movimento reduzido: sem canvas', (await page.locator('#L .mascot canvas').count()) === 0);
  check('movimento reduzido: imagem oficial visível', await page.locator('#L .mascot img').isVisible());
  await ctx.close();
}

// 3) sem WebGL: cai para a imagem
{
  const ctx = await browser.newContext({ viewport: { width: 1280, height: 800 } });
  await ctx.addInitScript(() => {
    const orig = HTMLCanvasElement.prototype.getContext;
    HTMLCanvasElement.prototype.getContext = function (type, ...a) {
      return /webgl/.test(type) ? null : orig.call(this, type, ...a);
    };
  });
  const page = await ctx.newPage();
  await page.goto(BASE, { waitUntil: 'networkidle' });
  await page.waitForTimeout(800);
  check('sem WebGL: sem canvas', (await page.locator('#L .mascot canvas').count()) === 0);
  check('sem WebGL: imagem oficial visível', await page.locator('#L .mascot img').isVisible());
  await ctx.close();
}

await browser.close();
const failed = results.filter((r) => !r).length;
console.log(failed ? `\n${failed} falha(s)` : '\ntudo certo');
process.exit(failed ? 1 : 0);
