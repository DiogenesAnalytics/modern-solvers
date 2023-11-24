# jupyter base image
FROM jupyter/scipy-notebook:lab-4.0.0

# first turn off git safe.directory
RUN git config --global safe.directory '*'

# turn off poetry venv
ENV POETRY_VIRTUALENVS_CREATE=false

# set src target dir
WORKDIR /usr/local/src/modern-solvers

# get src
COPY . .

# get poetry in order to install development dependencies
RUN pip install poetry

# config max workers
RUN poetry config installer.max-workers 10

# now install development dependencies
RUN poetry install --with dev -C .
