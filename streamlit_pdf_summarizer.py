import streamlit as st
import pypdf
import google.generativeai as genai



# Page configuration for better UX
st.set_page_config(page_title="PDF Summarizer with Gemini", page_icon="📄", layout="wide")

# Custom CSS for Futuristic UI & Modern Fonts
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;700&family=Inter:wght@300;400;600&display=swap');

    /* Global font changes */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    h1, h2, h3, h4, h5, h6 {
        font-family: 'Orbitron', sans-serif !important;
        color: #00F0FF !important; /* Neon Cyan */
        text-shadow: 0 0 8px rgba(0, 240, 255, 0.4);
    }

    /* App Background */
    .stApp {
        background-color: #0A0E17;
        background-image: radial-gradient(circle at 50% 0%, #151C2C 0%, #0A0E17 60%);
        color: #E0E6ED;
    }

    /* Main Body Text & Response ensuring visibility */
    .stMarkdown, .stMarkdown p, .stMarkdown li, .stText {
        color: #E0E6ED !important;
        font-size: 1.05rem;
        line-height: 1.6;
    }
    
    strong {
        color: #FFFFFF !important;
        text-shadow: 0 0 2px rgba(255,255,255,0.2);
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #0D131F !important;
        border-right: 1px solid rgba(0, 240, 255, 0.15);
    }

    /* Input Labels */
    label {
        color: #00F0FF !important;
        font-family: 'Orbitron', sans-serif;
    }

    /* Buttons */
    .stButton>button {
        background: linear-gradient(90deg, #00F0FF 0%, #7000FF 100%);
        color: #FFFFFF !important;
        border: none;
        border-radius: 8px;
        font-family: 'Orbitron', sans-serif;
        font-weight: 600;
        letter-spacing: 1px;
        box-shadow: 0 4px 15px rgba(112, 0, 255, 0.4);
        transition: all 0.3s ease-in-out;
    }

    .stButton>button:hover {
        box-shadow: 0 6px 20px rgba(0, 240, 255, 0.6);
        transform: translateY(-2px);
        border: none;
    }

    /* File Uploader Area */
    [data-testid="stFileUploadDropzone"] {
        background-color: rgba(13, 19, 31, 0.5);
        border: 1px dashed rgba(0, 240, 255, 0.4);
        border-radius: 10px;
    }

    /* Output/Summary Container */
    [data-testid="stVerticalBlockBorderWrapper"] {
        border: 1px solid rgba(0, 240, 255, 0.3) !important;
        background-color: rgba(10, 14, 23, 0.8) !important;
        border-radius: 12px;
        box-shadow: inset 0 0 20px rgba(0, 240, 255, 0.05);
        padding: 1.5rem;
    }

    /* Progress/Spinner Text */
    .stSpinner > div > div {
        color: #00F0FF !important;
        font-family: 'Orbitron', sans-serif;
    }
</style>
""", unsafe_allow_html=True)

st.title("📄 PDF Summarizer Powered by Gemini AI")
st.markdown("Upload your PDF document, extract its text, and get a comprehensive summary using Google's Gemini AI.")

# Sidebar for API Key and Configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    api_key = st.text_input("Enter Gemini API Key", type="password", help="Get your API key from Google AI Studio")
    if not api_key:
        st.warning("⚠️ Please enter your API Key to proceed.")
        st.markdown("[Get an API key here](https://aistudio.google.com/app/apikey)")
    st.markdown("---")
    st.markdown("""
    **How to use:**
    1. Enter your Gemini API Key in the sidebar.
    2. Upload a PDF file in the main area.
    3. Choose your desired summary format.
    4. Click on 'Generate Summary'.
    """)

# Main content area UI
col1, col2 = st.columns(2)

with col1:
    st.subheader("📁 Upload Document")
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
    
    if uploaded_file is not None:
        st.success(f"File '{uploaded_file.name}' uploaded successfully!")

with col2:
    st.subheader("📑 Summary Options")
    summary_type = st.radio(
        "Choose summary format:",
        ("Bullet Points", "Paragraph", "Executive Summary")
    )
    
    generate_btn = st.button("Generate Summary 🚀", use_container_width=True, disabled=not (uploaded_file and api_key))

# Processing and Output
if generate_btn and uploaded_file and api_key:
    # Set the Gemini API key
    genai.configure(api_key=api_key)

    extracted_text = ""
    with st.spinner("Extracting text from PDF..."):
        try:
            # 1. Extract text using pypdf
            reader = pypdf.PdfReader(uploaded_file)
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    extracted_text += text + "\n"
            
            if not extracted_text.strip():
                st.error("Could not extract any text from the PDF. It might be scanned or image-based.")
                st.stop()
                
        except Exception as e:
            st.error(f"Error reading PDF: {e}")
            st.stop()
            
    with st.spinner("Generating summary using Gemini AI..."):
        try:
            # 2. Initialize Gemini Client - This line is no longer strictly needed if using genai.configure()
            
            # 3. Construct prompt based on user choice
            if summary_type == "Bullet Points":
                format_instruction = "Format the output cleanly using Markdown with bullet points, highlighting key themes and essential data."
            elif summary_type == "Paragraph":
                format_instruction = "Provide a cohesive, well-structured multi-paragraph summary."
            else:
                format_instruction = "Provide a high-level executive summary, focusing on the main purpose, findings, and conclusions."

            prompt = f"""
            Please provide a comprehensive summary of the following text extracted from a PDF document.
            
            {format_instruction}
            
            Text to summarize:
            {extracted_text}
            """
            
            # 4. Generate content using Gemini 2.5 Flash
            # Directly call genai.GenerativeModel after configuring API key
            model = genai.GenerativeModel(model_name="gemini-2.5-flash")
            response = model.generate_content(
                contents=prompt + "\n\nInclude: funny and hilarious emoji reaction"
            )
            
            st.markdown("---")
            st.subheader("📊 Document Summary")
            with st.container(border=True):
                st.markdown(response.text)
            
        except errors.APIError as e:
            st.error(f"API Error occurred: {e}")
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")