import os
from kafka.admin import KafkaAdminClient, NewTopic

class KafkaConfig:
    # ↙️  usa 'kafka:9092' como valor-padrão dentro do Docker
    BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092").split(",")

    TOPICS = {
        "endpoint1": "queue_endpoint1",
        "endpoint2": "queue_endpoint2",
        "endpoint3": "queue_endpoint3",
    }

    @classmethod
    def create_topics(cls):
        """Cria os tópicos se não existirem (idempotente)."""
        admin = KafkaAdminClient(
            bootstrap_servers=cls.BOOTSTRAP_SERVERS,
            client_id="topic_creator",
        )
        topics = [
            NewTopic(name=t, num_partitions=3, replication_factor=1)
            for t in cls.TOPICS.values()
        ]
        try:
            admin.create_topics(topics, validate_only=False)
            print("✅ Tópicos criados ou já existentes.")
        except Exception as e:
            print(f"⚠️  create_topics: {e}")
        finally:
            admin.close()
