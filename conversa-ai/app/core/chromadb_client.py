import chromadb

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class ChromaDBClient:
    """
    Cliente para interactuar con ChromaDB Server vía HTTP.
    Gestiona colecciones separadas para conocimiento global, Q2Q index y memoria de usuario.
    Compatible con ChromaDB Server v1.0.0+.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ChromaDBClient, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Inicializa la conexión HTTP a ChromaDB."""
        try:
            self.client = chromadb.HttpClient(
                host=settings.CHROMA_HOST,
                port=settings.CHROMA_PORT,
            )
            # Verificar conectividad
            self.client.heartbeat()
            logger.info(f"Conectado a ChromaDB en {settings.CHROMA_HOST}:{settings.CHROMA_PORT}")
        except Exception as e:
            logger.error(f"Error conectando a ChromaDB: {e}")
            self.client = None

    def get_or_create_collection(self, name: str):
        """Obtiene o crea una colección vectorial."""
        if not self.client:
            return None
        try:
            return self.client.get_or_create_collection(name=name)
        except Exception as e:
            logger.error(f"Error obteniendo colección {name}: {e}")
            return None

    @property
    def knowledge_base(self):
        """Colección A: Documentos originales de la base de conocimiento (chunks)."""
        return self.get_or_create_collection("conversapay_knowledge_base")

    @property
    def q2q_index(self):
        """Colección Q2Q: Preguntas hipotéticas generadas para Question-to-Question matching."""
        return self.get_or_create_collection("conversapay_q2q_index")

    @property
    def episodic_memory(self):
        """Colección B: Memoria episódica por usuario (long-term memory)."""
        return self.get_or_create_collection("user_long_term_memory")
