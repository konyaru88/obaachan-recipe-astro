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

// Article category slugs
const articleCategories = ['teshigoto', 'life', 'story', 'column'];

// Build URL entries with hreflang pairs
const urls = [];

function addUrl(jaLoc, enLoc, priority, changefreq) {
  urls.push({ jaLoc, enLoc, priority, changefreq });
}

// Top page
addUrl('/', '/en/', '1.0', 'daily');

// Main listing pages
addUrl('/recipes/', '/en/recipes/', '0.9', 'daily');
addUrl('/regions/', '/en/regions/', '0.7', 'weekly');
addUrl('/articles/', '/en/articles/', '0.7', 'weekly');
addUrl('/support/', '/en/support/', '0.5', 'monthly');
addUrl('/about/', null, '0.6', 'monthly');
addUrl('/contact/', null, '0.3', 'yearly');

// Individual recipe pages
for (const recipe of recipes) {
  addUrl(
    `/recipes/${recipe.id}/`,
    `/en/recipes/${recipe.id}/`,
    '0.8',
    'monthly'
  );
}

// Region pages
for (const code of regions) {
  addUrl(
    `/region/${code}/`,
    `/en/region/${code}/`,
    '0.6',
    'weekly'
  );
}

// Article category pages
for (const cat of articleCategories) {
  addUrl(
    `/articles/${cat}/`,
    null,
    '0.7',
    'weekly'
  );
}

// Article pages
for (const article of articles) {
  if (article.id) {
    addUrl(
      `/articles/${article.id}/`,
      `/en/articles/${article.id}/`,
      '0.6',
      'monthly'
    );
  }
}

// Generate XML with xhtml:link hreflang
const xmlEntries = [];

for (const u of urls) {
  // Japanese URL entry
  let jaEntry = `  <url>\n    <loc>${SITE}${u.jaLoc}</loc>\n    <lastmod>${today}</lastmod>\n    <changefreq>${u.changefreq}</changefreq>\n    <priority>${u.priority}</priority>`;
  if (u.enLoc) {
    jaEntry += `\n    <xhtml:link rel="alternate" hreflang="ja" href="${SITE}${u.jaLoc}"/>`;
    jaEntry += `\n    <xhtml:link rel="alternate" hreflang="en" href="${SITE}${u.enLoc}"/>`;
    jaEntry += `\n    <xhtml:link rel="alternate" hreflang="x-default" href="${SITE}${u.jaLoc}"/>`;
  }
  jaEntry += `\n  </url>`;
  xmlEntries.push(jaEntry);

  // English URL entry (if exists)
  if (u.enLoc) {
    let enEntry = `  <url>\n    <loc>${SITE}${u.enLoc}</loc>\n    <lastmod>${today}</lastmod>\n    <changefreq>${u.changefreq}</changefreq>\n    <priority>${u.priority}`;
    enEntry += `</priority>\n    <xhtml:link rel="alternate" hreflang="ja" href="${SITE}${u.jaLoc}"/>`;
    enEntry += `\n    <xhtml:link rel="alternate" hreflang="en" href="${SITE}${u.enLoc}"/>`;
    enEntry += `\n    <xhtml:link rel="alternate" hreflang="x-default" href="${SITE}${u.jaLoc}"/>`;
    enEntry += `\n  </url>`;
    xmlEntries.push(enEntry);
  }
}

const xml = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:xhtml="http://www.w3.org/1999/xhtml">
${xmlEntries.join('\n')}
</urlset>
`;

const distDir = path.join(__dirname, '../dist');
if (!fs.existsSync(distDir)) {
  fs.mkdirSync(distDir, { recursive: true });
}

fs.writeFileSync(path.join(distDir, 'sitemap.xml'), xml);
const totalUrls = xmlEntries.length;
console.log(`✅ sitemap.xml generated with ${totalUrls} URLs (ja + en with hreflang)`);
