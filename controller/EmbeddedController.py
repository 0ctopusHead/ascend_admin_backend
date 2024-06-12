from service.EmbeddedService import EmbeddedService


class EmbeddedController:
    def __init__(self):
        self.embedded_service = EmbeddedService()

    def trigger_embedding_process(self):
        try:
            embedding_response, embedding_status = self.embedded_service.embedding_files()
            return embedding_response, embedding_status
        except Exception as e:
            return str(e), 400


