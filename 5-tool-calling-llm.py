from langchain_core.messages import   HumanMessage
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
load_dotenv()

llm = ChatOpenAI(model="gpt-4o")

class MessagesState(MessagesState):
  pass

def client_data_tool(name: str):
  """Used to find data from specified user
  
  Args:
      name: client name string
  """
  return f"Returning data from client: {name}"

llm_with_tools = llm.bind_tools([client_data_tool])

def tool_calling_llm(state: MessagesState):
   return {"messages": [llm_with_tools.invoke(state["messages"])]}
    
builder = StateGraph(MessagesState)

builder.add_node("tool_calling_llm", tool_calling_llm)
builder.add_node("tools", ToolNode([client_data_tool]))

builder.add_edge(START, "tool_calling_llm")
builder.add_conditional_edges(
  "tool_calling_llm",
  #Se a ultima mensagem (result) do llm é uma chamada de tool -> tools_condition roteia para tools
  #Se a ultima mensagem (result) do llm não for uma chamada de tool -> tools_condition roteia para END
  tools_condition
)
builder.add_edge("tools", END)

graph = builder.compile()

# Gerar Imagem do Grafo
img_bytes = graph.get_graph().draw_mermaid_png()

with open("5-tool-calling-llm.png", 'wb') as f:
  f.write(img_bytes)


result = graph.invoke({"messages": HumanMessage(content="Eliel")})

print(result)





