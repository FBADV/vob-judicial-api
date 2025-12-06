"""
INSTRUÇÕES DE USO (MOCK / LOCAL):
----------------------------------
Para testar este conector sem um certificado A1 real ou acesso ao PJe:

1. Defina a variável de ambiente MOCK_MODE=true
   export MOCK_MODE=true

2. Execute o arquivo diretamente:
   python -m app.connectors.connector_pje

3. Sem o MOCK_MODE, o script tentará carregar o certificado do caminho fornecido
   e acessar as URLs fictícias (o que falhará se não existirem).

DEPENDÊNCIAS EXTRAS:
--------------------
pip install playwright httpx cryptography
playwright install chromium
"""

import asyncio
import logging
import os
import random
from typing import List, Dict, Optional
import httpx
from playwright.async_api import async_playwright, Page, BrowserContext

# Configuração de Logs
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("PJeConnector")

# URLs Fictícias para Exemplo
PJE_URL_LOGIN = "https://pje-ficticio.jus.br/pje/login.seam"
PJE_URL_CONSULTA = "https://pje-ficticio.jus.br/pje/Processo/ConsultaProcesso/listView.seam"
PJE_URL_DETAIL = "https://pje-ficticio.jus.br/pje/Processo/ConsultaProcesso/Detalhe/list.seam"


class PJeA1Auth:
    """
    Classe responsável pela manipulação do Certificado A1.
    """
    def __init__(self):
        self._cert_data = None
        self._key_data = None

    def load_certificate(self, pfx_path: str, pfx_password: str) -> bool:
        """
        Carrega o arquivo .pfx (PKCS#12) e extrai chave/certificado.
        
        STUB: Implementação real deve usar `cryptography` ou `OpenSSL` para
        ler o .pfx e converter para formato aceito pelo requests/httpx
        ou injetar no Browser Context.
        
        PARA TROCAR POR HSM:
        Integrar com bibliotecas PKCS#11 (ex: PyKCS11) para acessar tokens físicos/nuvem.
        """
        if os.getenv("MOCK_MODE") == "true":
            logger.info("MOCK_MODE: Simulando carregamento de certificado A1.")
            self._cert_data = b"mock_cert"
            return True

        if not os.path.exists(pfx_path):
            logger.error(f"Certificado não encontrado em: {pfx_path}")
            return False

        try:
            # Exemplo de onde iria a lógica real de leitura:
            # with open(pfx_path, "rb") as f: pfx_data = f.read()
            # p12 = pkcs12.load_key_and_certificates(pfx_data, pfx_password.encode())
            logger.info(f"Carregando certificado real de {pfx_path}...")
            self._cert_data = "CERTIFICADO_CARREGADO"
            return True
        except Exception as e:
            logger.error(f"Erro ao ler certificado: {e}")
            return False


class PJeConnector:
    """
    Conector de automação para o sistema PJe usando Playwright.
    """
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.auth_handler = PJeA1Auth()
        self.browser = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.is_authenticated = False

    async def _init_browser(self):
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=self.headless)
        self.context = await self.browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
            accept_downloads=True
        )
        self.page = await self.context.new_page()

    async def close(self):
        if self.browser:
            await self.browser.close()

    async def autenticar_via_a1(self, pfx_path: str, pfx_password: str) -> bool:
        """
        Realiza login usando certificado digital A1.
        """
        if not self.browser:
            await self._init_browser()

        if not self.auth_handler.load_certificate(pfx_path, pfx_password):
            return False

        logger.info("Iniciando autenticação via Certificado Digital...")
        
        if os.getenv("MOCK_MODE") == "true":
            logger.info("MOCK_MODE: Login A1 simulado com sucesso.")
            self.is_authenticated = True
            return True

        try:
            # No cenário real, aqui injetariamos o certificado cliente na request
            # ou usaríamos uma extensão de browser que lida com o certificado.
            # O Playwright suporta client_certificates no new_context para mTLS.
            
            await self.page.goto(PJE_URL_LOGIN)
            await self.page.click("#btn-entrar-com-certificado") 
            # Aguardar redirecionamento/carregamento
            await self.page.wait_for_url("**/dashboard")
            self.is_authenticated = True
            return True
        except Exception as e:
            logger.error(f"Falha no login A1: {e}")
            return False

    async def autenticar_via_login(self, login: str, senha: str) -> bool:
        """
        Realiza login via usuário e senha (fallback).
        """
        if not self.browser:
            await self._init_browser()
            
        logger.info(f"Tentando login password flow para usuário: {login}")

        if os.getenv("MOCK_MODE") == "true":
            self.is_authenticated = True
            return True

        try:
            await self.page.goto(PJE_URL_LOGIN)
            await self.page.fill("#username", login)
            await self.page.fill("#password", senha)
            await self.page.click("#btn-entrar")
            await self.page.wait_for_selector(".painel-usuario", timeout=10000)
            self.is_authenticated = True
            return True
        except Exception as e:
            logger.error(f"Erro no login/senha: {e}")
            return False

    async def buscar_processos_por_oab(self, numero_oab: str, uf: str) -> List[Dict]:
        """
        Busca processos vinculados a uma OAB.
        """
        if not self.is_authenticated:
            raise Exception("Não autenticado. Execute login primeiro.")

        logger.info(f"Buscando processos para OAB {numero_oab}/{uf}...")

        if os.getenv("MOCK_MODE") == "true":
            # Retorno Mock
            return [
                {"numero": "5001234-88.2023.8.13.0024", "vara": "1ª Vara Cível", "link": "/processo/123"},
                {"numero": "5009876-12.2023.8.13.0024", "vara": "3ª Vara Família", "link": "/processo/456"}
            ]

        try:
            await self.page.goto(PJE_URL_CONSULTA)
            # Preencher campos de busca
            await self.page.fill("#oab", numero_oab)
            await self.page.select_option("#uf", uf)
            await self.page.click("#btn-pesquisar")
            
            # Extrair resultados da tabela
            await self.page.wait_for_selector("#tabela-resultados")
            
            resultados = []
            rows = await self.page.query_selector_all("#tabela-resultados tbody tr")
            for row in rows:
                numero = await row.query_selector(".col-numero").inner_text()
                vara = await row.query_selector(".col-vara").inner_text()
                link_el = await row.query_selector("a.link-detalhe")
                href = await link_el.get_attribute("href")
                
                resultados.append({
                    "numero": numero.strip(),
                    "vara": vara.strip(),
                    "link": href
                })
            
            return resultados

        except Exception as e:
            logger.error(f"Erro ao buscar processos: {e}")
            return []

    async def buscar_andamentos(self, numero_processo: str) -> List[Dict]:
        """
        Extrai andamentos de um processo específico.
        """
        logger.info(f"Extraindo andamentos do processo {numero_processo}...")

        if os.getenv("MOCK_MODE") == "true":
            return [
                {"data": "2023-12-01", "descricao": "Conclusos para Despacho"},
                {"data": "2023-11-20", "descricao": "Petição Juntada"}
            ]
        
        # Implementação real dependeria de navegar até o detalhe
        return []

    async def baixar_documento(self, document_id: str) -> str:
        """
        Baixa um documento PDF e retorna o caminho local.
        """
        logger.info(f"Baixando documento ID: {document_id}")
        
        path_destino = f"/tmp/doc_{document_id}.pdf"

        if os.getenv("MOCK_MODE") == "true":
            # Cria PDF fake
            with open(path_destino, "wb") as f:
                f.write(b"%PDF-1.4 mock content")
            return path_destino

        try:
            async with self.page.expect_download() as download_info:
                # Simula clique no botão de download
                await self.page.click(f"#btn-download-{document_id}")
            
            download = await download_info.value
            await download.save_as(path_destino)
            return path_destino

        except Exception as e:
            logger.error(f"Erro no download: {e}")
            return ""


# --- BLOCO DE EXECUÇÃO PRINCIPAL (TESTE) ---
if __name__ == "__main__":
    async def main():
        print("\n--- INICIANDO TESTE PJe CONNECTOR ---\n")
        
        # Forçar modo mock para testar a estrutura sem quebrar
        os.environ["MOCK_MODE"] = "true"
        
        connector = PJeConnector(headless=True)
        
        try:
            # 1. Testar Login
            sucesso = await connector.autenticar_via_a1("/path/fake.pfx", "123456")
            if sucesso:
                print("✅ Login A1 (Mock) realizado com sucesso.")
            else:
                print("❌ Falha no login.")
                return

            # 2. Buscar Processos
            processos = await connector.buscar_processos_por_oab("123456", "MG")
            print(f"✅ Processos encontrados: {len(processos)}")
            for p in processos:
                print(f"   - {p['numero']} ({p['vara']})")

            # 3. Baixar Documento
            if processos:
                doc_path = await connector.baixar_documento("999")
                print(f"✅ Documento baixado em: {doc_path}")

        finally:
            await connector.close()
            print("\n--- TESTE FINALIZADO ---")

    asyncio.run(main())
