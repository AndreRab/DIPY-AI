import ky from 'ky';


export const backendUrl = (import.meta.env.VITE_BACKEND_URL || import.meta.env.BACKEND_URL || 'http://localhost:8000').replace(/\/+$/, '');


export interface Conversation {
    id: number;
    title: string;
    created_at: string;
    updated_at: string;
}

export async function getConversations(): Promise<Conversation[]> {
    const response = await ky.get<Conversation[]>(`${backendUrl}/conversations`);
    return await response.json();
}

export async function getMessages(conversationId : number) {
    const response = await ky.get(`${backendUrl}/conversations/${conversationId}/messages`);
    return await response.json();
}
