import { defineConfig } from 'astro/config';

// https://astro.build/config
export default defineConfig({
  site: 'https://your-username.github.io',
  base: '/personal-website', // 如果使用 GitHub Pages 子路径，请设置此选项
  trailingSlash: 'never', // 确保 URL 末尾不带斜杠
});