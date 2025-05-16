#!/bin/bash

# Navigate to frontend directory
cd frontend

# Install dependencies
echo "Installing dependencies..."
npm install

# Generate Next.js types
echo "Generating Next.js types..."
npm run build || true

# Create .next directory if it doesn't exist
mkdir -p .next

# Create types directory
mkdir -p .next/types

echo "Frontend setup completed!" 