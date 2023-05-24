FROM databricksruntime/python:12.2-LTS as base

WORKDIR /app

# ignore 'Running pip as the root user...' warning
ENV PIP_ROOT_USER_ACTION=ignore

ENV PATH="/databricks/python3/bin:${PATH}"

# update pip
RUN pip install --upgrade pip

# ---------------------------------------------------------------------------------------------------------------------#
FROM base as builder

# install poetry
ENV POETRY_VERSION=1.4.2
RUN pip install "poetry==$POETRY_VERSION"

# copy application
WORKDIR /app
COPY ["pyproject.toml", "poetry.lock", "README.md", "./"]
COPY ["src/", "src/"]

# build wheel
RUN poetry build --format wheel

# ---------------------------------------------------------------------------------------------------------------------#
FROM base as production

# copy the wheel from the build stage
COPY --from=builder /app/dist/*.whl /app/

# install package
RUN pip install /app/*.whl
