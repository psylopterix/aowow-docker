# ==========================================
# Stage 1: Clone AoWoW source
# ==========================================
FROM alpine:latest AS builder

ARG AOWOW_REPO=https://github.com/azerothcore/aowow.git
ARG AOWOW_BRANCH=master

RUN apk add --no-cache git \
    && git clone --depth 1 --branch "${AOWOW_BRANCH}" "${AOWOW_REPO}" /aowow-src \
    && rm -rf /aowow-src/.git

# ==========================================
# Stage 2: PHP 8.4 + Apache runtime
# ==========================================
FROM php:8.4-apache

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpng-dev \
    libjpeg-dev \
    libfreetype6-dev \
    libxml2-dev \
    && docker-php-ext-configure gd --with-freetype --with-jpeg \
    && docker-php-ext-install mysqli gd simplexml xml \
    && rm -rf /var/lib/apt/lists/*

RUN a2enmod rewrite

COPY --from=builder /aowow-src /var/www/html
RUN chown -R www-data:www-data /var/www/html
