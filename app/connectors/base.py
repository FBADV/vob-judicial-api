from abc import ABC, abstractmethod

class TribunalConnectorBase(ABC):
    """
    Classe base abstrata para conectores de tribunais (PJe, e-SAJ, e-Proc, Projudi).
    Deve ser implementada para cada sistema específico.
    """

    def __init__(self, certificate=None):
        self.certificate = certificate

    @abstractmethod
    def login(self):
        """Realiza autenticação no portal do tribunal (usando certificado ou login/senha)."""
        pass

    @abstractmethod
    def consultar_processo(self, numero_processo: str):
        """Busca detalhes de um processo específico."""
        pass

    @abstractmethod
    def listar_processos_oab(self, oab: str, estado: str):
        """Lista processos vinculados a uma OAB."""
        pass

    @abstractmethod
    def download_documento(self, doc_id: str):
        """Baixa o PDF de um documento/peça."""
        pass

# --- Exemplos de Implementação Futura ---
# class PjeConnector(TribunalConnectorBase):
#     def login(self):
#         # Implementar login com certificado A1 via requests + pkcs12
#         pass
# ...
