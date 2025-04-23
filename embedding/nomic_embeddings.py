import traceback

import requests
from langchain_core.embeddings import Embeddings

import torch.nn.functional as F
from sentence_transformers import SentenceTransformer


class NomicEmbeddings(Embeddings):

    def __init__(self, model_name_or_path):
        self.model_name_or_path = model_name_or_path

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        embeddings = []
        for text in texts:
            embeddings.append(self.text_embedding(text)[0])
        return embeddings

    def embed_query(self, text: str) -> list[float]:
        return self.text_embedding(text)[0]

    def text_embedding(self, text):
        matryoshka_dim = 512

        model = SentenceTransformer(self.model_name_or_path,device='cpu', trust_remote_code=True)
        sentences = ['search_query:'+text]
        embeddings = model.encode(sentences)
        # embeddings = F.layer_norm(embeddings, normalized_shape=(embeddings.shape[1],))
        # embeddings = embeddings[:, :matryoshka_dim]
        # embeddings = F.normalize(embeddings, p=2, dim=1)
        # print(embeddings)

        return embeddings
