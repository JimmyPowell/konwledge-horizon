from __future__ import annotations

import argparse
import os
from typing import List

from rich.console import Console
from rich.table import Table

from embeddings.siliconflow import SiliconFlowEmbeddings
from utils.loader import load_file
from utils.chunk import split_text, build_ids, compute_checksum
from kb.chroma_remote import get_vectorstore, add_chunks, recall as kb_recall, delete_by_source


console = Console()


def cmd_init(args: argparse.Namespace) -> None:
    emb = SiliconFlowEmbeddings(
        api_key=args.api_key,
        model=args.model,
        dimensions=args.dimensions,
        batch_size=args.batch_size,
    )
    _ = get_vectorstore(
        collection=args.kb,
        embedding=emb,
        host=args.host,
        port=args.port,
    )
    console.print(f"[green]Collection ready:[/green] {args.kb} at {args.host}:{args.port}")


def cmd_add(args: argparse.Namespace) -> None:
    emb = SiliconFlowEmbeddings(
        api_key=args.api_key,
        model=args.model,
        dimensions=args.dimensions,
        batch_size=args.batch_size,
    )
    vs = get_vectorstore(
        collection=args.kb,
        embedding=emb,
        host=args.host,
        port=args.port,
    )

    for path in args.files:
        text, meta = load_file(path)
        if args.replace:
            delete_by_source(vs, meta["source"])

        chunks = split_text(
            text,
            chunk_size=args.chunk_size,
            chunk_overlap=args.chunk_overlap,
        )
        ids = build_ids(meta["source"], chunks)
        metadatas = []
        base_checksum = compute_checksum(text)
        for i, c in enumerate(chunks):
            m = dict(meta)
            m.update({
                "chunk_id": i,
                "checksum": base_checksum,
            })
            metadatas.append(m)

        console.print(f"Embedding and adding {len(chunks)} chunks from: {meta['source']}")
        add_chunks(vs, texts=chunks, metadatas=metadatas, ids=ids)
        console.print(f"[green]Done:[/green] {meta['source']}")


def cmd_recall(args: argparse.Namespace) -> None:
    emb = SiliconFlowEmbeddings(
        api_key=args.api_key,
        model=args.model,
        dimensions=args.dimensions,
        batch_size=args.batch_size,
    )
    vs = get_vectorstore(
        collection=args.kb,
        embedding=emb,
        host=args.host,
        port=args.port,
    )

    results = kb_recall(vs, query=args.text, top_k=args.topk)

    table = Table(show_lines=False)
    table.add_column("rank", justify="right")
    table.add_column("score")
    table.add_column("source")
    table.add_column("chunk_id")
    table.add_column("text")

    for i, (doc, score) in enumerate(results, start=1):
        source = doc.metadata.get("source", "")
        chunk_id = str(doc.metadata.get("chunk_id", ""))
        # Chroma returns a distance; if cosine, similarity ~ 1 - distance
        try:
            sim = 1.0 - float(score)
        except Exception:
            sim = float(score)
        if args.score_threshold is not None and sim < args.score_threshold:
            continue
        snippet = (doc.page_content[:180] + "...") if len(doc.page_content) > 180 else doc.page_content
        table.add_row(str(i), f"{sim:.4f}", source, chunk_id, snippet)

    console.print(table)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="rag-chroma", description="RAG with remote Chroma + SiliconFlow embeddings")
    sub = p.add_subparsers(dest="cmd", required=True)

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--kb", required=True, help="Collection name (knowledge base)")
    common.add_argument("--host", default="localhost")
    common.add_argument("--port", type=int, default=8002)
    common.add_argument("--model", default="Qwen/Qwen3-Embedding-8B")
    common.add_argument("--dimensions", type=int, default=1024)
    common.add_argument("--batch-size", type=int, default=32)
    common.add_argument("--api-key", default=os.getenv("SILICONFLOW_API_KEY"))

    p_init = sub.add_parser("init", parents=[common], help="Create/get a collection on remote Chroma")
    p_init.set_defaults(func=cmd_init)

    p_add = sub.add_parser("add", parents=[common], help="Parse, chunk, embed and add files to KB")
    p_add.add_argument("--files", nargs="+", required=True, help="File paths to ingest (PDF/TXT/MD)")
    p_add.add_argument("--chunk-size", type=int, default=1000)
    p_add.add_argument("--chunk-overlap", type=int, default=100)
    p_add.add_argument("--replace", action="store_true", help="Delete previous chunks for same source before add")
    p_add.set_defaults(func=cmd_add)

    p_recall = sub.add_parser("recall", parents=[common], help="Embed text and recall top-K similar chunks")
    p_recall.add_argument("--text", required=True, help="Query text for recall")
    p_recall.add_argument("--topk", type=int, default=5)
    p_recall.add_argument("--score-threshold", type=float, default=None)
    p_recall.set_defaults(func=cmd_recall)

    return p


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

