import { chromium, devices } from "playwright";
import path from "node:path";
import fs from "node:fs";

const outDir = "/Users/djbiggy/Downloads/Claude Code- File Agents/projects/ziyada-system/outputs/zia_exact_site_assets";
fs.mkdirSync(outDir, { recursive: true });

async function shot(url, outPath, opts = {}) {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext(opts);
  const page = await context.newPage();
  await page.goto(url, { waitUntil: "networkidle" });
  await page.waitForTimeout(2200);
  await page.screenshot({ path: outPath, fullPage: false });
  await browser.close();
}

const desktop = { viewport: { width: 1512, height: 920 } };
const mobile = devices["iPhone 14 Pro"];

await shot("http://127.0.0.1:5174/", path.join(outDir, "ziya_home_exact_en.png"), desktop);
await shot("http://127.0.0.1:5174/?lang=ar", path.join(outDir, "ziya_home_exact_ar.png"), desktop);
await shot("http://127.0.0.1:5174/?lang=ar", path.join(outDir, "ziya_home_exact_ar_mobile.png"), mobile);

console.log("Screenshots captured to:", outDir);
