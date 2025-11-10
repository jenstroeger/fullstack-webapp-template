
# Use bash as the shell when executing a rule's recipe. For more details:
# https://www.gnu.org/software/make/manual/html_node/Choosing-the-Shell.html
SHELL := bash


.PHONY: all all-frontend all-backend
all: all-frontend all-backend
all-frontend:
	$(MAKE) --directory frontend all
all-backend:
	$(MAKE) --directory backend all


.PHONY: init init-frontend init-backend
init: init-frontend init-backend
init-frontend:
	$(MAKE) --directory frontend init
init-backend:
	$(MAKE) --directory backend init


.PHONY: setup setup-frontend setup-backend
setup: setup-frontend setup-backend
	pre-commit install
setup-frontend:
	$(MAKE) --directory frontend setup
setup-backend:
	$(MAKE) --directory backend setup


.PHONY: check check-frontend check-backend
check: check-frontend check-backend
check-frontend:
	$(MAKE) --directory frontend check
check-backend:
	$(MAKE) --directory backend check


.PHONY: test test-frontend test-backend
test: test-frontend test-backend
test-frontend:
	$(MAKE) --directory frontend test
test-backend:
	$(MAKE) --directory backend test


.PHONY: build build-frontend build-backend build-docker build-docker-frontend build-docker-backend
build: build-frontend build-backend build-docker
build-docker: build-docker-frontend build-docker-backend
build-frontend:
	$(MAKE) --directory frontend build
build-docker-frontend:
	$(MAKE) --directory frontend build-docker
build-backend:
	$(MAKE) --directory backend build
build-docker-backend:
	$(MAKE) --directory backend build-docker


.PHONY: docs docs-frontend docs-backend
docs: docs-frontend docs-backend
docs-frontend:
	$(MAKE) --directory frontend docs
docs-backend:
	$(MAKE) --directory frontend docs


.PHONY: compose-up compose-down compose-up-develop compose-down-develop
compose-up:
	docker compose --file infra/docker-compose.yaml up
compose-down:
	docker compose --file infra/docker-compose.yaml down
compose-up-develop:
	docker compose --file infra/docker-compose-develop.yaml up
compose-down-develop:
	docker compose --file infra/docker-compose-develop.yaml down


.PHONY: clean clean-frontend clean-backend
clean: clean-frontend clean-backend
	rm -fr .coverage .mypy_cache/  # These backend/ files are created at the base of the repo.
clean-frontend:
	$(MAKE) --directory frontend clean
clean-backend:
	$(MAKE) --directory backend clean


.PHONY: nuke nuke-git-hooks nuke-frontend nuke-backend nuke-caches nuke-caches-frontend nuke-caches-backend
nuke: clean nuke-git-hooks nuke-caches nuke-frontend nuke-backend
nuke-caches: nuke-caches-frontend nuke-caches-backend
nuke-git-hooks:
	find .git/hooks/ -type f ! -name '*.sample' -delete
nuke-caches-frontend:
	$(MAKE) --directory frontend nuke-caches
nuke-frontend:
	$(MAKE) --directory frontend nuke
nuke-caches-backend:
	$(MAKE) --directory backend nuke-caches
nuke-backend:
	$(MAKE) --directory backend nuke
