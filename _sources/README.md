CMS Blog
========

The blog is viewable here:

http://coecms.github.io

See the jupyter-book docs for info on creating posts - https://jupyterbook.org/intro.html


[Creating special blocks (notes, warnings etc.)](https://jupyterbook.org/content/content-blocks.html#notes-warnings-and-other-admonitions)

Link to external documentation with "{func}`xarray.open_dataset`"

---
To create a new blog post:

1. `clone` the repo
1. Create new `branch`
1. Create a new page under the `posts` directory, named `YY-MM-DD-title`. Posts can be in rst, md or ipynb format
1. Add any tags to the file `posts_meta.yaml`
1. `commit` changes and `push` branch back to `coecms/coecms.github.io`
1. Open Pull Request and select CMS team member to review
1. After review squash and merge PR
1. Delete `branch`

---
The new blog post should appear within a few minutes at http://coecms.github.io 

If it doesn't, check under "Github Pages" here for error messages:

https://github.com/coecms/coecms.github.io/settings

---

To build the site locally, run
```
./generate_toc.py
jupyter-book build .
```

`generate_toc.py` sets up all of the tables of contents for latest posts, tags and archive based off of the filenames in `posts` and the tags listed in `posts_meta.yaml`.

NB rendering errors won't stop the book to be built and deployed, so check the logs under actions to make sure everything is rendered properly
