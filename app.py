import json

import streamlit as st
import os
from langchain.callbacks.base import BaseCallbackHandler
from langchain.chat_models import ChatOpenAI
from langchain_core.callbacks import CallbackManager
from core_agent import find_best_course, retrieve_additional_courses, retrieve_top_unique_courses, present_best_course, \
    get_tesda_course, update_current_recommended_courses, get_similar_courses, present_similar_courses, \
    generate_lesson_plan
from utils import get_course_information_from_dataset, get_courses

custom_css = """
<style>
.card {
    box-shadow: 0px 2px 4px rgba(0, 0, 0, 0.1);
    padding: 16px;
    border-radius: 8px;
    margin: 8px;
}
.metric-title {
    font-size: 16px;
    margin-bottom: 5px;
}
.metric-value {
    font-size: 24px;
    font-weight: bold;
    margin-bottom: 5px;
}
.metric-subvalue {
    font-size: 16px;
    color: gray;
}
</style>
"""

class StreamHandler(BaseCallbackHandler):
    def __init__(self, container, initial_text=""):
        self.container = container
        self.text = initial_text

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        self.text += token
        self.container.markdown(self.text, unsafe_allow_html=True)


def show_pwd_page():
    st.title('TESDA Course Generator for PWD Education')
    with st.form(key='lesson_plan_form'):
        interests = st.text_input("What are your interests?", "")
        options_list = [
            'Chronic Illness',
            'Hearing',
            'Learning',
            'Mental/Intellectual',
            'Orthopedic',
            'Psychosocial',
            'Speech Impairment',
            'Visual',
            'Multiple'
        ]
        disability = st.selectbox('Type of Disability', options_list)
        submit_button = st.form_submit_button(label='Generate TESDA courses')

    if submit_button:
        st.subheader('Suggested course most suitable for your interests')
        with st.spinner("Please wait..."):
            stream_handler = StreamHandler(st.empty())
            llm = ChatOpenAI(
                temperature=0,
                openai_api_key=st.secrets["OPENAI_API_KEY"],
                model=st.secrets['CHAT_MODEL'],
                streaming=True,
                callback_manager=CallbackManager([stream_handler])
            )
            avoidable_courses = []
            rag_documents = retrieve_additional_courses(interests, avoidable_courses)
            top_courses = retrieve_top_unique_courses(rag_documents)

            best_course = find_best_course(top_courses, disability=disability, interests=interests)

            course_information = get_tesda_course(best_course)
            additional_information = get_course_information_from_dataset(best_course)

            print(f'Additional information: {additional_information}')

            present_best_course({'best_course': best_course,
                                 'interests': interests,
                                 'disability': disability,
                                 'course_information': course_information.summary['section1'],
                                 'additional_information': additional_information}, llm)

            top_courses, avoidable_courses = update_current_recommended_courses(best_course, top_courses,
                                                                                avoidable_courses)
            similar_courses = get_similar_courses(top_courses, avoidable_courses, disability, interests)
            print(similar_courses)

            st.subheader('Similar courses to consider')
            presented_similar_courses = json.loads(present_similar_courses(similar_courses))

            for similar_course in presented_similar_courses:
                with st.expander(similar_course['name']):
                    st.write(similar_course['advisor_response'])

def show_tesda_page():
    st.title('TESDA Lesson Plan Generator for PWD Education')
    with st.form(key='lesson_plan_form'):
        course = st.selectbox('What course are you teaching?', get_courses())
        options_list = [
            'Chronic Illness',
            'Hearing',
            'Learning',
            'Mental/Intellectual',
            'Orthopedic',
            'Psychosocial',
            'Speech Impairment',
            'Visual',
            'Multiple'
        ]
        disability = st.selectbox('Type of Disability', options_list)
        submit_button = st.form_submit_button(label='Generate Lesson Plan')

    if submit_button:
        with st.spinner("Please wait..."):
            stream_handler = StreamHandler(st.empty())
            llm = ChatOpenAI(
                temperature=0,
                openai_api_key=st.secrets["OPENAI_API_KEY"],
                model=st.secrets['CHAT_MODEL'],
                streaming=True,
                callback_manager=CallbackManager([stream_handler])
            )
            generate_lesson_plan(course, disability, llm)


st.sidebar.title('Navigation')
page = st.sidebar.selectbox("Choose a page", ["For PWDs", "For TESDA teachers"])

if page == "For PWDs":
    show_pwd_page()
elif page == "For TESDA teachers":
    show_tesda_page()

