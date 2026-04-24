import sharp from 'sharp';
import { readFileSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const publicDir = resolve(__dirname, '..', 'public');

async function convert() {
  // 1. og-image.svg → og-image.png (1200x630)
  const ogSvg = readFileSync(resolve(publicDir, 'og-image.svg'));
  await sharp(ogSvg, { density: 150 })
    .resize(1200, 630)
    .png()
    .toFile(resolve(publicDir, 'og-image.png'));
  console.log('Created og-image.png (1200x630)');

  // 2. favicon.svg → apple-touch-icon.png (180x180)
  const faviconSvg = readFileSync(resolve(publicDir, 'favicon.svg'));
  await sharp(faviconSvg, { density: 300 })
    .resize(180, 180)
    .png()
    .toFile(resolve(publicDir, 'apple-touch-icon.png'));
  console.log('Created apple-touch-icon.png (180x180)');
}

convert().catch((err) => {
  console.error('Conversion failed:', err);
  process.exit(1);
});
