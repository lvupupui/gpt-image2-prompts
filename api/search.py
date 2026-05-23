# GPT Image 2 提示词搜索引擎 — Vercel Flask
# 调用: /api/search?keyword=奶茶&limit=2 → 下载TXT文件

import json, random, os
from flask import Flask, request, Response, jsonify

app = Flask(__name__)

# 从同目录加载数据文件
data_path = os.path.join(os.path.dirname(__file__), 'data.json')
with open(data_path, 'r', encoding='utf-8') as f:
    DATA = json.load(f)

CASES = DATA.get("cases", [])
CATS = DATA.get("cats", [])
BASE = "https://gpt-image2-prompts-sandy.vercel.app"

def search(kw, cat, lim):
    kw = kw.lower().strip() if kw else ""
    r = CASES
    if cat:
        r = [c for c in r if c.get("category","").lower() == cat.lower()]
    if kw:
        r = [c for c in r if kw in (c.get("title","") + c.get("prompt","") + " ".join(c.get("styles",[])) + " ".join(c.get("scenes",[]))).lower()]
        r = sorted(r, key=lambda c: -(kw in c.get("title","").lower())*100 - (kw in c.get("prompt","").lower())*10)
    return r[:lim]

def gen_txt(results, kw):
    L = []
    L.append("=" * 60)
    L.append("GPT Image 2 提示词搜索引擎 - 搜索结果")
    L.append("=" * 60)
    if kw: L.append("关键词：" + kw)
    L.append("匹配结果：" + str(len(results)) + " 条")
    L.append("完整版456条提示词+461张图：UUMit知识商店 198 UT")
    L.append("https://m.uumit.com/digital-assets/my/b18ab551-fa05-4232-8aea-f1bdd41702d2")
    L.append("=" * 60)
    L.append("")
    for i, c in enumerate(results, 1):
        L.append("-" * 60)
        L.append(f"【{i}】#{c.get('id','')} {c.get('title','')}")
        L.append(f"   分类：{c.get('category','')} | 风格：{'、'.join(c.get('styles',[]))}")
        if c.get("image"):
            fn = c["image"].split("/")[-1].replace(".jpg",".webp").replace(".png",".webp")
            L.append(f"   参考图：{BASE}/images/{fn}")
        p = c.get("prompt","")
        if len(p) > 300: p = p[:300] + "..."
        L.append("   提示词预览：")
        for l in p.split("\n"): L.append("     " + l)
        L.append("")
    L.append("=" * 60)
    L.append("完整版456条提示词+461张图：UUMit知识商店 198 UT")
    L.append("https://m.uumit.com/digital-assets/my/b18ab551-fa05-4232-8aea-f1bdd41702d2")
    L.append("=" * 60)
    return "\n".join(L)

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def catch_all(path):
    p = "/" + path.rstrip("/") if path else "/"
    kw = request.args.get("keyword", "")
    cat = request.args.get("category", "")
    lim = min(int(request.args.get("limit", "5")), 20)
    
    if p in ("/", "/api", "/api/search"):
        if not kw and not cat:
            return jsonify({"name": "GPT Image 2 提示词搜索引擎", "usage": "/api/search?keyword=奶茶&limit=5", "price": "10 UT/次，返回TXT下载"})
        txt = gen_txt(search(kw, cat, lim), kw)
        fn = "gpt-image2-search-" + (kw or "all") + ".txt"
        return Response(txt, mimetype="text/plain; charset=utf-8", headers={"Content-Disposition": f'attachment; filename="{fn}"'})
    
    if p == "/api/categories":
        return jsonify({"success": True, "total": len(CATS), "categories": CATS})
    
    if p == "/api/random":
        c = random.choice(CASES) if CASES else {}
        return Response(gen_txt([c], ""), mimetype="text/plain; charset=utf-8", headers={"Content-Disposition": 'attachment; filename="gpt-image2-random.txt"'})
    
    return jsonify({"error": "not found"}), 404
