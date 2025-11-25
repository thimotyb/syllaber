import markdown
from xhtml2pdf import pisa
from io import BytesIO

def convert_markdown_to_pdf(markdown_text):
    """
    Converts Markdown text to PDF bytes.
    
    Args:
        markdown_text (str): The markdown content.
        
    Returns:
        bytes: The generated PDF data.
    """
    # Convert Markdown to HTML
    html_content = markdown.markdown(markdown_text)
    
    # Add basic styling
    styled_html = f"""
    <html>
    <head>
        <style>
            body {{
                font-family: Helvetica, sans-serif;
                font-size: 12pt;
                line-height: 1.5;
            }}
            h1, h2, h3 {{
                color: #333;
            }}
            code {{
                background-color: #f4f4f4;
                padding: 2px;
                font-family: monospace;
            }}
            pre {{
                background-color: #f4f4f4;
                padding: 10px;
                white-space: pre-wrap;
            }}
        </style>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """
    
    # Convert HTML to PDF
    result = BytesIO()
    pisa_status = pisa.CreatePDF(styled_html, dest=result)
    
    if pisa_status.err:
        return None
        
    return result.getvalue()
