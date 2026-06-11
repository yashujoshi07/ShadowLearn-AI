import streamlit as st
import PyPDF2
import google.generativeai as genai

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="🚀 ShadowLearn AI", page_icon="📚", layout="wide")

# --- INITIALIZE SESSION STATE ---
# We use session state to keep data from disappearing when Streamlit reruns
if "extracted_text" not in st.session_state:
    st.session_state.extracted_text = ""
if "quiz_data" not in st.session_state:
    st.session_state.quiz_data = ""
if "flashcard_data" not in st.session_state:
    st.session_state.flashcard_data = ""
if "study_plan_data" not in st.session_state:
    st.session_state.study_plan_data = ""
if "exam_guide_data" not in st.session_state:
    st.session_state.exam_guide_data = ""
if "viva_data" not in st.session_state:
    st.session_state.viva_data = ""

# --- HELPER FUNCTIONS ---
def extract_text_from_pdf(pdf_file):
    """Extracts text from an uploaded PDF file."""
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted + "\n"
    return text

def generate_content(api_key, prompt, text):
    """Calls the Gemini API to generate content based on the prompt and text."""
    try:
        genai.configure(api_key=api_key)
        # Using gemini-2.5-flash as it is fast and excellent for text tasks
        model = genai.GenerativeModel('gemini-2.5-flash')
        full_prompt = f"{prompt}\n\nSource Text:\n{text}"
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:

        error = str(e)

        if "429" in error:
            return """
🚫 AI limit reached.

Please wait 30 seconds and try again.

Free Gemini accounts have request limits.
"""

        return f"Error: {error}"

# --- SIDEBAR: SETUP & UPLOAD ---
st.sidebar.title("⚙️ Setup & Upload")
api_key = st.sidebar.text_input("Enter Google Gemini API Key:", type="password")
st.sidebar.markdown("[Get an API key here](https://aistudio.google.com/app/apikey)")

st.sidebar.divider()

uploaded_file = st.sidebar.file_uploader("Upload your PDF Notes", type=["pdf"])

if uploaded_file is not None:
    if st.sidebar.button("Extract Text"):
        with st.spinner("Extracting text from PDF..."):
            extracted_text = extract_text_from_pdf(uploaded_file)
            st.session_state.extracted_text = extracted_text
            st.sidebar.success("Text extracted successfully!")

# --- MAIN LAYOUT ---
st.title("ShadowLearn AI")
st.caption(
    "AI-powered study assistant for quizzes, flashcards, viva preparation and exam success."
)
# Create tabs for different features
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(["📄 Extracted Notes", "📝 Quizzes", "🗂️ Flashcards", "📅 Study Plan", "💬 Ask Notes", "🎯 Exam Booster",  "🎤 Viva Questions"])

# TAB 1: Extracted Notes
with tab1:
    st.header("Extracted Text")
    if st.session_state.extracted_text:
        with st.expander("View Extracted Text", expanded=True):
            st.text_area("You can edit the text before generating materials if needed:", 
                         st.session_state.extracted_text, height=400)
    else:
        st.info("Please upload a PDF and click 'Extract Text' in the sidebar.")

# TAB 2: Quizzes
with tab2:
    st.header("Generate a Practice Quiz")
    if st.button("Generate Quiz"):
        if not api_key:
            st.warning("Please enter your API key in the sidebar.")
        elif not st.session_state.extracted_text:
            st.warning("Please extract text from a PDF first.")
        else:
            with st.spinner("Generating quiz..."):
                prompt = "Based on the following text, generate a 5-question multiple-choice quiz. Include an answer key at the very end."
                st.session_state.quiz_data = generate_content(api_key, prompt, st.session_state.extracted_text)
    
    if st.session_state.quiz_data:

        st.markdown(st.session_state.quiz_data)

        st.download_button(
            "Download Quiz",
            st.session_state.quiz_data,
            "quiz.txt"
        )

# TAB 3: Flashcards
with tab3:
    st.header("Generate Flashcards")
    if st.button("Generate Flashcards"):
        if not api_key:
            st.warning("Please enter your API key in the sidebar.")
        elif not st.session_state.extracted_text:
            st.warning("Please extract text from a PDF first.")
        else:
            with st.spinner("Generating flashcards..."):
                prompt = "Create 10 essential flashcards based on the following text. Format them clearly as 'Front: [Concept/Question]' and 'Back: [Definition/Answer]'."
                st.session_state.flashcard_data = generate_content(api_key, prompt, st.session_state.extracted_text)
    
    if st.session_state.flashcard_data:

        st.markdown(st.session_state.flashcard_data)

        st.download_button(
            "Download Flashcards",
            st.session_state.flashcard_data,
            "flashcards.txt"
        )
            
# TAB 4: Study Plan
with tab4:
    st.header("Generate a Study Plan")
    if st.button("Generate Study Plan"):
        if not api_key:
            st.warning("Please enter your API key in the sidebar.")
        elif not st.session_state.extracted_text:
            st.warning("Please extract text from a PDF first.")
        else:
            with st.spinner("Structuring study plan..."):
                prompt = "Analyze the following text and break it down into a structured, step-by-step study plan. Organize it logically by topics or study sessions."
                st.session_state.study_plan_data = generate_content(api_key, prompt, st.session_state.extracted_text)
    
    if st.session_state.study_plan_data:

        st.markdown(st.session_state.study_plan_data)

        st.download_button(
            "Download Study Plan",
            st.session_state.study_plan_data,
            "study_plan.txt"
        )
        
# TAB 5: Ask Notes

with tab5:
    st.header("Ask Your Notes")

    question = st.text_input(
        "Ask any question from your notes:"
    )

    if st.button("Ask AI Tutor"):

        if not api_key:
            st.warning("Please enter API key.")

        elif not st.session_state.extracted_text:
            st.warning("Please upload notes first.")

        else:

            prompt = f"""
            Answer only using these notes.

            Notes:
            {st.session_state.extracted_text}

            Question:
            {question}
            """

            answer = generate_content(
                api_key,
                prompt,
                ""
            )

            st.write(answer)
            
# TAB 6: Exam Booster

with tab6:

    st.header("Exam Booster")

    if st.button("Generate Exam Guide"):

        prompt = """
        Analyze the notes.

        Generate:

        1. Important Topics
        2. Most Likely Exam Questions
        3. Quick Revision Notes
        4. Key Formulas
        """

        st.session_state.exam_guide_data = generate_content(
            api_key,
            prompt,
            st.session_state.extracted_text
        )

    if st.session_state.exam_guide_data:

        st.markdown(
            st.session_state.exam_guide_data
        )

        st.download_button(
            "Download Exam Guide",
            st.session_state.exam_guide_data,
            "exam_guide.txt"
        )
        
# TAB 7: Viva Questions

with tab7:

    st.header("Viva Questions")

    if st.button("Generate Viva Questions"):

        if not api_key:
            st.warning("Please enter your API key.")

        elif not st.session_state.extracted_text:
            st.warning("Please upload notes first.")

        else:

            prompt = """
            Generate 15 viva questions and answers
            from these notes.

            Requirements:

            - Mix easy, medium and hard questions.
            - Keep answers concise.
            - Focus on conceptual understanding.
            - Format clearly.
            """

            st.session_state.viva_data = generate_content(
                api_key,
                prompt,
                st.session_state.extracted_text
            )

    if st.session_state.viva_data:

        st.markdown(
            st.session_state.viva_data
        )

        st.download_button(
            "Download Viva Questions",
            st.session_state.viva_data,
            "viva_questions.txt"
        )
        
        