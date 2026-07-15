import httpx
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import settings
from app.database import AsyncSessionLocal

app = FastAPI(
    title="Datasul RAG API",
    description="MVP de consulta inteligente a documentações técnicas e manuais funcionais do ERP Datasul.",
    version="1.0.0"
)

# Contrato de entrada (Pydantic)
class QueryRequest(BaseModel):
    pergunta: str

# Dependência para injetar a sessão assíncrona do banco de dados
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

# Função auxiliar para gerar o embedding da pergunta (mesmo fluxo da injestão)
async def gerar_embedding_pergunta(texto: str) -> list[float]:
    url = f"{settings.OLLAMA_BASE_URL}/api/embeddings"
    payload = { 
        "model": "nomic-embed-text",
        "prompt": texto           
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        resposta = await client.post(url, json=payload)
        resposta.raise_for_status()
        return resposta.json()["embedding"]
    
# Função auxiliar para chamar a LLM para a geração da resposta (Qwen)
async def gerar_resposta_llm(contexto: str, pergunta: str) -> str:
    url= f"{settings.OLLAMA_BASE_URL}/api/generate"

    prompt_sistema = (
        "Você é um Especialista no ERP TOTVS Datasul e Engenharia de Software.\n"
        "Responda à pergunta do usuário utilizando APENAS o contexto fornecido abaixo.\n"
        "Se o contexto não contiver a resposta, diga honestamente que não encontrou a informação nos manuais.\n\n"
        f"CONTEXTO DOS MANUAIS:\n{contexto}\n\n"
        f"PERGUNTA: {pergunta}\n\n"
        "RESPOSTA FUNDAMENTADA:"
    )

    payload = {
        "model": "qwen2.5:3b",
        "prompt": prompt_sistema,
        "stream": False
    }

    async with httpx.AsyncClient(timeout=180.0) as client:
        resposta = await client.post(url, json=payload)
        resposta.raise_for_status()
        return resposta.json()["response"]

@app.post("/query", summary="Consultar o RAG Datasul")
async def consultar_rag(request: QueryRequest, db: AsyncSession = Depends(get_db)):
    """
    Recebe uma pergunta, gera o embedding, busca os fragmentos similares no 
    PostgreSQL usando pgvector (<=>) e gera uma resposta contextualizada do Qwen
    """
    try:
        # 1. Transforma a pergunta do usuário em um vetor semântico
        vetor_pergunta = await gerar_embedding_pergunta(request.pergunta)

        # 2. Efetua a busca vetorial usando o operador de distância do cosseno (<=>)
        # Buscando os 3 blocos mais relevantes para compor o contexto
        query_vetorial = text("""
            SELECT conteudo, nome_arquivo
            FROM documentos_chunks
            ORDER BY vetor <=> :vetor_pergunta
            LIMIT 2;
        """)

        # O pgvector no SQLAlchemy assíncrono aceita a string no vetor mapeada
        resultado = await db.execute(query_vetorial, {"vetor_pergunta": str(vetor_pergunta)})
        linhas = resultado.fetchall()

        if not linhas:
            raise HTTPException(status_code=404, detail="Nenhum contexto relevante encontrado no banco de dados.")
        
        # 3. Consolida os textos encontrados para servir de contexto para a LLM
        contexto_manuais = "\n---\n".join([f"[{linha.nome_arquivo}]: {linha.conteudo}" for linha in linhas])

        # 4. Envia o contexto e a pergunta para o Qwen gerar a resposta final
        resposta_final = await gerar_resposta_llm(contexto_manuais, request.pergunta)

        return {
            "pergunta": request.pergunta,
            "resposta": resposta_final,
            "fontes": list(set([linha.nome_arquivo for linha in linhas]))
        }
    except httpx.HTTPError as http_err:
        raise HTTPException(status_code=502, detail=f"Erro de comunicação com o servidor Ollama: {repr(http_err)}")
    except Exception as err:
        raise HTTPException(status_code=500, detail=f"Erro interno no processamento do RAG: {repr(err)}")

@app.get("/health", summary="Verificar saúde da API")
async def health_check():
    return {"status": "healthy", "database": "connected"}