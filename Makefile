.PHONY: all jupyter pause address containers list-containers stop-containers \
        restart-containers lint tests pytest isort black flake8 mypy shell clear-nb \
        clean

# Usage:
# make                    # just alias to containers command
# make jupyter            # startup Docker container running Jupyter server
# make pause              # pause PSECS (to pause between commands)
# make address            # get Docker container address/port
# make containers         # launch all Docker containers
# make list-containers    # list all running containers
# make stop-containers    # simply stops all running Docker containers
# make restart-containers # restart all containers
# make lint               # run linters
# make tests              # run full testing suite
# make pytest             # run pytest in docker container
# make isort              # run isort in docker container
# make black              # run black in docker container
# make flake8             # run flake8 in docker container
# make mypy               # run mypy in docker container
# make shell              # create interactive shell in docker container
# make clear-nb           # simply clears Jupyter notebook output
# make clean              # combines all clearing commands into one


################################################################################
# GLOBALS                                                                      #
################################################################################

# make cli args
DCTNR := $(notdir $(PWD))
INTDR := notebooks
PSECS := 5

# notebook-related variables
CURRENTDIR := $(PWD)
NOTEBOOKS  := $(shell find ${INTDR} -name "*.ipynb" -not -path "*/.ipynb_*/*")

# docker-related variables
JPTCTNR = jupyter.${DCTNR}
SRCPATH = /usr/local/src/modern-solvers
DCKRIMG = ghcr.io/diogenesanalytics/modern-solvers:master
JPTRSRV = docker run --rm -v ${CURRENTDIR}:/home/jovyan -it ${DCKRIMG}
DCKRTST = docker run --rm -v ${CURRENTDIR}:${SRCPATH} -it ${DCKRIMG}

# jupyter nbconvert vars
NBCLER = jupyter nbconvert --clear-output --inplace

################################################################################
# COMMANDS                                                                     #
################################################################################

# launch jupyter
all: containers

# launch jupyter notebook development Docker image
jupyter:
	@ echo "Launching Jupyter in Docker container -> ${JPTCTNR} ..."
	@ if ! docker ps --format={{.Names}} | grep -q "${JPTCTNR}"; then \
	  docker run -d \
	             --rm \
	             --name ${JPTCTNR} \
	             -e JUPYTER_ENABLE_LAB=yes \
	             -p 8888 \
	             -v "${CURRENTDIR}":/usr/local/src/modern-solvers \
	             ${DCKROPT} \
	             ${DCKRIMG} && \
	  if ! grep -sq "${JPTCTNR}" "${CURRENTDIR}/.running_containers"; then \
	    echo "${JPTCTNR}" >> .running_containers; \
	  fi \
	else \
	  echo "Container already running. Try setting DCTNR manually."; \
	fi

# simply wait for a certain amount of time
pause:
	@ echo "Sleeping ${PSECS} seconds ..."
	@ sleep ${PSECS}

# get containerized server address
address:
	@ if [ -f "${CURRENTDIR}/.running_containers" ]; then \
	while read container; do \
	  if echo "$${container}" | grep -q "${JPTCTNR}" ; then \
	    echo "Server address: $$(docker logs $${container} 2>&1 | \
	          grep http://127.0.0.1 | tail -n 1 | \
	          sed s/:8888/:$$(docker port $${container} | \
	          grep '0.0.0.0:' | awk '{print $$3}' | sed 's/0.0.0.0://g')/g | \
	          tr -d '[:blank:]')"; \
	  else \
	    echo "Could not find running container: ${JPTCTNR}." \
	         "Try running: make list-containers"; \
	  fi \
	done < "${CURRENTDIR}/.running_containers"; \
	else \
	  echo ".running_containers file not found. Is a Docker container running?"; \
	fi

# launch all docker containers
containers: jupyter pause address

# list all running containers
list-containers:
	@ if [ -f "${CURRENTDIR}/.running_containers" ]; then \
	echo "Currently running containers:"; \
	while read container; do \
	  echo "-->  $${container}"; \
	done < "${CURRENTDIR}/.running_containers"; \
	else \
	  echo ".running_containers file not found. Is a Docker container running?"; \
	fi

# stop all containers
stop-containers:
	@ if [ -f "${CURRENTDIR}/.running_containers" ]; then \
	  echo "Stopping Docker containers ..."; \
	  while read container; do \
	    echo "Container $$(docker stop $$container) stopped."; \
	  done < "${CURRENTDIR}/.running_containers"; \
	  rm -f "${CURRENTDIR}/.running_containers"; \
	else \
	  echo "${CURRENTDIR}/.running_containers file not found."; \
	fi

# restart all containers
restart-containers: stop-containers containers

# run linters
lint: isort black flake8 mypy

# run full testing suite
tests: pytest lint

# run pytest in docker container
pytest:
	@ ${DCKRTST} pytest

# run isort in docker container
isort:
	@ ${DCKRTST} isort src/ tests/

# run black in docker container
black:
	@ ${DCKRTST} black src/ tests/

# run flake8 in docker container
flake8:
	@ ${DCKRTST} flake8

# run mypy in docker container
mypy:
	@ ${DCKRTST} mypy src/ tests/

# create interactive shell in docker container
shell:
	@ ${DCKRTST} bash || true

# remove output from executed notebooks
clear-nb:
	@ echo "Removing all output from Jupyter notebooks."
	@ ${JPTRSRV} ${NBCLER} ${NOTEBOOKS}

# cleanup everything
clean: clear-nb
