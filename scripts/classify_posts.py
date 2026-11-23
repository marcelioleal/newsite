#!/usr/bin/env python3
"""
Classify migrated posts into categories: software-dev / musica / arte / outros.

Reads every content/{pt-br,en}/posts/*/index.md, scores title+body against
three keyword sets, writes the winning bucket back as `categories:` in the
YAML front-matter. Idempotent by default — a post that already has a
`categories:` field is skipped unless --force is passed.

Scoring:
  - 1 point per body keyword hit (case-insensitive, word-boundary)
  - 3 points per title keyword hit
  - Winner = highest-scoring bucket; all-zero → "outros"
  - Tie → precedence software-dev > musica > arte

Usage:
  python3 scripts/classify_posts.py                      # live run, skip classified
  python3 scripts/classify_posts.py --dry-run            # print decisions only
  python3 scripts/classify_posts.py --force              # re-classify all
  python3 scripts/classify_posts.py --only software-dev  # filter output by bucket
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parent.parent
POST_GLOBS = [
    "content/pt-br/posts/*/index.md",
    "content/en/posts/*/index.md",
]

KEYWORDS: dict[str, list[str]] = {
    "software-dev": [
        "tech", "techie", "startup", "startups", "engineering", "engenharia",
        "engineer", "engenheiro", "engenheira", "product manager", "product owner",
        "produto", "product", "programador", "programadora", "programação", "programacao",
        "codigo", "código", "code", "coder", "coding", "php", "golang", "go lang",
        "java", "python", "docker", "kubernetes", "aws", "gcp", "azure", "cloud",
        "nubank", "qedu", "bhub", "amazon", "getyourguide", "tripda", "siteapps",
        "dafiti", "beyond tech", "framework", "frameworks", "linguagem", "linguagens",
        "scrum", "agile", "mvp", "sprint", "kanban", "backlog", "open source",
        "software livre", "github", "gitlab", "bitbucket", "api", "rest", "graphql",
        "sql", "database", "banco de dados", "backend", "frontend", "full stack",
        "fullstack", "devops", "ci/cd", "deploy", "javascript", "typescript", "node",
        "react", "vue", "angular", "ruby", "rails", "django", "flask", "spring",
        "kotlin", "android", "ios", "mobile", "microservices", "microservice",
        "serverless", "lambda", "terraform", "linux", "shell", "bash", "git",
        "gestão de tech", "arquitetura", "architecture", "liderança técnica",
        "tech lead", "engineering lead", "cto", "vpe", "advisor", "consultor",
        "vagas", "emprego", "carreira", "tcc", "classgenerator", "generator",
    ],
    "musica": [
        "música", "musica", "show", "shows", "festival", "festivais", "dj",
        "spotify", "cantor", "cantora", "nação zumbi", "nacao zumbi", "strokes",
        "silva", "legião", "legiao", "banda", "bandas", "forró", "forro",
        "carimbó", "carimbo", "techno", "house", "rock", "pop", "playlist",
        "playlists", "samba", "mpb", "álbum", "album", "concerto", "concert",
        "vinil", "disc", "setlist", "beat", "beats", "groove", "melódico",
        "melodico", "melody", "melodia", "innerbloom", "sounds of quartzo",
        "soundsofquartzo", "meca inhotim", "tribaltech", "abril pro rock",
        "planeta terra", "se rasgum", "reciferock", "wegoout", "ihateflash",
        "música eletrônica", "musica eletronica", "jazz", "blues", "hip hop",
        "rap", "trap", "funk", "brega", "tecnobrega", "guitarrada", "guitarra",
        "baterista", "bateria", "piano", "teclado", "violão", "violao",
        "compositor", "compositora", "tour", "turnê", "turne", "palco",
    ],
    "arte": [
        "galeria", "galerias", "pintura", "pinturas", "pintor", "pintora",
        "exposição", "exposicao", "exposições", "exposicoes", "bienal",
        "inhotim", "meca", "sp-arte", "sp arte", "museu", "museus",
        "arte contemporânea", "arte contemporanea", "performance", "artista",
        "artistas", "obra", "obras", "escultura", "esculturas", "escultor",
        "instalação", "instalacao", "fotografia", "fotógrafo", "fotografo",
        "fotógrafa", "fotografa", "célia leal", "celia leal",
        "lealmaurony", "arte em sp", "galeria alma da rua",
        "alma da rua", "mam", "masp", "pinacoteca", "ccbb", "street art",
        "grafite", "mural", "muralismo", "iurifernandes", "atelier",
    ],
}

BUCKET_ORDER = ["software-dev", "musica", "arte"]  # tie-break precedence


def compile_patterns(keywords: Iterable[str]) -> re.Pattern[str]:
    # Build a single alternation with \b boundaries. Keywords containing
    # spaces or punctuation are escaped; they still match whole-word at edges.
    escaped = sorted((re.escape(k) for k in keywords), key=len, reverse=True)
    return re.compile(r"(?<![a-zA-Z0-9])(?:" + "|".join(escaped) + r")(?![a-zA-Z0-9])", re.IGNORECASE)


PATTERNS = {bucket: compile_patterns(kws) for bucket, kws in KEYWORDS.items()}

FRONT_MATTER_RE = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.DOTALL)


def split_front_matter(text: str) -> tuple[str, str] | None:
    m = FRONT_MATTER_RE.match(text)
    if not m:
        return None
    return m.group(1), m.group(2)


def has_categories(fm: str) -> bool:
    # Match a top-level `categories:` key (not inside a nested block)
    return re.search(r"^categories:", fm, re.MULTILINE) is not None


def extract_title(fm: str) -> str:
    m = re.search(r"^title:\s*(.+)$", fm, re.MULTILINE)
    if not m:
        return ""
    return m.group(1).strip().strip("'\"")


def score(text: str, bucket: str) -> int:
    return len(PATTERNS[bucket].findall(text))


PRIMARY_MIN = 1  # winner needs at least this score, else → outros
SECONDARY_MIN = 5  # absolute floor for a secondary bucket
SECONDARY_RATIO = 0.4  # secondary must be ≥ 40% of the winner's score


def classify(title: str, body: str) -> tuple[list[str], dict[str, int]]:
    scores: dict[str, int] = {}
    for bucket in BUCKET_ORDER:
        body_hits = score(body, bucket)
        title_hits = score(title, bucket) * 3
        scores[bucket] = body_hits + title_hits
    if all(s < PRIMARY_MIN for s in scores.values()):
        return ["outros"], scores
    best = max(BUCKET_ORDER, key=lambda b: (scores[b], -BUCKET_ORDER.index(b)))
    buckets = [best]
    for b in BUCKET_ORDER:
        if b == best:
            continue
        if scores[b] >= SECONDARY_MIN and scores[b] >= SECONDARY_RATIO * scores[best]:
            buckets.append(b)
    return buckets, scores


def insert_categories(fm: str, categories: list[str]) -> str:
    rendered = "[" + ", ".join(categories) + "]"
    if has_categories(fm):
        return re.sub(
            r"^categories:.*$",
            f"categories: {rendered}",
            fm,
            count=1,
            flags=re.MULTILINE,
        )
    trimmed = fm.rstrip("\n")
    return f"{trimmed}\ncategories: {rendered}"


def process_file(path: Path, dry_run: bool, force: bool) -> tuple[list[str], dict[str, int]] | None:
    text = path.read_text(encoding="utf-8")
    split = split_front_matter(text)
    if split is None:
        print(f"skip (no front-matter): {path}", file=sys.stderr)
        return None
    fm, body = split
    if has_categories(fm) and not force:
        return None
    title = extract_title(fm)
    buckets, scores = classify(title, body)
    if dry_run:
        return buckets, scores
    new_fm = insert_categories(fm, buckets)
    new_text = f"---\n{new_fm}\n---\n{body}"
    path.write_text(new_text, encoding="utf-8")
    return buckets, scores


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="print decisions without writing")
    parser.add_argument("--force", action="store_true", help="re-classify posts that already have categories")
    parser.add_argument("--only", choices=BUCKET_ORDER + ["outros"], help="only print posts classified into this bucket")
    args = parser.parse_args()

    counts: dict[str, int] = {b: 0 for b in BUCKET_ORDER + ["outros"]}
    changed = 0
    examined = 0

    paths: list[Path] = []
    for pattern in POST_GLOBS:
        paths.extend(sorted(ROOT.glob(pattern)))

    for path in paths:
        examined += 1
        result = process_file(path, args.dry_run, args.force)
        if result is None:
            continue
        buckets, scores = result
        for b in buckets:
            counts[b] += 1
        changed += 1
        if args.only and args.only not in buckets:
            continue
        rel = path.relative_to(ROOT)
        joined = ",".join(buckets)
        print(f"{joined:>22s}  {rel}  {scores}")

    print(f"\nexamined: {examined}  changed: {changed}  by bucket (multi-counted): {counts}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
