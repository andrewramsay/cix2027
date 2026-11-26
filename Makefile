# Common tasks. `make check` runs the same steps as CI.

.PHONY: check validate images build serve install

install:
	pip install -r requirements.txt
	bundle install

validate:
	python3 scripts/validate.py

images: validate
	python3 scripts/process_images.py

build: images
	bundle exec jekyll build

check: build

# Local preview at http://localhost:4000 (re-run `make images` after changing photos or committee.yml).
# To view it from another machine, pick the address to listen on, e.g. `make serve HOST=0.0.0.0`.
HOST ?= 127.0.0.1
serve: images
	bundle exec jekyll serve --livereload --host $(HOST)
