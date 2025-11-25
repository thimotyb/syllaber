import streamlit as st
import os
from src.pdf_processor import extract_text_from_pdf
from src.syllabus_generator import generate_syllabus, generate_topic_mapping
from src.course_manager import CourseManager
from src.web_scraper import scrape_text_from_url

# ... (rest of imports and setup)

st.set_page_config(page_title="Syllaber", layout="wide")

# --- Custom CSS for Tighter Layout & Aesthetics ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
    
    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif;
    }
    
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        max-width: 1400px;
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
        margin-bottom: -10px;
    }
    
    .stExpander {
        border: 1px solid #E0E0E0;
        border-radius: 6px;
        background-color: #FAFAFA;
    }
    
    /* Header Styling */
    .header-container {
        display: flex;
        align-items: center;
        margin-bottom: 10px;
    }
    
    .app-title {
        font-size: 1.5rem;
        font-weight: 600;
        color: #333;
        margin-left: 10px;
    }
    
    /* Logo Button Styling */
    button[kind="secondary"] {
        border: none;
        background: transparent;
        padding: 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize CourseManager
course_manager = CourseManager()

# --- Header & Logo ---
# Using columns to place logo in top LEFT
h_col1, h_col2 = st.columns([1, 5])

with h_col1:
    # SVG Logo
    logo_svg = """
    <svg width="40" height="40" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="#4A90E2" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        <path d="M2 17L12 22L22 17" stroke="#4A90E2" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        <path d="M2 12L12 17L22 12" stroke="#4A90E2" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
    """
    
    if st.button("ℹ️ Syllaber", help="Click for Instructions"):
        @st.dialog("About Syllaber")
        def show_instructions():
            st.markdown("""
            ### Welcome to Syllaber!
            
            **Syllaber** helps you create course syllabi from PDF textbooks and web resources.
            
            #### How to use:
            1.  **Create/Select a Course** from the sidebar.
            2.  **Upload PDFs** in the *Resources* panel (right).
            3.  **Add Web Links** if needed.
            4.  **Enter Instructions** in the *Generation* panel (center).
            5.  Click **Generate Syllabus**.
            
            The agent will analyze all your resources and produce a structured syllabus in English and Italian, along with a topic mapping.
            """)
        show_instructions()

# Load key silently
api_key = ""
if os.path.exists("Key.txt"):
    with open("Key.txt", "r") as f:
        api_key = f.read().strip()

selected_course = None

# Sidebar for course management AND resources
with st.sidebar:
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
    
    # Auto-load latest version logic
    if 'last_selected_course' not in st.session_state:
        st.session_state['last_selected_course'] = None

    if selected_course != st.session_state['last_selected_course']:
        st.session_state['last_selected_course'] = selected_course
        # Clear current loaded version first
        if 'loaded_version' in st.session_state:
            del st.session_state['loaded_version']
            del st.session_state['loaded_version_name']
            
        if selected_course:
            versions = course_manager.get_versions(selected_course)
            if versions:
                # Sort by version number descending to get the latest
                versions.sort(key=lambda x: x['version'], reverse=True)
                latest_version = versions[0]
                
                content = course_manager.get_version_content(selected_course, latest_version['version'])
                if content:
                    st.session_state['loaded_version'] = content
                    st.session_state['loaded_version_name'] = latest_version['name']
                    # Rerun to refresh the view immediately
                    st.rerun()

    if selected_course:
        st.write("") # Spacer
        if st.button("Delete Current Course", type="primary"):
            course_manager.delete_course(selected_course)
            st.success(f"Deleted course '{selected_course}'")
            st.rerun()
            
        st.markdown("---")
        
        # --- Resources Section (Moved to Sidebar) ---
        st.subheader("📂 Resources")
        
        # Get current content
        content = course_manager.get_course_content(selected_course)
        
        with st.expander("PDF Documents", expanded=True):
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

        with st.expander("Web Resources", expanded=False):
            st.caption("Add URLs for the AI to reference (e.g., documentation, public articles). Note: The AI cannot read file contents from these links directly.")
            link_url = st.text_input("URL", placeholder="https://example.com")
            link_desc = st.text_input("Description", placeholder="Resource Title")
            
            if st.button("Add Link"):
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


if selected_course and api_key:
    # --- Main Area: Generation Prompt ---
    st.subheader(f"✨ {selected_course}")
    
    additional_instructions = st.text_area(
        "Instructions for the Agent", 
        height=150,
        placeholder="Describe how you want the syllabus to be structured. E.g., 'Focus on practical labs', 'Make it 8 weeks long', 'Include a section on ethics'."
    )
    
    if st.button("Generate Syllabus", type="primary"):
        # 1. Aggregate Text from all PDFs
        all_text = ""
        pdf_dir = os.path.join(course_manager.root_dir, selected_course, "pdfs")
        
        # Re-fetch content to ensure we have latest
        content = course_manager.get_course_content(selected_course)
        
        with st.spinner("Extracting text from all PDFs..."):
            for pdf_file in content['pdf_files']:
                file_path = os.path.join(pdf_dir, pdf_file)
                text = extract_text_from_pdf(file_path)
                all_text += f"\n--- Source PDF: {pdf_file} ---\n{text}\n"
        
        # 2. Scrape Text from Web Resources
        web_resources_text = ""
        scraped_web_content = ""
        
        if content['links']:
            with st.status("Processing Web Resources...") as status:
                for link in content['links']:
                    url = link['url']
                    desc = link['description']
                    status.write(f"Scraping {desc} ({url})...")
                    
                    scraped_text = scrape_text_from_url(url)
                    
                    # Add to the text context for the LLM
                    scraped_web_content += f"\n--- Source Web: {desc} ({url}) ---\n{scraped_text}\n"
                    
                    # Also keep the list format for the prompt's "Web Resources" section
                    web_resources_text += f"- {desc}: {url}\n"
                status.update(label="Web Resources Processed", state="complete")
        
        # Combine PDF text and Scraped Web text
        full_context_text = all_text + "\n" + scraped_web_content
        
        st.info(f"Total extracted text length: {len(full_context_text)} characters (PDFs + Web).")
        
        if len(full_context_text) < 50:
            st.warning("⚠️ Very little text extracted. The AI might hallucinate if it has no source material. Please ensure PDFs have selectable text or URLs are accessible.")

        # 3. Generate Content
        # 3. Generate Content
        # Generate English Syllabus
        with st.spinner("Generating English Syllabus..."):
            syllabus_en = generate_syllabus(full_context_text, web_resources_text, additional_instructions, api_key, language='en')
        
        # Generate Italian Syllabus
        with st.spinner("Generating Italian Syllabus..."):
            syllabus_it = generate_syllabus(full_context_text, web_resources_text, additional_instructions, api_key, language='it')
            
        # Generate Topic Mapping
        with st.spinner("Generating Topic Mapping..."):
            topic_mapping = generate_topic_mapping(full_context_text, api_key)
            
        # Save Version
        version_num = course_manager.save_version(selected_course, syllabus_en, syllabus_it, topic_mapping)
        st.success(f"Syllabus generated and saved as Version {version_num}!")
            
        # Display Results
        st.markdown("---")
        res_tabs = st.tabs(["English Syllabus", "Italian Syllabus", "Topic Mapping"])
        
        with res_tabs[0]:
            st.markdown(syllabus_en)
            st.download_button("Download English Syllabus", syllabus_en, file_name=f"{selected_course}_syllabus_en.md")
            
        with res_tabs[1]:
            st.markdown(syllabus_it)
            st.download_button("Download Italian Syllabus", syllabus_it, file_name=f"{selected_course}_syllabus_it.md")
            
        with res_tabs[2]:
            st.markdown(topic_mapping)
            st.download_button("Download Topic Mapping", topic_mapping, file_name=f"{selected_course}_topic_mapping.md")

elif not selected_course:
    st.info("Please create or select a course from the sidebar.")

# --- History Sidebar Section ---
if selected_course:
    with st.sidebar:
        st.markdown("---")
        st.subheader("📜 History")
        versions = course_manager.get_versions(selected_course)
        
        if versions:
            # Sort by version number descending
            versions.sort(key=lambda x: x['version'], reverse=True)
            
            selected_version_name = st.selectbox(
                "Select Version", 
                options=[v['name'] for v in versions],
                format_func=lambda x: f"{x} ({next((v['timestamp'] for v in versions if v['name'] == x), '')})"
            )
            
            if st.button("Load Version"):
                version_num = int(selected_version_name.replace("v", ""))
                content = course_manager.get_version_content(selected_course, version_num)
                
                if content:
                    st.session_state['loaded_version'] = content
                    st.session_state['loaded_version_name'] = selected_version_name
                    st.rerun()
        else:
            st.info("No history yet.")


# --- Display Loaded Version (if any) ---
if 'loaded_version' in st.session_state and selected_course:
    st.markdown(f"### 📜 Viewing: {st.session_state['loaded_version_name']}")
    
    # Edit Mode Toggle
    edit_mode = st.toggle("✏️ Edit Mode", value=False)
    
    content = st.session_state['loaded_version']
    version_num = int(st.session_state['loaded_version_name'].split(" ")[0].replace("v", ""))
    
    res_tabs = st.tabs(["English Syllabus", "Italian Syllabus", "Topic Mapping"])
    
    # Helper to display content with Edit/View logic
    def display_content_tab(tab_key, content_key, pdf_key, pdf_name_key, label):
        if edit_mode:
            new_text = st.text_area(f"Edit {label}", value=content[content_key], height=600, key=f"edit_{tab_key}")
            if st.button(f"Save {label}", key=f"save_{tab_key}"):
                if course_manager.update_version_content(selected_course, version_num, content_key, new_text):
                    st.success("Saved and PDF regenerated!")
                    # Reload content
                    updated_content = course_manager.get_version_content(selected_course, version_num)
                    st.session_state['loaded_version'] = updated_content
                    st.rerun()
                else:
                    st.error("Error saving.")
        else:
            # Clean content of potential code fences
            clean_text = content[content_key]
            if clean_text.startswith("```markdown"):
                clean_text = clean_text.replace("```markdown", "", 1)
            if clean_text.startswith("```"):
                clean_text = clean_text.replace("```", "", 1)
            if clean_text.endswith("```"):
                clean_text = clean_text[:-3]
                
            st.markdown(clean_text, unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            with col1:
                st.download_button("Download Markdown", content[content_key], file_name=f"{selected_course}_{content_key}.md", key=f"dl_{tab_key}_md")
            with col2:
                if pdf_key in content:
                    # Ensure file_name is just the basename, not a full path
                    pdf_fname = os.path.basename(content[pdf_name_key])
                    st.download_button("Download PDF", content[pdf_key], file_name=pdf_fname, mime="application/pdf", key=f"dl_{tab_key}_pdf")

    with res_tabs[0]:
        display_content_tab("en", "syllabus_en", "pdf_en", "pdf_name_en", "English Syllabus")
        
    with res_tabs[1]:
        display_content_tab("it", "syllabus_it", "pdf_it", "pdf_name_it", "Italian Syllabus")
        
    with res_tabs[2]:
        display_content_tab("tm", "topic_mapping", "pdf_tm", "pdf_name_tm", "Topic Mapping")
    
    if st.button("Close History View"):
        del st.session_state['loaded_version']
        del st.session_state['loaded_version_name']
        st.rerun()

