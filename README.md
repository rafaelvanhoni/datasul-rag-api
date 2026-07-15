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
│  ┌─────────────────────────────┐  ┌────────────────────────────┐    │
│  │  PostgreSQL 16 + pgvector   │  │  Ollama Server             │    │
│  │  (Docker Container)         │  │  ├── nomic-embed (768d)    │    │
│  └─────────────────────────────┘  │  └── qwen2.5:3b (LLM)      │    │
│                                   └────────────────────────────┘    │
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
| **Embeddings** | nomic-embed-text | Modelo leve (768 dims), viável em CPU doméstica |
| **LLM** | qwen2.5:3b-instruct | Geração de respostas com baixo consumo de RAM |
| **HTTP Client** | httpx | Chamadas assíncronas ao servidor Ollama remoto |
| **VPN** | Tailscale | Malha de rede privada entre as duas máquinas |

---

## 📁 Estrutura do Projeto

```
datasul-rag-api/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI + endpoint /query (busca vetorial + LLM)
│   ├── config.py        # Configurações via pydantic-settings (lê o .env)
│   ├── database.py      # Engine e sessão assíncrona (SQLAlchemy 2.0)
│   └── models.py        # DocumentoChunk com coluna vetorial (pgvector)
├── corpus/              # Documentação a indexar (local — não versionado por conter material de terceiros)
├── ingestao.py          # Pipeline de ingestão: chunking + embeddings + gravação
├── criar_tabelas.py     # Bootstrap do schema no PostgreSQL
├── docker-compose.yml   # PostgreSQL + pgvector
├── .env                 # Variáveis de ambiente locais (não versionado)
├── .env.example         # Template de configuração para novos ambientes
├── requirements.txt
└── .gitignore
```

> 🔧 **Refatoração planejada:** extrair `routers/`, `services/` e `schemas.py` conforme a API cresce — ver seção *Evolução do Projeto*.

---

## 🚀 Como Executar (Desenvolvimento Local)

### Pré-requisitos

- Python 3.13+
- Docker e docker-compose (para o PostgreSQL)
- Servidor Ollama acessível na rede (local ou via VPN) com `nomic-embed-text` e `qwen2.5:3b` instalados
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

# String de conexão assíncrona usada pela aplicação (SQLAlchemy + asyncpg)
DATABASE_URL=postgresql+asyncpg://<USUARIO>:<SENHA>@<HOST_DO_BANCO>:5432/datasul_rag

# Usadas pelo docker-compose ao criar o container do PostgreSQL
POSTGRES_USER=<USUARIO>
POSTGRES_PASSWORD=<SENHA>
```

---

## 🧠 Decisões de Design

- **Separação física da carga de trabalho:** máquina leve para código e API; servidor dedicado para inferência de IA e persistência — simula um cenário real de produção On-Premises.
- **100% local e privado:** nenhum dado trafega para serviços externos. Modelos de IA rodam inteiramente na CPU do servidor de laboratório via Ollama.
- **asyncpg sobre psycopg2:** driver não-bloqueante essencial para não travar o event loop do Uvicorn durante queries ao banco vetorial.
- **httpx sobre requests:** mesmo princípio — chamadas ao Ollama devem ser `await`áveis para manter a concorrência do FastAPI.
- **nomic-embed-text para embeddings:** modelo leve (768 dimensões) que roda com folga em CPU. O upgrade para bge-m3 (1024 dims, maior fidelidade em português) está planejado — exige migrar a coluna vetorial e re-ingerir o corpus, por isso é uma evolução consciente e não o ponto de partida.
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
- [x] Modelagem do banco vetorial via SQLAlchemy
- [x] Pipeline de ingestão (script) com chunking básico e sobreposição de contexto
- [x] Busca por similaridade com operador `<=>`
- [x] Endpoint `/query` com resposta fundamentada e citação de fontes
- [x] Prompt engineering com blindagem contra alucinações
- [ ] Refatoração em camadas (`routers/`, `services/`, `schemas.py`)
- [ ] Chunking consciente de estrutura (Markdown/PDF)
- [ ] Endpoint `/ingest` (upload de documentos)
- [ ] Health check real (banco + Ollama) e tratamento robusto de erros
- [ ] Testes automatizados (pytest)
- [ ] Upgrade de embeddings para bge-m3 (migração da coluna vetorial + re-ingestão)
- [ ] Provider de LLM configurável (Ollama local ↔ API externa)

---

## 📄 Licença

Projeto de estudo e portfólio. Uso educacional.
