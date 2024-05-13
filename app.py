
"""
# Sniper
A UI for anyone to check out the power of Vision Models + LLMs to automate Web browsing by giving control of mouse.
"""

import streamlit as st
import time
from PIL import Image, ImageOps, ImageDraw, ImageFont
import main
import tempfile
import os


st.title('Sniper 🧿')
st.subheader("Mouse Control Capability for Multi-Modal LLMs")

# Using object notation
with st.sidebar:
    st.header("Sniper Input window:")
    with st.form("My_form"):
        st.subheader("1.  Upload Your Web Screenshot OR image")
        uploaded_file = st.file_uploader("Upload a screenshot of just your Browser", type=['png', 'jpg'], accept_multiple_files = False)
        grid_size = st.number_input("Pinpoint Quality", value = 3,disabled= True)
        st.subheader("2. Write your Query")
        query = st.text_area("What are you trying to do? (Be Descriptive and obvious)", "Please click on ONLY the FIRST Suncorp Group data scientist role.")

        # Every form must have a submit button.
        submitted = st.form_submit_button("Submit")

if submitted:
    if uploaded_file is not None:
        tfile = tempfile.NamedTemporaryFile(delete=False) 
        tfile.write(uploaded_file.read())
        uploaded_image_name = os.path.basename(tfile.name)
        uploaded_image = Image.open(uploaded_file)
        uploaded_image.save(f"{uploaded_image_name}.png",quality=95)

    st.image(uploaded_file, caption='Input Image')
    with st.spinner('Wait for it...'):
        final_image_path = main.main(query, f"{uploaded_image_name}.png")
        st.image(final_image_path, caption='Taget Eliminated')
    st.success('Target Eliminated.')
    






