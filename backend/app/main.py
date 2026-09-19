from fastapi import FastAPI
from .routers import papers

app = FastAPI()

app.include_router(papers.router)


@app.get('/health')
def health():
    return {'status': 'ok'}