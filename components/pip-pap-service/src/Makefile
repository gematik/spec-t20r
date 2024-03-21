.PHONY: info requirements

info:
	@echo "Available commands:"
	@echo ""
	@echo "   make info - display this message"
	@echo "   make requirements - generate requirements.txt file"


requirements:
	poetry export --without-hashes --format=requirements.txt > requirements.txt