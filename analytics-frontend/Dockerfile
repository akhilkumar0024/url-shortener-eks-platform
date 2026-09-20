# Multi-stage Dockerfile: Node build -> Nginx static serving

# Stage 1: Build static React bundle
FROM node:20-alpine AS builder

WORKDIR /app

COPY package.json ./
RUN npm install

COPY . .

# Build arguments for Vite environment variables
ARG VITE_API_URL=http://localhost:8001
ARG VITE_SHORTENER_API_URL=http://localhost:8000
ENV VITE_API_URL=$VITE_API_URL
ENV VITE_SHORTENER_API_URL=$VITE_SHORTENER_API_URL

RUN npm run build

# Stage 2: Serve static production assets via Nginx
FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
