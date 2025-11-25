from pypdf import PdfWriter
import io

def create_dummy_pdf(filename):
    writer = PdfWriter()
    writer.add_blank_page(width=72, height=72)
    with open(filename, "wb") as f:
        writer.write(f)

if __name__ == "__main__":
    create_dummy_pdf("dummy.pdf")
