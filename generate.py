#!/usr/bin/env python3
"""Exodus Blog - 8 full articles per day generator"""

import datetime
import os

ARTICLES = [
    {
        "slug": "civilization-collapse-reality-vs-fiction",
        "title": "Civilization Collapse: Reality vs Fiction",
        "excerpt": "Most stories get the dramatic fall right. Few get what happens in the months and years after.",
        "content": "The moment the power goes out is rarely the end. It is the beginning of something much harder. The Exodus series shows the slow erosion of old rules and the painful birth of new ones. Other books rush to the action. These books stay with the people trying to remember who they were before everything changed."
    },
    {
        "slug": "trust-after-the-fall",
        "title": "Trust After the Fall",
        "excerpt": "When institutions disappear, trust becomes the most valuable and dangerous resource.",
        "content": "In stable societies we take trust for granted. After collapse it must be earned daily through actions, not words. The Exodus books examine how people decide who is worth risking everything for. This question sits at the center of every relationship in the story."
    },
    {
        "slug": "moral-compromise-survival",
        "title": "Moral Compromise in Survival Situations",
        "excerpt": "What would you do to keep your family alive? The books refuse easy answers.",
        "content": "Most post-apocalyptic fiction eventually gives characters a heroic choice. The Exodus series repeatedly forces characters into situations where every option is bad. This is closer to real human history than most readers want to admit."
    },
    {
        "slug": "leadership-without-authority",
        "title": "Leadership Without Authority",
        "excerpt": "When governments fall, who steps up and why do people follow them?",
        "content": "True leadership after collapse rarely comes from people who wanted the job. It comes from those who can solve problems when no one else can. The Exodus books track how authority forms organically and how quickly it can be lost."
    },
    {
        "slug": "grief-and-rebuilding",
        "title": "Grief and the Work of Rebuilding",
        "excerpt": "You cannot rebuild what you refuse to mourn. The series understands this.",
        "content": "Many stories treat the past as something characters simply move on from. The Exodus books show how grief shapes every decision long after the event. People carry their losses into every new community they try to build."
    },
    {
        "slug": "children-after-collapse",
        "title": "Children Born After the Collapse",
        "excerpt": "The generation that never knew the old world sees everything differently.",
        "content": "One of the most interesting elements in the Exodus series is how children who never experienced the old world view their parents choices. They have no nostalgia. They only see the world as it is now. This creates deep tension."
    },
    {
        "slug": "resource-scarcity-psychology",
        "title": "The Psychology of Resource Scarcity",
        "excerpt": "When everything is limited, human behavior changes in predictable ways.",
        "content": "The Exodus books pay close attention to how scarcity alters decision making. Small disagreements become life threatening. Generosity becomes dangerous. The series shows these shifts without judgment but with clear consequences."
    },
    {
        "slug": "hope-in-dark-times",
        "title": "Finding Hope When Hope Feels Stupid",
        "excerpt": "Hope is not optimism. It is a decision the characters keep making.",
        "content": "The Exodus series never offers cheap hope. Any light that appears is earned through difficult choices and real sacrifice. This makes the moments of connection between characters carry more weight than in most stories."
    }
]

def generate_article(article):
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{article['title']} - Exodus Field Notes</title>
    <style>
        body {{ font-family: system-ui, sans-serif; background: #0a0a0a; color: #ededed; max-width: 720px; margin: 0 auto; padding: 60px 24px; line-height: 1.8; }}
        h1 {{ font-size: 2.3rem; line-height: 1.2; margin-bottom: 24px; }}
        .meta {{ color: #666; margin-bottom: 40px; }}
        .content p {{ margin-bottom: 22px; font-size: 1.08rem; }}
        .cta {{ display: block; margin: 60px auto 0; text-align: center; background: white; color: black; padding: 16px 32px; border-radius: 999px; text-decoration: none; font-weight: 600; width: fit-content; }}
    </style>
</head>
<body>
    <h1>{article['title']}</h1>
    <p class="meta">Exodus Field Notes - {datetime.date.today().strftime("%B %d, %Y")}</p>
    <div class="content">
        {article['content']}
    </div>
    <a href="https://exodus.orsontbadger.com" class="cta">Read the Exodus series</a>
</body>
</html>"""
    with open(f"articles/{article['slug']}.html", "w") as f:
        f.write(html)

def generate_homepage():
    html = """<!DOCTYPE html>
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
    print(f"Generated {len(ARTICLES)} full articles")