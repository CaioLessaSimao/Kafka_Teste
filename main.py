from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from contextlib import asynccontextmanager
from producer import KafkaTaskProducer
from kafka_config import KafkaConfig


@asynccontextmanager
async def lifespan(app: FastAPI):
    KafkaConfig.create_topics()
    print("Tópicos criados")
    yield
     
app = FastAPI(title="Kafka Producer API", lifespan=lifespan)

# cria o producer (com retry interno) uma única vez
producer = KafkaTaskProducer()

class GenericRequest(BaseModel):
    payload: Dict[str, Any]

class TaskResponse(BaseModel):
    task_id: str
    status: str = "queued"
    message: str

class SetWebhookResponse(BaseModel):
    status: str  
    message: str

def enqueue(endpoint: str, data: Dict[str, Any]) -> TaskResponse:
    try:
        task_id = producer.send_task(endpoint, data)
        return TaskResponse(
            task_id=task_id,
            message=f"Tarefa adicionada à fila {endpoint}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/endpoint1", response_model=TaskResponse)
async def endpoint1(req: GenericRequest):
    return enqueue("endpoint1", req.payload)

@app.post("/endpoint2", response_model=TaskResponse)
async def endpoint2(req: GenericRequest):
    return enqueue("endpoint2", req.payload)

@app.post("/endpoint3", response_model=TaskResponse)
async def endpoint3(req: GenericRequest):
    return enqueue("endpoint3", req.payload)

@app.post("/set-webhook", response_model=SetWebhookResponse)
async def setWebhook(req: GenericRequest):
    """Salva o webhook no banco de dados para que o consumer saiba onde responder"""