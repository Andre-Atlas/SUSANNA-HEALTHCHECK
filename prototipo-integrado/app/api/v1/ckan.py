from fastapi import APIRouter, HTTPException, Query

from app.services.ckan_service import CKANService

router = APIRouter(prefix="/ckan", tags=["CKAN"])


async def _call(fn):
    try:
        return await fn()
    except Exception as exc:
        raise HTTPException(503, "CKAN indisponível ou não configurado.") from exc


@router.get("/packages", summary="Lista datasets pelo CKAN package_list")
async def packages(): return await _call(CKANService().list_packages)


@router.get("/packages/search", summary="Busca datasets pelo CKAN package_search")
async def package_search(q: str = Query(min_length=1, max_length=500)):
    return await _call(lambda: CKANService().search_packages(q))


@router.get("/packages/{dataset_id}", summary="Obtém dataset pelo CKAN package_show")
async def package_show(dataset_id: str):
    return await _call(lambda: CKANService().get_package(dataset_id))


@router.get("/groups", summary="Lista grupos pelo CKAN group_list")
async def groups(): return await _call(CKANService().list_groups)


@router.get("/tags", summary="Lista tags pelo CKAN tag_list")
async def tags(): return await _call(CKANService().list_tags)


@router.get("/resources/search", summary="Busca recursos pelo CKAN resource_search")
async def resource_search(query: str = Query(min_length=1, max_length=500)):
    return await _call(lambda: CKANService().search_resources(query))
