import os

from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.vectorstores.utils import DistanceStrategy
from langchain_core.documents import Document

vs_path = '/path/repo/vector_store/bge-large-zh-v1.5'
model_path = '/path/BAAI/bge-large-zh-v1.5'

embeddings = HuggingFaceBgeEmbeddings(model_name=model_path, model_kwargs={'device': 'cpu'}, query_instruction='为这个句子生成表示以用于检索相关文章：',encode_kwargs={'normalize_embeddings': True})

query = '如何提高母牛繁殖力？'

if not os.path.exists(vs_path):
    os.makedirs(vs_path)

if not os.path.isfile(os.path.join(vs_path, 'index.faiss')):
    doc = Document(page_content='init', metadata={})
    vs = FAISS.from_documents([doc], embeddings, normalize_L2=True)
    ids = list(vs.docstore._dict.keys())
    vs.delete(ids)
    vs.save_local(vs_path)

documents = [Document(
    page_content=query,
    metadata={"source": "tweet"},
)]

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
