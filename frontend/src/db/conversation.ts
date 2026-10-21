import ky from 'ky';
import { backendUrl } from '@/agent/agent';

export interface Conversation {
    id: number;
    title: string;
    created_at: string;
    updated_at: string;
}

export interface ConversationMessage {
    role: 'user' | 'assistant';
    content: string;
}

export async function getConversations(signal?: AbortSignal): Promise<Conversation[]> {
    const response = await ky.get<Conversation[]>(`${backendUrl}/conversations`, { signal });
    return await response.json();
}

export async function getMessages(conversationId: number, signal?: AbortSignal): Promise<ConversationMessage[]> {
    const response = await ky.get<ConversationMessage[]>(`${backendUrl}/conversations/${conversationId}/messages`, { signal });
    return await response.json();
}
