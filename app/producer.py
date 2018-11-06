from aiokafka import AIOKafkaProducer

class ProducerSingleton:
    instance = None

    class __ProducerSingleton:
        def __init__(self):
            self._producer = None

        def _initialize_producer(self, loop, config):
            bootstrap_servers = "{}:{}".format(config['kafka']['host'], config['kafka']['port'])
            self._producer = AIOKafkaProducer(loop=loop, bootstrap_servers=bootstrap_servers) 

    def __init__(self):
        if not ProducerSingleton.instance:
            ProducerSingleton.instance = ProducerSingleton.__ProducerSingleton()
      
    def get_producer(self, loop, config):
        if not self.instance._producer:
            self.instance._initialize_producer(loop, config)
        return self.instance._producer 