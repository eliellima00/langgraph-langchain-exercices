# Exercícios — LangGraph / LangChain

Bem-vindo aos exercícios do Módulo 1 — aqui você encontrará pequenos scripts que exploram conceitos básicos de grafos de estado, nodes/edges (incluindo condicionais), estado de mensagens para chat models, chamadas a LLMs e ToolNodes.

Este repositório é ideal para estudos e testes rápidos: cada script contém um exemplo simples com a ilustração do grafo (PNG gerado automaticamente) e uma chamada/execução demonstrativa.

## Estrutura do repositório

- `1-simple-graph.py` — Exemplo básico de StateGraph com 3 nodes e fluxo linear (START → start_node → middle_node → end_node → END). Gera `1-simple-graph.png`.
- `2-conditional-graph.py` — Exemplo de edge condicional: um node decide qual caminho seguir (node_A ou node_B) de acordo com o conteúdo do estado. Gera `2-conditional-graph.png`.
- `3-chat-model-simulated.py` — Simulação de ChatModel: usa `MessagesState` e `HumanMessage`/`AIMessage` para simular troca de mensagens e compor resposta. Gera `3-chat-model.png`.
- `4-call-llm.py` — Chamada real a um chat model (ChatOpenAI) com `langchain_openai`. Requer variáveis de ambiente (ver `.env.example`) para habilitar chamadas à API. Gera `4-call-llm.png`.
- `5-tool-calling-llm.py` — Exemplo de binding de ferramentas (tool binding): demonstra `ToolNode`, `tools_condition` e como um model pode emitir chamada de ferramenta e o grafo executar a ferramenta. Requer variáveis de ambiente para LLM. Gera `5-tool-calling-llm.png`.
- `6-reative-agent.py` — Agente ReAct com múltiplas ferramentas. Demonstra um loop agente → ferramenta → agente até que o agente retorne uma resposta final. Gera `6-reative-agent.png`.
- `7-memory-agent.py` — Demonstra persistência de estado entre invocações usando `MemorySaver` (checkpointer). Mostra como reusar `thread_id` para recuperar o estado anterior. Gera `7-memory-agent.png`.
- `.env.example` — Exemplo de variáveis de ambiente (copie para `.env` e preencha).
- `requirements.txt` — Lista de dependências usadas nos exemplos.

## Conceitos abordados

- StateGraph, nodes e reducers (funções que recebem e retornam o estado)
- START e END nodes e o método `graph.invoke` para executar o grafo
- Edges comuns e condicional edges (usando `add_conditional_edges` e funções de decisão)
- Estruturas de `State` via `TypedDict`
- Mensagens em chat (`HumanMessage`, `AIMessage`) e `MessagesState` para fluxo conversacional
- Invocação de LLMs via `ChatOpenAI` (LangChain) — como integrar com o grafo
- Tool binding com `ToolNode` e `tools_condition` — exemplo de agentes simples
- Agente ReAct e binding múltiplas `ToolNode` (loop `assistant -> tools -> assistant`), incluindo exemplos de funções locais de ferramenta.
- Persistência de estado com `MemorySaver` (checkpointer) e uso de `thread_id` para recuperar histórico entre invocações.

## Pré-requisitos

- Python 3.10+ recomendado
- Uma conta e chave de API (se for testar os exemplos com LLMs reais, p.ex. `OPENAI_API_KEY`)
- Recomenda-se criar um ambiente virtual

## Instalação e execução (exemplo)

1. Crie e ative um ambiente virtual

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Instale dependências

```bash
pip install -r requirements.txt
```

3. Configure variáveis de ambiente (opcional — necessário somente para os exemplos que chamam LLMs)

```bash
cp .env.example .env
# Edite .env e preencha OPENAI_API_KEY
```

4. Execute os scripts de exercício individualmente

```bash
python3 1-simple-graph.py
python3 2-conditional-graph.py
python3 3-chat-model-simulated.py
# Requer .env com OPENAI_API_KEY:
python3 4-call-llm.py
python3 5-tool-calling-llm.py
python3 6-reative-agent.py
python3 7-memory-agent.py
```

Cada script gera um PNG com a representação do grafo no mesmo diretório (`*.png`) e imprime o resultado do `invoke` no console.

## Observações sobre `4-call-llm.py` e `5-tool-calling-llm.py`

- Ambos os scripts usam `langchain_openai.ChatOpenAI`, que precisa das credenciais de API para funcionar.
- No arquivo `4-call-llm.py`, `llm = ChatOpenAI(model="gpt-4o")` está configurado para o modelo `gpt-4o`. Caso não tenha acesso, troque para outro modelo compatível (p.ex. `gpt-4o-mini`, `gpt-4o-realtime-preview` ou `gpt-3.5-turbo`) caso disponível.
- No `5-tool-calling-llm.py`, a função `client_data_tool` demonstra uma ferramenta local simples; `ToolNode` executa a função quando o chat retorna uma `ToolMessage` — assim o agent pode acionar ferramentas e reinjetar o resultado no diálogo, simulando um loop ReAct simples.
- `6-reative-agent.py` mostra um agente que faz binding com várias ferramentas locais (`client_data_tool`, `client_farm_tool`, `client_products_tool`, `sum_values_tool`). O agente usa `llm.bind_tools(tools)` e `ToolNode` para executar chamadas de ferramenta quando o chat model retorna uma `ToolMessage`, retornando em seguida ao agente para processar o resultado.
- `7-memory-agent.py` mostra como usar `MemorySaver` (via `checkpointer=memory` no `builder.compile`) e enviar `config={'thread_id':'1'}` ao `invoke` para preservar e recuperar o estado entre múltiplas invocaçōes do grafo. Isso permite fluxos stateful (ex.: perguntar dados em duas execuções separadas e o grafo manter o contexto).

  ⚠️ Nota: os scripts `6-reative-agent.py` e `7-memory-agent.py` também usam `ChatOpenAI` e portanto exigem variáveis de ambiente configuradas para a API (ex.: `OPENAI_API_KEY`). Se não quiser usar a API real durante testes, simule as mensagens como em `3-chat-model-simulated.py`.

  - Exemplo rápido para o `7-memory-agent.py`: o script já demonstra duas invocações (`result1` e `result2`) com o mesmo `thread_id` — ao rodar o script você verá que a consulta inicial recupera dados e a segunda pergunta usa o contexto salvo para responder quais produtos foram comprados.

## Sugestões e boas práticas

- Sempre execute os scripts num ambiente isolado (venv) para evitar correr riscos com dependências.
- Ao trabalhar com LLMs e ferramentas, use mensagens simuladas (como em `3-chat-model-simulated.py`) enquanto estiver testando para evitar custos desnecessários.
- Para deploy ou testes com Studio, você pode usar os recursos do LangGraph/Studio para visualizar grafo e fluxos.
