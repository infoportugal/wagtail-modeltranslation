.PHONY: clean-pyc clean-build help test
.DEFAULT_GOAL := help

help: ## print this help screen
	@perl -nle'print $& if m{^[a-zA-Z0-9_-]+:.*?## .*$$}' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-25s\033[0m %s\n", $$1, $$2}'

clean: clean-build clean-pyc
	@echo "all clean now .."

clean-build: ## remove build artifacts
	@rm -fr build/
	@rm -fr dist/
	@rm -fr htmlcov/
	@rm -fr *.egg-info
	@rm -rf .coverage

clean-pyc: ## remove Python file artifacts
	@find . -name '*.pyc' -exec rm -f {} +
	@find . -name '*.pyo' -exec rm -f {} +
	@find . -name '*.orig' -exec rm -f {} +
	@find . -name '*~' -exec rm -f {} +

release: clean ## package and upload a release (working dir must be clean)
	@while true; do \
		CURRENT=`python -c "import wagtail_modeltranslation; print(wagtail_modeltranslation.__version__)"`; \
		echo ""; \
		echo "=== The current version is $$CURRENT - what's the next one?"; \
		echo "==========================================================="; \
		echo "1 - new major version"; \
		echo "2 - new minor version"; \
		echo "3 - patch"; \
		echo ""; \
		read yn; \
		case $$yn in \
			1 ) bumpversion major; break;; \
			2 ) bumpversion minor; break;; \
			3 ) bumpversion patch; break;; \
			* ) echo "Please answer 1-3.";; \
		esac \
	done
	@python setup.py bdist_wheel && twine upload dist/*
