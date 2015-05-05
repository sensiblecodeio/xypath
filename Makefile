run:    build
	@docker run \
	    --rm \
		-ti \
	    xypath

build:
	@docker build -t xypath .

.PHONY: run build
