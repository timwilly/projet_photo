ELASTICSEARCH_BAT = elasticsearch-8.5.3/bin/elasticsearch.bat
export FLASK_APP=microblog.py

all: run

install:
	pip install -r requirements.txt

run:
	flask run --host 0.0.0.0

clean:
	rm -rf db/*.db
	rm -rf static/data/*.xml
	rm -rf static/data/*.csv