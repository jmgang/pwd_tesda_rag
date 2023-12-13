import chromadb
import os
import streamlit as st
from pprint import PrettyPrinter
from typing import List
from chromadb.utils import embedding_functions
from dotenv import load_dotenv
from rag_document import RagDocument

load_dotenv()
pp = PrettyPrinter(indent=4)
all_collection = 'all_docs'
chroma_client = chromadb.PersistentClient()
cohere_ef = embedding_functions.CohereEmbeddingFunction(api_key=st.secrets['COHERE_API_KEY'],
                                                        model_name="embed-english-v3.0")


def create_where_clause(avoidable_courses: List[str], metadata_field: str, sector_filter=None):
    where_clauses = []
    if avoidable_courses:
        if len(avoidable_courses) == 1:
            where_clauses.append({metadata_field: {'$ne': avoidable_courses[0]}})
        else:
            for course in avoidable_courses:
                where_clauses.append({metadata_field: {'$ne': course}})

    if sector_filter:
        where_clauses.append(sector_filter)

    if len(where_clauses) == 1:
        return where_clauses[0]
    elif len(where_clauses) > 1:
        return {'$and': where_clauses}
    else:
        return None


def filter_by_sectors(sectors: List[str], where: dict):
    if not sectors:
        return where

    if len(sectors) == 1:
        sector_filter = {'sector': {'$eq': sectors[0]}}
    else:
        sector_filter = {'$or': [{'sector': {'$eq': sector}} for sector in sectors]}

    if where and '$and' in where:
        new_where = where.copy()
        new_where['$and'].append(sector_filter)
    elif where:
        new_where = {'$and': [where, sector_filter]}
    else:
        new_where = sector_filter
    return new_where


def query_by_skills(interests: str, n=4, avoidable_courses: List[str] = None, preferred_sectors: List[str] = None):
    module_collection = chroma_client.get_or_create_collection(name=all_collection,
                                                               metadata={"hnsw:space": "cosine"},
                                                               embedding_function=cohere_ef)
    where_filter = None
    if preferred_sectors:
        if avoidable_courses:
            where_filter = create_where_clause(avoidable_courses, 'name', preferred_sectors)
        else:
            where_filter = filter_by_sectors(preferred_sectors, dict())
    else:
        if avoidable_courses:
            where_filter = create_where_clause(avoidable_courses, 'name', None)

    if where_filter:
        return module_collection.query(
            query_texts=[interests],
            n_results=n,
            where=where_filter
        )

    return module_collection.query(
        query_texts=[interests],
        n_results=n
    )


def to_rag_document_list(results: dict) -> List[RagDocument] :
    ids = results["ids"][0]
    distances = results["distances"][0]
    metadatas = results["metadatas"][0]
    documents = results["documents"][0]

    rag_document_list: List[RagDocument] = []
    for i in range(len(ids)):
        document_obj = RagDocument(
            id=ids[i],
            distance=distances[i],
            metadata=metadatas[i],
            document=documents[i]
        )
        rag_document_list.append(document_obj)
    return rag_document_list


def retrieve_unique_courses(rag_document_list: List[RagDocument]):
    return set([rag_document.metadata.get('name') for rag_document in rag_document_list])