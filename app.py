import streamlit as st
import pdfplumber
from google import genai

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="ShadowLearn AI",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- GLOBAL CSS (PREMIUM UI UPGRADES) ---
st.markdown("""
<style>
/* Main Background */
.stApp {
    background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #312e81 100%);
    color: #f8fafc;
}

/* Glassmorphism Metric Cards */
[data-testid="stMetric"] {
    background: rgba(255, 255, 255, 0.05);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    padding: 20px;
    border-radius: 16px;
    border: 1px solid rgba(255, 255, 255, 0.1);
    box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
    transition: transform 0.3s ease;
}
[data-testid="stMetric"]:hover {
    transform: translateY(-5px);
}

/* Primary Buttons */
.stButton > button {
    background: linear-gradient(90deg, #8b5cf6, #d946ef);
    color: white;
    border-radius: 12px;
    border: none;
    padding: 0.5rem 1rem;
    font-weight: 600;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(139, 92, 246, 0.3);
    width: 100%;
}
.stButton > button:hover {
    transform: scale(1.02);
    box-shadow: 0 6px 20px rgba(139, 92, 246, 0.5);
}

/* Download Buttons */
.stDownloadButton > button {
    background: linear-gradient(90deg, #06b6d4, #3b82f6);
    width: 100%;
    margin-top: 15px;
}

/* Flashcard CSS */
.flip-card {
    background-color: transparent;
    width: 100%;
    height: 250px;
    perspective: 1000px;
    margin-bottom: 25px;
}
.flip-card-inner {
    position: relative;
    width: 100%;
    height: 100%;
    text-align: center;
    transition: transform 0.6s cubic-bezier(0.4, 0.2, 0.2, 1);
    transform-style: preserve-3d;
    box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    border-radius: 20px;
}
.flip-card:hover .flip-card-inner {
    transform: rotateY(180deg);
}
.flip-card-front, .flip-card-back {
    position: absolute;
    width: 100%;
    height: 100%;
    backface-visibility: hidden;
    border-radius: 20px;
    padding: 25px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.2rem;
    font-weight: 600;
    line-height: 1.4;
    border: 1px solid rgba(255,255,255,0.2);
}
.flip-card-front {
    background: linear-gradient(135deg, #4f46e5, #7c3aed);
    color: white;
}
.flip-card-back {
    background: linear-gradient(135deg, #0ea5e9, #14b8a6);
    color: white;
    transform: rotateY(180deg);
}
.flashcard-label {
    position: absolute;
    top: 15px;
    left: 20px;
    font-size: 0.8rem;
    opacity: 0.7;
    text-transform: uppercase;
    letter-spacing: 1px;
}
</style>
""", unsafe_allow_html=True)

# --- INITIALIZE SESSION STATE ---
state_keys = ["extracted_text", "quiz_data", "flashcard_data", "study_plan_data", "exam_guide_data", "viva_data"]
for key in state_keys:
    if key not in st.session_state:
        st.session_state[key] = ""

# Dedicated state for the chatbot UI
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- HELPER FUNCTIONS ---
def extract_text_from_pdf(pdf_file):
    """Extracts text from an uploaded PDF file using pdfplumber."""
    text = ""
    try:
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
        
        if not text.strip():
            return "WARNING: No text found. If this is a scanned document or images of notes, you need an OCR tool to extract the text."
            
        return text
    except Exception as e:
        return f"Error reading PDF: {e}"

def generate_content(api_key, prompt, text=""):
    """Calls the Gemini API to generate content."""
    try:
        client = genai.Client(api_key=api_key)

        full_prompt = f"{prompt}\n\nSource Text:\n{text}" if text else prompt

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=full_prompt
        )

        return response.text

    except Exception as e:
        return f"Gemini API Error: {e}"

def create_flashcard_html(front, back):
    """Generates the HTML for the interactive 3D flip card."""
    return f"""
    <div class="flip-card">
      <div class="flip-card-inner">
        <div class="flip-card-front">
          <span class="flashcard-label">Question</span>
          <div>{front}</div>
        </div>
        <div class="flip-card-back">
          <span class="flashcard-label">Answer</span>
          <div>{back}</div>
        </div>
      </div>
    </div>
    """

# --- SIDEBAR ---
with st.sidebar:
    st.title("⚙️ Setup Workspace")
    
    api_key = st.text_input("🔑 Google Gemini API Key:", type="password")
    st.markdown("🔗 **[Get a free API key from Google AI Studio](https://aistudio.google.com/app/apikey)**")
    
    if not api_key:
        st.warning("⚠️ API Key required to generate content.")
    
    st.divider()
    
    uploaded_file = st.file_uploader("📄 Upload PDF Notes", type=["pdf"])
    if uploaded_file is not None:
        if st.button("Extract Text 🚀"):
            with st.spinner("Extracting knowledge..."):
                st.session_state.extracted_text = extract_text_from_pdf(uploaded_file)
                st.success("✅ Text extracted successfully!")

    st.divider()
    st.markdown("### 📊 Workspace Status")
    st.markdown(f"**API Key:** {'✅ Connected' if api_key else '❌ Missing'}")
    
    notes_status = '❌ Missing'
    if st.session_state.extracted_text:
        if "WARNING" in st.session_state.extracted_text:
            notes_status = '⚠️ Invalid PDF'
        else:
            notes_status = '✅ Loaded'
    st.markdown(f"**Notes:** {notes_status}")

# --- MAIN LAYOUT ---
st.markdown("<h1 style='text-align:center; font-size: 3.5rem; margin-bottom: 0;'>🚀 ShadowLearn AI</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; font-size: 1.2rem; color: #94a3b8; margin-bottom: 2rem;'>Your Next-Gen AI Study Companion</p>", unsafe_allow_html=True)

# Metrics Grid
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Tools Available", "7 Modules", "Active")
with col2:
    st.metric("AI Engine", "Gemini 2.5 Flash", "Turbo")
with col3:
    char_count = len(st.session_state.extracted_text) if "WARNING" not in st.session_state.extracted_text else 0
    st.metric("Notes Extracted", f"{char_count} chars", "Ready" if char_count > 0 else "Waiting")

st.write("<br>", unsafe_allow_html=True)

# --- TABS ---
tabs = st.tabs([
    "📄 Notes", "📝 Quizzes", "🗂️ Flashcards", 
    "📅 Study Plan", "💬 Tutor Chat", "🎯 Exam Booster", "🎤 Viva"
])

def is_ready():
    """Checks if API key and valid notes are present."""
    if not api_key:
        st.warning("⚠️ Please enter your Google Gemini API key in the sidebar.")
        return False
    if not st.session_state.extracted_text or "WARNING" in st.session_state.extracted_text:
        st.warning("⚠️ Please upload and extract valid text from a PDF first.")
        return False
    return True

# TAB 1: Extracted Notes
with tabs[0]:
    st.header("📄 Your Study Material")
    if st.session_state.extracted_text:
        if "WARNING: No text found" in st.session_state.extracted_text:
            st.error(st.session_state.extracted_text)
        else:
            st.text_area("Review and edit your extracted text:", st.session_state.extracted_text, height=400)
    else:
        st.info("👈 Please upload a PDF and extract text from the sidebar to begin.")

# TAB 2: Quizzes
with tabs[1]:
    st.header("📝 Knowledge Check")
    if st.button("Generate Quiz", key="btn_quiz"):
        if is_ready():
            with st.spinner("Crafting your quiz..."):
                prompt = "Based on the text, generate a 5-question multiple-choice quiz. Use bold headings. Include an answer key at the very end."
                st.session_state.quiz_data = generate_content(api_key, prompt, st.session_state.extracted_text)
            
    if st.session_state.quiz_data:
        st.markdown(st.session_state.quiz_data)
        st.download_button("📥 Download Quiz", st.session_state.quiz_data, "quiz.txt")

# TAB 3: Flashcards (Interactive 3D Grid)
with tabs[2]:
    st.header("🗂️ Smart Flashcards")
    st.markdown("Hover over the cards to reveal the answers!")
    if st.button("Generate Flashcards", key="btn_flash"):
        if is_ready():
            with st.spinner("Generating flashcards..."):
                prompt = """Generate EXACTLY 10 flashcards from the notes.
                Format EXACTLY like this (No markdown, no bullet points, no asterisks):
                QUESTION: [Your question here]
                ANSWER: [Your answer here]"""
                st.session_state.flashcard_data = generate_content(api_key, prompt, st.session_state.extracted_text)
                
    if st.session_state.flashcard_data:
        # Robust Parsing & 2-Column Grid Layout
        cards = st.session_state.flashcard_data.split("QUESTION:")
        valid_cards = []
        for card in cards:
            if "ANSWER:" in card:
                front, back = card.split("ANSWER:")
                # Clean up asterisks if AI accidentally adds them
                valid_cards.append((front.replace("*", "").strip(), back.replace("*", "").strip()))
        
        if valid_cards:
            col1, col2 = st.columns(2)
            for i, (front, back) in enumerate(valid_cards):
                with col1 if i % 2 == 0 else col2:
                    st.markdown(create_flashcard_html(front, back), unsafe_allow_html=True)

        st.download_button("📥 Download Flashcards as Text", st.session_state.flashcard_data, "flashcards.txt")

# TAB 4: Study Plan
with tabs[3]:
    st.header("📅 Personalized Study Plan")
    if st.button("Create Plan", key="btn_plan"):
        if is_ready():
            with st.spinner("Structuring study plan..."):
                prompt = "Break this text down into a structured, day-by-day study plan. Use markdown tables where appropriate to show Day, Topic, and Time required."
                st.session_state.study_plan_data = generate_content(api_key, prompt, st.session_state.extracted_text)
            
    if st.session_state.study_plan_data:
        st.markdown(st.session_state.study_plan_data)
        st.download_button("📥 Download Study Plan", st.session_state.study_plan_data, "study_plan.txt")

# TAB 5: Ask Notes (Modern Chat UI)
with tabs[4]:
    st.header("💬 Ask Your AI Tutor")
    st.markdown("Have a specific question? Chat directly with your notes!")
    
    # Display chat history
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat Input Box
    if question := st.chat_input("Ask a question about your notes..."):
        if not is_ready():
            pass # The is_ready function handles showing the warning
        else:
            # Show user message
            st.chat_message("user").markdown(question)
            st.session_state.chat_history.append({"role": "user", "content": question})
            
            # Generate & show AI response
            with st.spinner("Thinking..."):
                prompt = f"Answer strictly using these notes:\n{st.session_state.extracted_text}\n\nQuestion: {question}"
                answer = generate_content(api_key, prompt)
                
            st.chat_message("assistant").markdown(answer)
            st.session_state.chat_history.append({"role": "assistant", "content": answer})

# TAB 6: Exam Booster
with tabs[5]:
    st.header("🎯 Exam Booster")
    if st.button("Generate Exam Guide", key="btn_exam"):
        if is_ready():
            with st.spinner("Analyzing high-yield topics..."):
                prompt = """Analyze notes and generate: 
                1. 🌟 Important Topics 
                2. ❓ Most Likely Exam Questions 
                3. 📝 Quick Revision Notes 
                4. 🧮 Key Formulas/Concepts. 
                Use rich markdown formatting and emojis."""
                st.session_state.exam_guide_data = generate_content(api_key, prompt, st.session_state.extracted_text)
            
    if st.session_state.exam_guide_data:
        st.markdown(st.session_state.exam_guide_data)
        st.download_button("📥 Download Exam Guide", st.session_state.exam_guide_data, "exam_guide.txt")

# TAB 7: Viva Questions
with tabs[6]:
    st.header("🎤 Viva & Interview Prep")
    if st.button("Generate Viva Questions", key="btn_viva"):
        if is_ready():
            with st.spinner("Preparing oral questions..."):
                prompt = "Generate 15 viva/interview questions from these notes. Categorize them into '🟢 Easy', '🟡 Medium', and '🔴 Hard'. Keep answers concise."
                st.session_state.viva_data = generate_content(api_key, prompt, st.session_state.extracted_text)
            
    if st.session_state.viva_data:
        st.markdown(st.session_state.viva_data)
        st.download_button("📥 Download Viva Prep", st.session_state.viva_data, "viva_questions.txt")