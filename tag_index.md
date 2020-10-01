<div class="home">
    {% for tag in site.tags %}
    <h2 id="{{tag[0]}}">{{tag[0]}}</h2>
    <ul class="post-list">
    {%- for post in tag[1] -%}
        <li style="padding-bottom: 30px;">
            <h3><a class="post-link" href="{{ post.url | relative_url }}">
                {{ post.title | escape }}
            </a></h3>

            {{ post.excerpt }}
        </li>
    {%- endfor -%}
    </ul>
    {% endfor %}
</div>
