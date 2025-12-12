from langchain_core.messages import   HumanMessage
from langgraph.graph import StateGraph, MessagesState, START, END
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
load_dotenv()

llm = ChatOpenAI(model="gpt-4o")

class MessagesState(MessagesState):
  pass

def calling_llm(state: MessagesState):
   return {"messages": [llm.invoke(state["messages"])]}
    
builder = StateGraph(MessagesState)

builder.add_node("calling_llm", calling_llm)

builder.add_edge(START, "calling_llm")
builder.add_edge("calling_llm", END)

graph = builder.compile()

# Gerar Imagem do Grafo
img_bytes = graph.get_graph().draw_mermaid_png()

with open("4-call-llm.png", 'wb') as f:
  f.write(img_bytes)


result = graph.invoke({"messages": HumanMessage(content="Hello!")})

print(result)





