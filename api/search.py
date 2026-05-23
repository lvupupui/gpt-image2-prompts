# GPT Image 2 提示词搜索引擎 — Vercel Serverless API
# 调用方式:
#   GET /api/search?keyword=奶茶&limit=5
#   GET /api/search?category=Products&limit=10
#   GET /api/search?keyword=奶茶&category=Products
#   GET /api/categories  — 获取分类列表
#
# 返回: JSON { success, total, results: [...] }

import json, urllib.request, os, random

DATA_URL = "https://raw.githubusercontent.com/freestylefly/awesome-gpt-image-2/main/data/cases.json"
CASES = None
CATS = None
CACHED_RAW = None

def ensure_data():
    global CASES, CATS, CACHED_RAW
    if CASES is not None:
        return
    try:
        # Use a cache-friendly approach
        req = urllib.request.Request(DATA_URL, headers={"User-Agent": "UUMit/1.0"})
        resp = urllib.request.urlopen(req, timeout=15)
        CACHED_RAW = json.loads(resp.read())
        CASES = CACHED_RAW.get("cases", [])
        # Build categories
        cat_map = {}
        for c in CASES:
            cat = c.get("category", "Other")
            if cat not in cat_map:
                cat_map[cat] = {"name": cat, "count": 0, "styles": set()}
            cat_map[cat]["count"] += 1
            for s in c.get("styles", []):
                cat_map[cat]["styles"].add(s)
        CATS = [{"name": k, "count": v["count"], "styles": list(v["styles"])} for k, v in sorted(cat_map.items())]
    except Exception as e:
        CASES = []
        CATS = []

def search_cases(keyword, category, limit):
    kw = keyword.lower().strip() if keyword else ""
    results = CASES
    
    if category:
        results = [c for c in results if c.get("category", "").lower() == category.lower()]
    
    if kw:
        results = [c for c in results if kw in (
            c.get("title", "") + " " + c.get("prompt", "") + " " +
            " ".join(c.get("styles", [])) + " " + " ".join(c.get("scenes", []))
        ).lower()]
        # Sort by relevance
        results = sorted(results, key=lambda c: (
            -(kw in c.get("title", "").lower()) * 100 -
            (kw in c.get("prompt", "").lower()) * 10
        ))
    
    results = results[:limit]
    
    return {
        "total": len(CASES) if not kw and not category else None,
        "returned": len(results),
        "results": [{
            "id": c.get("id"),
            "title": c.get("title"),
            "category": c.get("category"),
            "styles": c.get("styles", []),
            "scenes": c.get("scenes", []),
            "prompt": c.get("prompt", ""),
            "imageUrl": f"https://raw.githubusercontent.com/freestylefly/awesome-gpt-image-2/main{c['image']}" if c.get("image") else None
        } for c in results]
    }

def handler(request):
    path = request.path.rstrip("/")
    
    # CORS headers
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, OPTIONS",
        "Content-Type": "application/json; charset=utf-8",
        "Cache-Control": "public, max-age=60, s-maxage=120"
    }
    
    if request.method == "OPTIONS":
        return (204, headers, "")
    
    ensure_data()
    
    # Parse query params
    from urllib.parse import parse_qs
    params = parse_qs(request.query_string.decode()) if request.query_string else {}
    
    kw = params.get("keyword", [""])[0]
    cat = params.get("category", [""])[0]
    lim = int(params.get("limit", ["10"])[0])
    lim = max(1, min(lim, 50))
    
    # Route
    if path in ("", "/", "/search"):
        if not kw and not cat:
            return (200, headers, json.dumps({
                "success": True,
                "name": "GPT Image 2 提示词搜索引擎",
                "usage": {
                    "search": "/api/search?keyword=奶茶&category=Products&limit=5",
                    "categories": "/api/categories",
                    "random": "/api/random",
                    "stats": "/api/stats"
                },
                "pricing": "10 UT per query on UUMit Data Plaza",
                "total_cases": len(CASES),
                "categories": len(CATS)
            }, ensure_ascii=False))
        
        result = search_cases(kw, cat, lim)
        return (200, headers, json.dumps({"success": True, "keyword": kw, "category": cat or "all", **result}, ensure_ascii=False))
    
    if path == "/categories":
        return (200, headers, json.dumps({"success": True, "total": len(CATS), "categories": CATS}, ensure_ascii=False))
    
    if path == "/random":
        if not CASES:
            return (200, headers, json.dumps({"success": False, "error": "暂无数据"}))
        c = random.choice(CASES)
        return (200, headers, json.dumps({"success": True, "result": {
            "id": c.get("id"),
            "title": c.get("title"),
            "category": c.get("category"),
            "styles": c.get("styles", []),
            "prompt": c.get("prompt", ""),
            "imageUrl": f"https://raw.githubusercontent.com/freestylefly/awesome-gpt-image-2/main{c['image']}" if c.get("image") else None
        }}, ensure_ascii=False))
    
    if path == "/stats":
        style_set = set()
        for c in CASES:
            for s in c.get("styles", []):
                style_set.add(s)
        return (200, headers, json.dumps({
            "success": True, "totalCases": len(CASES),
            "categories": len(CATS), "styles": len(style_set)
        }, ensure_ascii=False))
    
    return (404, headers, json.dumps({"success": False, "error": "not found", "hint": "try /api/search?keyword=奶茶"}, ensure_ascii=False))

# Vercel Python Runtime Entry
try:
    from flask import Flask, request, jsonify
    app = Flask(__name__)
    
    @app.route("/", defaults={"path": ""}, methods=["GET", "OPTIONS"])
    @app.route("/<path:path>", methods=["GET", "OPTIONS"])
    def catch_all(path):
        if request.method == "OPTIONS":
            return "", 204, {"Access-Control-Allow-Origin": "*"}
        class Req: pass
        req = Req()
        req.path = "/" + path
        req.query_string = request.query_string.encode() if request.query_string else b""
        req.method = request.method
        code, h, body = handler(req)
        return body, code, h
    
except ImportError:
    pass  # Running on Vercel, Flask not needed
