import streamlit as st
from langgraph.checkpoint.memory import MemorySaver
from graph import workflow

st.set_page_config(page_title="GSB Food AI Assistant", page_icon="🍔", layout="centered")
st.title("🍔 GSB Food AI Assistant")

if "graph_app" not in st.session_state:
    checkpointer = MemorySaver()
    st.session_state.graph_app = workflow.compile(checkpointer=checkpointer)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

app = st.session_state.graph_app

for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if user_query := st.chat_input("Ask about cooking recipes or nutritional values..."):
    with st.chat_message("user"):
        st.markdown(user_query)
    st.session_state.chat_history.append({"role": "user", "content": user_query})

    with st.chat_message("assistant"):
        status_placeholder = st.empty()
        response_placeholder = st.empty()
        final_text = ""
        
        config = {"configurable": {"thread_id": "production_user_session"}}
        inputs = {"messages": [("user", user_query)]}
        
        # Safe state update stream loop execution blocks
        for update in app.stream(inputs, config=config, stream_mode="updates"):
            for node, value in update.items():
                print("Node", node)
                print("Value", value)
                

                if node == "agent":
                    last_msg = value["messages"][-1]
                    
                    if last_msg.tool_calls:
                        tool_call = last_msg.tool_calls[0]
                        tool_name = tool_call["name"]
                        tool_args = tool_call["args"]
                        
                        if tool_name == "search_cookbook_recipes":
                            term = tool_args.get("query", "recipes")
                            status_placeholder.markdown(f"🔍 *Searching local cookbook vector store for:* **{term}**")
                        elif tool_name == "get_calorie_details":
                            term = tool_args.get("food_item", "ingredient")
                            status_placeholder.markdown(f"🍎 *Querying live USDA Data Registry for:* **{term}**")
                            
                    elif last_msg.content:
                        if isinstance(last_msg.content,list) and len(last_msg.content) > 0:
                            final_text = last_msg.content[0].get('text', '')
                        else:
                            final_text = last_msg.content    
                        response_placeholder.markdown(final_text)
                        
        status_placeholder.empty()
        if final_text:
            st.session_state.chat_history.append({"role": "assistant", "content": final_text})
        st.rerun()
