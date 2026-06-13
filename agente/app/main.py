from fastapi import FastAPI

app = FastAPI(title="Asistente de Consulta Analítica e Inteligencia Financiera")

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "agente-ia"}

@app.get("/")
async def root():
    return {"message": "Bienvenido al Microservicio de IA del Asistente Financiero"}
