# One image: the Telegram bot (node), the bridge (node) and the engine +
# pipeline (python). Split across containers it would need a shared socket
# volume and a second compose service to buy nothing - this is one tool.
FROM python:3.12-slim

# pandoc: .docx/.odt  |  tesseract: scanned PDFs  |  libreoffice: legacy .doc
# A corpus of standards has all three, and discovering that after deploying
# is worse than a larger image.
RUN apt-get update && apt-get install -y --no-install-recommends \
      nodejs npm pandoc tesseract-ocr libreoffice-writer ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# Language packs for OCR. Override at build time for other corpora:
#   docker build --build-arg OCR_LANGS="tesseract-ocr-deu tesseract-ocr-fra"
ARG OCR_LANGS="tesseract-ocr-rus tesseract-ocr-eng"
RUN apt-get update && apt-get install -y --no-install-recommends $OCR_LANGS \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY gateway/package.json gateway/
RUN cd gateway && npm install --omit=dev --no-audit --no-fund

COPY engine/ engine/
COPY pipeline/ pipeline/
COPY prompts/ prompts/
COPY ops/ ops/
COPY gateway/ gateway/
COPY deploy/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENV STANDARDS_ROOT=/data \
    STANDARDS_RAW=/data/corpus \
    RUN_DIR=/data/run \
    PYTHONIOENCODING=utf-8 \
    PYTHONUTF8=1
VOLUME ["/data"]
ENTRYPOINT ["/entrypoint.sh"]
