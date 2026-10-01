import ky from 'ky';

export interface AgentResponse {
    response: string;
}

async function invokeAgent(prompt : string) : Promise<AgentResponse> {
    const response = await ky.post<AgentResponse>('http://localhost:8000/invoke', {body: prompt})
    if (response.ok){
        return await response.json()
    } else {
        throw new Error('Failed to invoke agent')
    }
}

export default invokeAgent;