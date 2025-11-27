# MCP Server
Instruções de uso serão adicionadas posteriormente.
## 🛠️ MCP Server - Model Context Protocol

Este diretório contém a implementação do servidor MCP, que expõe funcionalidades de IA (Ferramentas) para Large Language Models (LLMs) externos.

### [cite_start]1. Arquitetura do MCP Server 

A arquitetura segue o padrão de **Service Discovery** do MCP:

* **Endpoint de Descoberta (`/mcp.json`):** É o ponto de entrada. [cite_start]Um cliente LLM (como o ChatGPT) faz uma requisição GET para este endpoint para descobrir quais ferramentas estão disponíveis e como chamá-las (schemas de entrada/saída, endpoint, método HTTP).
* **Módulos de Ferramentas (`tools/`):** Contém o código Python das ferramentas reais (`summarization_tool.py`).
* **Endpoint de Execução (`/v1/tools/summarize_text`):** É o endpoint real que o cliente LLM chama (via POST) quando decide usar a ferramenta. Ele recebe o JSON de entrada e retorna o JSON de saída.
* **Integração com o Core:** A ferramenta `summarize_text` reutiliza o `SummarizationService` principal do projeto (que lida com chunking, paralelismo e alternância de modelos).

### 2. Ferramentas Disponíveis

| Nome | Descrição | Endpoint de Execução |
| :--- | :--- | :--- |
| `summarize_text`  | Sumariza textos longos usando a estratégia de IA configurada. | `/v1/tools/summarize_text` |

### 3. Instruções de Conexão do Cliente MCP (Exemplo: ChatGPT/Gemini) 

Para que um cliente LLM (que suporte a integração de ferramentas) utilize este servidor, siga estes passos:

1.  **Garantir o Acesso:** Certifique-se de que este servidor esteja acessível publicamente (ex: rodando em um domínio `https://mcp.seuservico.com`). Se estiver rodando localmente, você pode usar um túnel como `ngrok`.
2.  **Configuração no Cliente:** No painel de configuração de ferramentas do seu LLM (por exemplo, na seção de "Plugins", "Tools" ou "Function Calling"), forneça a URL completa do endpoint de descoberta.

    > **URL de Descoberta:** `http://localhost:8080/mcp.json` (ou o seu endereço público)

3.  **Execução:** O LLM lerá o manifest, entenderá a função `summarize_text`  e, se o usuário solicitar um resumo de um texto longo, o modelo fará automaticamente a chamada `POST` para o endpoint `/v1/tools/summarize_text`.

### 4. Logs e Tolerância a Falhas [cite: 72]

* [cite_start]**Logs Básicos:** O servidor utiliza o logger estruturado (JSON) do projeto principal (`app/core/logger.py`) para registrar todas as chamadas e resultados[cite: 72].
* [cite_start]**Tratamento Mínimo de Erro:** O *endpoint* de execução da ferramenta possui um bloco `try...except` para capturar erros internos, retornar um HTTP 500 em caso de falha, e registrar o erro, garantindo que o servidor não caia e o modelo cliente receba um erro descritivo[cite: 72].