class File:
    def __init__(self, file_name, encoded_string, hash_key):
        self.file_name = file_name
        self.encoded_string = encoded_string
        self.hash_key = hash_key

    def to_dict(self):
        return {
            'file_name': self.file_name,
            'encoded_string': self.encoded_string,
            'hash_key': self.hash_key
        }
