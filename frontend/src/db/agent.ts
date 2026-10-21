import ky from 'ky';

export interface AgentResponse {
    response: string;
}

export const backendUrl = (import.meta.env.VITE_BACKEND_URL || import.meta.env.BACKEND_URL || 'http://localhost:8000').replace(/\/+$/, '');

async function invokeAgent(prompt : string) : Promise<AgentResponse> {
    const response = await ky.post<AgentResponse>(`${backendUrl}/invoke`, {json : {prompt: prompt}})
    return await response.json()
}

export default invokeAgent;
