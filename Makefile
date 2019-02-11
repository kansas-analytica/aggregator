agg:
	python3 main.py

build:
	pip install -r requirements.txt

dock: 
	docker build -t aggregator-image:latest .
	
run: 
	docker run -d -p 5000:5000 aggregator-image
	open http://localhost:5000

clean:
	chmod u+x ./docker_cleanup.sh
	./docker_cleanup.sh
