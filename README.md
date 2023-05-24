# How to: Run Python Wheel Tasks in Custom Docker Containers in Databricks

Based on the blog post [TODO: add link] by Johannes Schmidt.

## Prerequisites

- [Poetry](https://python-poetry.org/)
- [Docker](https://www.docker.com/)
- [Databricks](https://www.databricks.com/) on
  [Azure](https://azure.microsoft.com/) or [AWS](https://aws.amazon.com/) (standard tier)
- [Databricks Personal Access Token](https://docs.databricks.com/dev-tools/auth.html) (PAT)
- Container registry (e.g. [Azure Container Registry](https://azure.microsoft.com/de-de/products/container-registry))

## Structure

| folder    | sub-folder   | content                                                                         |
|-----------|--------------|---------------------------------------------------------------------------------|
| `scripts` |              | Python example scripts to create & trigger Databricks job runs using the `.env` |
| `src`     |              | Source code                                                                     |
|           | `databricks` | Databricks service                                                              |
|           | `dbscript1`  | Console script entrypoint 1                                                     |
|           | `dbscript2`  | Console script entrypoint 2                                                     |

## Getting started

Create a `.env` file from the `.env.sample` and add the following environment variables:

- DATABRICKS_URL
- DATABRICKS_PAT
- CR_USERNAME
- CR_PASSWORD

Enter values for the variables in the [Makefile](Makefile):

- **container_name**
- **acr_name**

Run the [Makefile](Makefile) targets to build and push the Docker image to the container registry (ACR):

```bash
make docker build
make acr-login
make docker-push
```

## Python version

The Python version used is **3.9** because it is the version supported by the latest LTS version of the Databricks
Runtime 12.2 LTS (May, 2023).

## Docker images

The Databricks base images can be found
on [GitHub](https://github.com/databricks/containers) & [DockerHub](https://hub.docker.com/u/databricksruntime)

- Databricks base
  image: [databricksruntime/python:latest:12.2-LTS](https://hub.docker.com/layers/databricksruntime/standard/12.2-LTS/images/sha256-6546a5e5c6084edaac2960de9b4c900d09c73aca17c6d322f05c27d45324659f)

- Wheel task image: [Docker image](Dockerfile)

## Resources & References

- Python CLI utilities with Poetry and
  Typer: https://www.pluralsight.com/tech-blog/python-cli-utilities-with-poetry-and-typer/
- [Typer](https://typer.tiangolo.com/)/[click](https://click.palletsprojects.com/en/8.1.x/)
  setting `standalone_mode=False` based on this [issue](https://github.com/tiangolo/typer/issues/129)
- Databricks Jobs API (2.1): https://docs.databricks.com/api/azure/workspace/jobs/submit
- [Use a Python wheel in a Databricks job](https://docs.databricks.com/workflows/jobs/how-to/use-python-wheels-in-workflows.html)
