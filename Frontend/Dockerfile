FROM node:22-alpine

# Set working directory
WORKDIR /app

# Install pnpm
RUN npm install -g pnpm

# Copy package files first for caching
COPY package.json pnpm-lock.yaml* ./

# Install dependencies
RUN pnpm install --no-frozen-lockfile

# Copy rest of the app
COPY . .

# Expose port
EXPOSE 3000

# Run dev server
CMD ["pnpm", "dev"]