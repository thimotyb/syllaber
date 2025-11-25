import streamlit as st
import os
from src.pdf_processor import extract_text_from_pdf
from src.syllabus_generator import generate_syllabus, generate_topic_mapping
from src.course_manager import CourseManager

st.set_page_config(page_title="Syllaber", layout="wide")

# --- Custom CSS for Tighter Layout & Aesthetics ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
    
    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif;
    }
    
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    h1, h2, h3 {
        font-weight: 600;
        color: #1E1E1E;
    }
    
    .stButton button {
        width: 100%;
        border-radius: 6px;
        font-weight: 600;
    }
    
    /* Reduce spacing between elements */
    div[data-testid="stVerticalBlock"] > div {
        margin-bottom: -15px;
    }
    
    .stExpander {
        border: 1px solid #E0E0E0;
        border-radius: 6px;
        background-color: #FAFAFA;
    }
</style>
""", unsafe_allow_html=True)

# Initialize CourseManager
course_manager = CourseManager()

st.title("Syllaber")
st.caption("Course Syllabus Generator")

# Sidebar for configuration and course management
with st.sidebar:
    st.header("Configuration")
    
    # Load key from Key.txt
    api_key = ""
    if os.path.exists("Key.txt"):
        with open("Key.txt", "r") as f:
            api_key = f.read().strip()
            
    if not api_key:
        st.error("API Key not found! Please create a 'Key.txt' file with your Gemini API key in the project root.")
    else:
        st.success("API Key loaded from Key.txt")
    
    st.markdown("---")
    st.header("Course Management")
    
    # Create New Course
    new_course_name = st.text_input("New Course Name")
    if st.button("Create Course"):
        if new_course_name:
            if course_manager.create_course(new_course_name):
                st.success(f"Course '{new_course_name}' created!")
                st.rerun()
            else:
                st.error("Course already exists.")
    
    st.markdown("---")
    
    # Select Course
    courses = course_manager.list_courses()
    selected_course = st.selectbox("Select Course", courses) if courses else None
    
    if selected_course:
        st.write("") # Spacer
        if st.button("Delete Current Course", type="primary"):
            course_manager.delete_course(selected_course)
            st.success(f"Deleted course '{selected_course}'")
            st.rerun()

if selected_course and api_key:
    st.header(f"Managing: {selected_course}")
    
    # Get current content
    content = course_manager.get_course_content(selected_course)
    
    # --- Resources Section ---
    with st.expander("📂 PDF Documents", expanded=True):
        uploaded_files = st.file_uploader("Upload PDFs", type="pdf", accept_multiple_files=True, label_visibility="collapsed")
        if uploaded_files:
            for uploaded_file in uploaded_files:
                course_manager.add_pdf(selected_course, uploaded_file, uploaded_file.name)
            st.success(f"Uploaded {len(uploaded_files)} files.")
            st.rerun()
            
        if content['pdf_files']:
            st.markdown("**Current PDFs:**")
            for pdf in content['pdf_files']:
                st.text(f"📄 {pdf}")
        else:
            st.info("No PDFs uploaded yet.")

    with st.expander("🔗 Web Resources", expanded=True):
        c1, c2, c3 = st.columns([3, 3, 1])
        with c1:
            link_url = st.text_input("URL", placeholder="https://example.com")
        with c2:
            link_desc = st.text_input("Description", placeholder="Resource Title")
        with c3:
            st.write("") # Spacer
            st.write("") # Spacer
            if st.button("Add"):
                if link_url and link_desc:
                    course_manager.add_link(selected_course, link_url, link_desc)
                    st.success("Added!")
                    st.rerun()
        
        if content['links']:
            st.markdown("**Current Links:**")
            for link in content['links']:
                st.markdown(f"- [{link['description']}]({link['url']})")
        else:
            st.info("No web links added yet.")

    st.markdown("---")
    
    # --- Generation Section ---
    st.subheader("Generation Settings")
    additional_instructions = st.text_area("Additional Instructions (Optional)", placeholder="e.g., Focus on practical examples, make it 8 weeks long, etc.")
    
    if st.button("Generate Syllabus"):
        # 1. Aggregate Text from all PDFs
        all_text = ""
        pdf_dir = os.path.join(course_manager.root_dir, selected_course, "pdfs")
        
        with st.spinner("Extracting text from all PDFs..."):
            for pdf_file in content['pdf_files']:
                file_path = os.path.join(pdf_dir, pdf_file)
                text = extract_text_from_pdf(file_path)
                all_text += f"\n--- Source: {pdf_file} ---\n{text}\n"
        
        st.info(f"Total extracted text length: {len(all_text)} characters.")
        
        # 2. Format Web Resources
        web_resources_text = ""
        for link in content['links']:
            web_resources_text += f"- {link['description']}: {link['url']}\n"
            
        # 3. Generate Content
        # Generate English Syllabus
        with st.spinner("Generating English Syllabus..."):
            syllabus_en = generate_syllabus(all_text, web_resources_text, additional_instructions, api_key, language='en')
        
        # Generate Italian Syllabus
        with st.spinner("Generating Italian Syllabus..."):
            syllabus_it = generate_syllabus(all_text, web_resources_text, additional_instructions, api_key, language='it')
            
        # Generate Topic Mapping
        with st.spinner("Generating Topic Mapping..."):
            topic_mapping = generate_topic_mapping(all_text, api_key)
            
        # Display Results
        res_col1, res_col2 = st.columns(2)
        
        with res_col1:
            st.subheader("English Syllabus")
            st.markdown(syllabus_en)
            st.download_button("Download English Syllabus", syllabus_en, file_name=f"{selected_course}_syllabus_en.md")
            
        with res_col2:
            st.subheader("Italian Syllabus")
            st.markdown(syllabus_it)
            st.download_button("Download Italian Syllabus", syllabus_it, file_name=f"{selected_course}_syllabus_it.md")
            
        st.subheader("Topic Mapping")
        st.markdown(topic_mapping)
        st.download_button("Download Topic Mapping", topic_mapping, file_name=f"{selected_course}_topic_mapping.md")

elif not selected_course:
    st.info("Please create or select a course from the sidebar.")
