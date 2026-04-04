import sharp from 'sharp';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.join(__dirname, '..');

const WIDTH = 1200;
const HEIGHT = 630;
const BG_COLOR = '#FAFAF8';
const ICON_SIZE = 280;

async function generate() {
  // Load and resize grandma icon
  const icon = await sharp(path.join(root, 'public/assets/images/grandma-icon.png'))
    .resize(ICON_SIZE, ICON_SIZE, { fit: 'contain', background: { r: 0, g: 0, b: 0, alpha: 0 } })
    .toBuffer();

  // Create SVG with site name text
  const textSvg = `
  <svg width="${WIDTH}" height="${HEIGHT}">
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Shippori+Mincho:wght@600');
      .title { font-family: 'Shippori Mincho', serif; font-size: 52px; fill: #47454B; font-weight: 600; }
      .subtitle { font-family: 'Shippori Mincho', serif; font-size: 24px; fill: #8a8888; font-weight: 400; }
    </style>
    <text x="${WIDTH / 2}" y="${HEIGHT / 2 + ICON_SIZE / 2 + 30}" text-anchor="middle" class="title">おばあちゃんのレシピ</text>
    <text x="${WIDTH / 2}" y="${HEIGHT / 2 + ICON_SIZE / 2 + 70}" text-anchor="middle" class="subtitle">全国のおばあちゃんの手料理が集まる文化メディア</text>
  </svg>`;

  // Composite everything
  await sharp({
    create: {
      width: WIDTH,
      height: HEIGHT,
      channels: 4,
      background: BG_COLOR,
    },
  })
    .composite([
      {
        input: icon,
        left: Math.round((WIDTH - ICON_SIZE) / 2),
        top: Math.round((HEIGHT - ICON_SIZE) / 2 - 60),
      },
      {
        input: Buffer.from(textSvg),
        left: 0,
        top: 0,
      },
    ])
    .jpeg({ quality: 90 })
    .toFile(path.join(root, 'public/assets/images/ogp-default.jpg'));

  console.log('✅ OGP画像を生成しました: public/assets/images/ogp-default.jpg');
}

generate().catch(console.error);
