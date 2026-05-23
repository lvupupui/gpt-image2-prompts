# GPT Image 2 提示词搜索引擎 — Vercel Python (Serverless)
# Vercel 会自动把 /api/index.py 映射到 /api/* 路由
# 用 Flask 或 WSGI 兼容写法

import json, random
from urllib.parse import urlparse, parse_qs

# 内嵌数据
DATA = json.loads("""{"cases":[{"id":1,"title":"城市数据看板信息图","category":"UI & Interfaces","image":"images/case1.webp","styles":["UI","Infographic"],"prompt":"Vertical 9:16 isometric cutaway infographic \\"智慧城市系统蓝图 / Urban Metabolism Atlas\\". Smart city from sky to bedrock: skyscrapers, streets, subway, utility tunnels, water/sewage/gas/heating pipes, fiber, data center, flood tanks, aquifers, geothermal wells, bedrock. Color-coded flows for power/water/data/traffic/waste. 12 numbered panels bilingual CN/EN: 供电系统/给排水管网/通信网络/数据中台/废物处理/交通枢纽/环境监测/公共安全/城市绿化/应急系统/商业服务/社区生活. 24h timeline at bottom. Style: engineering white paper + scientific atlas, light paper bg, crisp lines, 8K. No cyberpunk, no gibberish text, must show both ABOVE AND below ground."}],"cats":[{"name":"UI & Interfaces","count":1,"styles":["UI","Infographic"]}]}""")
CASES = DATA["cases"]
CATS = DATA["cats"]
BASE = "https://gpt-image2-prompts-sandy.vercel.app"

def do_search(keyword, category, limit):
    kw = keyword.lower().strip() if keyword else ""
    results = CASES
    if category:
        results = [c for c in results if c.get("category","").lower() == category.lower()]
    if kw:
        results = [c for c in results if kw in (
            c.get("title","") + " " + c.get("prompt","") + " " +
            " ".join(c.get("styles",[])) + " " + " ".join(c.get("scenes",[]))
        ).lower()]
        results = sorted(results, key=lambda c: (
            -(kw in c.get("title","").lower())*100 - (kw in c.get("prompt","").lower())*10
        ))
    return results[:limit]

def make_txt(results, keyword):
    lines = []
    lines.append("=" * 60)
    lines.append("GPT Image 2 提示词搜索引擎 - 搜索结果")
    lines.append("=" * 60)
    if keyword:
        lines.append("关键词：" + keyword)
    lines.append("匹配结果：" + str(len(results)) + " 条")
    lines.append("完整版456条提示词请访问UUMit知识商店（198 UT）：")
    lines.append("https://m.uumit.com/digital-assets/my/b18ab551-fa05-4232-8aea-f1bdd41702d2")
    lines.append("=" * 60)
    lines.append("")
    for i, c in enumerate(results, 1):
        lines.append("-" * 60)
        lines.append("【" + str(i) + "】#" + str(c.get("id","")) + " " + c.get("title",""))
        styles_str = "、".join(c.get("styles",[]))
        lines.append("   分类：" + c.get("category","") + " | 风格：" + styles_str)
        if c.get("image"):
            img_name = c["image"].split("/")[-1].replace(".jpg",".webp").replace(".png",".webp")
            lines.append("   参考图：https://gpt-image2-prompts-sandy.vercel.app/images/" + img_name)
        prompt = c.get("prompt","")
        if len(prompt) > 300:
            prompt = prompt[:300] + "..."
        lines.append("   提示词预览：")
        for pl in prompt.split("\n"):
            lines.append("     " + pl)
        lines.append("")
    lines.append("=" * 60)
    lines.append("完整版456条提示词+461张图：UUMit知识商店 198 UT")
    lines.append("https://m.uumit.com/digital-assets/my/b18ab551-fa05-4232-8aea-f1bdd41702d2")
    lines.append("=" * 60)
    return "\n".join(lines)

def handler(event, context):
    path = event.get("path", "/")
    method = event.get("httpMethod", "GET")
    params = event.get("queryStringParameters") or {}
    
    kw = params.get("keyword", "")
    cat = params.get("category", "")
    lim = min(int(params.get("limit", "5")), 20)
    
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, OPTIONS"
    }
    
    if method == "OPTIONS":
        return {"statusCode": 204, "headers": headers, "body": ""}
    
    path = path.rstrip("/")
    
    # API info
    if path in ("", "/", "/api", "/api/search"):
        if not kw and not cat:
            return {
                "statusCode": 200,
                "headers": {**headers, "Content-Type": "application/json"},
                "body": json.dumps({
                    "name": "GPT Image 2 提示词搜索引擎",
                    "usage": "GET /api/search?keyword=奶茶&limit=5",
                    "price": "10 UT/次，返回TXT文件含参考图链接+提示词预览"
                }, ensure_ascii=False)
            }
        
        results = do_search(kw, cat, lim)
        txt = make_txt(results, kw)
        fname = "gpt-image2-search-" + (kw or "all") + ".txt"
        
        return {
            "statusCode": 200,
            "headers": {
                **headers,
                "Content-Type": "text/plain; charset=utf-8",
                "Content-Disposition": 'attachment; filename="' + fname + '"'
            },
            "body": txt
        }
    
    if path == "/api/categories":
        return {
            "statusCode": 200,
            "headers": {**headers, "Content-Type": "application/json"},
            "body": json.dumps({"success": True, "total": len(CATS), "categories": CATS}, ensure_ascii=False)
        }
    
    if path == "/api/random":
        c = random.choice(CASES) if CASES else {}
        txt = make_txt([c], "")
        return {
            "statusCode": 200,
            "headers": {**headers, "Content-Type": "text/plain; charset=utf-8", "Content-Disposition": 'attachment; filename="gpt-image2-random.txt"'},
            "body": txt
        }
    
    return {
        "statusCode": 404,
        "headers": {**headers, "Content-Type": "application/json"},
        "body": json.dumps({"error": "not found"})
    }
