# -*- coding: utf-8 -*-
"""生成 GitHub 活动概览卡（十字分析表风格）SVG。
用法: python cross_stats.py <username> [输出路径]
依赖: 仅标准库（urllib）
"""
import sys
import json
import urllib.request

USER = sys.argv[1] if len(sys.argv) > 1 else "Noah-Deleveq"
OUT = sys.argv[2] if len(sys.argv) > 2 else "cross-stats.svg"


def api(url):
    req = urllib.request.Request(url, headers={"User-Agent": "cross-stats", "Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read().decode("utf-8"))


def main():
    events = api(f"https://api.github.com/users/{USER}/events/public?per_page=100")
    type_map = {
        "PushEvent": "Commits",
        "PullRequestReviewEvent": "Code review",
        "IssuesEvent": "Issues",
        "PullRequestEvent": "Pull requests",
    }
    counts = {v: 0 for v in type_map.values()}
    repos = set()
    for ev in events:
        t = type_map.get(ev.get("type", ""))
        if t:
            counts[t] += 1
        repo = ev.get("repo", {}).get("name", "")
        if repo:
            repos.add(repo)
    total = sum(counts.values()) or 1
    top_repos = sorted(repos)[:5]
    other = max(0, len(repos) - len(top_repos))

    W, H = 480, 208
    colors = {
        "Commits": "#3fb950",
        "Code review": "#d29922",
        "Issues": "#a371f7",
        "Pull requests": "#58a6ff",
    }
    rows = []
    x0, y0 = 24, 86
    bar_w = 300
    for i, (label, n) in enumerate(counts.items()):
        y = y0 + i * 26
        pct = n / total * 100
        c = colors[label]
        rows.append(f'<text x="{x0}" y="{y}" font-size="11" fill="#57606a" font-family="Arial">{label}</text>')
        rows.append(f'<text x="{x0 + bar_w + 8}" y="{y}" font-size="11" fill="#24292f" font-family="Arial">{pct:.0f}%</text>')
        rows.append(f'<rect x="{x0}" y="{y + 4}" width="{bar_w}" height="6" rx="3" fill="#eaeef2"/>')
        rows.append(f'<rect x="{x0}" y="{y + 4}" width="{bar_w * pct / 100:.1f}" height="6" rx="3" fill="{c}"/>')

    repo_text = "为 %d 个仓库做出贡献" % len(repos)
    if top_repos:
        repo_text += "：" + "、".join(r.split("/")[1] for r in top_repos)
        if other:
            repo_text += f" 等 {other} 个"

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <rect width="{W}" height="{H}" rx="10" fill="#ffffff" stroke="#d0d7de"/>
  <text x="24" y="34" font-size="15" font-weight="bold" fill="#24292f" font-family="Arial">活动概览</text>
  <text x="24" y="56" font-size="11" fill="#57606a" font-family="Arial">{repo_text}</text>
  <line x1="24" y1="70" x2="{W - 24}" y2="70" stroke="#eaeef2"/>
{chr(10).join(rows)}
  <text x="24" y="{H - 14}" font-size="10" fill="#8b949e" font-family="Arial">自动生成 · GitHub Actions</text>
</svg>'''
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"OK: {OUT} (活动 {total} 次 / 仓库 {len(repos)} 个)")


if __name__ == "__main__":
    main()
