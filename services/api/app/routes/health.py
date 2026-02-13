from fastapi import APIRouter

router = APIRouter(tags=['system'])


@router.get('/health')
def healthcheck() -> dict[str, str]:
    return {'status': 'ok'}
