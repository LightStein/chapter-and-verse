"""English locale, for a corpus of IEC / ISO / BS / NFPA style standards.

Written as the second locale so the seam is proven rather than assumed: the
engine must not contain anything language-specific, and the only way to know
that is to run it in a language it was not built for. Also the template to
copy for a new language.
"""

import re

MESSAGES = {
    "empty_index":
        "The document library is empty. Send standards files here "
        "(PDF, DOC, DOCX) and I will index them, then you can ask.",
    "no_chunks":
        "Nothing in the documents matches those words. Try rephrasing — "
        "a different term or a synonym.",
    "api_error":
        "Could not reach the server. Check the connection and try again. "
        "If it keeps happening, tell your administrator.",
    "refused":
        "The model declined to answer this one. Rephrase it, or tell your "
        "administrator.",
    "internal_error": "Assistant error: {error}",

    "reject_not_found":
        "The retrieved passages do not answer this directly. Try rephrasing "
        "— or if the document is not in the library, add it.",
    "reject_no_citation":
        "I found related text but could not point to an exact clause, "
        "so I am not showing that answer.",
    "reject_irrelevant":
        "The clause I found is not about what you asked, "
        "so I am not showing that answer.",
    "reject_ungrounded":
        "The answer quoted text that does not appear in the documents, "
        "so I am not showing it.",
    "reject_bad_clause":
        "The answer cited clause {clause}, which does not appear in the "
        "retrieved documents, so I am not showing it.",
    "sources_header": "I looked here — check for yourself:",

    "progress_reading": "🧠 Reading the clauses I found…",
    "progress_docs": "📚 Looking at: {names}{more}",
    "progress_ingest": "📥 Adding {n} document(s) — this takes a minute…",

    "ingest_unreadable":
        "Could not read the file “{name}”: {error}\n"
        "Send it again, or tell your administrator.",
    "ingest_nothing": "Nothing here to add.",
    "ingest_failed":
        "Saved the file but could not build the index. "
        "Tell your administrator.\n\n{names}",
    "ingest_done":
        "Done. Added:\n• {names}\n\nDocuments in the library: {total}. "
        "Ask away.",

    "page_label": "page {page}",
    "system_fallback":
        "Answer in English, using ONLY the passages provided. Always give "
        "the document, the clause number and an exact quote. If the answer "
        "is not in the passages, say so plainly.",
    "context_header": "DOCUMENT PASSAGES",
    "question_header": "QUESTION",
}

CITATION_RE = re.compile(r"📄|\bcl(?:ause)?\.?\s*\d|\bsec(?:tion)?\.?\s*\d|§\s*\d", re.I)
CLAUSE_CITED_RE = re.compile(r"(?:cl\.|clause|sec\.|section|§)\s*(\d+(?:\.\d+){1,3})", re.I)
REFLIST_RE = re.compile(r"(IEC|ISO|EN|BS|ASTM|NFPA|ANSI|DIN)\s*[\d.\-]{3,}", re.I)
DESIGNATION_RE = re.compile(r"^(?:[A-Z]{2,}(?:[-.][A-Z0-9]+)*|.*[\d].*|.*-.*)$")
TOKEN_RE = re.compile(r"[A-Za-z0-9]+(?:[-.][A-Za-z0-9]+)*")
SCRIPT_RE = re.compile(r"[a-zA-Z]")
STRIP_CHARS = "\"'“”(),.;:!?-—"
WORD_RE = re.compile(r"[\w]+")
NORM_WORD_RE = re.compile(r"[a-z0-9]+")

STOPWORDS = {
    "what", "which", "where", "when", "how", "why", "must", "shall",
    "should", "need", "needs", "required", "the", "and", "for", "with",
    "from", "that", "this", "are", "was", "were", "has", "have", "can",
    "may", "its", "it", "of", "on", "in", "to", "at", "be", "is",
}


def stem(w):
    """Crude suffix stem. English inflects far less than Russian, so this
    only has to collapse plurals and the common verb endings; anything more
    aggressive starts colliding words that matter in a standards corpus."""
    w = w.lower().strip(STRIP_CHARS)
    for suf in ("ings", "ing", "ies", "ed", "es", "s"):
        if len(w) > len(suf) + 3 and w.endswith(suf):
            return w[: -len(suf)]
    return w


def fold(text):
    return text.lower()
