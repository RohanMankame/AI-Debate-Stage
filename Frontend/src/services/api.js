import axios from 'axios';

const API_BASE = 'http://localhost:8000/v1';

const api = axios.create({
    baseURL: API_BASE,
    headers: {
        'Content-Type': 'application/json',
    },
});

export const createSession = async (data) => {
    const response = await api.post('/debate/session', data);
    return response.data;
};

export const advanceSession = async (sessionId) => {
    const response = await api.post(`/debate/session/${sessionId}/advance`);
    return response.data;
};

export const judgeSession = async (sessionId) => {
    const response = await api.post(`/debate/session/${sessionId}/judge`);
    return response.data;
};

export const getSessionState = async (sessionId) => {
    const response = await api.get(`/debate/session/${sessionId}`);
    return response.data;
};

export default api;
