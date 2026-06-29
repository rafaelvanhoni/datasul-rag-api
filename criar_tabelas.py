import asyncio
from app.database import engine, Base
# IMPORTANTE: Precisamos importar o models aqui para o Python carregar
# a classe DocumentoChunk na memória e registrá-la no catálogo da Base
from app import models

async def inicializar_banco() -> None:
    """ 
    Lê as definições do ORM e cria as tabelas fisicamente no PostgreeSQL.
    """
    print("Conectando ao banco de dados no servidor Dell e gerando tabelas...")

    # Abrimos uma conexão assíncrona utilizando o nosso motor (Engine)
    async with engine.begin() as conexao:
        # run_sync permite executar o método síncrono create_all
        # dentro do fluxo assíncrono do nosso driver
        await conexao.run_sync(Base.metadata.create_all)

    print("Tabela 'documentos_chunks' criada com sucesso com suporte a pgvector!")

# Ponto de entrada padrão para scripts Python executados via terminal
if __name__ == "__main__":
    asyncio.run(inicializar_banco())