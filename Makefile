MANAGE=python ./manage.py

all:
	echo "Specify a target"

sync:
	./synchronize

backup:
	$(MANAGE) dumpdata kadist taggit | gzip -c > kadist.json.gz

restore:
	$(MANAGE) loadata kadist.json
