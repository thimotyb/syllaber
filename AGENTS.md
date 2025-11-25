# Workflow Guide for Course Assembly

This guide describes how to reuse this workspace to build new syllabi sourced from PDF material and backed by Google Cloud lab references.

## 1. Extracting Text from PDFs
- Prefer `ps2ascii <input.pdf>` to capture raw text because it is preinstalled even when `pdftotext` is missing. Pipe it to `head`, `less`, or redirect into scratch files for review.
- When PDFs are numerous, keep them in the Dropbox path already mounted and inspect individual chapters as needed. Reference only the relevant sections instead of dumping entire files.
- If you need structured snippets, send `ps2ascii` output into helper files (e.g., `ps2ascii file.pdf > notes.txt`) so that you can annotate topic ideas before drafting the syllabus.

## 2. Organizing the Syllabus Content
- Draft distinct syllabus files for each language. Follow the pattern established by `modelops_syllabus_en.md` and `modelops_syllabus_it.md`: a short learning intent section, concise program blocks, and closing expectations.
- Keep every block uniform: theoretical anchors, organizational levers, and a Google Cloud labs line. This makes it easy to swap topics while preserving the course rhythm.
- Use ASCII only (no em dashes) unless the source documents already demand different characters.
- Deliver all course assets as Markdown (`.md`) files instead of `.txt` so they can be rendered directly without conversion.
- Keep lab or reference URLs out of the syllabus files; list only titles there and move all links into `topic_mapping.md`.
- In the Italian syllabus, minimize anglicismi and prefer clear Italian explanations; reserve English terms only when they are industry-standard and indispensable.
- Use Markdown structure (headings, bold labels, bullet lists) to separate sections and improve readability.

## 3. Capturing References and Lab Links
- Maintain a standalone mapping file (e.g., `topic_mapping.md`) that ties each syllabus block to the originating PDFs and the Google Skills / Cloud Skills Boost labs. This enables quick auditing of sources when adapting the course.
- Store full file names (including chapter numbers) under each topic to avoid ambiguity, and list the exact catalog URLs for the labs so that replacements are simple.

## 4. Suggested Workflow for New Courses
1. Review the provided PDFs with `ps2ascii` and take notes on themes, governance points, and technical angles.
2. Define 4–6 cohesive program blocks with clear theory + organization + lab coverage.
3. Write the primary syllabus file (typically English), then translate or localize to a second language if required.
4. Build or update the mapping file so every block references both literature and lab assets.
5. Share the Markdown files directly; when a PDF export is explicitly requested, generate it from the `.md` via `pandoc <file>.md -o <file>.pdf` (requires LaTeX, e.g., `xelatex`).

Keeping the instructions in this document lets any agent reproduce the pipeline without repeating user prompts.
