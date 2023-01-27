PYTHON=python3
JUPYTER_BOOK=jupyter-book

default: all

contents/contents.rst: posts/*
	$(PYTHON) generate_toc.py

all: contents/contents.rst
	$(JUPYTER_BOOK) build .

clean :
	rm -rf _build contents
