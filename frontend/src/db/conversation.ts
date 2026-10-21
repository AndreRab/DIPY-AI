

export const backendUrl = (import.meta.env.VITE_BACKEND_URL || import.meta.env.BACKEND_URL || 'http://localhost:8000').replace(/\/+$/, '');
