#syntax=docker/dockerfile:1

# Use the official Bun image with latest tag
FROM oven/bun:latest

# Set working directory
WORKDIR /app

# Copy your project files
COPY --link package.json bun.lockb ./

# Install dependencies
RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y nodejs \
    npm  
RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y nodejs \
    npm     
RUN bun install

COPY . .

# Expose your application port (optional, adjust based on your project)
EXPOSE 7000

# Start your application (replace with your command)
RUN bun run start
