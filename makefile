PYTHON=python3
JUPYTER_BOOK=jupyter-book

default: all

contents:
	$(PYTHON) generate_toc.py

all: contents
	$(PYTHON) ./generate_toc.py
	$(JUPYTER_BOOK) build .

clean :
	rm -rf _build contents
