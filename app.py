import streamlit as st
from transformers import pipeline

import fitz

st.set_page_config(page_title='🤗 Arabic Text Summarization App', layout="wide")
st.title('🤗 Arabic Text Summarization App')

txt_input = st.text_area('Enter your text', '', height=200)

# File uploader to upload PDF files
uploaded_file = st.file_uploader("Or upload a PDF file", type=['pdf'])

model_choice = st.sidebar.selectbox(
    "Choose a summarization model",
    ("Osame1/AraBART-finetuned-xlsum-ar", "Osame1/AraT5-msa-small-finetuned-xlsum-ar", "facebook/bart-large-cnn")
)

# Minimum and maximum length sliders
min_length = st.sidebar.slider("Minimum Length of Summary", 10, 100, 30, step=10)
max_length = st.sidebar.slider("Maximum Length of Summary", 50, 300, 130, step=10)

# Load the chosen model
@st.cache_resource
def load_model(model_name):
    summarizer = pipeline("summarization", model=model_name)
    return summarizer

def generate_chunks(inp_str):
    max_chunk = 500
    inp_str = inp_str.replace('.', '.<eos>')
    inp_str = inp_str.replace('?', '?<eos>')
    inp_str = inp_str.replace('!', '!<eos>')
    
    sentences = inp_str.split('<eos>')
    current_chunk = 0 
    chunks = []
    for sentence in sentences:
        if len(chunks) == current_chunk + 1: 
            if len(chunks[current_chunk]) + len(sentence.split(' ')) <= max_chunk:
                chunks[current_chunk].extend(sentence.split(' '))
            else:
                current_chunk += 1
                chunks.append(sentence.split(' '))
        else:
            chunks.append(sentence.split(' '))

    for chunk_id in range(len(chunks)):
        chunks[chunk_id] = ' '.join(chunks[chunk_id])
    return chunks

summarizer = load_model(model_choice)

def extract_text_from_pdf(uploaded_file):
    with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
        text = ""
        for page in doc:
            text += page.get_text()
    return text

def summarize_text(text):
    if text.strip() == "":
        return "Please enter text to summarize."
    summary = summarizer(text, max_length=max_length, min_length=min_length, do_sample=False)
    return summary[0]['summary_text']

button = st.button('Summarize')
with st.spinner("Generating Summary.."):
    if button:
        input_text = txt_input
        if uploaded_file is not None:
            input_text = extract_text_from_pdf(uploaded_file)
        chunks = generate_chunks(input_text)
        summary = []
        for chunk in chunks:
            summary.append(summarize_text(chunk))
        st.write(' '.join(summary))