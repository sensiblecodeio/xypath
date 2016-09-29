run:    build
	@docker run --rm --tty --interactive xypath

build:
	@docker build --tag xypath .

.PHONY: run build
