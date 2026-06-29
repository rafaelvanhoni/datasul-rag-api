from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from pgvector.sqlalchemy import Vector
from app.database import Base


class DocumentoChunk(Base):
    """ Mapeia a tabela de pedaços (chunks) de documentos do RAG.

    Esta classe entende a nossa Base declarativa e define a estrutura 
    física onde serão armazenados os textos e os vetores gerados pela IA.
    """

    __tablename__ = "documentos_chunks"

    # Identificador único (Primary Key com Autoincremento)
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Nome do arquivo de origem (ex: "manual_recebimento.pdf")
    nome_arquivo: Mapped[str] = mapped_column(String(255), nullable=False)

    # O conteúdo textual do pedaço fatiado
    conteudo: Mapped[str] = mapped_column(Text, nullable=False)

    # A coluna vetorial do pgvector para busca semântica (768 dimensões para o nomic-embed-text)
    vetor: Mapped[list[float]] = mapped_column(Vector(768), nullable=False)