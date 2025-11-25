import google.generativeai as genai
import os

# Load key
if os.path.exists("Key.txt"):
    with open("Key.txt", "r") as f:
        api_key = f.read().strip()
    
    genai.configure(api_key=api_key)
    
    print("Listing available models:")
    try:
        with open("models.txt", "w") as outfile:
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    print(m.name)
                    outfile.write(m.name + "\n")
    except Exception as e:
        print(f"Error listing models: {e}")
else:
    print("Key.txt not found.")
