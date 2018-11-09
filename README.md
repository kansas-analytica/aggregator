# aggregator
Data aggregation tool used to gather and translate information into an RDBMS format.

# Prerequisites
The main prereqresite for the project is Docker. Please visit https://www.docker.com/ and install Docker on your machine before getting started.

# Usage
Provided are a variety of scripts that can be used to easily run the project

`make agg` will run a completely local instance of the aggregator that is not in a docker container. This is useful for quick tests

`make dock` will build a new Docker image for the project

`make run` will set up a new Docker container for the project and open the project locally

`make clean` will remove all previously created Docker images and container instances.
