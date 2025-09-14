from fastapi import FastAPI

from api.routes.data import router as data_router

app = FastAPI(
    title="Teste Data Eng", description="API para teste de Data Eng", version="0.1.0"
)

app.include_router(data_router)


@app.get("/", tags=["Root"])
def read_root():
    return {"message": "API de dados no ar!"}
