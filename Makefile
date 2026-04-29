.venv:
	python -m venv .venv

install: .venv
	.venv/bin/pip install -r requirements.txt

dev: install
	.venv/bin/mkdocs serve --livereload

visualize: install
	.venv/bin/python visualize.py
