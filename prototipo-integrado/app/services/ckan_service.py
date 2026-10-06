from typing import Any

import httpx

from app.core.config import get_settings


class CKANService:
    """Adapter fino para a Action API do CKAN."""

    def __init__(self, base_url: str | None = None):
        settings = get_settings()
        self.base_url = (base_url or settings.ckan_base_url).rstrip("/")

    async def action(self, action: str, **params: Any) -> dict[str, Any]:
        if not self.base_url:
            raise RuntimeError("CKAN_BASE_URL não configurado.")
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{self.base_url}/api/3/action/{action}", params=params
            )
            response.raise_for_status()
            data = response.json()
            if data.get("success") is False:
                raise RuntimeError(data.get("error") or "CKAN retornou erro.")
            return data

    async def list_packages(self): return await self.action("package_list")
    async def get_package(self, dataset_id: str): return await self.action("package_show", id=dataset_id)
    async def search_packages(self, query: str): return await self.action("package_search", q=query)
    async def list_groups(self): return await self.action("group_list")
    async def list_tags(self): return await self.action("tag_list")
    async def search_resources(self, query: str): return await self.action("resource_search", query=query)
