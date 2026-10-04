import ky from 'ky';

export interface AgentResponse {
    response: string;
}

async function invokeAgent(prompt : string) : Promise<AgentResponse> {
    const response = await ky.post<AgentResponse>('http://localhost:8000/invoke', {json : {prompt: prompt}})
    return await response.json()
}

export default invokeAgent;