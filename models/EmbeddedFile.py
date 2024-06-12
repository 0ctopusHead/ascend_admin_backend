class EmbeddedFile:
    def __init__(self, file_name, text_chunk, embedded_array, hash_key):
        self.file_name = file_name
        self.text_chunk = text_chunk
        self.embedded_array = embedded_array
        self.hash_key = hash_key

    def to_dict(self):
        return {
            'file_name': self.file_name,
            'text_chunk': self.text_chunk,
            'embedded_array': self.embedded_array,
            'hash_key': self.hash_key
        }