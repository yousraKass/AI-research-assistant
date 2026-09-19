from fastapi import FastAPI
from .routers import papers, research

app = FastAPI()

app.include_router(papers.router)
app.include_router(research.router)


@app.get('/health')
def health():
    return {'status': 'ok'}