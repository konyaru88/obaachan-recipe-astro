import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const SITE = 'https://www.obaachan-recipe.com';
const today = new Date().toISOString().split('T')[0];

// Load recipes
const recipesData = JSON.parse(
  fs.readFileSync(path.join(__dirname, '../src/data/recipes.json'), 'utf-8')
);
const recipes = recipesData.recipes;

// Load articles
let articles = [];
const articlesPath = path.join(__dirname, '../src/data/articles.json');
if (fs.existsSync(articlesPath)) {
  const articlesData = JSON.parse(fs.readFileSync(articlesPath, 'utf-8'));
  articles = articlesData.articles || articlesData || [];
}

// Region codes
const regions = [
  'hokkaido', 'tohoku', 'kanto', 'koshinetsu',
  'hokuriku', 'tokai', 'kinki', 'chugoku',
  'shikoku', 'kyushu'
];

// Build URL entries
const urls = [];

// Top page - highest priority
urls.push({ loc: '/', priority: '1.0', changefreq: 'daily' });

// Main listing pages
urls.push({ loc: '/recipes/', priority: '0.9', changefreq: 'daily' });
urls.push({ loc: '/regions/', priority: '0.7', changefreq: 'weekly' });
urls.push({ loc: '/articles/', priority: '0.7', changefreq: 'weekly' });
urls.push({ loc: '/support/', priority: '0.5', changefreq: 'monthly' });

// Individual recipe pages
for (const recipe of recipes) {
  urls.push({
    loc: `/recipes/${recipe.id}/`,
    priority: '0.8',
    changefreq: 'monthly',
  });
}

// Region pages
for (const code of regions) {
  urls.push({
    loc: `/region/${code}/`,
    priority: '0.6',
    changefreq: 'weekly',
  });
}

// Article category pages
const articleCategories = ['teshigoto', 'life', 'story', 'column'];
for (const cat of articleCategories) {
  urls.push({
    loc: `/articles/${cat}/`,
    priority: '0.7',
    changefreq: 'weekly',
  });
}

// Article pages
for (const article of articles) {
  if (article.id) {
    urls.push({
      loc: `/articles/${article.id}/`,
      priority: '0.6',
      changefreq: 'monthly',
    });
  }
}

// Generate XML
const xml = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${urls.map(u => `  <url>
    <loc>${SITE}${u.loc}</loc>
    <lastmod>${today}</lastmod>
    <changefreq>${u.changefreq}</changefreq>
    <priority>${u.priority}</priority>
  </url>`).join('\n')}
</urlset>
`;

const distDir = path.join(__dirname, '../dist');
if (!fs.existsSync(distDir)) {
  fs.mkdirSync(distDir, { recursive: true });
}

fs.writeFileSync(path.join(distDir, 'sitemap.xml'), xml);
console.log(`✅ sitemap.xml generated with ${urls.length} URLs`);
