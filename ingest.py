import os
import re
import chromadb
import json
from tqdm import tqdm
from typing import List, Any
from chromadb.utils import embedding_functions
from dotenv import load_dotenv
from tesda_regulation_pdf import TesdaRegulationPDF

from utils import load_tesda_regulation_pdf_from_json

persist_directory='chroma/data/'
load_dotenv()

with open('datasets/sectors/sector_courses.json', 'r') as file:
    sector_courses = json.load(file)

def construct_metadata(tesda_regulation_pdf:TesdaRegulationPDF):
    toc_page = tesda_regulation_pdf.toc_page
    starting_core_pages = tesda_regulation_pdf.core_pages[0]
    ending_core_pages = tesda_regulation_pdf.core_pages[1]
    ter_pages = tesda_regulation_pdf.trainee_entry_requirements_pages
    s1_pages = tesda_regulation_pdf.section1_pages
    starting_ter_pages = ter_pages[0]
    ending_ter_pages = ter_pages[1] if len(ter_pages) == 2 else starting_ter_pages
    starting_section1_pages = s1_pages[0]
    ending_section1_pages = s1_pages[1] if len(s1_pages) == 2 else starting_section1_pages

    metadata_list = []
    for document in tesda_regulation_pdf.documents:
        page_number = document.metadata.get('page')
        metadata = dict()
        if page_number == toc_page:
            metadata['page_type'] = 'TABLE_OF_CONTENTS'
        elif starting_core_pages <= page_number <= ending_core_pages:
            metadata['page_type'] = 'CORE_COMPETENCIES'
        elif starting_ter_pages <= page_number <= ending_ter_pages:
            metadata['page_type'] = 'TRAINEE_ENTRY_REQUIREMENTS'
        elif starting_section1_pages <= page_number <= ending_section1_pages:
            metadata['page_type'] = 'SECTION_1'
        else:
            metadata['page_type'] = 'STANDARD'
        metadata['name'] = tesda_regulation_pdf.name
        metadata['sector'] = find_sector_by_course(tesda_regulation_pdf.name)
        metadata_list.append(metadata)
    return metadata_list


def find_sector_by_course(course_name):
    for item in sector_courses:
        if course_name in item["courses"]:
            return item["sector"]
    return "Course not found in any sector"

def ingest_docs(tesda_regulation_pdf:TesdaRegulationPDF, chroma_client:Any, embedding_fn:Any):
    collection_name = tesda_regulation_pdf.name.strip().replace(" ", "_")
    collection_name = re.sub(r"[^a-zA-Z0-9_-]", "", collection_name)
    module_collection = chroma_client.get_or_create_collection(name=collection_name,
                                                               metadata={"hnsw:space": "cosine"},
                                                               embedding_function=embedding_fn)
    documents = [doc.page_content for doc in tesda_regulation_pdf.documents]
    ids = [str(doc.metadata.get('page')) for doc in tesda_regulation_pdf.documents]
    metadatas = construct_metadata(tesda_regulation_pdf)
    module_collection.add(documents=documents, ids=ids, metadatas=metadatas)

    print(f"Added {module_collection.count()} documents to {collection_name} collection")

def ingest_all(collection_name: str,
               tesda_regulation_pdf_list:List[TesdaRegulationPDF],
               chroma_client:Any, embedding_fn:Any):
    module_collection = chroma_client.get_or_create_collection(name=collection_name,
                                                               metadata={"hnsw:space": "cosine"},
                                                               embedding_function=embedding_fn)
    for tesda_regulation_pdf in tesda_regulation_pdf_list:
        print(f'Ingesting into {tesda_regulation_pdf.name}')
        ids = []
        document_page_contents = [doc.page_content for doc in tesda_regulation_pdf.documents]
        metadatas = construct_metadata(tesda_regulation_pdf)
        for doc in tesda_regulation_pdf.documents:
            ids.append(f"{tesda_regulation_pdf.name}_{str(doc.metadata.get('page'))}")
        module_collection.add(documents=document_page_contents, ids=ids, metadatas=metadatas)

    print(f"Added {module_collection.count()} documents to {collection_name} collection")

if __name__ == "__main__":
    chroma_client = chromadb.PersistentClient()
    cohere_ef = embedding_functions.CohereEmbeddingFunction(api_key=os.environ['COHERE_API_KEY'],
                                                            model_name="embed-english-v3.0")

    tesda_regulation_pdf_list = []
    source_path = 'datasets/json/'
    for filename in os.listdir(source_path):
        tesda_regulation_pdf_list.append(load_tesda_regulation_pdf_from_json(os.path.join(source_path, filename)))

    # for tesda_regulation_pdf in tesda_regulation_pdf_list:
    #     ingest_docs(tesda_regulation_pdf, chroma_client, cohere_ef)

    #chroma_client.delete_collection("all_docs")
    #ingest_all('all_docs', tesda_regulation_pdf_list, chroma_client, cohere_ef)
