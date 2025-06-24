import json, time, uuid
from typing import Dict, Any
from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable
from kafka_config import KafkaConfig

def create_kafka_producer_with_retries(
    bootstrap_servers,
    retries: int = 5,
    delay: int = 5,
):
    for attempt in range(1, retries + 1):
        try:
            producer = KafkaProducer(
                bootstrap_servers=bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                key_serializer=lambda k: k.encode("utf-8") if k else None,
                acks="all",
                retries=3,
                max_in_flight_requests_per_connection=1,
            )
            print("Conectado ao Kafka!")
            return producer
        except NoBrokersAvailable:
            print(
                f"[Tentativa {attempt}/{retries}] Kafka indisponível… "
                f"novo retry em {delay}s."
            )
            time.sleep(delay)
    raise RuntimeError("Não foi possível conectar ao Kafka.")

class KafkaTaskProducer:
    def __init__(self):
                
        self.producer = create_kafka_producer_with_retries(
            KafkaConfig.BOOTSTRAP_SERVERS
        )

    def send_task(self, endpoint_name: str, task_data: Dict[Any, Any]) -> str:
        if endpoint_name not in KafkaConfig.TOPICS:
            raise ValueError(f"Endpoint {endpoint_name} não configurado")

        task_id = str(uuid.uuid4())
        message = {
            "task_id": task_id,
            "endpoint": endpoint_name,
            "data": task_data,
        }

        topic = KafkaConfig.TOPICS[endpoint_name]

        self.producer.send(topic=topic, key=task_id, value=message)
        self.producer.flush()
        print(f"Tarefa {task_id} enviada para {topic}")
        return task_id

    def close(self):
        self.producer.close()
