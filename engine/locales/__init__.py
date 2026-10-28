"""Locale packs: everything in the engine that is language-specific.

Two different things live here, and keeping them together is deliberate.

*Messages* are what the user reads. Obvious.

*Language data* is the part people forget: the stopword list, the stemmer,
and the patterns that recognise a citation ("п. 1.1.29") or a standard's
designation ("ГОСТ 12.1.030"). Retrieval quality depends on these as much as
on any scoring formula - a stemmer that cuts too little makes "розеточной"
unable to match "розеток", and the whole question fails. Porting this tool to
another language and corpus means writing one of these files, not editing the
engine.

Select with CV_LOCALE (default "ru"). See ru.py for a fully worked example and
en.py for the minimum a new locale must provide.
"""

import importlib
import os

LOCALE_NAME = os.environ.get("CV_LOCALE", "ru")


def load(name=None):
    name = name or LOCALE_NAME
    try:
        return importlib.import_module("locales.%s" % name)
    except ImportError:
        return importlib.import_module("engine.locales.%s" % name)
