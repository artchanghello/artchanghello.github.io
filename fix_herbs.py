#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从 446-query.html 提取方剂组成，彻底清理药材名
    方法：按行扫描，遇到 modal-overlay 开始计数，完整提取块内容
    策略：提取药名（找到剂量起点，前面就是药名），而非删除剂量
"""

import re, json

HTML_FILE = "446-query.html"
OUT_JS   = "446-formula-herbs.js"

with open(HTML_FILE, "r", encoding="utf-8") as f:
    lines = f.readlines()

# 药名白名单：本身含数字/单位字符的药材名，需要保护不被误切
HERB_WHITELIST = {
    "百合", "一枝黄花", "半枝莲", "三七", "五味子",
    "白芍", "白术", "白芷", "白蔹", "白及", "白前",
}

def clean_herb(raw):
    h = raw.strip()
    if not h:
        return None

    # 1. 去掉半角括号
    prev = ""
    while prev != h:
        prev = h
        h = re.sub(r"\([^)]*\)", "", h)
    # 2. 去掉全角括号
    prev = ""
    while prev != h:
        prev = h
        h = re.sub(r"（[^）]*）", "", h)

    # 3. 提取药名：先试白名单（最长匹配）
    matched_name = None
    for name in sorted(HERB_WHITELIST, key=len, reverse=True):
        if h.startswith(name):
            matched_name = name
            break

    if matched_name:
        h = matched_name
    else:
        # 找到剂量开始的位置：第一个阿拉伯数字、中文字符(一二三四五六七八九十)、或「半」
        # 注意：百千万不作为单独数字字符匹配，只在多位数中出现
        m = re.search(r"[\d一二三四五六七八九十半]", h)
        if m and m.start() > 0:
            # 剂量在中间，药名在前面
            h = h[:m.start()]
        elif m and m.start() == 0:
            # 整个字符串以数字开头，没有药名
            return None

    # 4. 去掉描述性/炮制文字
    h = re.sub(r"(大者|炮|生用|去皮破八片|去皮|熬黄|绵裹)", "", h)
    # 5. 去掉药材名末尾的「各」「等」
    h = re.sub(r"[各等]+$", "", h)
    h = h.strip()

    skip = ["", "炙", "生", "炮", "熬", "去皮", "破八片", "生用", "熬黄", "绵裹"]
    if not h or h in skip or len(h) > 4:
        return None
    return h

# ── 按行扫描，提取所有 modal-overlay 块 ──────────────────
blocks = []
i = 0
while i < len(lines):
    line = lines[i]
    if 'class="modal-overlay"' in line and 'id="modal-' in line:
        m_id = re.search(r'id="modal-([^"]+)"', line)
        if not m_id:
            i += 1
            continue
        modal_id = m_id.group(1)
        buf = [line]
        level = line.count("<div") - line.count("</div>")
        i += 1
        while i < len(lines) and level > 0:
            buf.append(lines[i])
            level += lines[i].count("<div") - lines[i].count("</div>")
            i += 1
        block_content = "".join(buf)
        blocks.append((modal_id, block_content))
    else:
        i += 1

print(f"找到 {len(blocks)} 个 modal-overlay 块")

# ── 从每个块中提取方剂名和组成 ────────────────────────────
results = []
for modal_id, block in blocks:
    m_name = re.search(r"<h2>(.*?)</h2>", block)
    if not m_name:
        continue
    fname = m_name.group(1).strip()
    if not fname:
        continue

    m_comp = re.search(r"<h4>组成</h4>\s*<p>([\s\S]*?)</p>", block)
    if not m_comp:
        continue
    comp_str = m_comp.group(1).strip()
    if not comp_str or comp_str.startswith("暂"):
        continue

    # 先整体去括号，再分割
    comp_str_clean = re.sub(r"\([^)]*\)", "", comp_str)
    comp_str_clean = re.sub(r"（[^）]*）", "", comp_str_clean)
    comp_str_clean = re.sub(r"各等分?", "", comp_str_clean)
    comp_str_clean = re.sub(r"等分", "", comp_str_clean)

    raw_herbs = re.split(r"[、，,]", comp_str_clean)

    herbs = []
    seen = set()
    for rh in raw_herbs:
        rh = rh.strip()
        if not rh:
            continue
        cleaned = clean_herb(rh)
        if cleaned and cleaned not in seen:
            seen.add(cleaned)
            herbs.append(cleaned)

    if herbs:
        results.append({"name": fname, "herbs": herbs})

# ── 去重（按方剂名）────────────────────────────────────────
seen_names = set()
unique_results = []
for r in results:
    if r["name"] not in seen_names:
        seen_names.add(r["name"])
        unique_results.append(r)

unique_results.sort(key=lambda x: x["name"])

with open(OUT_JS, "w", encoding="utf-8") as f:
    f.write("// 446辨证体系 - 72首核心方剂组成数据\n")
    f.write("// 自动生成，请勿手动编辑\n\n")
    f.write("const FORMULA_HERBS = ")
    f.write(json.dumps(unique_results, ensure_ascii=False, indent=2))
    f.write(";\n")

print(f"已生成 {len(unique_results)} 首方剂 -> {OUT_JS}")
print(f"去重药材数：{len(set(h for r in unique_results for h in r['herbs']))}")
