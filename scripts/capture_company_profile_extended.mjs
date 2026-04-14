import { chromium } from "playwright";
import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const htmlPath = `file://${path.join(root, "ziyada_company_profile_extended.html")}`;
const outDir = path.join(root, "tmp", "ziyada_company_profile_extended");
fs.mkdirSync(outDir, { recursive: true });

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({
  viewport: { width: 1360, height: 800 },
  deviceScaleFactor: 1,
});

await page.goto(htmlPath, { waitUntil: "networkidle" });
await page.waitForTimeout(1500);

const slides = page.locator(".slide");
const count = await slides.count();

for (let i = 0; i < count; i += 1) {
  const target = slides.nth(i);
  await target.screenshot({
    path: path.join(outDir, `slide-${String(i + 9).padStart(2, "0")}.png`),
  });
}

await browser.close();
console.log(outDir);
