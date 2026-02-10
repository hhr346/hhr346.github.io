# Academic Personal Homepage

一个学术型个人主页，风格克制、信息优先、模块化、可长期维护，部署在 GitHub Pages 上。

## 特性

- **技术栈**: Astro + TypeScript + Pagefind
- **风格**: 简洁 / 克制 / 文档式纵向结构
- **响应式**: 适配桌面端和移动端
- **搜索**: 集成 Pagefind 静态搜索
- **内容管理**: 支持 Markdown / MDX

## 项目结构

```
/
├─ public/
│  ├─ me.jpg                # 个人照片
│  ├─ cv.pdf                # 简历（可选）
│  └─ papers/               # 论文 PDF
│
├─ src/
│  ├─ components/
│  │  ├─ Header.astro
│  │  ├─ Footer.astro
│  │  ├─ Intro.astro        # 首页个人介绍区
│  │  ├─ Section.astro      # 通用栏目组件
│  │  └─ PublicationItem.astro
│  │
│  ├─ layouts/
│  │  ├─ BaseLayout.astro
│  │  └─ ContentLayout.astro
│  │
│  ├─ content/
│  │  ├─ projects/
│  │  ├─ blog/
│  │  ├─ notes/
│  │  └─ papers/
│  │
│  ├─ pages/
│  │  ├─ index.astro        # 首页（纵向文档）
│  │  ├─ projects.astro
│  │  ├─ blog.astro
│  │  ├─ notes.astro
│  │  ├─ papers.astro
│  │  └─ search.astro
│  │
│  └─ styles/
│     └─ global.css
│
├─ astro.config.mjs
├─ package.json
└─ README.md
```

## 开发

```bash
# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 构建生产版本
npm run build

# 预览生产构建
npm run preview
```

## 部署

此项目适用于 GitHub Pages 部署。修改 `astro.config.mjs` 中的 `site` 和 `base` 配置项以匹配您的仓库名称。

## 许可证

MIT