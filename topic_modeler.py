from bertopic import BERTopic
from utils import load_tesda_regulation_pdf_from_json
import cohere
from bertopic.backend import CohereBackend

def model_topics():
    client = cohere.Client("MY_API_KEY")
    embedding_model = CohereBackend(client)

    topic_model = BERTopic(embedding_model=embedding_model)

if __name__ == "__main__":
    topic_model = BERTopic()
    agri_nc1_tesda = load_tesda_regulation_pdf_from_json('datasets/json/Agricultural Crops Production NC I.json')
    documents = [doc.page_content for doc in agri_nc1_tesda.documents]

    topics, probs = topic_model.fit_transform(documents)

    print(topics)

