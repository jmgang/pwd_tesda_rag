import os

import chromadb
import json
import cohere
from chromadb.utils import embedding_functions
from langchain.embeddings import CohereEmbeddings
from dotenv import load_dotenv
from json_splitter import JSONSplitter
from tesda_regulation_pdf import TesdaRegulationPDF

persist_directory='chroma/data/'
load_dotenv()

def load_tesda_regulation_pdf_from_json(filename: str) -> TesdaRegulationPDF:
    with open(filename, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return TesdaRegulationPDF(**data)


if __name__ == '__main__':
    chroma_client = chromadb.PersistentClient()
    cohere_ef = embedding_functions.CohereEmbeddingFunction(api_key=os.environ['COHERE_API_KEY'],
                                                            model_name="large")
    agri_nc1_collection = chroma_client.get_or_create_collection(name="test",
                                                                 metadata={"hnsw:space": "cosine"})
    cohere_embeddings = CohereEmbeddings(model="embed-english-light-v3.0")
    agri_nc1_tesda = load_tesda_regulation_pdf_from_json('datasets/json/Barista NC II.json')
    # agri_nc1_collection.add(documents=documents[:5],
    #                         ids=pages[:5])
    #
    # print(f"Going to add {len(documents)} to Vector Store")

    # langchain_chroma = Chroma(
    #     client=chroma_client,
    #     collection_name="test",
    #     embedding_function=cohere_embeddings
    # )

    # langchain_chroma = Chroma.from_documents(
    #     documents=agri_nc1_tesda.documents[:5],
    #     client=chroma_client,
    #     collection_name="test",
    #     embedding=cohere_embeddings
    # )

    # print("There are ", langchain_chroma._collection.count(), " in the collection")

    query = "what are the requirements for this?"
    # docs = langchain_chroma.similarity_search_with_score(query)
    # print(docs)
    #print(docs[0])

    results = agri_nc1_collection.query(
        query_texts=[query],
        n_results=4
    )

    print(results)
    print(len(results['documents']))