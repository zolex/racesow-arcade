.PHONY: build help
.DEFAULT_GOAL:=help

venv: ## create venv
	rm -rf .venv
	python -m venv .venv
	.venv/bin/pip install -r requirements.txt

build: clean ## Build to folder
	pyinstaller RacesowArcade.spec

build1: clean ## Build to single file
	pyinstaller RacesowArcadeOneFile.spec

clean:
	rm -rf ./build

help: ## Display this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
