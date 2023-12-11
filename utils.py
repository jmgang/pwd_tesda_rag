import json
import os
import pandas as pd
from typing import List
from tesda_regulation_pdf import TesdaRegulationPDF

tesda_modules_df = pd.read_csv('datasets/csv/tesda_modules_with_tagging.csv')


def load_tesda_regulation_pdf_from_json(filename: str) -> TesdaRegulationPDF:
    with open(filename, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return TesdaRegulationPDF(**data)


source_filepath = 'datasets/tesda_regulations_json_section1_summarized/'
tesda_regulation_pdf_list = []
for filename in os.listdir(source_filepath):
    tesda_regulation_pdf_list.append(load_tesda_regulation_pdf_from_json(os.path.join(source_filepath, filename)))

def get_tesda_regulation_pdf(tesda_regulation_pdf_list: List[TesdaRegulationPDF],
                                        course_name: str) -> TesdaRegulationPDF:
    for tesda_regulation_pdf in tesda_regulation_pdf_list:
        if course_name == tesda_regulation_pdf.name:
            return tesda_regulation_pdf

def get_course_information_from_dataset(course:str):
    course_df = tesda_modules_df[tesda_modules_df['name'] == course]

    return course_df.to_json(orient='records', lines=True)


def get_courses():
    return [course.name for course in tesda_regulation_pdf_list]