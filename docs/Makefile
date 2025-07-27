# Makefile for Sphinx documentation

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD  ?= sphinx-build
SOURCEDIR    = .
BUILDDIR     = _build

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile clean examples

# Generate examples before building
examples:
	@echo "Generating examples..."
	@python generate_examples.py

# Clean build directory
clean:
	@echo "Cleaning build directory..."
	@rm -rf $(BUILDDIR)/*
	@rm -rf examples/*.md
	@echo "Clean completed."

# Build HTML with examples
html: examples
	@echo "Building HTML documentation..."
	@$(SPHINXBUILD) -b html "$(SOURCEDIR)" "$(BUILDDIR)/html" $(SPHINXOPTS) $(O)
	@echo "HTML documentation generated in $(BUILDDIR)/html/"

# Build HTML and open in browser
serve: html
	@echo "Opening documentation in browser..."
	@python -m webbrowser file://$(PWD)/$(BUILDDIR)/html/index.html

# Live reload development server
livehtml:
	@echo "Starting live reload server..."
	@sphinx-autobuild "$(SOURCEDIR)" "$(BUILDDIR)/html" --open-browser --watch ../jsonschema_diff --ignore "**/.*"

# Build PDF (requires LaTeX)
pdf: examples
	@echo "Building PDF documentation..."
	@$(SPHINXBUILD) -b latex "$(SOURCEDIR)" "$(BUILDDIR)/latex" $(SPHINXOPTS) $(O)
	@$(MAKE) -C "$(BUILDDIR)/latex" all-pdf
	@echo "PDF documentation generated in $(BUILDDIR)/latex/"

# Build ePub
epub: examples
	@echo "Building ePub documentation..."
	@$(SPHINXBUILD) -b epub "$(SOURCEDIR)" "$(BUILDDIR)/epub" $(SPHINXOPTS) $(O)
	@echo "ePub documentation generated in $(BUILDDIR)/epub/"

# Check links
linkcheck:
	@echo "Checking links..."
	@$(SPHINXBUILD) -b linkcheck "$(SOURCEDIR)" "$(BUILDDIR)/linkcheck" $(SPHINXOPTS) $(O)

# Build all formats
all: html pdf epub
	@echo "All documentation formats built."

# Development build (fast, no examples regeneration)
dev:
	@echo "Building documentation (development mode)..."
	@$(SPHINXBUILD) -b html "$(SOURCEDIR)" "$(BUILDDIR)/html" $(SPHINXOPTS) $(O)

# Full rebuild
rebuild: clean html
	@echo "Full rebuild completed."

# Check documentation coverage
coverage:
	@echo "Checking documentation coverage..."
	@$(SPHINXBUILD) -b coverage "$(SOURCEDIR)" "$(BUILDDIR)/coverage" $(SPHINXOPTS) $(O)
	@cat $(BUILDDIR)/coverage/python.txt

# Deploy to GitHub Pages (if using gh-pages branch)
deploy: html
	@echo "Deploying to GitHub Pages..."
	@git worktree add gh-pages gh-pages || true
	@rm -rf gh-pages/*
	@cp -r $(BUILDDIR)/html/* gh-pages/
	@cd gh-pages && git add . && git commit -m "Update documentation" && git push origin gh-pages
	@git worktree remove gh-pages

# Install documentation dependencies
install-deps:
	@echo "Installing documentation dependencies..."
	@pip install sphinx furo sphinx-autodoc-typehints sphinx-copybutton myst-parser sphinx-autobuild

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
