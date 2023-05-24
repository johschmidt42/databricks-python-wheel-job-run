# A Makefile is a collection of rules. Each rule is a recipe to do a specific
# thing, sort of like a grunt task or an npm package.json script.
#
# To do stuff with make, you type `make` in a directory that has a file called
# "Makefile". You can also type `make -f <makefile>` to use a different filename.
#
# A rule looks like this:
#
# <target>: <prerequisites...>
# 	<commands>
#
# The "target" is required. The prerequisites are optional, and the commands
# are also optional, but you have to have one or the other.
#
# Type `make` to show the available targets and a description of each.
#
.DEFAULT_GOAL := help
.PHONY: help
help:  ## Display this help
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Formatting

.PHONY: format-black
format-black: ## black (code formatter)
	@black .

.PHONY: format-isort
format-isort: ## isort (import formatter)
	@isort .

.PHONY: format
format: format-black format-isort ## run all formatters

##@ Linting

.PHONY: lint-black
lint-black: ## black in linting mode
	@black . --check

.PHONY: lint-isort
lint-isort: ## isort in linting mode
	@isort . --check

.PHONY: lint-flake8
lint-flake8: ## flake8 (linter)
	@flake8 .

lint: lint-black lint-isort lint-flake8 ## run all linters

##@ Build

build: ## build a wheel
	@poetry build --format wheel

##@ Docker

container_name = {container_name} # e.g. databricks-wheel-scripts:latest
acr_name = {acr_name} # e.g. databricksjobrunacr

docker-build: ## docker build image
	@docker build --file Dockerfile --tag $(container_name) --target production .

docker-run-bash: ## docker run container with bash
	@docker run -it --rm $(container_name) /bin/bash

acr-login: ## login to acr
	@az login
	@az acr login --name $(acr_name)

docker-tag: ## tag docker image to {acr}.azurecr.io/{image}
	@docker tag $(container_name) $(acr_name).azurecr.io/$(container_name)

docker-push: docker-tag ## docker push to container registry (acr)
	@docker push $(acr_name).azurecr.io/$(container_name)

##@ Clean-up

clean-cov: ## remove output files from pytest & coverage
	@rm -rf dist

clean: clean-cov ## run all clean commands
	@find . -name '__pycache__' -exec rm -fr {} +
