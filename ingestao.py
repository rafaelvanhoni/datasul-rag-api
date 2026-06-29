import os
import asyncio
import httpx
from app.config import settings
from app.database import AsyncSessionLocal
from app.models import DocumentoChunk

# ================================= #
# BLOCO 1: CONFIGURAÇÃO DO CHUNKING #
# ================================= #
CHUNK_SIZE = 500     # Tamanho máximo de caracteres por pedaço 
CHUNK_OVERLAP = 100  # Quantos caracteres repetir do bloco anterior

def faturar_texto(texto: str, tamanho: int = CHUNK_SIZE, sobreposicao: int = CHUNK_OVERLAP) -> list[str]:
    """
    Divide o texto em blocos menores com sobreposição de contexto.
    """
    chunks = []
    inicio = 0
    while inicio < len(texto):
        fim = inicio + tamanho
        chunks.append(texto[inicio:fim])
        inicio += (tamanho - sobreposicao)
        
    return chunks

# ======================================== #
# BLOCO 2: COMUNICAÇÃO COM O OLLAMA (DELL) #
# ======================================== #
async def gerar_embedding(texto: str) -> list[float]:
    """ 
    Chama o Ollama remotamente no Dell para gerar o vetor usando o modelo nomic-embed-text.
    """
    url= f"{settings.OLLAMA_BASE_URL}/api/embeddings"
    payload = {
        "model" : "nomic-embed-text",
        "prompt" : texto
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        resposta = await client.post(url, json=payload)
        resposta.raise_for_status()
        dados = resposta.json()
        return dados["embedding"]

# ==================================== #
# BLOCO 3: FLUXO PRINCIPAL DE INGESTÃO #
# ==================================== #
async def processar_ingestao(nome_arquivo: str):
    caminho_arquivo = os.path.join("corpus", nome_arquivo)

    if not os.path.exists(caminho_arquivo):
        print(f"❌ Arquivo não encontrado em: {caminho_arquivo}")
        return
    
    print(f"\n📖 Lendo o documento: {nome_arquivo}...")
    
    with open(caminho_arquivo, "r", encoding="utf-8") as f:
        conteudo_completo = f.read()

    print(f"✂️ Faturando o texto em pedaços inteligentes...")
    pedacos = faturar_texto(conteudo_completo)
    print(f"Total de pedaços gerados para {nome_arquivo}: {len(pedacos)}.")

    async with AsyncSessionLocal() as session:
        for i, pedaco_texto in enumerate(pedacos):
            print(f"🧠 Gerando vetor no Ollama para o bloco [{i+1}/{len(pedacos)}]...")

            try:
                # Gera o vetor chamando o Dell via API
                vetor = await gerar_embedding(pedaco_texto)

                # Instancia o modelo do SQLAlchemy
                chunk_banco = DocumentoChunk(
                    nome_arquivo = nome_arquivo,
                    conteudo = pedaco_texto,
                    vetor = vetor 
                )

                session.add(chunk_banco)
            
            except Exception as e:
                print(f"❌ Erro ao processar o bloco {i+1}: {e}")
                return
            
        print("💾 Gravando tudo no PostgreSQL do servidor Dell...")
        await session.commit()

        print(f"✅ Ingestão do '{nome_arquivo}' concluída com sucesso!")

# ======================== #
# ORQUESTRAÇÃO DA EXECUÇÃO #
# ======================== #
async def main():
    print("🚀 Iniciando o pipeline de ingestão de Manuais Datasul...")

    # Garante a criação da tabela antes de inserir (idempotente — não recria se já existir)
    from app.database import engine, Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Processando manuais da pasta corpus
    await processar_ingestao("manual_recebimento.md")
    await processar_ingestao("arquitetura_datasul.md")

if __name__ == "__main__":
    asyncio.run(main())