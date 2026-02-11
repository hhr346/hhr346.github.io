import { readFile, readdir } from 'node:fs/promises';
import { join } from 'node:path';

interface Post {
  url: string;
  data: {
    title: string;
    pubDate: Date;
    description?: string;
    tags: string[];
  };
}

interface Project {
  url: string;
  data: {
    title: string;
    pubDate?: Date;
    description: string;
    tags: string[];
    link?: string;
    repo?: string;
  };
}

interface Paper {
  url: string;
  data: {
    title: string;
    pubDate: Date;
    authors: string[];
    venue?: string;
    year?: number;
    draft?: boolean;
    abstract: string;
    link?: string;
    tags: string[];
  };
}

interface Note {
  url: string;
  data: {
    title: string;
    pubDate: Date;
    description: string;
    tags: string[];
  };
}

// 读取 Markdown 文件 frontmatter
async function parseMarkdown(path: string): Promise<{
  title: string;
  pubDate?: Date;
  description?: string;
  tags?: string[];
  [key: string]: any;
}> {
  const content = await readFile(path, 'utf-8');

  // 提取 frontmatter 部分
  const frontmatterMatch = content.match(/^---\n([\s\S]*?)\n---/);
  
  if (!frontmatterMatch) {
    console.warn(`No frontmatter found in ${path}`);
    return {};
  }

  const frontmatterStr = frontmatterMatch[1];
  const frontmatter: any = {};

  // 更精确地解析 frontmatter
  const lines = frontmatterStr.split('\n');
  let currentKey = '';
  let currentVal = '';
  let inMultilineValue = false;

  for (const line of lines) {
    // 检查是否是新的键值对
    const keyValueMatch = line.match(/^(\w+)\s*:\s*(.*)$/);
    
    if (keyValueMatch && !inMultilineValue) {
      // 保存上一个键值对
      if (currentKey) {
        frontmatter[currentKey] = parseValue(currentVal.trim());
      }
      
      // 开始新的键值对
      currentKey = keyValueMatch[1].trim();
      currentVal = keyValueMatch[2].trim();
      
      // 检查是否是多行值（如数组）
      if (currentVal.endsWith('|') || currentVal.endsWith('>')) {
        inMultilineValue = true;
        currentVal = currentVal.slice(0, -1);
      } else {
        inMultilineValue = false;
      }
    } else if (inMultilineValue) {
      currentVal += '\n' + line.trim();
    }
  }

  // 保存最后一个键值对
  if (currentKey) {
    frontmatter[currentKey] = parseValue(currentVal.trim());
  }

  // 转换日期
  if (frontmatter.pubDate) {
    try {
      frontmatter.pubDate = new Date(frontmatter.pubDate);
    } catch (error) {
      console.error(`Error parsing date in ${path}:`, frontmatter.pubDate);
      frontmatter.pubDate = new Date(); // 默认为今天
    }
  }

  return frontmatter;
}

// 辅助函数：解析值类型
function parseValue(value: string): any {
  // 尝试解析数组格式
  if (value.startsWith('[') && value.endsWith(']')) {
    try {
      // 处理 ['item1', 'item2'] 格式
      const arrayContent = value.substring(1, value.length - 1);
      return arrayContent.split(',').map(item => 
        item.trim().replace(/^'|'$/g, '').replace(/^"/, '"')
      );
    } catch (e) {
      // 如果解析失败，返回原始字符串
      return value;
    }
  }

  // 解析布尔值
  if (value.toLowerCase() === 'true') return true;
  if (value.toLowerCase() === 'false') return false;

  // 解析数字
  if (!isNaN(Number(value))) return Number(value);

  // 返回字符串
  return value.replace(/^'|'$/g, '').replace(/^"|"$|^'|'$/g, '');
}

// 读取 blog 文件
export async function getBlogPosts(): Promise<Post[]> {
  const posts: Post[] = [];

  try {
    const blogDir = await join(process.cwd(), 'src/content/blog');
    const files = await readdir(blogDir);

    for (const file of files) {
      const filePath = await join(blogDir, file);
      const url = `/blog/${file.replace(/\.md$/, '')}`;
      const frontmatter = await parseMarkdown(filePath);

      posts.push({
        url,
        data: {
          title: frontmatter.title,
          pubDate: frontmatter.pubDate || new Date(), // 默认为今天
          description: frontmatter.description,
          tags: frontmatter.tags || [],
        },
      });
    }

    // 按日期倒序排序
    posts.sort((a, b) => b.data.pubDate.getTime() - a.data.pubDate.getTime());
  } catch (error) {
    console.error('Error reading blog posts:', error);
  }

  return posts;
}

// 读取项目文件
export async function getProjects(): Promise<Project[]> {
  const projects: Project[] = [];

  try {
    const projectsDir = await join(process.cwd(), 'src/content/projects');
    const files = await readdir(projectsDir);

    for (const file of files) {
      const filePath = await join(projectsDir, file);
      const url = `/projects/${file.replace(/\.md$/, '')}`;
      const frontmatter = await parseMarkdown(filePath);

      projects.push({
        url,
        data: {
          title: frontmatter.title,
          pubDate: frontmatter.pubDate ? new Date(frontmatter.pubDate) : undefined,
          description: frontmatter.description || '',
          tags: frontmatter.tags || [],
          link: frontmatter.link,
          repo: frontmatter.repo,
        },
      });
    }

    // 按日期倒序排序
    projects.sort((a, b) =>
      b.data.pubDate?.getTime() ?? 0 - (a.data.pubDate?.getTime() ?? 0)
    );
  } catch (error) {
    console.error('Error reading projects:', error);
  }

  return projects;
}

// 读取论文文件
export async function getPapers(): Promise<Paper[]> {
  const papers: Paper[] = [];

  try {
    const papersDir = await join(process.cwd(), 'src/content/papers');
    const files = await readdir(papersDir);

    for (const file of files) {
      const filePath = await join(papersDir, file);
      const url = `/papers/${file.replace(/\.md$/, '')}`;
      const frontmatter = await parseMarkdown(filePath);

      // 提取 abstract
      const content = await readFile(filePath, 'utf-8');
      const abstractMatch = content.match(/^---([\s\S]*?)---/);
      const abstract = abstractMatch
        ? abstractMatch[0].split('\n').slice(2).join('\n').trim()
        : '';

      papers.push({
        url,
        data: {
          title: frontmatter.title,
          pubDate: frontmatter.pubDate,
          authors: frontmatter.authors || [],
          venue: frontmatter.venue,
          year: frontmatter.year,
          draft: frontmatter.draft || false,
          abstract,
          link: frontmatter.link,
          tags: frontmatter.tags || [],
        },
      });
    }

    // 按日期倒序排序
    papers.sort((a, b) => b.data.pubDate.getTime() - a.data.pubDate.getTime());
  } catch (error) {
    console.error('Error reading papers:', error);
  }

  return papers;
}

// 读取笔记文件
export async function getNotes(): Promise<Note[]> {
  const notes: Note[] = [];

  try {
    const notesDir = await join(process.cwd(), 'src/content/notes');
    const files = await readdir(notesDir);

    for (const file of files) {
      const filePath = await join(notesDir, file);
      const url = `/notes/${file.replace(/\.md$/, '')}`;
      const frontmatter = await parseMarkdown(filePath);

      console.log(`Processing note: ${file}`, frontmatter);

      notes.push({
        url,
        data: {
          title: frontmatter.title,
          pubDate: frontmatter.pubDate || new Date(),
          description: frontmatter.description || '',
          tags: frontmatter.tags || [],
        },
      });
    }

    // 按日期倒序排序
    notes.sort((a, b) => b.data.pubDate.getTime() - a.data.pubDate.getTime());
  } catch (error) {
    console.error('Error reading notes:', error);
  }

  return notes;
}
