// Simple client-side router

class Router {
    constructor() {
        this.routes = {};
        this.currentPage = null;

        // Handle navigation
        window.addEventListener('popstate', () => this.handleRoute());

        // Handle link clicks
        document.addEventListener('click', (e) => {
            if (e.target.matches('.nav-link')) {
                e.preventDefault();
                const page = e.target.dataset.page;
                this.navigate(page);
            }
        });
    }

    register(path, handler) {
        this.routes[path] = handler;
    }

    navigate(page) {
        const path = page === 'recipes' ? '/' : `/${page}`;
        window.history.pushState({}, '', path);
        this.handleRoute();
    }

    handleRoute() {
        const path = window.location.pathname;
        let page = 'recipes';

        if (path === '/create') page = 'create';
        else if (path === '/selection') page = 'selection';
        else if (path === '/shopping') page = 'shopping';
        else if (path.startsWith('/recipe/')) page = 'recipe-detail';

        // Update active nav link
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
            if (link.dataset.page === page) {
                link.classList.add('active');
            }
        });

        // Call the route handler
        if (this.routes[page]) {
            this.currentPage = page;
            this.routes[page](path);
        } else {
            this.routes['recipes']();
        }
    }

    getCurrentPage() {
        return this.currentPage;
    }
}

// Create global router instance
const router = new Router();
