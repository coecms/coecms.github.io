NOTEBOOKS := $(shell find notebooks -type f -name \*.ipynb -not -path \*/.ipynb_checkpoints/\*)
NB_POSTS   = $(patsubst notebooks/%.ipynb,_posts/%.md,${NOTEBOOKS})
NB_RENDERS = $(patsubst notebooks/%.ipynb,_includes/notebooks/%.html,${NOTEBOOKS})

all: ${NB_POSTS} ${NB_RENDERS}

_includes/notebooks/%.html: notebooks/%.ipynb
	jupyter nbconvert $< --output-dir $(dir $@) --output $(notdir $@) --template classic --to html

_posts/%.md:
	>  $@ echo "---"
	>> $@ echo "title: $(notdir $@)"
	>> $@ echo "layout: notebook"
	>> $@ echo "notebook: $*.html"
	>> $@ echo "excerpt: >-"
	>> $@ echo "    TODO: Add excerpt"
	>> $@ echo "tags: TODO: Add tags"
	>> $@ echo "---"

.PRECIOUS: _includes/notebooks/%.html
