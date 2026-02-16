# multi stage dockerfile


# Build stage, large node image
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package.json 
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . . 

# Build the app
RUN npm run build

# Production stage, smaller nginx image
FROM nginx:alpine

# Copy dist files from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx config for SPA routing
RUN echo 'server { \
    listen 80; \
    server_name _; \
    root /usr/share/nginx/html; \ 
    index index.html; \
    location / { \
        try_files $uri $uri/ /index.html; \
    } \
}' > /etc/nginx/conf.d/default.conf

#port
EXPOSE 80 

#start nginx
CMD ["nginx", "-g", "daemon off;"]