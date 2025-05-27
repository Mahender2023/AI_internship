# streamlit_translator_gcp.py (Relevant parts modified)
import streamlit as st
from google.cloud import translate_v2 as translate
import os
import html # <--- ADD THIS IMPORT
import dotenv

# --- Language Configuration ---
LANGUAGES = {
    "English": "en", "Spanish": "es", "French": "fr", "German": "de",
    "Italian": "it", "Portuguese": "pt", "Russian": "ru", "Japanese": "ja",
    "Korean": "ko", "Chinese (Simplified)": "zh-CN", "Chinese (Traditional)": "zh-TW",
    "Arabic": "ar", "Dutch": "nl", "Swedish": "sv",

    # Languages of India
    "Hindi": "hi", "Bengali": "bn", "Telugu": "te", "Marathi": "mr",
    "Tamil": "ta", "Urdu": "ur", "Gujarati": "gu", "Kannada": "kn",
    "Odia (Oriya)": "or", "Malayalam": "ml", "Punjabi": "pa", "Assamese": "as",
    "Maithili": "mai", "Sanskrit": "sa", "Nepali": "ne", "Konkani": "kok",
    "Sindhi": "sd", "Dogri": "doi", "Manipuri (Meitei)": "mni",
}
SOURCE_LANGUAGES_OPTIONS_GCP = {"Auto Detect": None, **LANGUAGES}
TARGET_LANGUAGES_OPTIONS_GCP = LANGUAGES

# ... (keep check_gcp_credentials and translate_text_gcp functions as they are) ...
def check_gcp_credentials(): # Keep this function
    if os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
        if os.path.exists(os.getenv("GOOGLE_APPLICATION_CREDENTIALS")):
            return True, "Service account credentials found."
        else:
            return False, "GOOGLE_APPLICATION_CREDENTIALS path is invalid."
    elif os.getenv("GOOGLE_API_KEY"):
        return True, "GOOGLE_API_KEY environment variable found."
    else:
        return None, "No explicit GOOGLE_APPLICATION_CREDENTIALS or GOOGLE_API_KEY found. Ensure Application Default Credentials (ADC) are configured (e.g., via `gcloud auth application-default login`)."


def translate_text_gcp(text, target_language, source_language=None, project_id_for_client=None): # Keep this function
    try:
        translate_client = translate.Client()
        if isinstance(text, bytes):
            text = text.decode("utf-8")
        result = translate_client.translate(
            text,
            target_language=target_language,
            source_language=source_language
        )
        detected_source = result.get('detectedSourceLanguage', source_language)
        return result["translatedText"], detected_source
    except Exception as e:
        return f"Error: {e}", source_language
# --- Streamlit UI ---
st.set_page_config(page_title="GCP Translator", layout="wide")
st.title("🌐 Language Translator (Google Cloud API)")
st.markdown("""
    Translate text using the official Google Cloud Translation API.
    This method is robust and recommended for reliable translations.
""")

st.sidebar.header("GCP Configuration")
gcp_project_id_input = st.sidebar.text_input(
    "GCP Project ID (Optional, for reference)",
    help="Usually inferred from credentials. Enter if you need to reference a specific project for your setup."
)
cred_status, cred_message = check_gcp_credentials()
if cred_status is True:
    st.sidebar.success(cred_message)
elif cred_status is False:
    st.sidebar.error(cred_message)
else:
    st.sidebar.warning(cred_message)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Input")
    text_to_translate = st.text_area("Enter text to translate:", height=200, key="input_text_gcp")
    source_lang_display_gcp = st.selectbox(
        "Source Language:",
        options=list(SOURCE_LANGUAGES_OPTIONS_GCP.keys()),
        index=0,
        key="source_lang_gcp"
    )
    source_lang_code_gcp = SOURCE_LANGUAGES_OPTIONS_GCP[source_lang_display_gcp]

with col2:
    st.subheader("Translation")
    target_lang_display_gcp = st.selectbox(
        "Target Language:",
        options=list(TARGET_LANGUAGES_OPTIONS_GCP.keys()),
        index=0,
        key="target_lang_gcp"
    )
    target_lang_code_gcp = TARGET_LANGUAGES_OPTIONS_GCP[target_lang_display_gcp]

    # Placeholder for the output area so it doesn't jump around
    output_placeholder = st.empty()

    if st.button("Translate", key="translate_button_gcp", use_container_width=True, type="primary"):
        if not text_to_translate:
            st.warning("Please enter some text to translate.")
            output_placeholder.markdown("") # Clear previous output
        elif not target_lang_code_gcp:
            st.warning("Please select a target language.")
            output_placeholder.markdown("") # Clear previous output
        elif source_lang_code_gcp == target_lang_code_gcp and source_lang_code_gcp is not None:
            st.info("Source and Target languages are the same. No translation needed.")
            # Display original text in the styled box
            escaped_original_text = html.escape(text_to_translate)
            styled_output_html = f"""
            <div style="
                padding: 15px;
                border: 1px solid #ddd;
                border-radius: 8px;
                background-color: #f9f9f9;
                min-height: 200px; /* Match text_area height */
                overflow-wrap: break-word; /* Ensure long words wrap */
                white-space: pre-wrap; /* Preserve whitespace and newlines */
            ">
                <strong>{escaped_original_text}</strong>
            </div>
            """
            output_placeholder.markdown(styled_output_html, unsafe_allow_html=True)
        else:
            if cred_status is False:
                 st.error(f"Cannot proceed with translation. {cred_message}")
                 output_placeholder.markdown("") # Clear previous output
            else:
                with st.spinner(f"Translating to {target_lang_display_gcp}..."):
                    translated_text, detected_source_code = translate_text_gcp(
                        text_to_translate,
                        target_lang_code_gcp,
                        source_lang_code_gcp,
                        project_id_for_client=gcp_project_id_input if gcp_project_id_input else None
                    )

                    if "Error:" in str(translated_text):
                        st.error(str(translated_text))
                        output_placeholder.markdown("") # Clear previous output
                    else:
                        if source_lang_display_gcp == "Auto Detect" and detected_source_code:
                            detected_lang_name = next((name for name, code in LANGUAGES.items() if code == detected_source_code), detected_source_code)
                            st.info(f"Detected source language: {detected_lang_name} ({detected_source_code})")
                        elif source_lang_display_gcp != "Auto Detect":
                             st.info(f"Source language: {source_lang_display_gcp} ({source_lang_code_gcp})")

                        st.success("Translation successful!")
                        
                        # --- MODIFIED OUTPUT ---
                        escaped_translated_text = html.escape(translated_text) # Escape HTML special chars
                        styled_output_html = f"""
                        <div style="
                            padding: 15px; /* More padding */
                            border: 1px solid #4CAF50; /* Green border for success */
                            border-radius: 8px; /* More rounded corners */
                            background-color: #e8f5e9; /* Light green background */
                            font-size: 1.05em; /* Slightly larger font */
                            min-height: 200px; /* Match text_area height */
                            overflow-wrap: break-word; /* Ensure long words wrap */
                            white-space: pre-wrap; /* Preserve whitespace and newlines */
                        ">
                            <strong>{escaped_translated_text}</strong>
                        </div>
                        """
                        output_placeholder.markdown(styled_output_html, unsafe_allow_html=True)
                        # --- END OF MODIFIED OUTPUT ---
    else:
        # Initial state for the output box (empty but styled)
        initial_empty_output_html = f"""
        <div style="
            padding: 15px;
            border: 1px solid #ddd;
            border-radius: 8px;
            background-color: #f9f9f9;
            min-height: 200px;
            color: #aaa; /* Placeholder text color */
        ">
            <strong>Translated text will appear here...</strong>
        </div>
        """
        output_placeholder.markdown(initial_empty_output_html, unsafe_allow_html=True)


st.sidebar.header("Language Codes")
with st.sidebar.expander("Show common language codes"):
    st.json(LANGUAGES)