MANAGE=python ./manage.py

all:
	echo "Specify a target"

sync:
	./synchronize

backup:
	$(MANAGE) dumpdata -n kadist taggit | gzip -c > kadist.json.gz

restore:
	$(MANAGE) loaddata kadist.json.gz
