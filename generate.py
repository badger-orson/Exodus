#!/usr/bin/env python3
"""Exodus Blog - Full essays + strong dark visual theme"""

import datetime
import os

ARTICLES = [
    {
        "slug": "civilization-collapse-reality",
        "title": "What Civilization Collapse Actually Looks Like",
        "excerpt": "Most stories get the dramatic fall. Few understand the long, quiet aftermath that follows.",
        "content": """When people imagine the end of the world, they usually picture sudden violence and burning cities. The reality is slower and far more difficult. The Exodus series begins after the dramatic part is already over. What remains is the long, grinding work of trying to remember how to live when every system that once supported life has disappeared.

The books focus on the months and years after the collapse, not the collapse itself. This is the part most stories skip because it is not exciting. It is the part where people realize that the old rules no longer apply and new ones must be created from nothing. Trust becomes the most valuable resource, and it is earned only through consistent action over time.

What makes the series stand out is how honestly it shows the psychological cost. People do not simply adapt and move on. They carry their losses into every decision. Some never recover. The books refuse to offer easy redemption or heroic transformation. They show the slow, uneven process of rebuilding when hope is in short supply.""",
        "image": "https://picsum.photos/id/1018/1200/630"
    },
    {
        "slug": "trust-after-collapse",
        "title": "Trust After Everything Falls Apart",
        "excerpt": "When institutions disappear, trust must be rebuilt from zero every single day.",
        "content": """In stable societies, trust is something we rarely think about. We trust that food will be available, that contracts will be honored, and that strangers will generally follow basic social rules. After collapse, none of these assumptions hold. Every interaction becomes a calculation of risk.

The Exodus series examines this shift with unusual clarity. Characters must decide who is worth risking everything for, often with very little information. Small betrayals carry enormous consequences. The books show how communities form around shared necessity rather than shared values, and how fragile those bonds remain.

This is one of the most realistic elements of the series. Trust is not a feeling. It is a repeated pattern of behavior that must be proven again and again. The stories explore what happens when that pattern breaks and how difficult it is to repair.""",
        "image": "https://picsum.photos/id/1005/1200/630"
    }
]

def generate_article(article):
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{article['title']} - Exodus</title>
    <style>
        body {{ font-family: system-ui, sans-serif; background: #0a0a0a; color: #ededed; max-width: 720px; margin: 0 auto; padding: 60px 24px; line-height: 1.85; }}
        h1 {{ font-size: 2.4rem; line-height: 1.2; margin-bottom: 24px; }}
        .meta {{ color: #666; margin-bottom: 32px; }}
        img {{ width: 100%; border-radius: 12px; margin: 32px 0; }}
        .content p {{ margin-bottom: 22px; font-size: 1.08rem; }}
        .cta {{ display: block; margin: 60px auto 0; text-align: center; background: white; color: black; padding: 16px 32px; border-radius: 999px; text-decoration: none; font-weight: 600; width: fit-content; }}
    </style>
</head>
<body>
    <h1>{article['title']}</h1>
    <p class="meta">Exodus Field Notes - {datetime.date.today().strftime("%B %d, %Y")}</p>
    <img src="{article['image']}" alt="">
    <div class="content">
        {article['content']}
    </div>
    <a href="https://exodus.orsontbadger.com" class="cta">Read the Exodus series</a>
</body>
</html>"""
    with open(f"articles/{article['slug']}.html", "w") as f:
        f.write(html)

def generate_homepage():
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Exodus - Field Notes</title>
    <style>
        body {{ font-family: system-ui, sans-serif; background: #0a0a0a; color: #ededed; margin: 0; padding: 0; }}
        .header {{ max-width: 1100px; margin: 0 auto; padding: 60px 24px 40px; text-align: center; }}
        h1 {{ font-size: 3rem; margin: 0 0 16px; }}
        .tagline {{ color: #888; font-size: 1.2rem; }}
        .section {{ max-width: 1100px; margin: 40px auto; padding: 0 24px; }}
        .post-card {{ background: #111; border: 1px solid #222; border-radius: 16px; padding: 32px; margin-bottom: 24px; }}
        .post-card h2 {{ margin: 0 0 12px; font-size: 1.45rem; }}
        .post-card p {{ color: #aaa; }}
        .read-more {{ color: #fff; text-decoration: none; font-weight: 600; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Exodus</h1>
        <p class="tagline">Field notes from the edge of collapse</p>
    </div>
    <div class="section">"""
    
    for article in ARTICLES:
        html += f"""
        <div class="post-card">
            <h2>{article['title']}</h2>
            <p>{article['excerpt']}</p>
            <a href="articles/{article['slug']}.html" class="read-more">Read full article</a>
        </div>"""
    
    html += """
    </div>
</body>
</html>"""
    with open("index.html", "w") as f:
        f.write(html)

if __name__ == "__main__":
    os.makedirs("articles", exist_ok=True)
    for article in ARTICLES:
        generate_article(article)
    generate_homepage()
    print(f"Generated {len(ARTICLES)} full essays with dark theme")