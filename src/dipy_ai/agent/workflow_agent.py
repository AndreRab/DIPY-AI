from dipy_ai.agent.base_agent import BaseAgent, UserMessage
from dipy_ai.tools import ToolBundleEnum, ToolBundle, build_tool_selection_schema
from langgraph.graph import StateGraph, START, END
from concurrent.futures import ThreadPoolExecutor
from typing import Any, TypedDict
from openai import OpenAI
import logging
import json
from dataclasses import asdict, is_dataclass
from enum import Enum


def _json_default(value: Any) -> Any:
    if is_dataclass(value) and not isinstance(value, type):
        return asdict(value)
    if isinstance(value, Enum):
        return value.value
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")


class WorkflowState(TypedDict):
    history: list[dict[str, str]]
    active_tool_bundle: ToolBundleEnum | None
    tool_bundle_results: dict[str, Any] | None
    model_response: str


class WorkflowAgent(BaseAgent):
    def __init__(self, 
            api_key: str,
            base_url: str,
            model_name: str,
            system_prompt_final_answer: str,
            system_prompt_tool_selection: str,
            tool_bundles: dict[ToolBundleEnum, ToolBundle],
            agent_name: str = "WorkflowAgent",
            logger: logging.Logger | None = None,
            use_logger: bool = False,
        ):
        super().__init__(agent_name)
        if use_logger and logger is None:
            raise ValueError("logger must be provided when use_logger is True")
        self._logger = logger if use_logger else None
        self._client = OpenAI(api_key=api_key, base_url=base_url)
        self._system_prompt_final_answer = system_prompt_final_answer
        self._system_prompt_tool_selection = system_prompt_tool_selection
        self._tool_bundles = tool_bundles
        self._model_name = model_name
        
        self._graph = self._build_graph()
        self._current_state: WorkflowState = {
            "history": [
                {"role": "system", "content": self._system_prompt_final_answer},
            ],
            "active_tool_bundle": None,
            "tool_bundle_results": {},
            "model_response": ""
        }
        
    def _build_graph(self):
        graph = StateGraph(WorkflowState)
        graph.add_node('select_tool_bundle', self._select_tool_bundle)
        graph.add_node('execute_tool_bundle', self._execute_tool_bundle)
        graph.add_node('invoke_llm', self._invoke_llm)
        
        graph.add_edge(START, 'select_tool_bundle')
        graph.add_edge('select_tool_bundle', 'execute_tool_bundle')
        graph.add_edge('execute_tool_bundle', 'invoke_llm')
        graph.add_edge('invoke_llm', END)
        
        return graph.compile()

    def _select_tool_bundle(self, state: WorkflowState) -> dict:
        allowed_values = [
            bundle.value
            for bundle in self._tool_bundles
        ]

        bundle_descriptions = "\n".join(
            f"- {bundle.value}: {self._tool_bundles[bundle].description}"
            for bundle in self._tool_bundles
        )

        system_prompt = self._system_prompt_tool_selection.format(
            tool_bundles=bundle_descriptions
        )

        last_message = state["history"][-1]["content"]

        response = self._client.chat.completions.create(
            model=self._model_name,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": last_message,
                },
            ],
            response_format=build_tool_selection_schema(
                allowed_values
            ),
        )

        content = response.choices[0].message.content
        selected_value = json.loads(content)["bundle"]

        selected_bundle = next(
            bundle
            for bundle in self._tool_bundles
            if bundle.value == selected_value
        )
        if self._logger is not None:
            self._logger.info("Selected tool bundle: %s", selected_bundle.value)

        return {"active_tool_bundle": selected_bundle}

    def _execute_tool_bundle(self, state: WorkflowState) -> dict:
        selected_bundle = state["active_tool_bundle"]
        if selected_bundle is None:
            return {"tool_bundle_results": None}
        bundle = self._tool_bundles.get(selected_bundle)
        if self._logger is not None:
            self._logger.info(
                "Executing tool bundle %s with tools: %s",
                selected_bundle.value,
                [tool.name for tool in bundle.tools],
            )
        with ThreadPoolExecutor(max_workers=max(1, len(bundle.tools))) as executor:
            futures = {
                tool.name: executor.submit(tool.execute, n=10)
                for tool in bundle.tools
            }
            results = {
                tool_name: future.result()
                for tool_name, future in futures.items()
            }
        if self._logger is not None:
            self._logger.info("Tool bundle %s completed", selected_bundle.value)
        return {"tool_bundle_results": results}

    def _invoke_llm(self, state: WorkflowState) -> dict:
        results = state["tool_bundle_results"]
        messages = list(state["history"])

        if results is not None:
            messages.append(
                {
                    "role": "system",
                    "content": "Workflow tool results (JSON):\n" + json.dumps(
                        results,
                        default=_json_default,
                        ensure_ascii=False,
                        allow_nan=False,
                        indent=2,
                    ),
                }
            )
        
        if self._logger is not None:
            self._logger.info(messages[-1]["content"])  
            
        response = self._client.chat.completions.create(
            model=self._model_name,
            messages=messages,
        )

        return {
            "model_response": response.choices[0].message.content
        }

    def handle_message(self, message: UserMessage) -> str:
        if self._logger is not None:
            self._logger.info("Handling user message")
        self._current_state["history"].append({"role": "user", "content": message.message})
        self._current_state = self._graph.invoke(self._current_state)
        self._current_state["history"].append({"role": "assistant", "content": self._current_state["model_response"]})
        if self._logger is not None:
            self._logger.info("Workflow response generated")
        return self._current_state["model_response"]