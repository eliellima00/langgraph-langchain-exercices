from typing_extensions import TypedDict
from typing import Literal
from langgraph.graph import StateGraph, START, END

class state(TypedDict):
  message: str

def start_node(state: state):
  print("---Start Node---")
  return {"message": state['message'] + "Start"}

def node_A(state:state):
  print("---Node A---")
  return {"message": state['message'] + "-> Node A"}

def node_B(state: state):
  print("---Node B---")
  return {"message": state['message'] + "-> Node B"}


def decide_fn(state):
    if "A" in state["message"]:
        return "node_A"
    return "node_B"

builder = StateGraph(state)
builder.add_node("start_node", start_node)
builder.add_node("node_A", node_A)
builder.add_node("node_B", node_B)

# Logic
builder.add_edge(START, "start_node")

builder.add_conditional_edges("start_node", decide_fn, {
   "node_A": "node_A",
   "node_B": "node_B"
})

builder.add_edge("node_A", END)
builder.add_edge("node_B", END)

graph = builder.compile()

img_bytes = graph.get_graph().draw_mermaid_png()

with open("2-conditional-graph.png", 'wb') as f:
  f.write(img_bytes)

result = graph.invoke({"message": "go to B: "})

print(result)