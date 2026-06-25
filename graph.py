from typing import Annotated, Sequence
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import START, StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from tools import PROVIDABLE_TOOLS

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]

llm = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite")
llm_with_tools = llm.bind_tools(PROVIDABLE_TOOLS)

def call_agent(state: AgentState):
    messages = state["messages"]
    system_template = (
    "You are a strict GSB Cookbook AI. Follow these rules:\n\n"
    
    "1. General queries: Use ONLY `search_cookbook_recipes` with just the dish name. "
    "Provide text info and ingredients with measurements. Do not include calories.\n\n"
    
    "2. Calorie queries: Call `search_cookbook_recipes` using ONLY the dish name to find the recipe text. "
    "Extract ingredients and weights. Before calling `get_calorie_details`, translate regional terms "
    "to standard global terms to avoid database errors (e.g., convert 'poha/beaten rice' to 'flattened rice', "
    "'cooking soda' to 'baking soda', 'jaggery' to 'brown sugar' or 'cane sugar').\n\n"
    
    "3. Verification & Safety: Check tool outputs against common sense. If a tool claims a dry spice has "
    "over 900 kcal/100g (like a turmeric glitch), ignore that specific tool calorie count and use a standard "
    "spice estimate (~300 kcal/100g) or skip it.\n\n"
    
    "4. Handling Failures: If some ingredients return completely mismatched or corrupt data, do not say "
    "'I don't know' for the whole recipe. Instead, calculate the total using the valid data, list the items "
    "you successfully calculated, and explicitly warn the user about which items were excluded due to missing data.")


    has_system = any(isinstance(m, SystemMessage) for m in messages)
    active_messages = [SystemMessage(content=system_template)] + list(messages) if not has_system else list(messages)
    
    response = llm_with_tools.invoke(active_messages)
    return {"messages": [response]}

def should_continue(state: AgentState):
    last_message = state["messages"][-1]
    return "tools" if last_message.tool_calls else END

# Construct the state-driven application routing workflow
workflow = StateGraph(AgentState)
workflow.add_node("agent", call_agent)
workflow.add_node("tools", ToolNode(PROVIDABLE_TOOLS))

workflow.add_edge(START, "agent")
workflow.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
workflow.add_edge("tools", "agent")
