# chapter-and-verse

Ask your standards library in plain language. Get the clause, the page, and
the exact quote — or an honest "not found".

A self-hosted Telegram assistant over your own corpus of regulatory or
technical documents. Built for an electrical inspector who owned ~160
standards in Russian and English and spent **4–5 hours** locating a single
clause.

```
Telegram ──► bot.js ──► bridge ──► ask.py ──► Claude API (one stateless call)
                                      │
                                      ├─ index/catalog.md     which documents?
                                      └─ index/docs/*/full.md  rank passages
```

```
Q: на какой высоте от пола ставить выключатель?

   Выключатели — 0,8–1,7 м от пола; в помещениях для детей — 1,8 м.

   📄 И 1.00-12, п. 4.12, стр. 91: «выключатели и розетки должны
      устанавливаться на высоте 1,8 м»

   ⚠️ СП 256 п. 15.36 требует согласовывать высоту с заданием на
      проектирование — документы расходятся.

   _Проверь в первоисточнике._
```

## Why this instead of a RAG template

The retrieval is ordinary. What is not ordinary is that **the citation is
verified before you see it**, because the thing that makes this useful is
also the thing that makes it dangerous.

Asked what colour a protective-earth conductor is, an early version answered
*"синего цвета"* — blue, which is the **neutral**; earth is yellow-green. It
cited a clause number that did not exist and quoted a sentence that appears
nowhere in the corpus. It was confident, well-formatted, and wrong, in a
domain where the reader signs off on installations.

So every answer passes four guards before anyone reads it:

| guard | catches |
|---|---|
| **citation present** | an authoritative-sounding answer with no source |
| **citation relevant** | a real clause that is not about the question |
| **quote grounded** | text that appears nowhere in the retrieved passages |
| **clause exists** | a real quote labelled with another clause's number |

The last two are the ones that matter. Shape and topicality cannot detect
invention — only the source can. A failed guard suppresses the answer and
names the documents it searched, so the reader is pointed somewhere rather
than told "no".

## Design decisions worth stealing

**No local model.** A 7B model on a 4 GB GPU answered under half the
questions, took 42–112s, and produced the wrong answer above. One stateless
API call with passages the code already retrieved costs ~$0.13 and answers
in ~20s. Measured, not assumed.

**No agent loop, no tools.** The predecessor let the model re-run retrieval
itself with grep: 195k–1.1M input tokens per question, 15× cost variance,
and a `--max-turns` cap returned an *empty answer* on half the test
questions. Passing the passages costs ~25k tokens with no variance — and the
model cannot reach a shell.

**No vector database.** Lexical scoring over heading-delimited chunks, one
`.npy`-free dependency-free path. For a corpus this size the honest
bottleneck was recall, not embedding quality — see `ops/recall.py`.

**Mechanical text conversion.** `pipeline/update.py` converts PDFs with no
model in the loop. A model that rewrites a standard can silently "correct" a
clause number or a measurement, and a revisor cites those. The model is used
only for judgement — titles, topics, bilingual keywords.

**Page numbers.** The extractor knows what page text came from; that survives
into the index so a citation reads *«п. 1.1.29, стр. 140»*. In a 500-page
PDF that is the difference between seconds and minutes.

## Two test harnesses, because one is not enough

`ops/eval.py` measures whether answers carry citations. That proxy **scored
the blue-conductor answer as a pass** — it had the shape of a citation — and
scored the honest refusal that replaced it as a failure.

`ops/correctness.py` asserts facts: the expected value, the dangerous wrong
value, and where the expectation was verified. Cases taken from the model's
own output are marked `pending` and excluded by default, because encoding a
model's claim as ground truth only proves it is self-consistent.

`ops/recall.py` asks the question that should drive retrieval work: *did a
passage containing the answer survive?* Adding it immediately found that
keyword expansion was outvoting the question's own words 21 to 9 and pushing
correct passages out of the budget.

## Setup

You need: Docker, an [Anthropic API key](https://console.anthropic.com)
(workspace-scoped), and a Telegram bot token from
[@BotFather](https://t.me/BotFather).

```bash
git clone https://github.com/LightStein/chapter-and-verse
cd chapter-and-verse
cp .env.example .env            # fill in the three values
mkdir -p data/corpus            # put your PDFs/DOCX here
docker compose up -d --build
```

Then:

1. Add the bot to a Telegram group and **make it an administrator** —
   without that, Telegram's privacy mode hides ordinary messages from it.
2. Send `/chatid` in the group, put the number in `gateway/registry.json`,
   and `docker compose restart`.
3. Build the index: `docker compose exec chapter-and-verse python3 pipeline/update.py`
4. Ask a question in the group.

Afterwards, documents are added by **sending the file to the chat** — it is
indexed and confirmed in the chat.

## Another language or another corpus

Everything language-specific lives in `engine/locales/`. The engine contains
no stopwords, no stemmer, no clause patterns. `ru.py` is the worked example
(GOST/SP/SNiP/PUE); `en.py` is the template (IEC/ISO/BS/NFPA). Copy one,
replace its contents, set `CV_LOCALE`.

A locale owns the user-facing messages *and* the retrieval-critical pieces:
the stemmer, the stopword list, and the patterns that recognise a citation
or a standard's designation. These matter as much as any scoring formula — a
stemmer that cuts too little makes one inflection unable to match another and
the question simply fails.

Answer style lives in `prompts/answer.<locale>.md`.

## Cost

Measured on a 56-document, 15 MB corpus with Claude Opus 5.5:

| | |
|---|---|
| per question | **$0.10–0.14** (~25k input tokens) |
| latency | 8–22 s |
| indexing | one cheap metadata call per document, once |

`claude-sonnet-5-5` roughly halves it; `claude-haiku-4-5` is ~5× cheaper.
Every answer is appended to `data/state/answers.jsonl` with its token usage
and cost — so the bill is auditable, and so is what the assistant told
people.

## Limits, honestly

- **Tables are flattened.** `page.get_text()` renders them as column soup. In
  an electrical corpus the highest-value content is tabular — ampacity by
  cross-section, IP rating by zone. Unfixed.
- **Retrieval is lexical.** Synonymy across languages is handled by
  model-written bilingual keywords in `meta.json`, which is a weaker bridge
  than embeddings would be.
- **It only knows what you give it.** A "not found" means retrieval missed,
  which is not the same as the standards being silent — do not read it as
  evidence of absence.
- **The quote is verified; the reasoning is not.** The guards prove a
  citation is real and on-topic. They cannot prove the answer's
  interpretation is right. The last line of every answer says to check the
  original, and it means it.

## Licence

MIT. No warranty — least of all for anything safety-critical.
