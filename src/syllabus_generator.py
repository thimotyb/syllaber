import google.generativeai as genai
import os

def generate_syllabus(text, web_resources_text, additional_instructions, api_key, language='en'):
    """
    Generates a course syllabus from the provided text and web resources using Gemini API.
    
    Args:
        text (str): The source text from the PDFs.
        web_resources_text (str): Formatted string of web resources.
        additional_instructions (str): User-provided custom instructions.
        api_key (str): Google Gemini API Key.
        language (str): Target language ('en' or 'it').
        
    Returns:
        str: Generated syllabus in Markdown format.
    """
    genai.configure(api_key=api_key)
    # Use a model that is definitely available
    model = genai.GenerativeModel('gemini-2.0-flash')
    
    lang_instruction = "English" if language == 'en' else "Italian"
    
    prompt = f"""
    You are an expert curriculum designer. Create a course syllabus based on the following text and web resources.
    The syllabus should be in {lang_instruction}.
    
    Follow this structure:
    1. **Learning Intent**: A short section describing the goal of the course.
    2. **Program Modules**: 4-6 cohesive modules. Each module must have:
        - **Theory**: Theoretical anchors.
        - **Organization**: Organizational levers.
        - **Labs**: A placeholder line for Google Cloud labs (e.g., "Lab: [Relevant Lab Title]").
    3. **Expectations**: Closing expectations.
    
    Do NOT include specific URLs for labs, just titles.
    Use Markdown formatting.
    
    Additional Instructions from User:
    {additional_instructions}
    
    Web Resources to incorporate:
    {web_resources_text}
    
    Source Text (excerpt):
    {text[:30000]} 
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating syllabus: {e}"

def generate_topic_mapping(text, api_key):
    """
    Generates a topic mapping file linking syllabus blocks to references and labs.
    
    Args:
        text (str): The source text.
        api_key (str): Google Gemini API Key.
        
    Returns:
        str: Generated topic mapping in Markdown format.
    """
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash')
    
    prompt = f"""
    Based on the following text, create a 'Topic Mapping' document.
    For each major topic or block identified in the text:
    1. List the specific chapters or sections from the source text that cover it.
    2. Suggest relevant Google Cloud Skills Boost labs or similar hands-on activities (just titles if URLs are unknown, but try to be specific).
    
    Format as a Markdown table or list.
    
    Source Text:
    {text[:30000]}
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating topic mapping: {e}"
