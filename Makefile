.venv:
	python -m venv .venv

install: .venv
	.venv/bin/pip install -r requirements.txt

dev: install
	.venv/bin/mkdocs serve --livereload

visualize: install
	.venv/bin/python visualize.py

inject: install
	.venv/bin/python -c "
from visualize import inject_og_tags
with open('docs/$(FILE)', 'r') as f: html = f.read()
html = inject_og_tags(html, title='$(FILE)', url='https://caldwell.pages.dev/$(FILE)')
with open('docs/$(FILE)', 'w') as f: f.write(html)
print('Injected OG tags into docs/$(FILE)')
"
