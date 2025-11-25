# Syllaber

Syllaber is a local AI agent designed to help instructors create course syllabi from PDF textbooks and web resources. It uses Google's Gemini API to generate structured course plans in English and Italian.

## Features
- **PDF Extraction**: Upload multiple PDF textbooks.
- **Web Resources**: Add links to relevant web content.
- **Course Management**: Create, manage, and delete multiple courses.
- **Syllabus Generation**: Automatically generates a structured syllabus (Learning Intent, Program Blocks, Expectations) and a Topic Mapping file.
- **Custom Instructions**: Tailor the output with specific prompts.

## Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/thimotyb/syllaber.git
    cd syllaber
    ```
2.  Install dependencies:
    ```bash
    pip install streamlit pypdf google-generativeai
    ```
3.  **API Key**: Create a file named `Key.txt` in the root directory and paste your Google Gemini API key inside.

## Usage

Run the application:
```bash
streamlit run app.py
```

## Project Structure
- `app.py`: Main Streamlit application.
- `src/`: Source code for PDF processing, syllabus generation, and course management.
- `courses/`: Directory where course data (PDFs, resources, outputs) is stored.
