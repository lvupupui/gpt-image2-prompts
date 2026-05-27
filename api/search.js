// GPT Image 2 提示词搜索引擎 + JSON API — Vercel Node.js
// 机器用: /api/json                      → 全部456条JSON
// 搜索用: /api/search?keyword=奶茶&limit=5 → JSON结果
// 分类:   /api/categories               → 分类列表JSON

const { readFileSync } = require('fs');
const { join } = require('path');

const raw = JSON.parse(readFileSync(join(__dirname, 'data.json'), 'utf-8'));
const CASES = raw.cases || [];
const CATS = raw.cats || [];
const BASE = 'https://gpt-image2-prompts-sandy.vercel.app';

function search(keyword, category, limit) {
  let kw = (keyword || '').toLowerCase().trim();
  let results = [...CASES];
  if (category) results = results.filter(c => (c.category || '').toLowerCase() === category.toLowerCase());
  if (kw) {
    results = results.filter(c => {
      try {
        let s = c.title + ' ' + c.prompt + ' ' + (Array.isArray(c.styles) ? c.styles.join(' ') : '') + ' ' + (Array.isArray(c.scenes) ? c.scenes.join(' ') : '');
        return s.toLowerCase().includes(kw);
      } catch(e) { return false; }
    });
    results.sort((a, b) => {
      const at = (a.title || '').toLowerCase().includes(kw) ? 100 : 0;
      const bt = (b.title || '').toLowerCase().includes(kw) ? 100 : 0;
      return bt - at;
    });
  }
  results.forEach(c => {
    if (c.image) {
      let fn = c.image.split('/').pop().replace('.jpg','.webp').replace('.png','.webp');
      c.image_url = BASE + '/images/' + fn;
    }
  });
  return results.slice(0, limit);
}

module.exports = async (req, res) => {
  const path = req.url.split('?')[0].replace(/\/+$/, '') || '/';
  const { keyword, category, limit: lim } = req.query;
  const limit = Math.min(parseInt(lim) || 5, 20);

  res.setHeader('Access-Control-Allow-Origin', '*');
  
  if (req.method === 'OPTIONS') {
    res.status(204).end();
    return;
  }

  // 全部JSON — 机器用
  if (path === '/api/json') {
    res.json({
      success: true,
      total: CASES.length,
      categories: CATS.length,
      base_url: BASE,
      data: CASES.map(c => ({
        id: c.id,
        title: c.title,
        category: c.category,
        prompt: c.prompt,
        styles: Array.isArray(c.styles) ? c.styles : [],
        scenes: Array.isArray(c.scenes) ? c.scenes : [],
        image: c.image ? (BASE + '/images/' + c.image.split('/').pop().replace('.jpg','.webp').replace('.png','.webp')) : null,
        imageAlt: c.imageAlt || '',
        sourceLabel: c.sourceLabel || '',
        sourceUrl: c.sourceUrl || ''
      }))
    });
    return;
  }

  // 搜索 — JSON返回
  if (path === '/' || path === '/api' || path === '/api/search') {
    if (!keyword && !category) {
      res.json({
        name: 'GPT Image 2 提示词搜索引擎',
        usage: '/api/search?keyword=奶茶&limit=5',
        json_api: '/api/json',
        categories_api: '/api/categories',
        total_prompts: CASES.length,
        price: '0.50 UT/次'
      });
      return;
    }
    const results = search(keyword, category, limit);
    res.json({
      success: true,
      keyword: keyword || '',
      category: category || '',
      total_matched: results.length,
      limit: limit,
      results: results.map(c => ({
        id: c.id,
        title: c.title,
        category: c.category,
        prompt: c.prompt && c.prompt.length > 300 ? c.prompt.slice(0,300) + '...' : (c.prompt || ''),
        prompt_full: c.prompt || '',
        styles: Array.isArray(c.styles) ? c.styles : [],
        scenes: Array.isArray(c.scenes) ? c.scenes : [],
        image: c.image_url || null
      }))
    });
    return;
  }

  if (path === '/api/categories') {
    res.json({ success: true, total: CATS.length, categories: CATS });
    return;
  }

  if (path === '/api/random') {
    const c = CASES.length ? CASES[Math.floor(Math.random() * CASES.length)] : null;
    res.json({ success: true, result: c ? {
      id: c.id, title: c.title, category: c.category, prompt: c.prompt,
      styles: Array.isArray(c.styles) ? c.styles : [],
      image: c.image ? (BASE + '/images/' + c.image.split('/').pop().replace('.jpg','.webp').replace('.png','.webp')) : null
    } : null });
    return;
  }

  res.status(404).json({ error: 'not found' });
};
