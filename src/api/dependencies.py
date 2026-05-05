from api.rabbitmq import RabbitMQ

rabbitmq = RabbitMQ()


def get_rabbitmq() -> RabbitMQ:
    return rabbitmq
