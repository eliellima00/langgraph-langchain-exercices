from typing_extensions import TypedDict
from langchain_core.messages import AnyMessage, AIMessage, HumanMessage
from langgraph.graph import StateGraph, START, END



class MessagesState(TypedDict):
  messages: list[AnyMessage]


def my_chat_node(state: MessagesState):
    messages = state["messages"] + [
        AIMessage(
            content="O céu é azul. O que mais você deseja saber sobre o céu?",
            name="model"
        )
    ]

    return {
        "messages": messages
    }
    
builder = StateGraph(MessagesState)

builder.add_node("my_chat_node", my_chat_node)

builder.add_edge(START, "my_chat_node")
builder.add_edge("my_chat_node", END)

graph = builder.compile()

# Gerar Imagem do Grafo
img_bytes = graph.get_graph().draw_mermaid_png()

with open("3-chat-model.png", 'wb') as f:
  f.write(img_bytes)


# Estado Inicial
initial_messages = [
    AIMessage(content="Olá user, tudo bem. Em que posso ajudar hoje?", name="model"),
    HumanMessage(content="O céu é?", name="user")
]

result = graph.invoke({"messages": initial_messages})

print(result)





