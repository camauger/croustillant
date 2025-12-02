# Croustillant Recipe Management App - Justfile
# A modern serverless recipe management application

# Default recipe (run when `just` is called without arguments)
default:
    @just --list

# Development
# Start local development server with Netlify CLI
dev:
    @echo "🚀 Starting Netlify dev server..."
    netlify dev

# Install dependencies
# Install Python dependencies for Netlify functions and migration tools
install:
    @echo "📦 Installing Python dependencies..."
    pip install -r netlify/functions/requirements.txt
    pip install -r migration/requirements.txt
    @echo "✅ Dependencies installed!"

# Install Netlify CLI globally (if not already installed)
install-netlify:
    @echo "📦 Installing Netlify CLI..."
    npm install -g netlify-cli
    @echo "✅ Netlify CLI installed!"

# Setup
# Set up environment variables from example file
setup:
    @if [ ! -f .env ]; then \
        echo "📝 Creating .env file from .env.example..."; \
        cp .env.example .env; \
        echo "⚠️  Please edit .env and add your Supabase credentials"; \
    else \
        echo "✅ .env file already exists"; \
    fi

# Database
# Run database migration from SQLite to Supabase
migrate:
    @echo "🔄 Running database migration..."
    cd migration && pip install -r requirements.txt && python migrate-to-supabase.py

# Test API endpoints locally
test-api:
    @echo "🧪 Testing API endpoints..."
    @echo "GET /api/recipes"
    @curl -s http://localhost:8888/api/recipes | head -20
    @echo "\n\nGET /api/recipe-detail/1"
    @curl -s http://localhost:8888/api/recipe-detail/1 | head -20

# Test shopping list endpoint
test-shopping-list:
    @echo "🧪 Testing shopping list generation..."
    @curl -X POST http://localhost:8888/api/shopping-list \
        -H "Content-Type: application/json" \
        -d '{"recipe_ids":[1,2],"exclude_pantry":false}' \
        | python -m json.tool

# Lint and format (if tools are available)
lint:
    @echo "🔍 Checking code style..."
    @if command -v flake8 >/dev/null 2>&1; then \
        flake8 netlify/functions/*.py netlify/functions/utils/*.py; \
    else \
        echo "⚠️  flake8 not installed. Install with: pip install flake8"; \
    fi

# Clean
# Remove Python cache files and virtual environment artifacts
clean:
    @echo "🧹 Cleaning up..."
    find . -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete 2>/dev/null || true
    find . -type f -name "*.pyo" -delete 2>/dev/null || true
    find . -type d -name "*.egg-info" -exec rm -r {} + 2>/dev/null || true
    @echo "✅ Cleanup complete!"

# Deploy
# Deploy to Netlify (requires Netlify CLI and authentication)
deploy:
    @echo "🚀 Deploying to Netlify..."
    netlify deploy --prod

# Deploy preview (for testing before production)
deploy-preview:
    @echo "🚀 Creating preview deployment..."
    netlify deploy

# Check Netlify status
status:
    @echo "📊 Checking Netlify status..."
    netlify status

# Show environment variables (without values for security)
env-show:
    @echo "🔐 Environment variables:"
    @if [ -f .env ]; then \
        grep -v "^#" .env | grep -v "^$$" | cut -d'=' -f1 | sed 's/^/  - /'; \
    else \
        echo "⚠️  .env file not found. Run 'just setup' first."; \
    fi

# Help
# Show available recipes
help:
    @just --list

