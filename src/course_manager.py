import os
import shutil
import json
from typing import List, Dict

class CourseManager:
    def __init__(self, root_dir="courses"):
        self.root_dir = root_dir
        os.makedirs(self.root_dir, exist_ok=True)

    def create_course(self, name: str) -> bool:
        """Creates a new course directory structure."""
        course_path = os.path.join(self.root_dir, name)
        if os.path.exists(course_path):
            return False
        
        os.makedirs(os.path.join(course_path, "pdfs"))
        os.makedirs(os.path.join(course_path, "output"))
        
        # Initialize resources.json
        resources = {"links": []}
        with open(os.path.join(course_path, "resources.json"), "w") as f:
            json.dump(resources, f)
            
        return True

    def list_courses(self) -> List[str]:
        """Returns a list of existing course names."""
        return [d for d in os.listdir(self.root_dir) if os.path.isdir(os.path.join(self.root_dir, d))]

    def delete_course(self, name: str):
        """Deletes a course and all its data."""
        course_path = os.path.join(self.root_dir, name)
        if os.path.exists(course_path):
            shutil.rmtree(course_path)

    def add_pdf(self, course_name: str, file_obj, filename: str):
        """Saves an uploaded PDF to the course's pdfs directory."""
        save_path = os.path.join(self.root_dir, course_name, "pdfs", filename)
        with open(save_path, "wb") as f:
            f.write(file_obj.getbuffer())

    def add_link(self, course_name: str, url: str, description: str):
        """Adds a web resource link to resources.json."""
        json_path = os.path.join(self.root_dir, course_name, "resources.json")
        
        with open(json_path, "r") as f:
            data = json.load(f)
            
        data["links"].append({"url": url, "description": description})
        
        with open(json_path, "w") as f:
            json.dump(data, f, indent=4)

    def get_course_content(self, course_name: str) -> Dict:
        """
        Returns a dictionary with:
        - 'pdf_files': List of PDF filenames
        - 'links': List of link dictionaries
        """
        course_path = os.path.join(self.root_dir, course_name)
        pdf_dir = os.path.join(course_path, "pdfs")
        
        pdf_files = [f for f in os.listdir(pdf_dir) if f.lower().endswith('.pdf')]
        
        json_path = os.path.join(course_path, "resources.json")
        with open(json_path, "r") as f:
            data = json.load(f)
            
        return {
            "pdf_files": pdf_files,
            "links": data["links"]
        }
