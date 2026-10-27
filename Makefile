.PHONY: clean all run car

clean:
	rm -rf build/

all: clean
	mkdir -p build/
	cp -r assets/ build/
	cp -r src/* build/

run: all
	.venv/bin/python build/syserverX.py

car: run
