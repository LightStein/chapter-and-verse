"""Russian locale, for a corpus of GOST / SP / SNiP / PUE style standards.

This is the worked example: it is the configuration the tool was built and
measured against. A new locale copies this file and replaces its contents -
the engine itself contains no language-specific anything.
"""

import re

# ---------------------------------------------------------------- messages
# {placeholders} are filled by the engine. Keep them.
MESSAGES = {
    "empty_index":
        "База документов пока пустая. Пришлите сюда файлы стандартов "
        "(PDF, DOC, DOCX) — я их добавлю, и можно будет спрашивать.",
    "no_chunks":
        "По этим словам ничего не нашёл в документах. Попробуйте "
        "переформулировать — другими словами или синонимом.",
    "api_error":
        "Не удалось связаться с сервером. Проверьте, что интернет есть, "
        "и попробуйте ещё раз. Если повторяется — сообщите администратору.",
    "refused":
        "Модель отказалась отвечать на этот вопрос. Переформулируйте "
        "или сообщите администратору.",
    "internal_error": "Внутренняя ошибка помощника: {error}",

    # the four guards; each is shown INSTEAD of an answer that failed it
    "reject_not_found":
        "В найденных фрагментах прямого ответа нет. Попробуйте "
        "переформулировать — или, если документа в базе нет, добавьте его.",
    "reject_no_citation":
        "Нашёл похожий текст, но не смог указать точный пункт документа — "
        "не показываю такой ответ.",
    "reject_irrelevant":
        "Нашёл ссылку на пункт, но он не про то, о чём вопрос — "
        "не показываю такой ответ.",
    "reject_ungrounded":
        "Ответ ссылался на цитату, которой нет в документах — "
        "не показываю такой ответ.",
    "reject_bad_clause":
        "Ответ ссылался на пункт {clause}, которого нет в найденных "
        "документах — не показываю такой ответ.",
    "sources_header": "Смотрел здесь — проверьте сами:",

    # progress lines, shown while the turn runs
    "progress_reading": "🧠 Читаю найденные пункты…",
    "progress_docs": "📚 Смотрю: {names}{more}",
    "progress_ingest": "📥 Добавляю {n} док. в базу — это займёт минуту…",

    # document ingestion
    "ingest_unreadable":
        "Не смог прочитать файл «{name}»: {error}\n"
        "Пришлите его ещё раз или сообщите администратору.",
    "ingest_nothing": "Не нашёл, что добавить.",
    "ingest_failed":
        "Файл сохранил, но не смог построить индекс. "
        "Сообщите администратору.\n\n{names}",
    "ingest_done":
        "Готово. Добавил:\n• {names}\n\nВсего документов в базе: {total}. "
        "Можно спрашивать.",

    # the page label prefixed to each retrieved chunk
    "page_label": "страница {page}",
    # fallback if prompts/answer.<locale>.md is missing
    "system_fallback":
        "Отвечай по-русски, только по приведённым фрагментам, всегда "
        "указывай документ, пункт и точную цитату. Если ответа во "
        "фрагментах нет — скажи прямо.",
    "context_header": "ФРАГМЕНТЫ ДОКУМЕНТОВ",
    "question_header": "ВОПРОС",
}

# ------------------------------------------------------------ recognisers
# A source line: the marker, or an explicit clause reference.
CITATION_RE = re.compile(r"📄|\bп\.\s*\d|\bпункт\s*\d", re.I)
# A clause the answer claims to cite. Dotted forms only - a bare "п. 7"
# cannot be told apart from an ordinary number in the source text.
CLAUSE_CITED_RE = re.compile(r"(?:п\.|пункт|§)\s*(\d+(?:\.\d+){1,3})", re.I)
# A chunk that is mostly standard designations is a normative-references
# list: it matches many terms and answers nothing.
REFLIST_RE = re.compile(r"(ГОСТ|МЭК|ИСО|IEC|ISO|СП|СНиП|EN)\s*[Р\s]*[\d.\-]{3,}", re.I)
# Words the tokeniser keeps whole: acronyms and standard designations.
DESIGNATION_RE = re.compile(r"^(?:[A-ZА-ЯЁ]{2,}(?:[-.][A-ZА-ЯЁ0-9]+)*|.*[\d].*|.*-.*)$")
TOKEN_RE = re.compile(r"[A-Za-zА-Яа-яЁё0-9]+(?:[-.][A-Za-zА-Яа-яЁё0-9]+)*")
# Letters that mark this language, for "should the stemmer touch this word".
SCRIPT_RE = re.compile(r"[а-яёА-ЯЁ]")

STOPWORDS = {
    "какой", "какая", "какое", "какие", "какого", "каком", "чему", "чего",
    "который", "должен", "должна", "должно", "нужно", "надо", "можно",
    "быть", "если", "или", "для", "при", "над", "под", "это", "как",
    "что", "где", "когда", "почему", "сколько", "ставить", "делать",
    "what", "which", "the", "and", "for", "with", "from", "should", "must",
}

def stem(w):
    """Prefix stem for Russian inflection.

    Cutting only the last two characters is not enough: "розеточной" became
    "розеточн", which cannot match "розеток" - and that is exactly how a
    question about socket circuits missed a clause about sockets. A fixed
    short prefix collides the inflections that matter ("розето" matches both)
    and also catches some compounding ("труб" reaches "трубопровод").
    """
    if not re.search(r"[а-яёА-ЯЁ]", w):
        return w
    if len(w) > 6:
        return w[:6]
    if len(w) >= 5:
        return w[:4]
    return w

# Punctuation stripped from a token before stemming - includes the guillemets
# Russian typography uses for quotation.
STRIP_CHARS = "«»\"'(),.;:!?-—"
# Words inside a keyword phrase, for splitting multi-word meta.json keywords.
WORD_RE = re.compile(r"[\wа-яёА-ЯЁ]+")


# Words as compared for quote grounding, after folding. Matching is done on
# these, so anything the OCR or the model might vary - case, ё/е - must be
# normalised away here or a genuine quote will be rejected as fabricated.
NORM_WORD_RE = re.compile(r"[a-zа-я0-9]+")


def fold(text):
    """Lowercase and remove the distinctions that are not meaningful."""
    return text.lower().replace("ё", "е")
