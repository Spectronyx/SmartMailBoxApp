import api from './api';

const TOKEN_KEY = 'smart_mailbox_access_token';
const REFRESH_KEY = 'smart_mailbox_refresh_token';
const USER_KEY = 'smart_mailbox_user';

export const authService = {
    setTokens(access, refresh) {
        localStorage.setItem(TOKEN_KEY, access);
        localStorage.setItem(REFRESH_KEY, refresh);
    },

    setUser(user) {
        localStorage.setItem(USER_KEY, JSON.stringify(user));
    },

    getAccessToken() {
        return localStorage.getItem(TOKEN_KEY);
    },

    getRefreshToken() {
        return localStorage.getItem(REFRESH_KEY);
    },

    getUser() {
        const user = localStorage.getItem(USER_KEY);
        return user ? JSON.parse(user) : null;
    },

    isAuthenticated() {
        return !!this.getAccessToken();
    },

    async getGoogleAuthUrl() {
        const response = await api.get('/auth/google/url/');
        return response.data.url;
    },

    logout() {
        localStorage.removeItem(TOKEN_KEY);
        localStorage.removeItem(REFRESH_KEY);
        localStorage.removeItem(USER_KEY);
        window.location.href = '/login';
    }
};
