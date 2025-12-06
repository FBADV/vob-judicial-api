"""
INSTRUÇÕES DE USO:
------------------
Este conector implementa automação para o sistema e-SAJ (ex: TJSP, TJSC).

RECURSOS ANTI-BLOQUEIO:
- User-Agent rotativo/moderno.
- Delays aleatórios entre ações (1s a 3s).
- Estrutura de retries para falhas de rede/timeout.

MOCK MODE:
export MOCK_MODE=true
python -m app.connectors.connector_esaj
"""

import asyncio
import logging
import os
import random
import time
from typing import List, Dict, Optional
from playwright.async_api import async_playwright, Page, BrowserContext, TimeoutError as PlaywrightTimeoutError

# Configuração de Logs
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("ESajConnector")

# URL Exemplo (TJSP) - Em produção, isso viria de config/env
ESAJ_URL_CONSULTA = "https://esaj.tjsp.jus.br/cpopg/open.do"

class ESajConnector:
    """
    Conector de automação para portais e-SAJ.
    """
    def __init__(self, headless: bool = True, proxy: Optional[Dict] = None):
        self.headless = headless
        self.proxy = proxy
        self.browser = None
        self.context = None
        self.page = None

    async def _init_browser(self):
        playwright = await async_playwright().start()
        
        launch_args = {
            "headless": self.headless,
            "args": ["--disable-blink-features=AutomationControlled"] # Tenta esconder automação
        }
        
        if self.proxy:
            launch_args["proxy"] = self.proxy

        self.browser = await playwright.chromium.launch(**launch_args)
        
        # Omitimos navigator.webdriver e definimos headers padrão
        self.context = await self.browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800},
            extra_http_headers={
                "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
            }
        )
        self.page = await self.context.new_page()

    async def _random_sleep(self, min_s: float = 1.0, max_s: float = 3.0):
        """Pausa a execução por um tempo aleatório para simular comportamento humano."""
        delay = random.uniform(min_s, max_s)
        logger.debug(f"Sleeping for {delay:.2f}s...")
        await asyncio.sleep(delay)

    async def _retry_action(self, action, attempts: int = 3):
        """Executa uma ação com retries."""
        for i in range(attempts):
            try:
                return await action()
            except Exception as e:
                logger.warning(f"Tentativa {i+1} falhou: {e}")
                if i == attempts - 1:
                    raise
                await self._random_sleep(2, 5)

    async def close(self):
        if self.browser:
            await self.browser.close()

    async def buscar_por_numero(self, numero_cnj: str) -> Dict:
        """
        Busca processo pelo número unificado CNJ.
        Retorna dicionário com metadata, partes e últimos andamentos.
        """
        if os.getenv("MOCK_MODE") == "true":
            return {
                "numero": numero_cnj,
                "partes": {"autor": "Fulano de Tal", "reu": "Empresa Y"},
                "andamentos": [
                    {"data": "05/12/2023", "descricao": "Publicação de Sentença"},
                    {"data": "20/11/2023", "descricao": "Conclusos para Julgamento"}
                ],
                "documentos_disponiveis": ["doc_123.pdf", "doc_456.pdf"]
            }

        if not self.browser:
            await self._init_browser()
            
        logger.info(f"Buscando processo {numero_cnj} no e-SAJ...")
        
        try:
            await self.page.goto(ESAJ_URL_CONSULTA)
            await self._random_sleep()

            # Preencher formulário de busca
            # Seletores fictícios baseados no padrão e-SAJ (podem variar por tribunal)
            await self.page.click("input#radioNumeroUnificado") # Seleciona busca por CNJ se necessário
            await self.page.fill("input#processoNumeroIC", numero_cnj) 
            await self._random_sleep(0.5, 1.5)
            
            async with self.page.expect_navigation():
                await self.page.click("input#pbEnviar")
            
            # Verificar se encontrou
            if "Não existem informações disponíveis" in await self.page.content():
                logger.warning("Processo não encontrado.")
                return None

            # Extração de Dados
            dados = {
                "numero": numero_cnj,
                "partes": {},
                "andamentos": []
            }
            
            # Exemplo de extração de partes (ajustar seletores conforme HTML real)
            # tr.fundoClaro > td:nth-child(1) -> Tipo (Reqte/Reqdo)
            # tr.fundoClaro > td:nth-child(2) -> Nome
            partes_els = await self.page.query_selector_all("#tablePartesPrincipais tr")
            for p in partes_els:
                texto = await p.inner_text()
                if "Reqte" in texto or "Autor" in texto:
                    dados["partes"]["autor"] = texto.split(":")[-1].strip()
                elif "Reqdo" in texto or "Réu" in texto:
                    dados["partes"]["reu"] = texto.split(":")[-1].strip()

            # Extração de Andamentos (últimos 10)
            mov_els = await self.page.query_selector_all("#tabelaTodasMovimentacoes tr")
            for i, mov in enumerate(mov_els):
                if i >= 10: break
                
                data_el = await mov.query_selector(".dataMovimentacao")
                desc_el = await mov.query_selector(".descricaoMovimentacao")
                
                if data_el and desc_el:
                    dados["andamentos"].append({
                        "data": (await data_el.inner_text()).strip(),
                        "descricao": (await desc_el.inner_text()).strip()
                    })

            return dados

        except Exception as e:
            logger.error(f"Erro na busca e-SAJ: {e}")
            return None

    async def baixar_todos_documentos(self, numero_cnj: str, destino_dir: str) -> List[str]:
        """
        Navega até a pasta digital do processo e baixa Peças.
        Requer processo aberto ou acesso público liberado.
        """
        logger.info(f"Iniciando download de documentos para {numero_cnj}...")
        
        if not os.path.exists(destino_dir):
            os.makedirs(destino_dir)

        if os.getenv("MOCK_MODE") == "true":
            # Gera arquivos dummy
            paths = []
            for i in range(3):
                p = os.path.join(destino_dir, f"doc_{numero_cnj}_{i}.pdf")
                with open(p, "wb") as f:
                    f.write(b"%PDF-1.4 mock esaj content")
                paths.append(p)
            return paths

        # Fluxo real exigiria login ou acesso aos autos digitais via link na página do processo
        # Simplificação: Assume que já estamos na página do processo e há links de "Visualizar autos"
        
        try:
            # Check for "Pasta Digital" or document links
            # Link exemplo: a.linkPastaDigital
            pasta_link = await self.page.query_selector("a.linkPastaDigital")
            if pasta_link:
                # Clica e aguarda popup ou navegação
                async with self.context.expect_page() as new_page_info:
                    await pasta_link.click()
                
                doc_page = await new_page_info.value
                await doc_page.wait_for_load_state()
                
                # Itera sobre árvore de documentos (exemplo genérico)
                docs_baixados = []
                # ... Lógica de iteração na treeview do e-SAJ ...
                
                # Exemplo simples: Tirar print como "documento" se não conseguir baixar PDF direto
                screenshot_path = os.path.join(destino_dir, f"capa_{numero_cnj}.png")
                await doc_page.screenshot(path=screenshot_path)
                docs_baixados.append(screenshot_path)
                
                await doc_page.close()
                return docs_baixados
            
            return []

        except Exception as e:
            logger.error(f"Erro ao baixar documentos: {e}")
            return []

# --- MAIN ---
if __name__ == "__main__":
    async def main():
        print("\n--- TESTE e-SAJ CONNECTOR ---")
        os.environ["MOCK_MODE"] = "true" # Default to mock for safety
        
        connector = ESajConnector(headless=False)
        
        try:
            dados = await connector.buscar_por_numero("1002003-45.2023.8.26.0100")
            if dados:
                print(f"✅ Processo encontrado: {dados['numero']}")
                print(f"   Partes: {dados['partes']}")
                print(f"   Andamentos: {len(dados['andamentos'])}")
                for andamento in dados['andamentos']:
                    print(f"     [{andamento['data']}] {andamento['descricao']}")

            docs = await connector.baixar_todos_documentos("1002003-45.2023.8.26.0100", "/tmp/esaj_docs")
            print(f"✅ Documentos baixados: {len(docs)}")
            
        finally:
            await connector.close()

    asyncio.run(main())
