"""
Reset Script — Wipe ChromaDB and optionally re-ingest documents.
----------------------------------------------------------------
Usage:
    python scripts/reset_db.py                        # wipe only
    python scripts/reset_db.py --reingest ./docs/     # wipe + re-ingest
    python scripts/reset_db.py --dry-run              # preview only
"""

import argparse
import os
import shutil
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "../backend/.env"))


def wipe_chroma(persist_dir: str, dry_run: bool = False):
    if not os.path.exists(persist_dir):
        print(f"  ChromaDB directory not found: {persist_dir} (nothing to wipe)")
        return

    size_mb = sum(
        os.path.getsize(os.path.join(dp, f))
        for dp, _, files in os.walk(persist_dir)
        for f in files
    ) / (1024 * 1024)

    print(f"  ChromaDB at: {persist_dir}  ({size_mb:.1f} MB)")

    if dry_run:
        print("  [DRY RUN] Would delete the directory above.")
        return

    shutil.rmtree(persist_dir)
    print("  ✓ ChromaDB wiped.")


def reingest(docs_dir: str, chunk_size: int, chunk_overlap: int):
    from backend.data_pipeline.ingestor import ingest_directory
    from backend.vector_store.chroma_client import ChromaStore
    from backend.vector_store.embedder import Embedder

    print(f"\n  Re-ingesting from: {docs_dir}")
    chunks = ingest_directory(docs_dir, chunk_size, chunk_overlap)
    print(f"  Chunks created: {len(chunks)}")

    if not chunks:
        print("  No documents found — nothing ingested.")
        return

    print("  Loading embedding model...")
    embedder = Embedder(os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2"))

    print("  Generating embeddings...")
    embeddings = embedder.embed([c["content"] for c in chunks])

    print("  Storing in ChromaDB...")
    store = ChromaStore(
        persist_dir=os.getenv("CHROMA_PERSIST_DIR", "./backend/chroma_db"),
        collection_name=os.getenv("CHROMA_COLLECTION_NAME", "knowledge_base"),
    )
    count = store.upsert(chunks, embeddings)

    print(f"\n  ✓ Stored {count} chunks.")
    print(f"  Total in collection: {store.count()}")
    print(f"  Sources: {store.list_sources()}")


def main():
    parser = argparse.ArgumentParser(description="Reset KnowledgeAgent vector store.")
    parser.add_argument("--reingest", metavar="DOCS_DIR", help="Directory to re-ingest after wiping")
    parser.add_argument("--chunk-size", type=int, default=500)
    parser.add_argument("--chunk-overlap", type=int, default=50)
    parser.add_argument("--dry-run", action="store_true", help="Preview only — do not delete")
    parser.add_argument(
        "--chroma-dir",
        default=os.getenv("CHROMA_PERSIST_DIR", "./backend/chroma_db"),
        help="Path to ChromaDB persistence directory",
    )
    args = parser.parse_args()

    print("\nKnowledgeAgent — Database Reset")
    print("=" * 40)

    if not args.dry_run:
        confirm = input(f"\n  This will DELETE all vectors in '{args.chroma_dir}'.\n  Type 'yes' to continue: ")
        if confirm.strip().lower() != "yes":
            print("  Aborted.")
            sys.exit(0)

    wipe_chroma(args.chroma_dir, dry_run=args.dry_run)

    if args.reingest and not args.dry_run:
        reingest(args.reingest, args.chunk_size, args.chunk_overlap)
    elif args.reingest and args.dry_run:
        print(f"\n  [DRY RUN] Would re-ingest from: {args.reingest}")

    print("\nDone.\n")


if __name__ == "__main__":
    main()