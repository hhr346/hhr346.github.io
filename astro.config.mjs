import { defineConfig } from 'astro/config';

// https://astro.build/config
export default defineConfig({
  site: 'https://hhr346.github.io',
  base: '/',
  trailingSlash: 'never', // 确保 URL 末尾不带斜杠
});