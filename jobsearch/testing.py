import PyPDF2 as p
import re
import pandas as pd
from exclude_words import EXCLUDE_WORDS

MY_EXCLUDE_WORDS = set().union(*EXCLUDE_WORDS.values())

def count_resume_words(file_path):

    with open (file_path, 'rb') as pdf_file:
        reader = p.PdfReader(pdf_file)

        counts = {}

        for page in reader.pages:
            text = page.extract_text()
            if text:

                lower = text.lower()
                words = re.findall(r"[a-z][a-z\.\+\#]*", lower)

                filtered_list = [
                    word for word in words 
                    if word not in MY_EXCLUDE_WORDS and len(word) > 2
                ]

                for word in filtered_list:
                    if word not in counts:
                        counts[word] = 1
                    else:
                        counts[word] += 1

    return counts

pd_file_path = 'Logan Haack_Resume.pdf'

word_count = count_resume_words(pd_file_path)

for word, count in sorted(word_count.items(), key=lambda x: x[1], reverse=True):
    print(f"{word}: {count}")

# import PyPDF2

# def extract_text_from_pdf(pdf_path):
#     text = ""
#     with open(pdf_path, 'rb') as file:
#         reader = PyPDF2.PdfReader(file)
#         for page in reader.pages:
#             text += page.extract_text() or "" # Use an empty string if extract_text returns None
#     return text

# # Example usage:
# resume_text = extract_text_from_pdf("Logan Haack_Resume.pdf")
# print(resume_text)