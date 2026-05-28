#!/usr/bin/env python3
"""Exodus Blog - Full article blog with dark theme"""

import os
import datetime

ARTICLES = [
    {
        "slug": "what-happens-when-civilization-collapses",
        "title": "What Actually Happens When Civilization Collapses",
        "excerpt": "Most post-apocalyptic fiction gets the fall right and the aftermath wrong. The Exodus series gets both right.",
        "content": """<p>When most people imagine the end of the world, they picture dramatic scenes — burning cities, desperate crowds, sudden violence. The Exodus series starts after all of that has already happened.</p>

<p>The real story begins in the quiet that follows. The moment when the last generator runs out of fuel. When the last can of food is opened. When people realize that no one is coming to save them.</p>

<p>This is where the series separates itself from most post-apocalyptic stories. It doesn't romanticize the collapse. It shows the slow, grinding reality of what comes next — the moral compromises, the new social structures that form, and the psychological cost of living in a world that no longer has rules.</p>

<p>Other stories focus on the strong surviving. Exodus focuses on what "strong" actually means when everything that defined strength has been stripped away.</p>""",
        "image": "https://picsum.photos/id/1018/1200/630"
    },
    {
        "slug": "the-hidden-cost-of-starting-over",
        "title": "The Hidden Cost of Starting Over",
        "excerpt": "Rebuilding isn't the heroic fresh start most stories pretend it is. The Exodus books show the real price.",
        "content": """<p>Starting over after everything is gone sounds romantic in theory. In practice, it's one of the most psychologically destructive things a person can experience.</p>

<p>The Exodus series doesn't skip this part. It shows the grief that never fully leaves. The constant calculation of who you can still trust. The slow realization that some people will never recover from what they've lost — and what they've had to do to survive.</p>

<p>Compare this to most post-apocalyptic fiction, which treats rebuilding as an exciting new chapter. Exodus treats it as the hard, unglamorous work it actually is. This is why the series resonates so deeply with readers who have lived through real loss.</p>""",
        "image": "https://picsum.photos/id/1005/1200/630"
    }
]

def generate_article(article):
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{article['title']} • Exodus</title>
    <style>
        body {{ font-family: system-ui, sans-serif; background: #0a0a0a; color: #ededed; max-width: 720px; margin: 0 auto; padding: 60px 24px; line-height: 1.8; }}
        h1 {{ font-size: 2.4rem; line-height: 1.2; margin-bottom: 24px; }}
        img {{ width: 100%; border-radius: 12px; margin: 32px 0; }}
        .meta {{ color: #666; margin-bottom: 40px; }}
        .content p {{ margin-bottom: 20px; font-size: 1.1rem; }}
        .cta {{ display: block; margin: 60px auto 0; text-align: center; background: white; color: black; padding: 16px 32px; border-radius: 999px; text-decoration: none; font-weight: 600; width: fit-content; }}
    </style>
</head>
<body>
    <h1>{article['title']}</h1>
    <p class="meta">Exodus Field Notes • {datetime.date.today().strftime("%B %d, %Y")}</p>
    
    <img src="{article['image']}" alt="">
    
    <div class="content">
        {article['content']}
    </div>
    
    <a href="https://exodus.orsontbadger.com" class="cta">Read the Exodus series →</a>
</body>
</html>"""
    
    with open(f"articles/{article['slug']}.html", "w") as f:
        f.write(html)
    print(f"Generated article: {article['slug']}")

def generate_homepage():
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Exodus • Field Notes</title>
    <style>
        body {{ font-family: system-ui, sans-serif; background: #0a0a0a; color: #ededed; margin: 0; padding: 0; }}
        .header {{ max-width: 1100px; margin: 0 auto; padding: 60px 24px 40px; text-align: center; }}
        h1 {{ font-size: 3rem; margin: 0 0 16px; }}
        .tagline {{ color: #888; font-size: 1.2rem; }}
        .section {{ max-width: 1100px; margin: 60px auto; padding: 0 24px; }}
        .post-card {{ background: #111; border: 1px solid #222; border-radius: 16px; padding: 32px; margin-bottom: 24px; }}
        .post-card h2 {{ margin: 0 0 12px; font-size: 1.5rem; }}
        .post-card p {{ color: #aaa; }}
        .read-more {{ color: #fff; text-decoration: none; font-weight: 600; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Exodus</h1>
        <p class="tagline">Field notes from the edge of collapse</p>
    </div>
    
    <div class="section">
"""
    
    for article in ARTICLES:
        html += f"""
        <div class="post-card">
            <h2>{article['title']}</h2>
            <p>{article['excerpt']}</p>
            <a href="articles/{article['slug']}.html" class="read-more">Read full article →</a>
        </div>
"""
    
    html += """
    </div>
</body>
</html>"""
    
    with open("index.html", "w") as f:
        f.write(html)
    print("Generated homepage")

if __name__ == "__main__":
    for article in ARTICLES:
        generate_article(article)
    generate_homepage()
    print("Blog generated successfully")