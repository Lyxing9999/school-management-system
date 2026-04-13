FROM node:22-alpine

WORKDIR /app

RUN npm install -g pnpm

COPY package.json pnpm-lock.yaml* ./
RUN pnpm install --no-frozen-lockfile

COPY . .

RUN pnpm build

EXPOSE 3000

CMD ["node", ".output/server/index.mjs"]