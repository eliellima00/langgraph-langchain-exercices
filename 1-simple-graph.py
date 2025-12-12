from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END

class state(TypedDict):
  message: str

def start_node(state:state):
  print("---Start Node---")
  return {"message": state['message'] + "Start->"}

def middle_node(state:state):
  print("---Middle Node---")
  return {"message": state['message'] + "Middle->"}

def end_node(state:state):
  print("---End Node---")
  return {"message": state['message'] + "End"}

#build graph
builder = StateGraph(state)
builder.add_node("start_node", start_node)
builder.add_node("middle_node", middle_node)
builder.add_node("end_node", end_node)

#graph router
builder.add_edge(START, "start_node")
builder.add_edge("start_node", "middle_node")
builder.add_edge("middle_node", "end_node")
builder.add_edge("end_node", END)

graph = builder.compile()

img_bytes = graph.get_graph().draw_mermaid_png()
with open("1-simple-graph.png", 'wb') as f:
  f.write(img_bytes)
  
result = graph.invoke({"message": "This is the graph:"})

print(result)


