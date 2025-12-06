import asyncio
import yaml
import os
import logging
from sqlalchemy.orm import Session
from .celery_app import celery_app
from .database import SessionLocal
from .models import Processo, Advogado
from .connectors.connector_pje import PJeConnector
from .connectors.connector_esaj import ESajConnector

# Logging Setup
logger = logging.getLogger("Worker")

def load_tribunais_config():
    path = os.path.join(os.getcwd(), "config", "tribunais.yml")
    if not os.path.exists(path):
        return []
    with open(path, "r") as f:
        data = yaml.safe_load(f)
        return data.get("tribunais", [])

async def _process_tribunal(tribunal_config, oab_num, oab_uf, credenciais):
    """
    Executa a busca em um tribunal específico usando o conector apropriado.
    """
    tipo = tribunal_config.get("tipo")
    connector = None
    
    # Factory simplificada
    if tipo == "pje":
        connector = PJeConnector(headless=True)
    elif tipo == "esaj":
        connector = ESajConnector(headless=True)
    else:
        logger.warning(f"Tipo de tribunal desconhecido: {tipo}")
        return []

    try:
        # Autenticação
        authenticated = False
        if credenciais.get("auth_method") == "a1":
            pfx_path = os.getenv("PFX_PATH", "/tmp/cert.pfx") # Path padrão ou vindo de request
            authenticated = await connector.autenticar_via_a1(pfx_path, credenciais.get("pfx_password"))
        else:
            authenticated = await connector.autenticar_via_login(credenciais.get("login"), credenciais.get("senha"))

        if not authenticated:
            logger.error(f"Falha de autenticação no {tribunal_config['nome']}")
            return []

        # Busca
        # Nota: Alguns conectores podem precisar de adaptação para buscar só por OAB+UF
        # O PJeConnector exemplo já tem `buscar_processos_por_oab`
        processos = await connector.buscar_processos_por_oab(oab_num, oab_uf)
        return processos

    except Exception as e:
        logger.error(f"Erro processando {tribunal_config['nome']}: {e}")
        return []
    finally:
        await connector.close()

@celery_app.task(bind=True, name="app.worker.job_importar_processos")
def job_importar_processos(self, oab_num: str, oab_uf: str, credenciais: dict):
    """
    Task Celery que orquestra a importação de processos.
    """
    logger.info(f"Iniciando importação para OAB {oab_num}/{oab_uf}")
    
    tribunais = load_tribunais_config()
    total_encontrados = 0
    total_novos = 0
    erros = 0
    
    # Para rodar async dentro do Celery (que é sync por padrão), usamos asyncio.run
    # ou loop policy ajustada. Aqui usamos asyncio.run para cada tribunal ou um gather geral.
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    db: Session = SessionLocal()
    
    try:
        for trib in tribunais:
            # Filtro opcional: só rodar tribunais da UF da OAB? 
            # Por enquanto roda todos configurados se UF bater ou se for abrangência nacional.
            if trib.get("uf") != oab_uf:
                 continue

            logger.info(f"Consultando {trib['nome']}...")
            try:
                # Executa o conector async de forma síncrona para o worker
                resultados = loop.run_until_complete(_process_tribunal(trib, oab_num, oab_uf, credenciais))
                
                for proc_data in resultados:
                    total_encontrados += 1
                    
                    # Verifica existência no DB
                    cnj = proc_data.get("numero")
                    existe = db.query(Processo).filter(Processo.numero_cnj == cnj).first()
                    
                    if not existe:
                        # Criar Advogado se não existir (simplificado)
                        adv = db.query(Advogado).filter(Advogado.oab == oab_num).first()
                        if not adv:
                            adv = Advogado(oab=oab_num, nome="Importado Auto")
                            db.add(adv)
                            db.commit()
                            db.refresh(adv)
                        
                        novo_proc = Processo(
                            numero_cnj=cnj,
                            titulo=f"Importado de {trib['nome']}",
                            advogado_id=adv.id,
                            # Outros campos...
                        )
                        db.add(novo_proc)
                        total_novos += 1
                
                db.commit()

            except Exception as e:
                logger.error(f"Erro no loop do tribunal {trib['nome']}: {e}")
                erros += 1

    finally:
        db.close()
        loop.close()

    return {
        "status": "concluido",
        "encontrados": total_encontrados,
        "novos": total_novos,
        "erros": erros
    }
