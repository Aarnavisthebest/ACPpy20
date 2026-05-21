import base64
from io import BytesIO

import streamlit as st
from PIL import Image
from groq import Groq
import config

st.set_page_config(page_title="AI Food Guesser", page_icon="🍽️", layout="centered")

STYLES = {
    "Normal": (
        "Look at this image carefully and write a clear, detailed report. "
        "Describe the scene, /10 rating, and what could it be."
    ),
    "Detailed": (
        "Look at this image carefully and write a detailed image report. "
        "Mention color, details, and make the report have a list of which possible food it could be, and a list of ingredients,"
        "but still describe the food image correctly."
    ),
    "Detective": (
        "Look at this image like an expert. "
        "Write an inferance report with list of possible ingredients, observations, and smart deductions of what this food could be."
    ),
    "Cook": (
        "Look at this image and describe it in with cooking vocabulary. "
        "Make the report with cooking terms, possible recipes, and a guess of what the food is."
    ),
    "Hard Core": (
        "Look at this image with food and write 10 paragraphs about it. "
        "Describe the possible ingredients, /100 rating, possible recipes, and how if it is actually edible food, and if you should go to it."
    ),
}

client = Groq(api_key=config.GROQ_API_KEY)


st.title("🍽️ The Food Guesser")
st.write("Upload an image and let AI guess the item!")
st.markdown(
    "Choose an image, pick the report style, and click **Analyze Image**. "
    "The AI will study the image and write a detailed report."
)


def analyze_image(uploaded_file, style):
    encoded = base64.b64encode(uploaded_file.getvalue()).decode("utf-8")
    response = client.chat.completions.create(
        model=config.GROQ_VISION_MODEL,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": STYLES.get(style, STYLES["Normal"])},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{uploaded_file.type};base64,{encoded}"
                        },
                    },
                ],
            }
        ],
        temperature=0.8,
        max_completion_tokens=1000,
    )
    return response.choices[0].message.content


uploaded_file = st.file_uploader(
    "Upload an image",
    type=["png", "jpg", "jpeg", "webp"],
)


report_style = st.selectbox("Choose report style", list(STYLES))


if uploaded_file:
    st.image(
        Image.open(BytesIO(uploaded_file.getvalue())),
        caption="Uploaded Image",
        use_container_width=True,
    )

if st.button("🔍 Analyze Image"):
    if not config.GROQ_API_KEY:
        st.error("Groq API key is missing. Please add it to your .env file.")
    elif not uploaded_file:
        st.warning("Please upload an image first.")
    else:
        with st.spinner("The AI is studying your image..."):
            try:
                st.success("Report ready!")
                st.subheader("📝 AI Report")
                st.write(analyze_image(uploaded_file, report_style))
            except Exception as error:
                st.error(f"Something went wrong: {error}")