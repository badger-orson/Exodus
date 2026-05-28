#!/usr/bin/env python3
"""Exodus Blog - High-quality SEO/GEO/AEO content generator"""

import datetime

def generate_site():
    date = datetime.date.today().strftime("%B %d, %Y")
    
    posts = [
        {
            "title": "What Actually Happens When Civilization Collapses",
            "slug": "civilization-collapse",
            "content": """Most post-apocalyptic stories focus on the action. The Exodus series focuses on what comes after — the slow, grinding reality of rebuilding when every system you relied on is gone.

This is the part most people get wrong. It's not just about guns and supplies. It's about trust, leadership, and the brutal math of who gets to survive when resources are finite.

The books explore these questions without easy answers.""",
            "cta": "See how the story unfolds in the Exodus series"
        },
        {
            "title": "The Hidden Cost of Starting Over",
            "slug": "hidden-cost",
            "content": """Starting over after everything is destroyed isn't romantic. It's exhausting. The Exodus books don't skip the psychological toll — the grief, the moral compromises, and the constant calculation of who you can still trust.

This is the part that makes the series feel real.""",
            "cta": "Read the Exodus series"
        }
    ]
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Exodus — Field Notes from the Edge</title>
    <style>
        body {{ font-family: system-ui, -apple-system, sans-serif; max-width: 720px; margin: 60px auto; padding: 20px; line-height: 1.75; color: #222; }}
        h1 {{ font-size: 2.1rem; margin-bottom: 8px; }}
        .meta {{ color: #666; margin-bottom: 48px; }}
        .post {{ margin-bottom: 72px; }}
        .post h2 {{ font-size: 1.55rem; margin-bottom: 16px; line-height: 1.3; }}
        .post p {{ margin-bottom: 18px; }}
        .cta {{ display: inline-block; margin-top: 20px; padding: 12px 24px; background: #111; color: white; text-decoration: none; border-radius: 6px; font-weight: 600; }}
        .footer {{ margin-top: 80px; font-size: 0.9rem; color: #777; }}
    </style>
</head>
<body>
    <h1>Exodus — Field Notes from the Edge</h1>
    <p class="meta">Thoughtful writing on collapse, survival, and what comes after. Updated {date}.</p>
"""
    
    for post in posts:
        html += f"""
    <div class="post">
        <h2>{post['title']}</h2>
        {post['content'].replace(chr(10), '<p>')}
        <a href="https://exodus.orsontbadger.com" class="cta">{post['cta']} →</a>
    </div>
"""
    
    html += """
    <div class="footer">
        This site exists to explore the questions at the heart of the Exodus series.
    </div>
</body>
</html>"""
    
    with open("index.html", "w") as f:
        f.write(html)
    print("Generated high-quality index.html")

if __name__ == "__main__":
    generate_site()
