FROM nginx:alpine@sha256:dc48b7a872a79fb541ba5081d320b11b549231bc63ba465a7495afaa7d2ebcb8

COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 5353/udp
