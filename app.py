import streamlit as st
import google.generativeai as genai
import os
import PyPDF2 as pdf
from dotenv import load_dotenv
import json

load_dotenv() ## load all our environment variables

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
def get_available_models():
    try:
        models = genai.list_models()
        names = []
        for m in models:
            if isinstance(m, dict):
                names.append(m.get("name") or m.get("model") or str(m))
            else:
                names.append(getattr(m, "name", str(m)))
        return names
    except Exception:
        return []


def get_gemini_repsonse(prompt, model_name="text-bison-001"):
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt)
        return getattr(response, "text", getattr(response, "content", str(response)))
    except Exception as e:
        return f"Model call error for '{model_name}': {e}"

def input_pdf_text(uploaded_file):
    reader=pdf.PdfReader(uploaded_file)
    text=""
    for page in range(len(reader.pages)):
        page=reader.pages[page]
        text+=str(page.extract_text())
    return text

#Prompt Template

input_prompt="""
Hey Act Like a skilled or very experience ATS(Application Tracking System)
with a deep understanding of tech field,software engineering,data science ,data analyst
and big data engineer. Your task is to evaluate the resume based on the given job description.
You must consider the job market is very competitive and you should provide 
best assistance for improving thr resumes. Assign the percentage Matching based 
on Jd and
the missing keywords with high accuracy
resume:{text}
description:{jd}

I want the response in one single string having the structure
{{"JD Match":"%","MissingKeywords:[]","Profile Summary":""}}
"""

## streamlit app
st.title("Smart ATS")
st.text("Improve Your Resume ATS")
jd=st.text_area("Paste the Job Description")
uploaded_file=st.file_uploader("Upload Your Resume",type="pdf",help="Please uplaod the pdf")

# Try to get available models and let user pick one (falls back to common default)
available = get_available_models()
default_models = ["text-bison-001", "gemini-1.5", "gemini-1.0", "gemini-1.5-flash"]
model_options = available if available else default_models
st.write("Available models:", model_options if available else "Could not fetch remote list; showing defaults.")
model_name = st.selectbox("Choose model to use", model_options, index=0)

submit = st.button("Submit")

if submit:
    if uploaded_file is not None:
        text=input_pdf_text(uploaded_file)
        formatted = input_prompt.format(text=text, jd=jd)
        response = get_gemini_repsonse(formatted, model_name=model_name)
        st.subheader(response)