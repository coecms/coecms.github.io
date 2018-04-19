---
# You don't need to edit this file, it's empty on purpose.
# Edit theme's home layout instead if you wanna make some changes
# See: https://jekyllrb.com/docs/themes/#overriding-theme-defaults
layout: default
---

<div class="home">
    <ul class="post-list">
    {%- for post in site.posts -%}
        <li>
            <h3><a class="post-link" href="{{ post.url | relative_url }}">
                {{ post.title | escape }}
            </a></h3>

            {{ post.excerpt }}
        </li>
    {%- endfor -%}
    </ul>
</div>
