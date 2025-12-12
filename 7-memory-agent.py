from langchain_core.messages import   HumanMessage, SystemMessage
from langgraph.graph import StateGraph, MessagesState, START
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
load_dotenv()

llm = ChatOpenAI(model="gpt-4o")

class MessagesState(MessagesState):
  pass

def client_data_tool(name: str):
  """Usado para buscar todos os dados do perfil do cliente"""
  return {
    "cliente": name,
    "dados": {
      "email": "eliel@example.com",
      "idade": 25,
      "pais": "Brazil"
    }
  }

def client_farm_tool(name: str):
  """Usado para buscar todos os dados das fazendas do cliente"""
  return {
    "cliente": name,
    "propriedades": ["Fazenda Toca da Onça", "Fazenda Serra Bonita"]
  }

def client_products_tool(name: str):
    """Usado para buscar todos os produtos comprados pelo cliente"""
    return {
        "cliente": name,
        "produtos": [
            {"nome": "Soja", "preco": 5000},
            {"nome": "Milho", "preco": 300},
        ]
    }
    
def sum_values_tool(values: list[int]):
  """Usado para somar uma lista de valores"""
  
  return sum(values)

tools = [client_data_tool, client_farm_tool, client_products_tool, sum_values_tool]
llm_with_tools = llm.bind_tools(tools)

SYSTEM_PROMPT = """
Você é um assistente que faz a gestão de dados de clientes e que usa todas as ferramentas disponíveis para trazer os dados solicitados.

Você irá responder apenas com os dados especificados nas tools. Caso seja solicitado alguma informação que você não tenha. Responda com:
"Essa informação não esta disponível na nossa base de dados".

Posso reponder sobre os seguintes itens: *Coloque aqui todos os itens disponiveis para o cliente*
"""
sys_msg = SystemMessage(content=SYSTEM_PROMPT)

#node
def assistant(state: MessagesState):
   return {"messages": [llm_with_tools.invoke(state["messages"])]}
    
builder = StateGraph(MessagesState)

builder.add_node("assistant", assistant)
builder.add_node("tools", ToolNode(tools))

builder.add_edge(START, "assistant")
builder.add_conditional_edges(
  "assistant",
    # If the latest message (result) from assistant is a tool call -> tools_condition routes to tools
    # If the latest message (1result) from assistant is a not a tool call -> tools_condition routes to END
  tools_condition
)
builder.add_edge("tools", "assistant")

memory = MemorySaver()
graph = builder.compile(checkpointer=memory)
config = {"configurable": {"thread_id": "1"}}

# Gerar Imagem do Grafo
img_bytes = graph.get_graph().draw_mermaid_png()

with open("7-memory-agent.png", 'wb') as f:
  f.write(img_bytes)

result1 = graph.invoke(
    {"messages": [sys_msg, HumanMessage(content="Me traga todos os dados do perfil cliente Eliel")]}, 
    config
)

for m in result1['messages']:
  m.pretty_print()

result2 = graph.invoke(
    {"messages": [HumanMessage(content="Agora me diga quais produtos ele comprou")]},
    config
)

for m in result2['messages']:
  m.pretty_print()






