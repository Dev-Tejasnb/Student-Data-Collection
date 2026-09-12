class AuthManager {
    constructor() {
        this.tokenKey = 'access_token';
        this.userKey = 'user_data';
    }

    getToken() {
        return sessionStorage.getItem(this.tokenKey);
    }

    setToken(token) {
        sessionStorage.setItem(this.tokenKey, token);
    }

    clearToken() {
        sessionStorage.removeItem(this.tokenKey);
    }

    getUser() {
        const userData = sessionStorage.getItem(this.userKey);
        return userData ? JSON.parse(userData) : null;
    }

    setUser(user) {
        sessionStorage.setItem(this.userKey, JSON.stringify(user));
    }

    clearUser() {
        sessionStorage.removeItem(this.userKey);
    }

    isAuthenticated() {
        return !!this.getToken();
    }

    getAuthHeader() {
        const token = this.getToken();
        return token ? { 'Authorization': `Bearer ${token}` } : {};
    }

    async handleResponse(response) {
        if (response.status === 401) {
            this.clearToken();
            this.clearUser();
            if (window.location.pathname !== '/login') {
                window.location.href = '/login';
            }
            throw new Error('Session expired. Please login again.');
        }
        return response;
    }

    async fetchWithAuth(url, options = {}) {
        const headers = {
            'Content-Type': 'application/json',
            ...this.getAuthHeader(),
            ...options.headers
        };

        const response = await fetch(url, {
            ...options,
            headers
        });

        await this.handleResponse(response);
        return response;
    }

    logout() {
        this.clearToken();
        this.clearUser();
        window.location.href = '/login';
    }

    redirectIfAuthenticated() {
        if (this.isAuthenticated() && window.location.pathname === '/login') {
            window.location.href = '/dashboard';
        }
    }

    redirectIfNotAuthenticated() {
        if (!this.isAuthenticated() && window.location.pathname !== '/' && window.location.pathname !== '/login') {
            window.location.href = '/login';
        }
    }
}

const auth = new AuthManager();