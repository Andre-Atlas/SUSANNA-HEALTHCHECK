import asyncio
import logging
import sys
import time
import uuid
from pathlib import Path

# Adiciona o diretório raiz ao sys.path para import de app
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.core.config import get_settings
from app.db.session import SessionLocal
from app.models.chunk import DocumentChunk
from app.models.document import Document
from app.models.establishment import Establishment
from app.models.source import Source
from app.providers.ollama import OllamaProvider
from app.schemas.chat import ChatContext
from app.services.chat_service import ChatService
from app.services.ckan_service import CKANService

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("ckan_live_test")


async def run_live_demo():
    settings = get_settings()
    print("\n" + "=" * 80)
    print("🚀 TESTE EM TEMPO REAL: FLUXO COMPLETO DA ARQUITETURA SUSANA + API CKAN")
    print("=" * 80 + "\n")

    # 1. Testar chamada à Action API do CKAN
    print("1️⃣ [CKAN API] Consultando pacotes de dados no CKAN (https://demo.ckan.org)...")
    t0 = time.perf_counter()
    ckan = CKANService(base_url="https://demo.ckan.org")
    packages_data = await ckan.list_packages()
    t1 = time.perf_counter()
    ckan_latency = (t1 - t0) * 1000
    packages_count = len(packages_data.get("result", []))
    print(f"   ✓ Resposta recebida da API CKAN em {ckan_latency:.2f} ms")
    print(f"   ✓ Total de pacotes encontrados: {packages_count}\n")

    # 2. Ingerir dados estruturados de teste via CKAN no banco PostgreSQL + pgvector
    print("2️⃣ [POPOULANDO BANCO] Inserindo dados de teste vinculados à origem CKAN no PostgreSQL...")
    async with SessionLocal() as db:
        # Criar ou recuperar Source
        source = Source(
            id=uuid.uuid4(),
            name="Portal de Dados Abertos CKAN — SES-DF",
            url="https://demo.ckan.org/dataset/saude-df",
            description="Dados cadastrais de unidades de saúde extraídos via CKAN Action API",
        )
        db.add(source)
        await db.commit()
        await db.refresh(source)

        # Inserir Estabelecimento para Samambaia
        unit_samambaia = Establishment(
            id=uuid.uuid4(),
            source_id=source.id,
            external_id="CKAN_UBS1_SAMAMBAIA",
            name="UBS 1 de Samambaia",
            type="UBS",
            ra="Samambaia",
            address="QS 408 Área Especial, Samambaia Norte, DF",
            cep="72318-000",
            phone="(61) 3358-1234",
            opening_hours="Segunda a Sexta, das 07:00 às 19:00",
        )
        db.add(unit_samambaia)

        vacina_text = (
            "A Unidade Básica de Saúde 1 (UBS 1) de Samambaia oferece atendimento de vacinação de rotina, "
            "imunização infantil, vacina da gripe e COVID-19. Horário de funcionamento da sala de vacina: "
            "segunda a sexta das 08:00 às 17:00. Endereço: QS 408 Área Especial, Samambaia Norte."
        )

        # Criar Documento para RAG com informação de vacinação
        doc = Document(
            id=uuid.uuid4(),
            source_id=source.id,
            title="Guia Oficial de Vacinação e Atendimento — Samambaia",
            category="vacinacao",
            url="https://demo.ckan.org/dataset/vacinacao-samambaia",
            content=vacina_text,
            content_hash="ckan_hash_123",
            status="indexed",
        )
        db.add(doc)
        await db.commit()
        await db.refresh(doc)

        # Gerar embedding real no Ollama para o RAG pgvector
        ollama = OllamaProvider()
        vector = await ollama.embed(vacina_text)

        chunk = DocumentChunk(
            id=uuid.uuid4(),
            document_id=doc.id,
            chunk_index=0,
            content=vacina_text,
            embedding=vector,
        )
        db.add(chunk)
        await db.commit()
        print("   ✓ Dados estruturados e embeddings vetoriais (pgvector) salvos no banco com sucesso!\n")

    # 3. Executar o fluxo completo do ChatService (Scope -> RAG/SQL -> System Prompt -> Ollama LLM)
    print("3️⃣ [PIPELINE COMPLETO] Processando pergunta do usuário através do ChatService em tempo real...")
    question = "Estou em Samambaia. Onde posso vacinar e qual o horário de funcionamento da UBS?"
    context = ChatContext(ra="Samambaia")

    print(f"   💬 Pergunta do Usuário: '{question}'")
    print(f"   📍 Contexto Territorial: {context.model_dump()}\n")

    async with SessionLocal() as db:
        chat_service = ChatService(db=db, llm=ollama, embeddings=ollama)
        session_id = str(uuid.uuid4())

        start_pipeline = time.perf_counter()
        response = await chat_service.process(session_id, question, context)
        end_pipeline = time.perf_counter()

        pipeline_ms = (end_pipeline - start_pipeline) * 1000

    print("=" * 80)
    print("🏁 RESULTADO DA EXECUÇÃO EM TEMPO REAL")
    print("=" * 80)
    print(f"⏱️  Tempo Total do Pipeline: {pipeline_ms:.2f} ms ({pipeline_ms/1000:.2f} s)")
    print(f"📌 Status da Resposta: {response.status}")
    print(f"🎯 Intenção Identificada: {response.intent}")
    print(f"📚 Fontes Utilizadas: {[s.source for s in response.sources]}")
    print(f"🔍 Trechos de Evidência Recuperados: {len(response.evidence)}")
    for idx, ev in enumerate(response.evidence, 1):
        print(f"   [{idx}] Score de Similaridade: {ev.score:.4f} | Conteúdo: {ev.content[:90]}...")

    print("\n🤖 RESPOSTA GERADA PELA SUSANA:")
    print("-" * 80)
    print(response.reply)
    print("-" * 80 + "\n")


if __name__ == "__main__":
    asyncio.run(run_live_demo())
