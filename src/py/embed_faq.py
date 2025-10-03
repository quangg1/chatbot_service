"""
Embed FAQ_END_USER.md into MongoDB `embedding` collection using BGEM3.

Documents schema (existing collection assumed):
- productId: str | None
- text: str
- embedding: List[float]
- type: str in {"product", "price", "faq", ...}
- source: str

This script will:
1) Load MongoDB connection from env or defaults used in rag_system.py
2) Read `FAQ_END_USER.md`
3) Split into sections (by level-2 headers or paragraphs)
4) Embed each chunk with BAAI/bge-m3
5) Upsert into `embedding` collection with metadata: type="faq", source="FAQ_END_USER.md"

Run:
    python embed_faq.py
"""

import os
import re
from typing import List, Dict
from pymongo import MongoClient, UpdateOne
from FlagEmbedding import BGEM3FlagModel


def load_mongo_collection() -> tuple[MongoClient, str, str]:
    mongo_uri = os.getenv(
        "MONGO_URI",
        "mongodb+srv://hailoaidientich:quang01012004@cluster0.qsitilq.mongodb.net/Health_Care_App",
    )
    db_name = os.getenv("MONGO_DB", "Health_Care_App")
    col_name = os.getenv("MONGO_COLLECTION", "embedding")
    client = MongoClient(mongo_uri)
    return client, db_name, col_name


def read_faq_markdown(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def split_markdown_into_chunks(md: str, max_chars: int = 1200) -> List[Dict[str, str]]:
    # Split by H2 sections first (## ...)
    sections = re.split(r"\n##\s+", md)
    chunks: List[Dict[str, str]] = []
    for i, sec in enumerate(sections):
        if not sec.strip():
            continue
        # Recover title if present
        if i == 0:
            # may contain header line starting with '# '
            title_match = re.match(r"^#\s*(.*)$", sec.strip().splitlines()[0])
            title = title_match.group(1).strip() if title_match else "FAQ"
        else:
            first_line = sec.splitlines()[0]
            title = first_line.strip()
        body = sec if i == 0 else "\n".join(sec.splitlines()[1:])
        body = body.strip()
        if not body:
            body = title

        # Further split large bodies by paragraphs to keep under max_chars
        paras = [p.strip() for p in re.split(r"\n\s*\n", body) if p.strip()]
        buffer = ""
        for p in paras:
            if len(buffer) + len(p) + 2 <= max_chars:
                buffer = (buffer + "\n\n" + p).strip()
            else:
                if buffer:
                    chunks.append({"title": title, "text": buffer})
                if len(p) <= max_chars:
                    buffer = p
                else:
                    # hard split long paragraph
                    for start in range(0, len(p), max_chars):
                        part = p[start:start + max_chars]
                        chunks.append({"title": title, "text": part})
                    buffer = ""
        if buffer:
            chunks.append({"title": title, "text": buffer})
    return chunks


def embed_texts(model: BGEM3FlagModel, texts: List[str]) -> List[List[float]]:
    out = model.encode(texts, return_dense=True, return_sparse=False, return_colbert_vecs=False)
    vecs = out["dense_vecs"]
    return [list(map(float, v)) for v in vecs]


def build_operations(chunks: List[Dict[str, str]], embeddings: List[List[float]]) -> List[UpdateOne]:
    ops: List[UpdateOne] = []
    for idx, (ch, emb) in enumerate(zip(chunks, embeddings)):
        doc_id = f"faq::{idx}"
        text = ch.get("text", "").strip()
        title = ch.get("title", "FAQ").strip()
        ops.append(
            UpdateOne(
                {"_id": doc_id},
                {
                    "$set": {
                        "productId": None,
                        "title": title,
                        "text": text,
                        "embedding": emb,
                        "type": "faq",
                        "source": "FAQ_END_USER.md",
                    }
                },
                upsert=True,
            )
        )
    return ops


def main() -> None:
    faq_path = os.path.join(os.path.dirname(__file__), "FAQ_END_USER.md")
    if not os.path.exists(faq_path):
        raise FileNotFoundError(f"FAQ file not found: {faq_path}")

    print("📖 Reading FAQ markdown...")
    md = read_faq_markdown(faq_path)
    print("✂️ Splitting into chunks...")
    chunks = split_markdown_into_chunks(md)
    texts = [c["text"] for c in chunks]
    print(f"🧩 {len(chunks)} chunks prepared")

    print("🧠 Loading embedding model BAAI/bge-m3...")
    model = BGEM3FlagModel("BAAI/bge-m3")
    print("🔢 Computing embeddings...")
    embeddings = embed_texts(model, texts)

    print("🗄️ Connecting to MongoDB...")
    client, db_name, col_name = load_mongo_collection()
    col = client[db_name][col_name]

    print("⬆️ Upserting documents into collection...")
    ops = build_operations(chunks, embeddings)
    if ops:
        res = col.bulk_write(ops, ordered=False)
        print(
            f"✅ Upserted: matched={res.matched_count}, modified={res.modified_count}, upserted={len(res.upserted_ids)}"
        )
    else:
        print("⚠️ No chunks to upsert.")

    print("🏁 Done.")


if __name__ == "__main__":
    main()


