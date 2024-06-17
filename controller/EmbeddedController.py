from service.EmbeddedService import EmbeddedService


class EmbeddedController:
    def __init__(self):
        self.embedded_service = EmbeddedService()

    def trigger_embedding_process(self):
        try:
            response_data, status_code = self.embedded_service.embedding_files()
            return response_data, status_code
        except Exception as e:
            return str(e), 400


