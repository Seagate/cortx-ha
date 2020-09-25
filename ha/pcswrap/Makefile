.PHONY: default
default: build

.PHONY: help
help:
	@echo 'General targets:'
	@echo '  build   - build binary components (hax)'
	@echo '  test    - run tests'
	@echo '  clean   - remove build artefacts'
	@echo '  install - system-wide installation, respects DESTDIR'
	@echo
	@echo 'Code linters:'
	@echo '  check   - run `flake8` and `mypy` linters for Python code'
	@echo '  flake8  - run `flake8` for Python code'
	@echo '  mypy    - run `mypy` for Python code'

# Globals --------------------------------------------- {{{1
#

SHELL := bash

TOP_SRC_DIR := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
PY_VENV_DIR := $(TOP_SRC_DIR).py3venv
PYTHON      := python3.6
PY_VENV     := source $(PY_VENV_DIR)/bin/activate
PIP         := $(PY_VENV); pip3
SETUP_PY    := $(PY_VENV); $(PYTHON) setup.py
PY3_VERSION := 36
PY3_VERSION_MINOR := $(shell grep -o . <<<$(PY3_VERSION) | tail -n1)

# Build ----------------------------------------------- {{{1
#

.PHONY: build
build: pcswrap
	@$(MAKE) --quiet check

.PHONY: pcswrap
PCS_VERSION := $(shell cat VERSION)
PCSWRAP_WHL := dist/pcswrap-$(PCS_VERSION)-py3-none-any.whl
pcswrap: $(PCSWRAP_WHL)

PCSWRAP_SRC := $(shell find pcswrap -type f -name '*.py')
$(PCSWRAP_WHL): $(PY_VENV_DIR) $(PCSWRAP_SRC)
	@$(call _info,Building pcswrap .whl package)
	@$(SETUP_PY) bdist_wheel

$(PY_VENV_DIR): requirements.txt
	@$(call _info,Initializing virtual env in $(PY_VENV_DIR))
	@$(PYTHON) -m venv $@
	@$(call _info,Installing pip modules in virtual env)
	@$(PIP) install -r ./requirements.txt

# Install ----------------------------------------------- {{{1
#

PCSWRAP_EXE        = $(DESTDIR)/bin/pcswrap
PCSWRAP_EGG_LINK   = $(DESTDIR)/lib/python3.$(PY3_VERSION_MINOR)/site-packages/pcswrap.egg-link


.PHONY: install-pcswrap-deps
install-pcswrap-deps: requirements.txt $(PY_VENV_DIR)
	@$(call _info,Installing pcswrap dependencies)
	@$(PIP) install --ignore-installed --prefix $(DESTDIR) -r $<

.PHONY: install
install: PCSWRAP_INSTALL_CMD = $(PIP) install --ignore-installed --prefix $(DESTDIR) $(PCSWRAP_WHL:pcswrap/%=%)
install: install-pcswrap-deps $(PCSWRAP_EXE)

$(PCSWRAP_EGG_LINK) $(PCSWRAP_EXE): $(PCSWRAP_WHL)
	@$(call _info,Installing pcswrap with '$(PCSWRAP_INSTALL_CMD)')
	@$(PCSWRAP_INSTALL_CMD)

# Clean ----------------------------------------------- {{{1
#

.PHONY: clean
clean:
	@$(call _info,Cleaning pcswrap)
	@rm -rvf {build,dist,pcswrap.egg-info}
	@find ./ -name '__pycache__' | while read d; do \
	     if [[ -e $$d ]]; then \
	         $(call _log,removing $$d); \
	         rm -rf $$d; \
	     fi; \
	 done

# Linters --------------------------------------------- {{{1
#

.PHONY: check
check: flake8 mypy test

.PHONY: test
test: $(PY_VENV_DIR) $(PCSWRAP_SRC)
	@$(SETUP_PY) test

.PHONY: flake8
flake8:
	@$(call _info,Checking files with flake8)
	@$(PY_VENV); flake8 pcswrap

.PHONY: mypy
mypy:
	@$(call _info,Checking files with mypy)
	@$(PY_VENV); \
	 set -eu -o pipefail; MYPYPATH=stubs mypy $(MYPY_OPTS) pcswrap

# Functions ------------------------------------------- {{{1
#

define _info
    if [[ -t 1 ]]; then \
        CYAN=$$(tput bold; tput setaf 6); \
        NC=$$(tput sgr0); \
    fi; \
    echo "$${CYAN}--> $(1)$${NC}"
endef

define _log
    if [[ -t 1 ]]; then \
        YELLOW=$$(tput setaf 3); \
        NC=$$(tput sgr0); \
    fi; \
    echo "$${YELLOW}    $(1)$${NC}"
endef

# vim: textwidth=80 nowrap foldmethod=marker
