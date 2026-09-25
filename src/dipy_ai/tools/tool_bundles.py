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



def generate_tool_bundles_from_simulator(simulator: BaseSimulator) -> dict[ToolBundleEnum, ToolBundle]:
    """Generate a dictionary of tool bundles."""
    return {
        ToolBundleEnum.CURRENT_SITUATION: ToolBundle(
            name = ToolBundleEnum.CURRENT_SITUATION,
            description = "Current situation analysis",
            tools = [
                CurrentStateTool(simulator=simulator),
                AnomalyTool(simulator=simulator),
            ]
        ),
        ToolBundleEnum.ANOMALY_ANALYSIS: ToolBundle(
            name = ToolBundleEnum.ANOMALY_ANALYSIS,
            description = "Anomaly analysis",
            tools = [
                CurrentStateTool(simulator=simulator),
                AnomalyTool(simulator=simulator),
                HistoryTool(simulator=simulator),
                RAGTool(),
            ]
        ),
        ToolBundleEnum.ROOT_CAUSE: ToolBundle(
            name = ToolBundleEnum.ROOT_CAUSE,
            description = "Root cause analysis",
            tools = [
                CurrentStateTool(simulator=simulator),
                AnomalyTool(simulator=simulator),
                HistoryTool(simulator=simulator),
                RAGTool(),
                MachineContextTool()
            ]
        ),
        ToolBundleEnum.HISTORICAL_COMPARISON: ToolBundle(
            name = ToolBundleEnum.HISTORICAL_COMPARISON,
            description = "Historical comparison",
            tools = [
                CurrentStateTool(simulator=simulator),
                HistoryTool(simulator=simulator),
            ]
        ),
        ToolBundleEnum.DOMAIN_QA: ToolBundle(
            name = ToolBundleEnum.DOMAIN_QA,
            description = "Domain-specific questions and answers",
            tools = [
                RAGTool(),
                MachineContextTool()
            ]
        ),
        ToolBundleEnum.RECOMMENDATION: ToolBundle(
            name = ToolBundleEnum.RECOMMENDATION,
            description = "Recommendations",
            tools = [
                CurrentStateTool(simulator=simulator),
                AnomalyTool(simulator=simulator),
                HistoryTool(simulator=simulator),
                RAGTool(),
                MachineContextTool()
            ]
        )
    }