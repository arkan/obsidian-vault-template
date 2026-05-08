#!/usr/bin/env python3
"""Extract text and table of contents from a PDF using pymupdf (fitz)."""

import json
import sys


def extract_pdf(pdf_path: str, extract_toc: bool = True) -> dict:
    """Extract full text and optional ToC from a PDF file.

    Returns:
        dict with keys: text (full body text), toc (list of {title, page, level}),
                        pages (total page count)
    """
    try:
        import fitz  # pymupdf
    except ImportError:
        print(
            "Erreur : pymupdf n'est pas installé. Installe-le avec : pip install pymupdf",
            file=sys.stderr,
        )
        sys.exit(1)

    result: dict = {"text": "", "toc": [], "pages": 0}

    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        print(f"Erreur : impossible d'ouvrir le PDF — {e}", file=sys.stderr)
        sys.exit(1)

    result["pages"] = len(doc)

    # Extract table of contents
    if extract_toc:
        raw_toc = doc.get_toc(simple=True)  # list of [level, title, page]
        for entry in raw_toc:
            result["toc"].append(
                {"level": entry[0], "title": entry[1], "page": entry[2]}
            )

    # Extract full text
    full_text_parts = []
    for page_num in range(len(doc)):
        try:
            page = doc.load_page(page_num)
            text = page.get_text("text")
            if text.strip():
                full_text_parts.append(
                    f"\n--- Page {page_num + 1} ---\n{text}"
                )
        except Exception:
            # Skip pages that can't be read (e.g., images-only pages)
            full_text_parts.append(
                f"\n--- Page {page_num + 1} ---\n[Page non extractible]"
            )

    result["text"] = "\n".join(full_text_parts)
    doc.close()

    # Warn if document appears to be a scan (very little text extracted)
    word_count = len(result["text"].split())
    if word_count < result["pages"] * 5:
        print(
            "Attention : Ce PDF contient très peu de texte — il s'agit probablement d'un scan sans OCR.",
            file=sys.stderr,
        )

    return result


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Extract text and ToC from PDF using pymupdf"
    )
    parser.add_argument("pdf_path", help="Path to the PDF file")
    parser.add_argument("--toc", action="store_true", default=True,
                        help="Extract table of contents (default: True)")
    parser.add_argument("--no-toc", dest="toc", action="store_false",
                        help="Skip table of contents extraction")

    args = parser.parse_args()

    try:
        result = extract_pdf(args.pdf_path, extract_toc=args.toc)
    except SystemExit:
        raise
    except Exception as e:
        print(f"Erreur inattendue : {e}", file=sys.stderr)
        sys.exit(1)

    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
