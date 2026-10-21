import ky from 'ky';

export interface AgentResponse {
    response: string;
    conversation_id: number;
}

export interface AgentRequest {
    prompt: string;
    conversation_id?: number;
}

export const backendUrl = (import.meta.env.VITE_BACKEND_URL || import.meta.env.BACKEND_URL || 'http://localhost:8000').replace(/\/+$/, '');

async function invokeAgent(request: AgentRequest): Promise<AgentResponse> {
    const response = await ky.post<AgentResponse>(`${backendUrl}/invoke`, {
        json: request,
        retry: 0,
        timeout: false,
    })
    return await response.json()
}

export default invokeAgent;
