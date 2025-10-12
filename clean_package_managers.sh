#!/bin/bash

# Clean up package manager conflicts in Commercial-View
echo "🧹 Cleaning up package manager conflicts..."

# Remove conflicting lockfiles (keep only package-lock.json for npm)
echo "📦 Standardizing on npm as package manager..."

# Remove yarn.lock if it exists
if [ -f "yarn.lock" ]; then
    echo "  🗑️  Removing yarn.lock"
    rm yarn.lock
fi

# Remove pnpm-lock.yaml if it exists
if [ -f "pnpm-lock.yaml" ]; then
    echo "  🗑️  Removing pnpm-lock.yaml"
    rm pnpm-lock.yaml
fi

# Remove bun.lockb if it exists
if [ -f "bun.lockb" ]; then
    echo "  🗑️  Removing bun.lockb"
    rm bun.lockb
fi

# Check frontend directory
if [ -d "frontend" ]; then
    cd frontend
    
    echo "📂 Cleaning frontend directory..."
    
    if [ -f "yarn.lock" ]; then
        echo "  🗑️  Removing frontend/yarn.lock"
        rm yarn.lock
    fi
    
    if [ -f "pnpm-lock.yaml" ]; then
        echo "  🗑️  Removing frontend/pnpm-lock.yaml"
        rm pnpm-lock.yaml
    fi
    
    if [ -f "bun.lockb" ]; then
        echo "  🗑️  Removing frontend/bun.lockb"
        rm bun.lockb
    fi
    
    # Ensure we have package-lock.json
    if [ ! -f "package-lock.json" ] && [ -f "package.json" ]; then
        echo "  📦 Generating package-lock.json..."
        npm install
    fi
    
    cd ..
fi

# Ensure root package-lock.json exists if package.json exists
if [ ! -f "package-lock.json" ] && [ -f "package.json" ]; then
    echo "📦 Generating root package-lock.json..."
    npm install
fi

echo "✅ Package manager cleanup completed!"
echo "📋 Summary:"
echo "  - Package Manager: npm (standardized)"
echo "  - Lockfile: package-lock.json (kept)"
echo "  - Removed: yarn.lock, pnpm-lock.yaml, bun.lockb (if present)"
