#!/usr/bin/env python3
"""Exodus Book Blog - Autonomous content generator"""

import datetime

POSTS = [
    {
        "title": "What Would You Do If Society Collapsed Tomorrow?",
        "slug": "society-collapse",
        "excerpt": "The world of Exodus explores exactly this question. Here's what the books get right about human nature when everything falls apart.",
        "link": "https://exodus.orsontbadger.com"
    },
    {
        "title": "The Real Cost of Starting Over After Everything Is Gone",
        "slug": "starting-over",
        "excerpt": "Most post-apocalyptic stories skip the hard part. Exodus doesn't. The emotional and practical price of rebuilding is the core of the series.",
        "link": "https://exodus.orsontbadger.com"
    },
]

def generate_index():
    html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Exodus — Thoughts from the Wasteland</title>
    <style>
        body { font-family: system-ui, sans-serif; max-width: 720px; margin: 60px auto; padding: 20px; line-height: 1.7; }
        h1 { font-size: 2.2rem; }
        .post { margin-bottom: 48px; }
        .title { font-size: 1.45rem; margin-bottom: 8px; }
        .excerpt { color: #444; }
        .cta { display: inline-block; margin-top: 12px; padding: 10px 18px; background: #111; color: white; text-decoration: none; border-radius: 6px; }
    </style>
</head>
<body>
    <h1>Exodus — Thoughts from the Wasteland</h1>
    <p>Stories and ideas from the world of the Exodus series by Orson T. Badger.</p>
"""

    for post in POSTS:
        html += f"""
    <div class="post">
        <div class="title">{post['title']}</div>
        <div class="excerpt">{post['excerpt']}</div>
        <a href="{post['link']}" class="cta">Read the books →</a>
    </div>
"""

    html += """
</body>
</html>"""

    with open("index.html", "w") as f:
        f.write(html)
    print("Generated index.html")

if __name__ == "__main__":
    generate_index()
