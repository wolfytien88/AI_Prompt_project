.PHONY: lint test check

lint:
	python3 tools/check_layers.py

test:
	python3 -m unittest discover -s tests -v

check: lint test
