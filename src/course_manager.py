import os
import shutil
import json
from typing import List, Dict
from src.pdf_generator import convert_markdown_to_pdf

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

    def save_version(self, course_name: str, syllabus_en: str, syllabus_it: str, topic_mapping: str):
        """Saves a new version of the generated content (Markdown and PDF)."""
        course_path = os.path.join(self.root_dir, course_name)
        output_dir = os.path.join(course_path, "output")
        versions_file = os.path.join(course_path, "versions.json")
        
        # Load existing versions
        if os.path.exists(versions_file):
            with open(versions_file, "r") as f:
                versions = json.load(f)
        else:
            versions = []
            
        # Determine new version number
        next_version_num = len(versions) + 1
        version_name = f"v{next_version_num}"
        version_dir = os.path.join(output_dir, version_name)
        os.makedirs(version_dir, exist_ok=True)
        
        # Save Markdown files
        with open(os.path.join(version_dir, "syllabus_en.md"), "w", encoding="utf-8") as f:
            f.write(syllabus_en)
        with open(os.path.join(version_dir, "syllabus_it.md"), "w", encoding="utf-8") as f:
            f.write(syllabus_it)
        with open(os.path.join(version_dir, "topic_mapping.md"), "w", encoding="utf-8") as f:
            f.write(topic_mapping)
            
        # Save PDF files
        pdf_en = convert_markdown_to_pdf(syllabus_en)
        if pdf_en:
            pdf_name_en = f"{course_name}_Syllabus_English_{version_name}.pdf"
            with open(os.path.join(version_dir, pdf_name_en), "wb") as f:
                f.write(pdf_en)
                
        pdf_it = convert_markdown_to_pdf(syllabus_it)
        if pdf_it:
            pdf_name_it = f"{course_name}_Syllabus_Italian_{version_name}.pdf"
            with open(os.path.join(version_dir, pdf_name_it), "wb") as f:
                f.write(pdf_it)
                
        pdf_tm = convert_markdown_to_pdf(topic_mapping)
        if pdf_tm:
            pdf_name_tm = f"{course_name}_Topic_Mapping_{version_name}.pdf"
            with open(os.path.join(version_dir, pdf_name_tm), "wb") as f:
                f.write(pdf_tm)
            
        # Update metadata
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        versions.append({
            "version": next_version_num,
            "name": version_name,
            "timestamp": timestamp,
            "pdf_en": pdf_name_en if pdf_en else None,
            "pdf_it": pdf_name_it if pdf_it else None,
            "pdf_tm": pdf_name_tm if pdf_tm else None
        })
        
        with open(versions_file, "w") as f:
            json.dump(versions, f, indent=4)
            
        return next_version_num

    def get_versions(self, course_name: str) -> List[Dict]:
        """Returns list of versions for a course."""
        versions_file = os.path.join(self.root_dir, course_name, "versions.json")
        if os.path.exists(versions_file):
            with open(versions_file, "r") as f:
                return json.load(f)
        return []

    def get_version_content(self, course_name: str, version_num: int) -> Dict:
        """Returns content of a specific version, including PDF paths."""
        version_dir = os.path.join(self.root_dir, course_name, "output", f"v{version_num}")
        versions_file = os.path.join(self.root_dir, course_name, "versions.json")
        
        content = {}
        try:
            # Read Markdown
            with open(os.path.join(version_dir, "syllabus_en.md"), "r", encoding="utf-8") as f:
                content["syllabus_en"] = f.read()
            with open(os.path.join(version_dir, "syllabus_it.md"), "r", encoding="utf-8") as f:
                content["syllabus_it"] = f.read()
            with open(os.path.join(version_dir, "topic_mapping.md"), "r", encoding="utf-8") as f:
                content["topic_mapping"] = f.read()
                
            # Get PDF filenames from metadata
            if os.path.exists(versions_file):
                with open(versions_file, "r") as f:
                    versions = json.load(f)
                    version_meta = next((v for v in versions if v['version'] == version_num), None)
                    if version_meta:
                        if version_meta.get("pdf_en"):
                            with open(os.path.join(version_dir, version_meta["pdf_en"]), "rb") as f:
                                content["pdf_en"] = f.read()
                                content["pdf_name_en"] = version_meta["pdf_en"]
                        if version_meta.get("pdf_it"):
                            with open(os.path.join(version_dir, version_meta["pdf_it"]), "rb") as f:
                                content["pdf_it"] = f.read()
                                content["pdf_name_it"] = version_meta["pdf_it"]
                        if version_meta.get("pdf_tm"):
                            with open(os.path.join(version_dir, version_meta["pdf_tm"]), "rb") as f:
                                content["pdf_tm"] = f.read()
                                content["pdf_name_tm"] = version_meta["pdf_tm"]
                                
        except FileNotFoundError:
            return None
            
        return content

    def update_version_content(self, course_name: str, version_num: int, content_type: str, new_text: str):
        """
        Updates the content of a specific version and regenerates the PDF.
        
        Args:
            course_name (str): Name of the course.
            version_num (int): Version number.
            content_type (str): 'syllabus_en', 'syllabus_it', or 'topic_mapping'.
            new_text (str): The new markdown content.
        """
        version_dir = os.path.join(self.root_dir, course_name, "output", f"v{version_num}")
        versions_file = os.path.join(self.root_dir, course_name, "versions.json")
        
        # Map content type to filenames
        file_map = {
            "syllabus_en": ("syllabus_en.md", f"{course_name}_Syllabus_English_v{version_num}.pdf", "pdf_en"),
            "syllabus_it": ("syllabus_it.md", f"{course_name}_Syllabus_Italian_v{version_num}.pdf", "pdf_it"),
            "topic_mapping": ("topic_mapping.md", f"{course_name}_Topic_Mapping_v{version_num}.pdf", "pdf_tm")
        }
        
        if content_type not in file_map:
            return False
            
        md_filename, pdf_filename, json_key = file_map[content_type]
        
        # 1. Save Markdown
        with open(os.path.join(version_dir, md_filename), "w", encoding="utf-8") as f:
            f.write(new_text)
            
        # 2. Regenerate PDF
        pdf_bytes = convert_markdown_to_pdf(new_text)
        if pdf_bytes:
            with open(os.path.join(version_dir, pdf_filename), "wb") as f:
                f.write(pdf_bytes)
                
        # 3. Ensure metadata is correct (though filenames are stable)
        if os.path.exists(versions_file):
            with open(versions_file, "r") as f:
                versions = json.load(f)
            
            updated = False
            for v in versions:
                if v['version'] == version_num:
                    if v.get(json_key) != pdf_filename:
                        v[json_key] = pdf_filename
                        updated = True
                    break
            
            if updated:
                with open(versions_file, "w") as f:
                    json.dump(versions, f, indent=4)
                    
        return True
