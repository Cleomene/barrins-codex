PYTHON=python
JSON=AtomicCards.json.gz

.PHONY: clean

all: models

$(JSON):
	# wget -N https://mtgjson.com/json/$(JSON)
	# curl --remote-time -o ${JSON} https://mtgjson.com/json/$(JSON)
	## What we really want here is to use remote timestamp if file exists, else
	## use the current timestamp.
	## https://mtgjson.com/api/v5/AtomicCards.json.gz
	curl -o ${JSON} https://mtgjson.com/api/v5/$(JSON)

library: $(JSON)
	$(PYTHON) build_library.py && touch $@

clean:
	rm $(JSON)
