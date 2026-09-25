from dipy_ai.agent.base_agent import BaseAgent, UserMessage
from dipy_ai.tools import ToolBundleEnum, ToolBundle
from langgraph.graph import StateGraph, START, END
from typing import TypedDict
from openai import OpenAI


class WorkflowState(TypedDict):
    history: list[dict['str', 'str']]
    active_tool_bundle: ToolBundleEnum
    tool_bundle_results: dict[ToolBundleEnum, dict['str', 'str']]
    model_response: str


class WorkflowAgent(BaseAgent):
    def __init__(self, 
            api_key: str,
            base_url: str,
            model_name: str,
            system_prompt: str,
            tool_bundles: dict[ToolBundleEnum, ToolBundle],
            agent_name: str = 'OneStepLLMAgent'
        ):
        super().__init__(agent_name)
        self._client = OpenAI(api_key=api_key, base_url=base_url)
        self._system_prompt = system_prompt
        self._tool_bundles = tool_bundles
        self._model_name = model_name
        
        self._graph = self._build_graph()
        self._current_state: WorkflowState = {
            "history": [
                {"role": "system", "content": self._system_prompt},
            ],
            "active_tool_bundle": None,
            "tool_bundle_results": {},
            "model_response": ""
        }

    def _build_graph(self) -> StateGraph:
        graph = StateGraph(WorkflowState)
        graph.add_node('select_tool_bundle', self._select_tool_bundle)
        graph.add_node('execute_tool_bundle', self._execute_tool_bundle)
        graph.add_node('invoke_llm', self._invoke_llm)
        
        graph.add_edge(START, 'select_tool_bundle')
        graph.add_edge('select_tool_bundle', 'execute_tool_bundle')
        graph.add_edge('execute_tool_bundle', 'invoke_llm')
        graph.add_edge('invoke_llm', END)
        return graph
        
    
    def _select_tool_bundle(self, state: WorkflowState) -> None:
        pass

    
    def _execute_tool_bundle(self, state: WorkflowState) -> None:
        pass
        
    def _invoke_llm(self, state: WorkflowState) -> None:
        pass    
        
        
    def handle_message(self, message: UserMessage) -> str:
        self._current_state["history"].append({"role": "user", "content": message})
        self._graph.run(self._current_state)
        return self._current_state["model_response"]