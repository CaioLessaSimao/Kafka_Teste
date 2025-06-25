import json, time, random
from kafka import KafkaConsumer
from kafka.errors import NoBrokersAvailable

from kafka_config import KafkaConfig

def create_consumer_with_retries(
    bootstrap_servers,
    retries: int = 5,
    delay: int = 5,
) -> KafkaConsumer:
    """Tenta criar KafkaConsumer com N tentativas e retardo exponencial."""
    group_id = f"meu-grupo-{random.randint(1000, 9999)}"

    for attempt in range(1, retries + 1):
        try:
            consumer = KafkaConsumer(
                KafkaConfig.TOPICS["endpoint1"],
                bootstrap_servers=bootstrap_servers,
                group_id=group_id,
                value_deserializer=lambda m: json.loads(m.decode("utf-8")),
                auto_offset_reset="earliest",
            )
            print(f"✅ Consumer conectado (group_id={group_id})")
            return consumer

        except NoBrokersAvailable:
            print(
                f"[Tentativa {attempt}/{retries}] Broker fora. "
                f"Novo retry em {delay}s..."
            )
            time.sleep(delay)

        except Exception as e:
            # Qualquer outro erro de configuração / rede
            print(f"❌ Erro inesperado ao criar consumer: {e}")
            time.sleep(delay)

    # Se chegou aqui, todas as tentativas falharam
    raise RuntimeError("Não foi possível conectar ao Kafka após vários retries.")


class KafkaConsumerEndpoint1:
    def __init__(self):
        self.consumer = create_consumer_with_retries(
            KafkaConfig.BOOTSTRAP_SERVERS
        )

    def start_consuming(self):
        try:
            print("📡 Aguardando mensagens… Ctrl+C para sair.")
            for message in self.consumer:
                print(f"🔔 Recebido: {message.value}")

        except Exception as e:
            print(f"Falha na inicialização do consumer: {e}")

        finally:
            self.consumer.close()
            print("✅ Conexão Kafka fechada.")


if __name__ == "__main__":
    try:
        consumer = KafkaConsumerEndpoint1()
        consumer.start_consuming()
    except Exception as e:
        print(f"Falha na inicialização do consumer: {e}")
