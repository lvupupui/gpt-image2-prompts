// GPT Image 2 提示词搜索引擎 — Vercel Node.js
// 调用: /api/search?keyword=奶茶&limit=2  → TXT下载
// Vercel Node.js 零依赖，无需npm install

const { readFileSync } = require('fs');
const { join } = require('path');

// 加载数据
const raw = JSON.parse(readFileSync(join(__dirname, 'data.json'), 'utf-8'));
const CASES = raw.cases || [];
const CATS = raw.cats || [];
const BASE = 'https://gpt-image2-prompts-sandy.vercel.app';

function search(keyword, category, limit) {
  let kw = (keyword || '').toLowerCase().trim();
  let results = [...CASES];
  if (category) results = results.filter(c => (c.category || '').toLowerCase() === category.toLowerCase());
  if (kw) {
    results = results.filter(c => (c.title + ' ' + c.prompt + ' ' + (c.styles||[]).join(' ') + ' ' + (c.scenes||[]).join(' ')).toLowerCase().includes(kw));
    results.sort((a, b) => {
      const at = (a.title || '').toLowerCase().includes(kw) ? 100 : 0;
      const bt = (b.title || '').toLowerCase().includes(kw) ? 100 : 0;
      return bt - at;
    });
  }
  return results.slice(0, limit);
}

function genTxt(results, kw) {
  let L = [];
  L.push('='.repeat(60));
  L.push('GPT Image 2 提示词搜索引擎 - 搜索结果');
  L.push('='.repeat(60));
  if (kw) L.push('关键词：' + kw);
  L.push('匹配结果：' + results.length + ' 条');
  L.push('完整版456条提示词+461张图：UUMit知识商店 198 UT');
  L.push('https://m.uumit.com/digital-assets/my/b18ab551-fa05-4232-8aea-f1bdd41702d2');
  L.push('='.repeat(60));
  L.push('');
  results.forEach((c, i) => {
    L.push('-'.repeat(60));
    L.push('【' + (i+1) + '】#' + (c.id||'') + ' ' + (c.title||''));
    L.push('   分类：' + (c.category||'') + ' | 风格：' + ((c.styles||[]).join('、')));
    if (c.image) {
      let fn = c.image.split('/').pop().replace('.jpg','.webp').replace('.png','.webp');
      L.push('   参考图：' + BASE + '/images/' + fn);
    }
    let p = c.prompt || '';
    if (p.length > 300) p = p.slice(0,300) + '...';
    L.push('   提示词预览：');
    p.split('\n').forEach(l => L.push('     ' + l));
    L.push('');
  });
  L.push('='.repeat(60));
  L.push('完整版456条提示词+461张图：UUMit知识商店 198 UT');
  L.push('https://m.uumit.com/digital-assets/my/b18ab551-fa05-4232-8aea-f1bdd41702d2');
  L.push('='.repeat(60));
  return L.join('\n');
}

module.exports = async (req, res) => {
  const path = req.url.split('?')[0].replace(/\/+$/, '') || '/';
  const { keyword, category, limit: lim } = req.query;
  const limit = Math.min(parseInt(lim) || 5, 20);

  // CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  
  if (req.method === 'OPTIONS') {
    res.status(204).end();
    return;
  }

  if (path === '/' || path === '/api' || path === '/api/search') {
    if (!keyword && !category) {
      res.json({ name: 'GPT Image 2 提示词搜索引擎', usage: '/api/search?keyword=奶茶&limit=5', price: '10 UT/次，返回TXT下载' });
      return;
    }
    const results = search(keyword, category, limit);
    const txt = genTxt(results, keyword);
    const fn = 'gpt-image2-search-' + (keyword || 'all') + '.txt';
    res.setHeader('Content-Type', 'text/plain; charset=utf-8');
    res.setHeader('Content-Disposition', 'attachment; filename="' + fn + '"');
    res.send(txt);
    return;
  }

  if (path === '/api/categories') {
    res.json({ success: true, total: CATS.length, categories: CATS });
    return;
  }

  if (path === '/api/random') {
    const c = CASES.length ? CASES[Math.floor(Math.random() * CASES.length)] : {};
    const txt = genTxt([c], '');
    res.setHeader('Content-Type', 'text/plain; charset=utf-8');
    res.setHeader('Content-Disposition', 'attachment; filename="gpt-image2-random.txt"');
    res.send(txt);
    return;
  }

  res.status(404).json({ error: 'not found' });
};
