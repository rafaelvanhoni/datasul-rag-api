from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """ Gerencia e valida as variáveis de ambiente da aplicação.

    Essa classe utiliza o Pydantic Settings para ler o arquivo .env
    na raiz do projeto, garantindo tipagem estrita e falha rapida (fail-fast)
    caso alguma configuração mandatória esteja ausente
    """

    OLLAMA_BASE_URL: str
    DATABASE_URL: str

    class Config:
        # Indica ao Pydantic onde procurar os arquivo de segredos local
        env_file = ".env"
        env_file_encoding = "utf-8"

# Instanciamos o objeto global para importação facilitada no projeto
settings = Settings()