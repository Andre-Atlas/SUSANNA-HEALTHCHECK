import asyncio

from app.db.session import SessionLocal
from app.models.establishment import Establishment
from app.models.service import Service
from app.models.source import Source


async def seed() -> None:
    async with SessionLocal() as db:
        source = Source(
            name="SES-DF (DEMO)",
            url="https://info.saude.df.gov.br/",
            source_type="official",
            description="Registro inicial de desenvolvimento. Substituir/validar antes de uso real.",
        )
        unit = Establishment(
            external_id="DEMO-UBS-001",
            name="Unidade DEMO — substituir por dado oficial",
            type="UBS",
            ra="Samambaia",
            address="DADO DEMO — substituir por endereço oficial",
        )
        db.add_all([source, unit])
        await db.flush()
        db.add(Service(
            establishment_id=unit.id,
            name="Serviço DEMO",
            category="demo",
            description="Registro fictício apenas para testar GET/POST/PUT/DELETE.",
        ))
        await db.commit()
        print(f"Seed concluído. Fonte={source.id} Unidade={unit.id}")


if __name__ == "__main__": asyncio.run(seed())
