FROM nginx:alpine
COPY working/nginx.conf /etc/nginx/nginx.conf
EXPOSE 5353
