#!/usr/bin/env python

from glob import glob
import os
import jinja2
from pathlib import Path

# All the posts, in reverse chronological order
posts = sorted(glob('posts/*'), reverse=True)
posts = [os.path.basename(p) for p in posts]
posts = [os.path.splitext(p)[0] for p in posts]

redirect_template = jinja2.Template("""<!DOCTYPE HTML>
<html lang="en-US">
    <head>
        <meta charset="UTF-8">
        <meta http-equiv="refresh" content="0; url={{target}}">
        <script type="text/javascript">
            window.location.href = "{{target}}"
        </script>
        <title>Page Redirection</title>
    </head>
    <body>
        If you are not redirected automatically <a href='{{target}}'>please see here</a>.
    </body>
</html>
""")

outdir = Path('_build/html')

for p in posts:
    oldpath = outdir / (p.replace('-','/',3) + '.html')
    print(oldpath)
    oldpath.parent.mkdir(parents=True, exist_ok=True)
    with open(oldpath, 'w') as f:
        f.write(redirect_template.render(target='../../../posts/' + p + '.html'))
    
