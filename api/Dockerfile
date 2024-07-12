#syntax=docker/dockerfile:1

# Use the official Bun image with latest tag
FROM oven/bun:latest

# Set working directory
WORKDIR /app

# Copy your project files
COPY --link package.json bun.lockb ./

# Install dependencies
RUN rm /bin/sh && ln -s /bin/bash /bin/sh
RUN apt-get update &&\
    apt-get install --yes git curl build-essential

RUN curl -sL https://deb.nodesource.com/setup_current.x | bash - &&\
    apt-get update && \
    apt-get install --yes --no-install-recommends nodejs

RUN bun install
COPY . .

# Expose your application port (optional, adjust based on your project)
EXPOSE 7000

# Start your application (replace with your command)
CMD ["bun", "run", "start"]
