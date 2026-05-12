FROM python:3.12-alpine AS builder

ARG TAG=global

WORKDIR /build

COPY pyproject.toml tags.json ./
COPY src/ src/

RUN pip install --no-cache-dir . && \
    eidolon --tag "${TAG}" --tags-file /build/tags.json --output /build/nginx.conf

FROM nginx:alpine

COPY --from=builder /build/nginx.conf /etc/nginx/nginx.conf

EXPOSE 5353
