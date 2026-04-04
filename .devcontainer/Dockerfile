# FROM mcr.microsoft.com/devcontainers/python:1-3.14-bullseye
FROM python:3.14
# moveing to python 3.14 because of the new features and improvements, and also to stay up to date with the latest python version.
ENV PYTHONUNBUFFERED=1
ENV UV_SYSTEM_PYTHON=1

# Install UV from the official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

# Create user 'mike' with home directory and add to sudoers
# Grant mike ownership of Python site-packages so UV_SYSTEM_PYTHON=1 installs work without sudo
RUN useradd -ms /bin/bash mike \
    && apt-get update \
    && apt-get install -y sudo \
    && echo "mike ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers \
    && chown -R mike:mike /usr/local/lib/python3.14/site-packages /usr/local/bin

USER mike
WORKDIR /home/mike

# [Optional] If your requirements rarely change, uncomment this section to add them to the image.
# COPY requirements.txt /tmp/pip-tmp/
# RUN pip3 --disable-pip-version-check --no-cache-dir install -r /tmp/pip-tmp/requirements.txt \
#    && rm -rf /tmp/pip-tmp

# [Optional] Uncomment this section to install additional OS packages.
# RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
#     && apt-get -y install --no-install-recommends <your-package-list-here>
