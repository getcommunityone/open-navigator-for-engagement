FROM node:20-slim

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --prefer-offline --no-audit

# Copy source code
COPY . .

# Build the app
RUN npm run build

# Install a simple static server
RUN npm install -g serve

# Expose port 7860 (HuggingFace Spaces default)
EXPOSE 7860

# Serve the built app
CMD ["serve", "-s", "dist", "-l", "7860"]
