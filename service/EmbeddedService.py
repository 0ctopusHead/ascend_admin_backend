from openai import OpenAI
import os
import tiktoken
import base64
from bson import ObjectId
from flask import jsonify
from io import BytesIO
import PyPDF2
from app import mongo
from utils.OpenAIStorageUtils import OpenAIStorageUtils
from dotenv import load_dotenv
load_dotenv()
GPT_MODEL = "gpt-3.5-turbo"
EMBEDDING_MODEL = "text-embedding-3-small"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
client = OpenAI()
db = mongo.db


class EmbeddedService:
    def __init__(self):
        self.database = db
        self.openai_storage_utils = OpenAIStorageUtils()

    def embedding_files(self):
        try:
            encoded_files = self.database.EncodedPDF.find({})
            for file in encoded_files:
                hash_key = file['hash_key']
                file_name = file['file_name']
                if OpenAIStorageUtils.check_file_exists(hash_key):
                    continue
                encoded_string = file['encoded_string']
                decoded_text = self.read_decoded_pdf(self.decode_pdf([encoded_string]))[0]
                all_chunks = self.split_strings_from_subsection(decoded_text, max_tokens=2048)

                embedded_chunks = self.prepare_embedded_chunks(file_name, hash_key, all_chunks)

                for chunk in embedded_chunks:
                    self.save_embedded_chunk(chunk, file['file_name'])

            return jsonify({'message': 'Embedded files success'}), 200

        except Exception as e:
            raise e

    def save_embedded_chunk(self, chunk, file_name):
        data = {
            'file_name': chunk['file_name'],
            'text_chunk': chunk['text_chunk'],
            'embedded_array': chunk['embedded_array'],
            'hash_key': str(chunk['hash_key'])
        }
        self.openai_storage_utils.store_json_to_openai(file_name, data)

    @staticmethod
    def num_tokens(text: str, model: str = GPT_MODEL) -> int:
        encoding = tiktoken.encoding_for_model(model)
        return len(encoding.encode(text))

    @staticmethod
    def halved_by_delimiter(string: str, delimiter: str = "\n") -> list[str, str]:
        chunks = string.split(delimiter)
        if len(chunks) == 1:
            return [string, ""]
        elif len(chunks) == 2:
            return chunks
        else:
            total_tokens = EmbeddedService.num_tokens(string)
            halfway = total_tokens // 2
            best_diff = halfway
            for i, chunk in enumerate(chunks):
                left = delimiter.join(chunks[: i + 1])
                left_tokens = EmbeddedService.num_tokens(left)
                diff = abs(halfway - left_tokens)
                if diff >= best_diff:
                    break
                else:
                    best_diff = diff
            left = delimiter.join(chunks[:i])
            right = delimiter.join(chunks[i:])
            return [left, right]

    @staticmethod
    def truncated_string(
            string: str,
            model: str,
            max_tokens: int,
            print_warning: bool = True,
    ):
        encoding = tiktoken.encoding_for_model(model)
        encoded_string = encoding.encode(string)
        truncated_string = encoding.decode(encoded_string[:max_tokens])
        if print_warning and len(encoded_string) > max_tokens:
            print(f"Warning: Truncated string from {len(encoded_string)} tokens to {max_tokens} tokens.")
        return truncated_string

    @staticmethod
    def split_strings_from_subsection(
            subsection: str,
            max_tokens: int = 500,
            model: str = GPT_MODEL,
            max_recursion: int = 5,
    ) -> list[str]:
        text = subsection
        string = "".join(text)
        num_tokens_in_string = EmbeddedService.num_tokens(string)
        if num_tokens_in_string <= max_tokens:
            return [string]
        elif max_recursion == 0:
            return [EmbeddedService.truncated_string(string, model=model, max_tokens=max_tokens)]
        else:
            text = subsection
            for delimiter in ["\n\n", "\n", ". "]:
                left, right = EmbeddedService.halved_by_delimiter(text, delimiter=delimiter)
                if left == "" or right == "":
                    continue
                else:
                    results = []
                    for half in [left, right]:
                        half_subsection = (half)
                        half_strings = EmbeddedService.split_strings_from_subsection(
                            half_subsection,
                            max_tokens=max_tokens,
                            model=model,
                            max_recursion=max_recursion - 1,
                        )
                        results.extend(half_strings)
                    return results
        return [EmbeddedService.truncated_string(string, model=model, max_tokens=max_tokens)]

    @staticmethod
    def decode_pdf(encode_list):
        pdf_files = []
        for encode_text in encode_list:
            decoded_bytes = base64.b64decode(encode_text)
            pdf_files.append(BytesIO(decoded_bytes))
        return pdf_files

    @staticmethod
    def read_decoded_pdf(pdf_files):
        all_chunk = []
        for pdf_text in pdf_files:
            pdf_reader = PyPDF2.PdfReader(pdf_text)
            content = ""
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                content += page.extract_text()
            all_chunk.append(content)
        return all_chunk

    @staticmethod
    def prepare_embedded_chunks(file_name, hash_key, all_chunks):
        embedded_chunks = []
        for chunk_index, text_chunk in enumerate(all_chunks):
            response = client.embeddings.create(model=EMBEDDING_MODEL, input=text_chunk)
            embeddings = [e.embedding for e in response.data]
            chunk = {'file_name': file_name, 'hash_key': hash_key, 'text_chunk': text_chunk, 'embedded_array': embeddings,
                     '_id': str(ObjectId())}
            embedded_chunks.append(chunk)
        return embedded_chunks




