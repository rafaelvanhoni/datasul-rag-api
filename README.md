# 🧠 Datasul RAG API

> 🚧 **Status:** Em desenvolvimento ativo

MVP de um ecossistema assíncrono de *Retrieval-Augmented Generation* (RAG) privado, desenvolvido em Python com FastAPI, projetado especificamente para indexação, busca semântica e consulta inteligente de documentações técnicas, manuais funcionais e notas de release do ERP TOTVS Datasul.

O projeto resolve um problema real de ecossistemas legados robustos: toneladas de documentação espalhada, regras de negócio acumuladas ao longo de décadas e nenhuma forma prática de consultar esse conhecimento de forma conversacional — sem depender de nuvem, sem expor dados sensíveis.

---

## 🏛️ Arquitetura & Infraestrutura

A topologia foi desenhada para simular um cenário de produção híbrido (Edge/On-Premises), separando de forma estrita o ambiente de desenvolvimento leve da camada pesada de persistência e inferência de IA:

```
┌─────────────────────────────────────────────────────────────────────┐
│  MACBOOK AIR M1 (Ambiente de Código)                                │
│                                                                     │
│  ┌──────────────────────┐       ┌────────────────────────────────┐  │
│  │  FastAPI + Uvicorn   │◄─────►│       HTTPX Client (Async)     │  │
│  │  Python 3.13         │       └────────────────┬───────────────┘  │
│  └──────────────────────┘                        │                  │
│            │                         Tailscale VPN Mesh             │
│            │                              │                         │
└────────────┼──────────────────────────────┼─────────────────────────┘
             │                              │
             ▼                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│  DELL INSPIRON (Servidor de Laboratório / Linux Mint XFCE)          │
│                                                                     │
│  ┌─────────────────────────────┐  ┌────────────────────────────┐   │
│  │  PostgreSQL 16 + pgvector   │  │  Ollama Server             │   │
│  │  (Docker Container)         │  │  ├── bge-m3 (Embeddings)   │   │
│  └─────────────────────────────┘  │  └── qwen2.5:3b (LLM)     │   │
│                                   └────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

**Camada de Aplicação (Mac M1):** Runtime Python 3.13 e framework FastAPI. Leve, responsivo, ideal para o ciclo de desenvolvimento.

**Camada de Inferência & Dados (Dell / Linux):** Centraliza os serviços pesados — servidor Ollama com os modelos de IA e o container PostgreSQL com extensão vetorial.

**Canal de Comunicação:** Tailscale VPN Mesh. Rede privada segura sem necessidade de expor portas em roteadores residenciais.

---

## 🎯 Objetivo

O projeto documenta e implementa na prática os fundamentos de um sistema RAG de ponta a ponta, conectando conceitos de:

- Arquitetura assíncrona com FastAPI e SQLAlchemy 2.0
- Geração de embeddings semânticos e busca por similaridade vetorial
- Prompt engineering para respostas fundamentadas em documentação técnica
- Infraestrutura de IA local, privada e reproduzível

É também parte de uma transição técnica deliberada: do ecossistema legado **Progress 4GL / TOTVS Datasul** para o desenvolvimento backend moderno com Python.

---

## 🛠️ Stack Tecnológico

| Categoria | Tecnologia | Papel no Sistema |
|---|---|---|
| **Linguagem** | Python 3.13.1 | Type Hints estritos, Google Style |
| **Framework Web** | FastAPI | Arquitetura orientada a eventos assíncronos |
| **Servidor ASGI** | Uvicorn | Engine de alta performance para HTTP |
| **ORM** | SQLAlchemy 2.0 | Mapeamento objeto-relacional com asyncio |
| **Driver de Banco** | asyncpg | Driver binário não-bloqueante para PostgreSQL |
| **Banco Vetorial** | PostgreSQL 16 + pgvector | Persistência e busca por similaridade |
| **Orquestração** | Docker / docker-compose | Gerenciamento do container de banco de dados |
| **Runtime de IA** | Ollama | Servidor local de modelos de linguagem |
| **Embeddings** | bge-m3 | Modelo multilíngue de alta fidelidade para português |
| **LLM** | qwen2.5:3b-instruct | Geração de respostas com baixo consumo de RAM |
| **HTTP Client** | httpx | Chamadas assíncronas ao servidor Ollama remoto |
| **VPN** | Tailscale | Malha de rede privada entre as duas máquinas |

---

## 📁 Estrutura do Projeto

```
datasul-rag-api/
├── app/
│   ├── __init__.py
│   ├── main.py          # Ponto de entrada do FastAPI
│   ├── config.py        # Configurações e variáveis de ambiente
│   ├── database.py      # Conexão assíncrona com o Postgres (SQLAlchemy)
│   ├── models.py        # Modelos de tabela com suporte a vetores (pgvector)
│   ├── schemas.py       # Contratos de entrada e saída da API (Pydantic)
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── ingest.py    # Endpoint de ingestão e indexação de documentos
│   │   └── query.py     # Endpoint de consulta semântica ao RAG
│   └── services/
│       ├── __init__.py
│       ├── ollama.py    # Comunicação assíncrona com o servidor Ollama
│       └── vector_db.py # Operações vetoriais (inserção e busca por similaridade)
├── corpus/
│   ├── publico/         # Amostras de documentação técnica para teste e demonstração
│   └── proprio/         # Exemplos e casos de uso em Progress 4GL / ABL
├── .env                 # Variáveis de ambiente locais (não versionado)
├── .env.example         # Template de configuração para novos ambientes
├── requirements.txt
└── .gitignore
```

---

## 🚀 Como Executar (Desenvolvimento Local)

### Pré-requisitos

- Python 3.13+
- Docker e docker-compose (para o PostgreSQL)
- Servidor Ollama acessível na rede (local ou via VPN) com `bge-m3` e `qwen2.5:3b` instalados
- Arquivo `.env` configurado (ver `.env.example`)

### Passo a passo

**1. Clonar o repositório:**
```bash
git clone https://github.com/rafaelvanhoni/datasul-rag-api.git
cd datasul-rag-api
```

**2. Criar e ativar o ambiente virtual:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**3. Instalar as dependências:**
```bash
pip install -r requirements.txt
```

**4. Configurar as variáveis de ambiente:**
```bash
cp .env.example .env
# Edite o .env com o IP do seu servidor Ollama e credenciais do Postgres
```

**5. Subir o container do banco de dados:**
```bash
docker compose up -d
```

**6. Iniciar o servidor de desenvolvimento:**
```bash
uvicorn app.main:app --reload
```

Acesse a documentação interativa (Swagger UI) em: `http://127.0.0.1:8000/docs`

---

## ⚙️ Variáveis de Ambiente

O arquivo `.env` (não versionado) deve conter:

```env
# Servidor Ollama (IP Tailscale ou localhost)
OLLAMA_BASE_URL=http://<IP_DO_SERVIDOR>:11434

# PostgreSQL
POSTGRES_HOST=<HOST_DO_BANCO>
POSTGRES_PORT=5432
POSTGRES_DB=datasul_rag
POSTGRES_USER=<USUARIO>
POSTGRES_PASSWORD=<SENHA>
```

---

## 🧠 Decisões de Design

- **Separação física da carga de trabalho:** máquina leve para código e API; servidor dedicado para inferência de IA e persistência — simula um cenário real de produção On-Premises.
- **100% local e privado:** nenhum dado trafega para serviços externos. Modelos de IA rodam inteiramente na CPU do servidor de laboratório via Ollama.
- **asyncpg sobre psycopg2:** driver não-bloqueante essencial para não travar o event loop do Uvicorn durante queries ao banco vetorial.
- **httpx sobre requests:** mesmo princípio — chamadas ao Ollama devem ser `await`áveis para manter a concorrência do FastAPI.
- **bge-m3 para embeddings:** escolhido pela alta fidelidade semântica em português, essencial para documentação técnica em língua nativa.
- **qwen2.5:3b-instruct para geração:** equilíbrio entre qualidade de resposta e viabilidade de execução em CPU doméstica.
- **pgvector sobre ChromaDB:** aproveita infraestrutura PostgreSQL já existente e elimina dependência de um banco vetorial separado.

---

## ⚠️ Observações

- O arquivo `.env` está no `.gitignore`. Nunca versionar credenciais.
- O projeto utiliza SQLAlchemy no modo `asyncio`; misturar operações síncronas em rotas `async def` causará bloqueio do event loop.
- O operador `<=>` (distância de cosseno) requer que a extensão `vector` esteja ativa no banco: `CREATE EXTENSION vector;`

---

## 📈 Evolução do Projeto

- [x] Infraestrutura híbrida (Mac M1 + Dell Linux) via Tailscale VPN
- [x] Servidor Ollama configurado e liberado para rede mesh
- [x] Container PostgreSQL migrado para pgvector
- [x] Correção de collation mismatch no cluster Postgres
- [x] Homologação de conectividade ponta a ponta
- [ ] Modelagem do banco vetorial via SQLAlchemy
- [ ] Pipeline de chunking para PDF e Markdown
- [ ] Endpoints `/ingest` e `/query`
- [ ] Busca por similaridade com operador `<=>`
- [ ] Prompt engineering com blindagem contra alucinações
- [ ] Tratamento robusto de erros e refatoração SOLID

---

## 📄 Licença

Projeto de estudo e portfólio. Uso educacional.
