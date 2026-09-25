from dataclasses import dataclass
from enum import Enum
from dipy_ai.simulation import BaseSimulator
from dipy_ai.tools.base_tool import BaseTool
from dipy_ai.tools.anomaly_tool import AnomalyTool
from dipy_ai.tools.current_state_tool import CurrentStateTool
from dipy_ai.tools.history_tool import HistoryTool
from dipy_ai.tools.machine_context_tool import MachineContextTool
from dipy_ai.tools.rag_tool import RAGTool


class ToolBundleEnum(Enum):
    """Docstring for ToolBundles."""
    CURRENT_SITUATION = "current_situation"
    ANOMALY_ANALYSIS = "anomaly_analysis"
    ROOT_CAUSE = "root_cause_analysis"
    HISTORICAL_COMPARISON = "historical_comparison"
    DOMAIN_QA = "domain_qa"
    RECOMMENDATION = "recommendation"
    
    
@dataclass(frozen=True)
class ToolBundle:
    name: ToolBundleEnum
    description: str
    tools: list[BaseTool]



def generate_tool_bundles_from_simulator(
    simulator: BaseSimulator
) -> dict[ToolBundleEnum, ToolBundle]:

    return {
        ToolBundleEnum.CURRENT_SITUATION: ToolBundle(
            name=ToolBundleEnum.CURRENT_SITUATION,
            description=(
                "Use when the user asks about the current machine or process state, "
                "including current measurements, operating conditions, active anomalies, "
                "or whether anything unusual is happening right now."
            ),
            tools=[
                CurrentStateTool(simulator=simulator),
                AnomalyTool(simulator=simulator),
            ]
        ),

        ToolBundleEnum.ANOMALY_ANALYSIS: ToolBundle(
            name=ToolBundleEnum.ANOMALY_ANALYSIS,
            description=(
                "Use when the user asks to analyze or explain a detected anomaly, "
                "including its meaning, severity, behavior, possible impact, or how it "
                "relates to recent process history and domain knowledge."
            ),
            tools=[
                CurrentStateTool(simulator=simulator),
                AnomalyTool(simulator=simulator),
                HistoryTool(simulator=simulator),
                RAGTool(),
            ]
        ),

        ToolBundleEnum.ROOT_CAUSE: ToolBundle(
            name=ToolBundleEnum.ROOT_CAUSE,
            description=(
                "Use when the user asks why a problem or anomaly occurred, what may have "
                "caused it, or requests identification of possible root causes based on "
                "current state, anomaly data, process history, machine context, and "
                "domain knowledge."
            ),
            tools=[
                CurrentStateTool(simulator=simulator),
                AnomalyTool(simulator=simulator),
                HistoryTool(simulator=simulator),
                RAGTool(),
                MachineContextTool(),
            ]
        ),

        ToolBundleEnum.HISTORICAL_COMPARISON: ToolBundle(
            name=ToolBundleEnum.HISTORICAL_COMPARISON,
            description=(
                "Use when the user asks to compare the current process state with past "
                "states, layers, builds, runs, or events, or asks whether the current "
                "behavior has happened before."
            ),
            tools=[
                CurrentStateTool(simulator=simulator),
                HistoryTool(simulator=simulator),
            ]
        ),

        ToolBundleEnum.DOMAIN_QA: ToolBundle(
            name=ToolBundleEnum.DOMAIN_QA,
            description=(
                "Use for general domain-specific questions about the manufacturing "
                "process, machine, materials, parameters, procedures, terminology, "
                "manuals, or documented process knowledge that do not primarily require "
                "analysis of the current process state."
            ),
            tools=[
                RAGTool(),
                MachineContextTool(),
            ]
        ),

        ToolBundleEnum.RECOMMENDATION: ToolBundle(
            name=ToolBundleEnum.RECOMMENDATION,
            description=(
                "Use when the user asks what should be done next, what action should be "
                "taken, what should be checked, or how to respond to the current machine "
                "state, anomaly, or process problem."
            ),
            tools=[
                CurrentStateTool(simulator=simulator),
                AnomalyTool(simulator=simulator),
                HistoryTool(simulator=simulator),
                RAGTool(),
                MachineContextTool(),
            ]
        ),
    }
    
def build_tool_selection_schema(allowed_values: list[str]) -> dict:
    return {
        "type": "json_schema",
        "json_schema": {
            "name": "tool_bundle_selection",
            "strict": True,
            "schema": {
                "type": "object",
                "properties": {
                    "bundle": {
                        "type": "string",
                        "enum": allowed_values,
                    }
                },
                "required": ["bundle"],
                "additionalProperties": False,
            },
        },
    }