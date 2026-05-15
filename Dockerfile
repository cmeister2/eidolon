FROM nginx:alpine@sha256:feb6f75a08aa55b44576f98c15b8859819ecf54f3e4d2157f42c2d01cb58a3d2

COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 5353/udp
