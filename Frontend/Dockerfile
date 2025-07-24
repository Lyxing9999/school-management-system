FROM node:22-alpine

WORKDIR /app


RUN npm install -g pnpm


COPY package.json pnpm-lock.yaml* ./


RUN pnpm install --no-frozen-lockfile


COPY . .


CMD ["pnpm", "dev"]
