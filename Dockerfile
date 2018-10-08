FROM ubuntu:latest AS base
WORKDIR /workspace

FROM base AS dependencies
RUN apt-get update && \
    apt-get -y install gcc python3 python3-pip && \
    pip3 install bcolz cython rqalpha -i https://pypi.doubanio.com/simple && \
    rm -rf /var/lib/apt/lists/*

FROM dependencies AS build
WORKDIR /workspace
COPY . /workspace

FROM python:3.6-alpine3.7 AS release
WORKDIR /workspace
COPY --from=dependencies /root/.cache /root/.cache
RUN apk add --no-cache --update gcc g++ freetype-dev libpng-dev && \
    ln -s /usr/include/locale.h /usr/include/xlocale.h && \
    pip3 install --no-cache-dir bcolz cython rqalpha -i https://pypi.doubanio.com/simple
COPY --from=build /workspace/ ./
RUN rqalpha update_bundle