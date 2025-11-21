FROM node:20-alpine as build
WORKDIR /app
COPY frontend/package.json frontend/vite.config.js frontend/index.html /app/
COPY frontend/.eslintrc.cjs /app/
COPY frontend/src /app/src
RUN npm install && npm run build

FROM nginx:1.25-alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
