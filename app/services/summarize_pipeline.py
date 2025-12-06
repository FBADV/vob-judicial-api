import os
import logging
import pytesseract
from pdf2image import convert_from_path
from typing import List, Dict, Optional
import tiktoken
from openai import OpenAI

# Configuração de Logs
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("SummarizePipeline")

# Prompt Especializado
PROMPT_JURIDICO = """
Você é um assistente jurídico sênior especializado em análise de peças processuais.
Analise o trecho de texto fornecido (extraído de um PDF jurídico) e forneça:

1. **Resumo Técnico (1 parágrafo)**: Descreva a natureza do documento, o pedido principal e os fundamentos jurídicos centrais.
2. **Pontos Legais**: Liste artigos de lei, súmulas ou jurisprudências citadas.
3. **Entidades**: Identifique partes (Autor/Réu), valores monetários, e datas relevantes.

Formato de Saída (JSON):
{
  "resumo_tecnico": "Texto...",
  "pontos_legais": ["Art. X", "Súmula Y"],
  "entidades": {
    "autor": "Nome",
    "reu": "Nome",
    "valor": "R$ 0,00",
    "datas": ["dd/mm/aaaa"]
  }
}
"""

class SummarizePipeline:
    def __init__(self, openai_api_key: Optional[str] = None):
        self.api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key) if self.api_key else None
        
        # Tokenizer para chunking (cl100k_base é usado pelo gpt-4/3.5-turbo)
        self.tokenizer = tiktoken.get_encoding("cl100k_base")

    def run(self, pdf_path: str) -> Dict:
        """
        Executa o pipeline completo:
        1. OCR (PDF -> Imagens -> Texto)
        2. Normalização
        3. Chunking
        4. Resumo com LLM
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"Arquivo não encontrado: {pdf_path}")

        logger.info(f"Iniciando processamento de {pdf_path}")
        
        # 1. OCR
        raw_text = self._extract_text_ocr(pdf_path)
        if not raw_text.strip():
            return {"error": "OCR não detectou texto válido."}

        # 2. Normalização
        clean_text = self._normalize_text(raw_text)

        # 3. Chunking
        chunks = self._chunk_text(clean_text, max_tokens=1200, overlap=200)
        logger.info(f"Gerados {len(chunks)} chunks.")

        # 4. LLM Summary
        summary = self._summarize_with_llm(chunks, PROMPT_JURIDICO)
        
        return summary

    def _extract_text_ocr(self, pdf_path: str) -> str:
        """Converte PDF para imagens e aplica OCR."""
        logger.info("Executando OCR...")
        try:
            images = convert_from_path(pdf_path)
            text_pages = []
            for i, image in enumerate(images):
                # Lang='por' assume tesseract-ocr-por instalado
                text = pytesseract.image_to_string(image, lang='por')
                text_pages.append(text)
            return "\n".join(text_pages)
        except Exception as e:
            logger.error(f"Erro no OCR: {e}")
            # Fallback mock se não tiver tesseract instalado no ambiente dev
            if os.getenv("MOCK_MODE") == "true":
                return "TEXTO MOCK DO PDF JURIDICO. PROCESSO NUMERO 12345. AUTOR FULANO. REU SICRANO."
            raise

    def _normalize_text(self, text: str) -> str:
        """Remove quebras de página repetitivas e espaços extras."""
        lines = text.split('\n')
        normalized = []
        for line in lines:
            if len(line.strip()) < 3: continue # Remove linhas muito curtas/ruído
            normalized.append(line.strip())
        return " ".join(normalized)

    def _chunk_text(self, text: str, max_tokens: int, overlap: int) -> List[str]:
        """Divide o texto em chunks baseados em tokens."""
        tokens = self.tokenizer.encode(text)
        total_tokens = len(tokens)
        chunks = []
        start = 0
        
        while start < total_tokens:
            end = min(start + max_tokens, total_tokens)
            chunk_tokens = tokens[start:end]
            chunks.append(self.tokenizer.decode(chunk_tokens))
            start += (max_tokens - overlap)
        
        return chunks

    def _summarize_with_llm(self, chunks: List[str], prompt: str) -> Dict:
        """
        Envia chunks para LLM e agrega resultados.
        Implementação simplificada: Resume apenas o primeiro chunk ou concatena.
        Para chunks múltiplos, idealmente faria Map-Reduce.
        """
        if not self.client:
            logger.warning("OPENAI_API_KEY não definida. Retornando Mock.")
            return {
                "resumo_short": "Resumo Mock: Documento jurídico processado.",
                "resumo_technical": "Este é um resumo técnico simulado pois a API Key não foi fornecida.",
                "citations": ["Art. 186 CC", "Súmula 123 STJ"]
            }

        # Exemplo simples: Resume o primeiro chunk mais relevante (início da petição)
        # Se precisar de todos, teria que iterar.
        main_chunk = chunks[0] if chunks else ""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo", # Ou gpt-4
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": f"Analise este texto:\n{main_chunk[:3000]}"} # Limit char count just in case
                ],
                temperature=0.0
            )
            content = response.choices[0].message.content
            
            # Aqui deveriamos fazer o parse do JSON retornado pelo LLM
            # Simplificando para string pura se o LLM não retornar JSON válido
            return {
                "raw_llm_output": content,
                "resumo_short": "Resumo gerado via OpenAI.",
                "resumo_technical": content, # Assumindo que o prompt instruiu o formato
                "citations": []
            }

        except Exception as e:
            logger.error(f"Erro na chamada OpenAI: {e}")
            return {"error": "Falha na geração de resumo IA"}

if __name__ == "__main__":
    # Teste local
    pipeline = SummarizePipeline()
    # Crie um pdf dummy se não existir para testar o mock OCR
    if not os.path.exists("test.pdf"):
        with open("test.pdf", "w") as f: f.write("dummy") // Na verdade precisa ser PDF binário valido para OCR real
    
    # Para teste do script, definimos mock mode
    os.environ["MOCK_MODE"] = "true"
    result = pipeline.run("test.pdf")
    print("Resultado Pipeline:", result)
