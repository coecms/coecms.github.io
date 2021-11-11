#!/usr/bin/env python

from glob import glob
import yaml
import jinja2
import os

# All the posts, in reverse chronological order
posts = sorted(glob('posts/*'), reverse=True)
posts = [os.path.basename(p) for p in posts]
posts = [os.path.splitext(p)[0] for p in posts]

# Grouped by year
posts_by_year = {}
for p in posts:
    year = p[:4]

    if year not in posts_by_year:
        posts_by_year[year] = []

    posts_by_year[year].append(p)


# Get the tags from meta.yaml
with open('post_meta.yaml') as f:
    meta = yaml.safe_load(f)

# Grouped by tags
posts_by_tag = {}
for p, m in meta.items():
    if p in posts and 'tags' in m:
        for t in m['tags']:
            if t not in posts_by_tag:
                posts_by_tag[t] = []

            posts_by_tag[t].append(p)

if not os.path.exists('contents'):
    os.mkdir('contents')

subtree_template = jinja2.Template("""
{{title}}
--------------------------------------------------------------------------------

.. toctree::
    :caption: {{title}}
    :maxdepth: 1

    {% for p in posts -%}
    /posts/{{p}}
    {% endfor %}
""")

for y, ps in posts_by_year.items():
    with open(f'contents/year-{y}.rst', 'w') as f:
        f.write(subtree_template.render(title=y, posts=ps))

for t, ps in posts_by_tag.items():
    with open(f'contents/tag-{t}.rst', 'w') as f:
        f.write(subtree_template.render(title=t, posts=ps))


contents_template = jinja2.Template("""
.. toctree::
    :caption: Latest
    :maxdepth: 1

    {% for p in posts[:5] -%}
    /posts/{{p}}
    {% endfor %}

.. toctree::
    :caption: Tags
    :maxdepth: 2

    {% for t in tags -%}
    /contents/tag-{{t}}
    {% endfor %}

.. toctree::
    :caption: Archive
    :maxdepth: 2
    :hidden:

    {% for y in years -%}
    /contents/year-{{y}}
    {% endfor %}
""")

with open('contents/contents.rst', 'w') as f:
    f.write(contents_template.render(posts=posts, tags=sorted(posts_by_tag.keys()), years=sorted(posts_by_year.keys(), reverse=True)))
