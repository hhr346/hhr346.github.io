import { defineCollection } from 'astro:content';
import { z } from 'zod';

// 项目集合
const projectsCollection = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    description: z.string(),
    pubDate: z.coerce.date(),
    tags: z.array(z.string()).optional(),
    draft: z.boolean().optional(),
  }),
});

// 博客集合
const blogCollection = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    description: z.string(),
    pubDate: z.coerce.date(),
    tags: z.array(z.string()).optional(),
    draft: z.boolean().optional(),
  }),
});

// 笔记集合
const notesCollection = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    description: z.string(),
    pubDate: z.coerce.date(),
    tags: z.array(z.string()).optional(),
    draft: z.boolean().optional(),
  }),
});

// 论文集合
const papersCollection = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    authors: z.string(),
    venue: z.string().optional(),
    year: z.number(),
    pdf: z.string().optional(),
    link: z.string().optional(),
    draft: z.boolean().optional(),
  }),
});

export const collections = {
  projects: projectsCollection,
  blog: blogCollection,
  notes: notesCollection,
  papers: papersCollection,
};