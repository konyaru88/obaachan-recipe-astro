import { defineConfig } from 'astro/config';

export default defineConfig({
  site: 'https://www.obaachan-recipe.com',
  output: 'static',
  trailingSlash: 'always',
  compressHTML: true,
  i18n: {
    defaultLocale: 'ja',
    locales: ['ja', 'en'],
    routing: {
      prefixDefaultLocale: false,
    },
  },
});
