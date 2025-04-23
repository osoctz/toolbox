import os
from uuid import uuid4

import faiss
from langchain_community.docstore import InMemoryDocstore
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.vectorstores.utils import DistanceStrategy
from langchain_core.documents import Document

vs_path = '/path/repo/vector_store/bge-large-zh-v1.5'
model_path = '/path/BAAI/bge-large-zh-v1.5'

# embeddings = HuggingFaceBgeEmbeddings(model_name=model_path, model_kwargs={'device': 'cpu'}, query_instruction='')
import getpass
import os

if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter API key for OpenAI: ")

from langchain_openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings(model="text-embedding-3-large")

query = '积极治疗繁殖机能障碍？'

if not os.path.exists(vs_path):
    os.makedirs(vs_path)

if not os.path.isfile(os.path.join(vs_path, 'index.faiss')):
    doc = Document(page_content='init', metadata={})
    vs = FAISS.from_documents([doc], embeddings, normalize_L2=True)
    ids = list(vs.docstore._dict.keys())
    vs.delete(ids)
    vs.save_local(vs_path)

# index = faiss.IndexFlatL2(len(embeddings.embed_query(query)))
#
# vs = FAISS(
#     embedding_function=embeddings,
#     index=index,
#     docstore=InMemoryDocstore(),
#     index_to_docstore_id={},
# )

documents = [Document(
    page_content=query,
    metadata={"source": "tweet"},
)]

# uuids = [str(uuid4()) for _ in range(len(documents))]
# vs.add_documents(documents=documents, ids=uuids)

vs = FAISS.load_local(vs_path, embeddings, normalize_L2=True, allow_dangerous_deserialization=True,
                      distance_strategy=DistanceStrategy.EUCLIDEAN_DISTANCE)
texts = [x.page_content for x in documents]
metadata_list = [x.metadata for x in documents]
_embeddings = embeddings.embed_documents(texts)
vs.add_embeddings(text_embeddings=zip(texts, _embeddings), metadatas=metadata_list)
vs.save_local(vs_path)

top_k = 3
# vector_store = FAISS.load_local(vs_path, embeddings, normalize_L2=True, distance_strategy="COSINE")
docs = vs.similarity_search_with_relevance_scores(query=query, k=top_k)

print(f"query:{query}")
for d in docs:
    print(f"相关性分数:{d[1]},文档:{d[0]}")
