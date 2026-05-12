FROM python:3.12-alpine@sha256:236173eb74001afe2f60862de935b74fcbd00adfca247b2c27051a70a6a39a2d AS builder

ARG TAG=global

WORKDIR /build

COPY pyproject.toml tags.json ./
COPY src/ src/

RUN pip install --no-cache-dir . && \
    eidolon --tag "${TAG}" --tags-file /build/tags.json --output /build/nginx.conf

FROM nginx:alpine@sha256:5616878291a2eed594aee8db4dade5878cf7edcb475e59193904b198d9b830de

COPY --from=builder /build/nginx.conf /etc/nginx/nginx.conf

EXPOSE 5353
