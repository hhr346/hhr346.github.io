import { z } from 'astro:content';

// 博客文章 Schema
export const blog = z.object({
  title: z.string(),
  pubDate: z.coerce.date(),
  description: z.string().optional(),
  tags: z.array(z.string()).default([]),
  author: z.string().optional(),
});

// 项目 Schema
export const projects = z.object({
  title: z.string(),
  pubDate: z.coerce.date().optional(),
  description: z.string(),
  tags: z.array(z.string()).default([]),
  link: z.string().url().optional(),
  image: z.string().url().optional(),
  repo: z.string().url().optional(),
});

// 论文 Schema
export const papers = z.object({
  title: z.string(),
  pubDate: z.coerce.date(),
  authors: z.array(z.string()).default([]),
  venue: z.string().optional(),
  year: z.coerce.number().optional(),
  draft: z.boolean().optional(),
  link: z.string().url().optional(),
  tags: z.array(z.string()).default([]),
});

// 笔记 Schema
export const notes = z.object({
  title: z.string(),
  pubDate: z.coerce.date(),
  description: z.string(),
  tags: z.array(z.string()).default([]),
});
