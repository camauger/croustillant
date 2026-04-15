# Croustillant Recipe Management App - Justfile
# A modern serverless recipe management application

# Set shell for Windows compatibility (uses Git Bash if available)
set shell := ["bash", "-cu"]

# Default recipe (run when `just` is called without arguments)
default:
    @just --list

# Development
# Serveur local Python : static (public/) + API /api/* — les handlers sont les mêmes que sur Netlify.
# (netlify dev n'exécute pas les fonctions Python localement → 404 sur /.netlify/functions/*.)

dev:
    @echo "🚀 Démarrage du serveur local (static + API Python)…"
    @python scripts/local_dev_server.py

# Netlify CLI (proxy + static) — utile pour tester redirects/headers ; l'API Python reste absente en local.
# Clears Deno cache and kills processes before starting to avoid EBUSY errors
dev-netlify:
    @echo "🚀 Starting Netlify dev server..."
    @echo "🧹 Killing Deno/Netlify processes and clearing cache..."
    @just kill-deno-processes >/dev/null 2>&1 || true
    @just clear-deno-cache >/dev/null 2>&1 || true
    @echo "⚠️  Note: Edge Functions errors can be ignored - Python functions will work in production"
    @if command -v netlify >/dev/null 2>&1; then \
        netlify dev; \
    elif [ -f "/c/usr/local/netlify" ]; then \
        /c/usr/local/netlify dev; \
    elif command -v npx >/dev/null 2>&1; then \
        echo "⚠️  Using npx to run netlify (not in PATH)"; \
        npx --yes netlify-cli dev; \
    else \
        echo "❌ Error: Netlify CLI is not installed"; \
        echo "   Install it with: just install-netlify"; \
        echo "   Or manually: npm install -g netlify-cli"; \
        exit 1; \
    fi

# Development (PowerShell version - use if bash shell doesn't work)
dev-ps:
    @echo "🚀 Démarrage du serveur local (static + API Python)…"
    @python scripts/local_dev_server.py

# Kill Deno and Netlify processes (fixes EBUSY errors on Windows)
kill-deno-processes:
    @echo "🔪 Killing Deno/Netlify processes..."
    @cmd.exe /c "taskkill /F /IM deno.exe 2>nul & taskkill /F /IM netlify.exe 2>nul & echo ✅ Processes killed (if any were running)"

# Clear Netlify Deno cache (fixes EBUSY errors on Windows)
# Note: Run kill-deno-processes first to avoid EBUSY errors
clear-deno-cache:
    @echo "🧹 Clearing Netlify Deno cache..."
    @echo "Attempting to remove: C:\\Users\\camauger\\AppData\\Roaming\\netlify\\Config\\deno-cli"
    @cmd.exe /c "taskkill /F /IM deno.exe 2>nul & timeout /t 2 /nobreak >nul & if exist \"C:\Users\camauger\AppData\Roaming\netlify\Config\deno-cli\" (rmdir /s /q \"C:\Users\camauger\AppData\Roaming\netlify\Config\deno-cli\" 2>nul && echo ✅ Cache cleared) else (echo ✅ Cache directory does not exist)"

# Clear Netlify function cache (fixes JSON parsing errors)
clear-netlify-cache:
    @echo "🧹 Clearing Netlify function cache..."
    @if [ -d ".netlify" ]; then \
        echo "Removing .netlify cache directory..."; \
        rm -rf .netlify 2>/dev/null || cmd.exe /c "rmdir /s /q .netlify 2>nul" || echo "⚠️  Could not clear .netlify directory"; \
        echo "✅ Cache cleared"; \
    else \
        echo "✅ No .netlify cache directory found"; \
    fi

# Debug: Check function files and configuration
debug-functions:
    @echo "🔍 Checking function configuration..."
    @echo "Functions directory: netlify/functions"
    @echo "Python files found:"
    @ls -1 netlify/functions/*.py 2>/dev/null | sed 's|netlify/functions/||' || echo "  No Python files found"
    @echo ""
    @echo "Runtime file:"
    @cat netlify/functions/runtime.txt 2>/dev/null || echo "  ❌ runtime.txt not found"
    @echo ""
    @echo "Requirements file:"
    @cat netlify/functions/requirements.txt 2>/dev/null || echo "  ❌ requirements.txt not found"
    @echo ""
    @echo "Checking for handler functions:"
    @grep -l "def handler" netlify/functions/*.py 2>/dev/null | sed 's|netlify/functions/||' | sed 's/^/  ✅ /' || echo "  ❌ No handler functions found"

# Diagnostic complet - vérifie tout
diagnostic:
    @echo "🔍 DIAGNOSTIC COMPLET - Croustillant"
    @echo ""
    @echo "1. Serveur Netlify:"
    @curl -s -o /dev/null -w "   Status: %{http_code}\n" http://localhost:8888 2>/dev/null || echo "   ❌ Serveur non démarré"
    @echo ""
    @echo "2. Fonctions API:"
    @curl -s http://localhost:8888/api/recipes 2>/dev/null | head -c 100 | grep -q "success\|recipes\|error" && echo "   ✅ Accessibles" || echo "   ❌ Non disponibles ou erreur"
    @echo ""
    @echo "3. Configuration:"
    @if [ -f .env ]; then echo "   ✅ .env existe"; else echo "   ❌ .env MANQUANT - Créez-le avec DATABASE_URL"; fi
    @if [ -f netlify.toml ]; then echo "   ✅ netlify.toml existe"; else echo "   ❌ netlify.toml MANQUANT"; fi
    @echo ""
    @echo "4. Fonctions Python:"
    @count=$$(ls -1 netlify/functions/*.py 2>/dev/null | wc -l | tr -d ' '); \
    if [ "$$count" = "3" ]; then echo "   ✅ $$count fichiers trouvés"; else echo "   ❌ $$count fichiers (attendu: 3)"; fi
    @echo ""
    @echo "5. Variables d'environnement:"
    @if [ -f .env ]; then \
        if grep -q "DATABASE_URL" .env 2>/dev/null; then \
            echo "   ✅ DATABASE_URL défini"; \
        else \
            echo "   ❌ DATABASE_URL manquant dans .env"; \
        fi; \
    else \
        echo "   ❌ Fichier .env n'existe pas"; \
    fi
    @echo ""
    @echo "=== FIN DU DIAGNOSTIC ==="

# Install dependencies
# Install Python dependencies for Netlify functions and local scripts (import favoris, etc.)
install:
    @echo "📦 Installing Python dependencies..."
    pip install -r netlify/functions/requirements.txt
    pip install -r scripts/requirements.txt
    @echo "✅ Dependencies installed!"

# Appliquer neon-schema.sql sur Neon (variable DATABASE_URL dans .env)
db-schema:
    @python scripts/apply_neon_schema.py

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

# Import recipes from Chrome bookmarks (folder "Recettes" by default). Requires scripts/requirements.txt and DATABASE_URL.
import-bookmarks *ARGS:
    @echo "📥 Import favoris → Croustillant..."
    python scripts/import_bookmarks_to_croustillant.py {{ARGS}}

# Test API endpoints locally
# Note: Requires Netlify dev server to be running (use 'just dev' in another terminal)
test-api:
    @echo "🧪 Testing API endpoints..."
    @if ! curl -s http://localhost:8888 >/dev/null 2>&1; then \
        echo "❌ Error: Netlify dev server is not running on port 8888"; \
        echo "   Start it with: just dev"; \
        exit 1; \
    fi
    @echo "GET /api/recipes"
    @curl -s http://localhost:8888/api/recipes | head -20 || echo "❌ Failed to fetch recipes"
    @echo "\n\nGET /api/recipe-detail/1"
    @curl -s http://localhost:8888/api/recipe-detail/1 | head -20 || echo "❌ Failed to fetch recipe detail"

# Test shopping list endpoint
# Note: Requires Netlify dev server to be running (use 'just dev' in another terminal)
test-shopping-list:
    @echo "🧪 Testing shopping list generation..."
    @if ! curl -s http://localhost:8888 >/dev/null 2>&1; then \
        echo "❌ Error: Netlify dev server is not running on port 8888"; \
        echo "   Start it with: just dev"; \
        exit 1; \
    fi
    @curl -X POST http://localhost:8888/api/shopping-list \
        -H "Content-Type: application/json" \
        -d '{"recipe_ids":[1,2],"exclude_pantry":false}' \
        -s \
        | python -m json.tool 2>/dev/null || echo "❌ Failed to generate shopping list. Check server logs."

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
    @if command -v netlify >/dev/null 2>&1; then \
        netlify deploy --prod; \
    elif [ -f "/c/usr/local/netlify" ]; then \
        /c/usr/local/netlify deploy --prod; \
    elif command -v npx >/dev/null 2>&1; then \
        npx --yes netlify-cli deploy --prod; \
    else \
        echo "❌ Error: Netlify CLI is not installed"; \
        echo "   Install it with: just install-netlify"; \
        exit 1; \
    fi

# Deploy preview (for testing before production)
deploy-preview:
    @echo "🚀 Creating preview deployment..."
    @if command -v netlify >/dev/null 2>&1; then \
        netlify deploy; \
    elif [ -f "/c/usr/local/netlify" ]; then \
        /c/usr/local/netlify deploy; \
    elif command -v npx >/dev/null 2>&1; then \
        npx --yes netlify-cli deploy; \
    else \
        echo "❌ Error: Netlify CLI is not installed"; \
        echo "   Install it with: just install-netlify"; \
        exit 1; \
    fi

# Check Netlify status
status:
    @echo "📊 Checking Netlify status..."
    @if command -v netlify >/dev/null 2>&1; then \
        netlify status; \
    elif [ -f "/c/usr/local/netlify" ]; then \
        /c/usr/local/netlify status; \
    elif command -v npx >/dev/null 2>&1; then \
        npx --yes netlify-cli status; \
    else \
        echo "❌ Error: Netlify CLI is not installed"; \
        echo "   Install it with: just install-netlify"; \
        exit 1; \
    fi

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

