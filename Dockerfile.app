# Teleoscope web app (teleoscope.ca)
FROM node:22-alpine AS base

# Install pnpm
RUN corepack enable && corepack prepare pnpm@latest --activate

WORKDIR /app

# Copy package files
COPY package.json pnpm-lock.yaml ./
COPY teleoscope.ca/package.json teleoscope.ca/pnpm-lock.yaml ./teleoscope.ca/

# Install root deps (react-joyride)
RUN pnpm install --frozen-lockfile

# Install app deps
WORKDIR /app/teleoscope.ca
RUN pnpm install --frozen-lockfile

# Copy app source (schema artifacts are pre-generated and committed to the repo)
COPY teleoscope.ca ./

# Build
ENV NODE_ENV=production
RUN pnpm build

EXPOSE 3000
CMD ["pnpm", "start"]
