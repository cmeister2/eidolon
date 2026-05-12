FROM python:3.14-alpine@sha256:a3de013592ea520507c1f18d880592338bd21abfe706237e68ed4126e21b6900 AS builder

ARG TAG=global

WORKDIR /build

COPY pyproject.toml tags.json ./
COPY src/ src/

RUN pip install --no-cache-dir . && \
    eidolon --tag "${TAG}" --tags-file /build/tags.json --output /build/nginx.conf

FROM nginx:alpine@sha256:5616878291a2eed594aee8db4dade5878cf7edcb475e59193904b198d9b830de

COPY --from=builder /build/nginx.conf /etc/nginx/nginx.conf

EXPOSE 5353
