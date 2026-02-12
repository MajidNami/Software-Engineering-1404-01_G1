# Build team9 frontend
FROM node:20-alpine AS frontend-build
WORKDIR /app
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Serve frontend with nginx reverse proxy
FROM nginx:alpine
COPY gateway.conf /etc/nginx/conf.d/default.conf
COPY --from=frontend-build /app/dist /usr/share/nginx/html/team9/

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
