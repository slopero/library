FROM nginx:alpine

RUN rm /etc/nginx/conf.d/default.conf

# Копируем наш конфиг
COPY nginx.conf /etc/nginx/conf.d/

# Копируем все файлы фронтенда в папку которую раздаёт nginx
COPY . /usr/share/nginx/html/

EXPOSE 5000
