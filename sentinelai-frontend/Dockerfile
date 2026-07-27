FROM node:22-alpine AS base

FROM base AS deps
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci --only=production && \
    npm cache clean --force

FROM base AS build
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci
COPY . .
ARG VITE_API_BASE_URL
ARG VITE_APP_ENV
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
ENV VITE_APP_ENV=$VITE_APP_ENV
RUN npm run build

FROM nginx:1.27-alpine AS runner
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nginx -u 1001
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
RUN chown -R nginx:nginx /usr/share/nginx/html && \
    chmod -R 755 /usr/share/nginx/html
EXPOSE 80
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget -qO- http://localhost:80/health || exit 1
USER nginx
CMD ["nginx", "-g", "daemon off;"]
