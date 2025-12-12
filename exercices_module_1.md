# Exercícios — Módulo 1 (LangGraph / LangChain basics)

Este material contém exercícios para reforçar e masterizar os conceitos que você viu no módulo 1. Todas as questões usam apenas os tópicos deste módulo: estado do grafo, `TypedDict`, nodes, edges (normais e condicionais), `START`/`END`, messages/chat state, chat models & tool binding, agents (ReAct), memória (checkpointer/MemorySaver), ToolNode, e conceitos de Studio/Deployment.

A cada exercício há: objetivo, enunciado, dicas (hint) e a solução (resposta) — faça os exercícios antes de ver a solução.

---

## Sumário rápido dos tópicos do módulo 1

- Estados do grafo via TypedDict (`State`, `MessagesState`, etc.)
- Nodes: funções Python que recebem um estado e retornam o novo estado
- Reducers: como os nodes atualizam o estado
- Edges: conexões entre nodes (normais e condicionais)
- Condicional edges: funções que decidem o próximo node
- START e END nodes e o método `invoke` do grafo
- Mensagens (`HumanMessage`, `AIMessage`, `SystemMessage`) como estado
- Chat models (p.ex. `ChatOpenAI`) e binding de ferramentas (tools)
- Tool calling e `ToolNode` / `tools_condition`
- Agentes (ReAct): act → observe → reason (loop com retorno ao assistant)
- Memória (checkpointer), `MemorySaver`, thread ids
- Studio / Deployment: conceitos de testar local via Studio e deploy no cloud

---

## Nível Fácil

### Exercício 1 — Graph simples com 3 nodes

Objetivo: construir um grafo simples com 3 nodes.

Enunciado:

- Defina um `TypedDict` chamado `State` com chave `message: str`.
- Crie três nodes: `start_node` que anexa "start", `middle_node` que anexa " -> middle", e `end_node` que anexa " -> end" ao valor de `message`.
- Construa um `StateGraph` com `START -> start_node -> middle_node -> end_node -> END`.
- Execute `invoke` com `{"message": "Hello"}` e escreva o resultado.

Hint:

- Use `builder.add_node(...)`, `add_edge(...)`, `compile()` e `graph.invoke(...)`.

Solução:

```python
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END

class State(TypedDict):
    message: str

def start_node(state):
    return {"message": state["message"] + " start"}

def middle_node(state):
    return {"message": state["message"] + " -> middle"}

def end_node(state):
    return {"message": state["message"] + " -> end"}

builder = StateGraph(State)
builder.add_node("start_node", start_node)
builder.add_node("middle_node", middle_node)
builder.add_node("end_node", end_node)
builder.add_edge(START, "start_node")
builder.add_edge("start_node", "middle_node")
builder.add_edge("middle_node", "end_node")
builder.add_edge("end_node", END)

graph = builder.compile()
res = graph.invoke({"message": "Hello"})
print(res)  # Esperado: { 'message': 'Hello start -> middle -> end' }
```

---

### Exercício 2 — Edge condicional determinística

Objetivo: criar uma conditional edge que escolhe o caminho baseado em uma palavra-chave no `message`.

Enunciado:

- Use o `State` do exercício anterior (`message: str`).
- Adicione um node `decision_node` que examina `message` e retorna `node_A` se a string contiver a substring "A", senão `node_B`.
- Implementar `node_A` e `node_B` que anexem " -> A" e " -> B" respectivamente.
- Execute com ambos os inputs e mostre os outputs.

Hint:

- Conditionally add edges com `builder.add_conditional_edges("decision_node", decide_fn)` onde `decide_fn` retorna o nome do próximo node.

Solução (resumida):

```python
def decide(state):
    if "A" in state["message"]:
        return "node_A"
    return "node_B"

# adicionar nodes e condicional entre decision_node -> (node_A | node_B)
```

---

## Nível Intermediário

### Exercício 3 — Usando mensagens como estado e invocando um ChatModel (simulado)

Objetivo: trabalhar com `MessagesState` e simular a execução de um chat model.

Enunciado:

- Crie `MessagesState` com `messages: list[AnyMessage]` (ou importe `MessagesState` na biblioteca).
- Crie um node `my_chat_node(state)` que monta uma resposta do modelo simulada: sempre retorne um `AIMessage` com content = "Simulado: " + último `HumanMessage` content.
- Compile um graph com START -> my_chat_node -> END e invoque com `HumanMessage(content="Qual é a capital do Brasil?")`.

Hint:

- Em vez de usar ChatOpenAI (que exige API), implemente a lógica diretamente retornando objetos do tipo `AIMessage`.

Solução (resumida):

```python
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import MessagesState

def my_chat_node(state: MessagesState):
    last_human = [m for m in state["messages"] if isinstance(m, HumanMessage)][-1]
    return {"messages": [AIMessage(content="Simulado: " + last_human.content)]}
```

---

### Exercício 4 — Ferramenta simples e ToolNode

Objetivo: entender binding de ferramentas e `ToolNode`.

Enunciado:

- Implemente uma função `double(n: int) -> int` que retorna 2\*n.
- Crie um `ToolNode` que seja inicializado com `[double]`.
- Crie um node que chama um chat model simulado que retorne um `ToolMessage` com `name='double'` e `arguments='{"n": 5}` (note que estamos simulando o comportamento).
- Faça o fluxo: START -> chat_node -> tools -> END.
- Explique o que acontece quando o chat produz um `ToolMessage` com `name='double'`.

Hint:

- `ToolNode` chamará a função `double` com os argumentos decodificados do JSON em `ToolMessage.arguments` e retornará uma `ToolMessage` com o resultado transformado em `ToolMessage` output.

Solução (conceitual):

- Chat produz ToolMessage; `ToolNode` executa `double(5)` -> 10; então as mensagens resultantes incluirão a saída da ferramenta.

---

## Nível Avançado / Mastery

### Exercício 5 — Agente ReAct: loop até saída natural

Objetivo: montar um grafo que reenviará o resultado para o `assistant` até que a resposta não seja um `ToolMessage`.

Enunciado:

- Simule um `assistant` node que alterna: quando recebe um `HumanMessage` do tipo "compute: SUM 1 2 3" ele deve retornar um `ToolMessage` chamando `sum_tool` com `arguments` contendo a lista; caso contrário, ele responde com `AIMessage`.
- Crie `ToolNode([sum_tool])`, e conecte `assistant` -> `tools` (conditional) -> `assistant` loop (como no notebook do agente). O loop se encerra quando `assistant` produz uma resposta que não é `ToolMessage`.
- Teste com o fluxo: "compute: SUM 1 2 3" e depois uma pergunta final para encerrar.

Hint:

- Use a `tools_condition` prebuilt ou reimplemente a função condicional que verifica se a última mensagem é um `ToolMessage`.
- Você pode simular `sum_tool` com uma função Python normal.

Solução (resumida):

- `assistant` retorna ToolMessage indicando sum call
- `ToolNode` executa sum, escreve resultado como mensagem
- `assistant` agora vê resultado e responde com `AIMessage` com o resultado final — terminando o loop.

---

### Exercício 6 — Persistência: preservar estado entre invocações

Objetivo: usar `MemorySaver` (checkpointer) para simular memória entre execuções.

Enunciado:

- Compile um graph e use `MemorySaver()` como checkpointer: `graph = builder.compile(checkpointer=memory)`.
- Execute o grafo com `thread_id='alice'` para adicionar um valor no estado (ex: lembrete: 7).
- Em seguida, execute outro invoke usando a mesma `thread_id='alice'` com uma pergunta que depende do valor salvo.
- Explique por que a versão sem checkpointer perde o valor e a versão com `MemorySaver` preserva.

Hint:

- Veja `agent-memory.ipynb` — o checkpointer salva o estado por `thread_id` entre runs; sem ele, cada invoke começa do estado fornecido apenas naquele run.

Solução (conceitual):

- Usando `MemorySaver`, o grafo escreve o estado em memória a cada passo; chamadas subsequentes que usam o mesmo `thread_id` reconstroem o ultimo estado e continuam.

---

### Exercício 7 — Debugging: reducer sobrescrevendo (merge vs override)

Objetivo: investigar e corrigir um caso onde dois nodes querem atualizar o mesmo campo sem perder dados.

Enunciado:

- Suponha um `State` com `chat_history: str`. Dois nodes `a` e `b` são executados em sequência e ambos retornam `{"chat_history": state["chat_history"] + "X"}`. Mas se o segundo node retornar apenas `{"chat_history": "Y"}` sem usar o valor anterior, o histórico será perdido.
- Explique o comportamento padrão de sobrescrita e demonstre duas estratégias para preservar os dados:
  1. Node `b` usa o valor já em `state` para concatenar;
  2. Usar um reducer customizado (ou lógica no node) que mescle campos.

Hint:

- O comportamento padrão no módulo é que o valor retornado pelo node sobreescreve o valor do estado anterior. Para mesclar, sempre leia `state['chat_history']` antes de gerar a nova string.

Solução (resumida):

- Certifique-se de que o node sempre retorne algo como `{"chat_history": state['chat_history'] + '...new...'}`.

---

### Exercício 8 — Conceito: deploy & studio (escreva os passos)

Objetivo: relembrar (teórico) as etapas básicas para rodar localmente no Studio e publicar uma implantação no LangSmith Cloud.

Enunciado:

- Liste os comandos e passos para: (1) rodar o servidor local do Studio (LangGraph Studio), (2) encontrar e carregar o `langgraph.json` de `module-1/studio`, (3) conectar um repositório GitHub e fazer deploy no LangSmith Cloud.

Hint:

- Veja `deployment.ipynb` — procure `langgraph dev`, `get_client(url=...)` e as instruções de deploy.

Solução (resumida):

1. cd module-1/studio; `langgraph dev` para rodar local. 2) Abrir Studio UI no URL exibido e carregar a configuração apontando para `module-1/studio/langgraph.json`. 3) No LangSmith, adicionar novo deployment apontando para o repo/GitHub e a localização do langgraph config; fornecer variáveis de ambiente (ex.: API keys).

---

## Dicas de prática (💡)

- Exercite implementando cada grafo em um Notebook separado e invocando com diferentes inputs.
- Ao trabalhar com tools, comece simulando ToolMessages e implementando `ToolNode` com funções locais para evitar fazer chamadas para APIs reais enquanto treina.
- Para agente ReAct, faça pequenos exercícios: primeiro faça um agente que chama somente 1 ferramenta; depois aumente para uma sequência de ferramentas com loop.

---

## Como usar este arquivo

- Faça os exercícios em ordem, vá do simples para o avançado.
- Tente responder sem olhar as soluções — verifique a solução apenas quando precisar.
- Se quiser, posso transformar esses exercícios em um Jupyter Notebook com células interativas (perguntas em markdown + soluções em células de código) — quer que eu gere o notebook também?

---

Se quiser, eu já crio também a versão em Notebook (`module-1/exercises.ipynb`) para você executar interativamente. Quer que eu crie o notebook agora? :rocket:
