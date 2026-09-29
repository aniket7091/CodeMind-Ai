"""
CodeMind AI - Developer Documentation Crawler

Downloads developer documentation from configured official sources
and builds a clean knowledge_base/ directory.

Install:
    pip install requests beautifulsoup4

Run from backend/:
    python app/script/prepare_developer_docs.py
"""

from pathlib import Path
from urllib.parse import urljoin, urlparse, urldefrag
from urllib.robotparser import RobotFileParser
from collections import deque
import json
import re
import shutil
import time

import requests
from bs4 import BeautifulSoup, Comment


# ============================================================
# CONFIG
# ============================================================

OUTPUT_DIR = Path("knowledge_base")

# Default page limit per technology (can be overridden below)
DEFAULT_MAX_PAGES = 60

PAGE_LIMITS = {
    "python": 140,
    "nodejs": 100,
    "java": 120,
    "django": 100,
    "fastapi": 90,
    "laravel": 80,
    "dotnet": 80,
}

REQUEST_DELAY = 1.0
TIMEOUT = 30

USER_AGENT = (
    "CodeMindAI-DeveloperDocsCrawler/1.0 "
    "(documentation research crawler)"
)

MAX_HTML_BYTES = 5 * 1024 * 1024
MAX_TEXT_CHARS = 250_000

# Delete old files of a technology before re-crawling it
CLEAN_BEFORE_CRAWL = True


# ============================================================
# SOURCES
# ============================================================
#
# Each source:
#   url        -> starting page
#   path       -> allowed URL path prefix (crawler never leaves it)
#   max_pages  -> (optional) cap for this source only
#   exclude    -> (optional) regex list; matching paths are skipped
#   pin_regex  -> (optional) if the start URL redirects (e.g. to a
#                 versioned URL), the matched part of the final path
#                 becomes the new allowed path

# skips versioned / snapshot doc paths like /6.5-SNAPSHOT/, /6.4/, /3.5.2/
VERSION_EXCLUDE = [
    r"/\d+\.\d+(\.\d+)?(-[A-Za-z0-9]+)?(/|$)",
    r"(?i)snapshot",
]

# Rails guides keep old versions at /v7.1/...
RAILS_EXCLUDE = [r"^/v\d"]

SOURCES = {
    "python": [
        {"url": "https://docs.python.org/3/tutorial/", "path": "/3/tutorial/", "max_pages": 30},
        {"url": "https://docs.python.org/3/library/", "path": "/3/library/", "max_pages": 80},
        {"url": "https://docs.python.org/3/howto/", "path": "/3/howto/", "max_pages": 30},
    ],

    "nodejs": [
        {"url": "https://nodejs.org/docs/latest/api/", "path": "/docs/latest/api/", "max_pages": 70},
        {"url": "https://expressjs.com/en/guide/", "path": "/en/guide/", "max_pages": 25},
        {"url": "https://expressjs.com/en/5x/api.html", "path": "/en/5x/", "max_pages": 5},
    ],

    "nestjs": [
        {"url": "https://docs.nestjs.com/", "path": "/"},
    ],

    "java": [
        {
            "url": "https://docs.spring.io/spring-boot/reference/",
            "path": "/spring-boot/reference/",
            "exclude": VERSION_EXCLUDE,
            "max_pages": 50,
        },
        {
            "url": "https://docs.spring.io/spring-security/reference/",
            "path": "/spring-security/reference/",
            "exclude": VERSION_EXCLUDE,
            "max_pages": 35,
        },
        {
            "url": "https://docs.spring.io/spring-framework/reference/",
            "path": "/spring-framework/reference/",
            "exclude": VERSION_EXCLUDE,
            "max_pages": 35,
        },
    ],

    "django": [
        {"url": "https://docs.djangoproject.com/en/stable/intro/", "path": "/en/stable/intro/", "max_pages": 15},
        {"url": "https://docs.djangoproject.com/en/stable/topics/", "path": "/en/stable/topics/", "max_pages": 40},
        {"url": "https://docs.djangoproject.com/en/stable/ref/", "path": "/en/stable/ref/", "max_pages": 30},
        {"url": "https://docs.djangoproject.com/en/stable/howto/", "path": "/en/stable/howto/", "max_pages": 15},
    ],

    "flask": [
        {"url": "https://flask.palletsprojects.com/en/stable/", "path": "/en/stable/"},
    ],

    "fastapi": [
        {"url": "https://fastapi.tiangolo.com/tutorial/", "path": "/tutorial/", "max_pages": 60},
        {"url": "https://fastapi.tiangolo.com/advanced/", "path": "/advanced/", "max_pages": 30},
    ],

    "laravel": [
        {
            # /docs redirects to the latest version, so pin whatever it lands on
            "url": "https://laravel.com/docs",
            "path": "/docs",
            "pin_regex": r"^/docs/[^/]+",
        },
    ],

    "rails": [
        {
            "url": "https://guides.rubyonrails.org/",
            "path": "/",
            "exclude": RAILS_EXCLUDE,
        },
    ],

    "dotnet": [
        {
            "url": "https://learn.microsoft.com/en-us/aspnet/core/",
            "path": "/en-us/aspnet/core/",
        },
    ],

    "go": [
        {"url": "https://go.dev/doc/tutorial/", "path": "/doc/tutorial/", "max_pages": 20},
        {"url": "https://gin-gonic.com/docs/", "path": "/docs/", "max_pages": 40},
    ],

    "flutter": [
        {"url": "https://docs.flutter.dev/get-started/", "path": "/get-started/"},
        {"url": "https://docs.flutter.dev/ui/", "path": "/ui/"},
        {"url": "https://docs.flutter.dev/data-and-backend/", "path": "/data-and-backend/"},
        {"url": "https://firebase.google.com/docs/flutter/", "path": "/docs/flutter/"},
    ],

    "react": [
        {"url": "https://react.dev/learn", "path": "/learn"},
        {"url": "https://react.dev/reference/react", "path": "/reference"},
        {"url": "https://reactrouter.com/start/declarative/", "path": "/start/declarative/"},
    ],
}


# ============================================================
# GLOBALS
# ============================================================

session = requests.Session()
session.headers.update(
    {
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }
)

robots_cache = {}


# ============================================================
# URL HELPERS
# ============================================================

def normalize_url(url: str) -> str:
    """
    - remove fragment and query
    - keep trailing slash (needed so relative links resolve correctly)
    - /index.html -> /
    """
    url, _ = urldefrag(url)
    p = urlparse(url)

    path = p.path or "/"

    if path.endswith("/index.html"):
        path = path[: -len("index.html")]

    return f"{p.scheme.lower()}://{p.netloc.lower()}{path}"


def get_host(url: str) -> str:
    return urlparse(url).netloc.lower()


def get_path(url: str) -> str:
    path = urlparse(url).path or "/"

    if path != "/":
        path = path.rstrip("/")

    return path


def is_http_url(url: str) -> bool:
    p = urlparse(url)
    return p.scheme in {"http", "https"} and bool(p.netloc)


def is_allowed_path(url: str, allowed_path: str) -> bool:
    current = get_path(url)
    allowed = allowed_path or "/"

    if allowed == "/":
        return True

    allowed = allowed.rstrip("/")

    return current == allowed or current.startswith(allowed + "/")


def is_allowed_url(url: str, source: dict) -> bool:
    if not is_http_url(url):
        return False

    if get_host(url) != get_host(source["url"]):
        return False

    if not is_allowed_path(url, source["path"]):
        return False

    path = get_path(url)

    for pat in source.get("exclude", []):
        if re.search(pat, path):
            return False

    return True


# ============================================================
# ROBOTS
# ============================================================

def get_robots(url: str):
    p = urlparse(url)
    robots_url = f"{p.scheme}://{p.netloc}/robots.txt"

    if robots_url in robots_cache:
        return robots_cache[robots_url]

    try:
        response = session.get(robots_url, timeout=10)

        if response.status_code == 200:
            parser = RobotFileParser()
            parser.set_url(robots_url)
            parser.parse(response.text.splitlines())
            robots_cache[robots_url] = parser
            return parser

    except requests.RequestException:
        pass

    robots_cache[robots_url] = None
    return None


def allowed_by_robots(url: str) -> bool:
    parser = get_robots(url)

    if parser is None:
        return True

    try:
        return parser.can_fetch(USER_AGENT, url)
    except Exception:
        return True


# ============================================================
# URL FILTERING
# ============================================================

SKIP_EXTENSIONS = (
    ".jpg", ".jpeg", ".png", ".gif", ".svg", ".webp", ".ico", ".bmp", ".tiff",
    ".pdf", ".zip", ".tar", ".gz", ".rar", ".7z",
    ".mp4", ".webm", ".avi", ".mov",
    ".mp3", ".wav", ".ogg",
    ".woff", ".woff2", ".ttf", ".eot",
    ".css", ".js", ".map",
    ".xml", ".json", ".md", ".txt",
)

# Index/search/static pages generated by Sphinx and similar tools
SKIP_PATH_RE = re.compile(
    r"/(genindex|search|py-modindex|modindex)(\.html)?$"
    r"|/_(sources|static|modules)/"
    r"|/objects\.inv$"
    r"|/all\.html$"  # Node.js giant duplicate page
)


def should_skip_url(url: str) -> bool:
    path = urlparse(url).path.lower()

    if SKIP_PATH_RE.search(path):
        return True

    return path.endswith(SKIP_EXTENSIONS)


# ============================================================
# FETCH
# ============================================================

def fetch_page(url: str):
    """Returns (html_bytes, final_url) or None."""
    try:
        response = session.get(url, timeout=TIMEOUT, allow_redirects=True)

        if response.status_code != 200:
            print(f"    SKIP [{response.status_code}]: {url}")
            return None

        content_type = response.headers.get("Content-Type", "").lower()

        if "text/html" not in content_type and "application/xhtml" not in content_type:
            print(f"    SKIP non-HTML: {url}")
            return None

        if len(response.content) > MAX_HTML_BYTES:
            print(f"    SKIP giant page: {url}")
            return None

        # bytes (not .text) so BeautifulSoup detects encoding itself
        return response.content, normalize_url(response.url)

    except requests.RequestException as exc:
        print(f"    ERROR: {url}")
        print(f"    {exc}")
        return None


# ============================================================
# HTML EXTRACTION
# ============================================================

# "aside" is handled separately so Python footnotes are kept
REMOVE_TAGS = {
    "script", "style", "noscript", "nav", "footer",
    "form", "svg", "canvas", "iframe",
}

# Tags that are block-level; excluded when reading a tag's "own" text
BLOCKS = {"ul", "ol", "pre", "p", "dl", "table", "div"}


def clean_text(text: str) -> str:
    text = text.replace("\xa0", " ")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def inline_text(el) -> str:
    return re.sub(r"\s+", " ", el.get_text()).replace("¶", "").strip()


def own_text(el) -> str:
    """Text of el without nested block children (avoids duplicate lines)."""
    parts = []

    for c in el.children:
        if isinstance(c, Comment):
            continue

        if isinstance(c, str):
            parts.append(str(c))
            continue

        if c.name in BLOCKS:
            continue

        parts.append(c.get_text())

    return re.sub(r"\s+", " ", "".join(parts)).replace("¶", "").strip()


def extract_code(block) -> str:
    for br in block.find_all("br"):
        br.replace_with("\n")

    code = block.get_text()
    code = code.replace("\r\n", "\n").replace("\r", "\n")
    code = "\n".join(line.rstrip() for line in code.split("\n"))
    code = re.sub(r"\n{4,}", "\n\n\n", code)

    return code.strip()


def detect_code_language(block) -> str:
    nodes = [block] + list(block.find_all("code", limit=1)) + list(block.parents)[:3]

    for n in nodes:
        classes = n.get("class", []) or []

        if isinstance(classes, str):
            classes = [classes]

        for cls in classes:
            m = re.search(
                r"(?:language|lang|highlight)-([A-Za-z0-9_+#.-]+)",
                str(cls),
                re.IGNORECASE,
            )

            if m and m.group(1).lower() not in {"default", "none"}:
                return m.group(1)

    return ""


def extract_content(html, url: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")

    for tag_name in REMOVE_TAGS:
        for tag in soup.find_all(tag_name):
            tag.decompose()

    # remove asides except footnotes
    for tag in soup.find_all("aside"):
        classes = tag.get("class", []) if tag.attrs else []
        if "footnote" not in " ".join(classes or []):
            tag.decompose()

    for a in soup.select("a.headerlink"):
        a.decompose()

    title = ""

    if soup.title:
        title = clean_text(soup.title.get_text(" ", strip=True))

    content_root = None

    for sel in ("main", "article", "div[role=main]", "div.body", "#apicontent"):
        content_root = soup.select_one(sel)

        if content_root:
            break

    if content_root is None:
        content_root = soup.body or soup

        # fallback to whole body: drop site header too
        for tag in content_root.find_all("header"):
            tag.decompose()

    sections = []

    if title:
        sections.append(f"# {title}")

    sections.append(f"SOURCE: {url}")

    code_blocks = 0

    for element in content_root.find_all(
        ["h1", "h2", "h3", "h4", "h5", "h6", "p", "li", "dt", "dd", "pre"]
    ):
        name = element.name

        if name == "pre":
            code = extract_code(element)

            if not code:
                continue

            language = detect_code_language(element)

            sections.append("")
            sections.append("CODE EXAMPLE")

            if language:
                sections.append(f"LANGUAGE: {language}")

            sections.append("```")
            sections.append(code)
            sections.append("```")

            code_blocks += 1
            continue

        text = own_text(element) if name in {"li", "dd"} else inline_text(element)

        if not text:
            continue

        if name == "dt":
            # blank line so each signature + description stays one block
            sections.append("")

        if name.startswith("h"):
            level = int(name[1])
            sections.append("")
            sections.append(f"{'#' * level} {text}")

        elif name == "li":
            sections.append(f"- {text}")

        else:
            sections.append(text)

    final_text = "\n".join(sections)
    final_text = re.sub(r"\n{4,}", "\n\n\n", final_text).strip()

    if len(final_text) > MAX_TEXT_CHARS:
        final_text = final_text[:MAX_TEXT_CHARS] + "\n\n[PAGE TRUNCATED]\n"

    return {
        "title": title,
        "url": url,
        "text": final_text,
        "code_blocks": code_blocks,
    }


# ============================================================
# LINK EXTRACTION
# ============================================================

def find_links(html, current_url: str, source: dict):
    soup = BeautifulSoup(html, "html.parser")

    links = set()

    for anchor in soup.find_all("a", href=True):
        href = anchor.get("href", "").strip()

        if not href:
            continue

        if href.startswith(("#", "mailto:", "javascript:", "tel:")):
            continue

        absolute = normalize_url(urljoin(current_url, href))

        if should_skip_url(absolute):
            continue

        if not is_allowed_url(absolute, source):
            continue

        links.add(absolute)

    return links


# ============================================================
# FILENAME / SAVE
# ============================================================

def url_to_filename(url: str) -> str:
    path = urlparse(url).path.strip("/")

    name = "index" if not path else path.replace("/", "_")
    name = re.sub(r"[^A-Za-z0-9._-]+", "_", name)

    if not name.endswith(".txt"):
        name += ".txt"

    return name[:180]


def save_document(technology: str, url: str, data: dict, used_names: set):
    technology_dir = OUTPUT_DIR / technology
    technology_dir.mkdir(parents=True, exist_ok=True)

    filename = url_to_filename(url)
    base = filename[:-4]
    counter = 2

    while filename in used_names:
        filename = f"{base}_{counter}.txt"
        counter += 1

    used_names.add(filename)

    output_path = technology_dir / filename
    output_path.write_text(data["text"], encoding="utf-8")

    return output_path


# ============================================================
# CRAWL ONE SOURCE
# ============================================================

def crawl_source(
    technology: str,
    source: dict,
    global_seen: set,
    metadata: list,
    used_names: set,
    limit: int,
):
    start_url = normalize_url(source["url"])

    queue = deque([start_url])
    local_seen = set()
    pages_saved = 0

    print()
    print(f"  SOURCE: {start_url}")
    print(f"  ALLOWED PATH: {source['path']}")
    print(f"  PAGE LIMIT: {limit}")

    while queue and pages_saved < limit:
        url = queue.popleft()
        is_start = url == start_url

        if url in local_seen:
            continue

        local_seen.add(url)

        if url in global_seen:
            continue

        global_seen.add(url)

        if not is_allowed_url(url, source):
            continue

        if should_skip_url(url):
            continue

        if not allowed_by_robots(url):
            print(f"    ROBOTS BLOCKED: {url}")
            continue

        print(f"    GET {url}")

        res = fetch_page(url)

        if res is None:
            if is_start:
                print("    WARNING: start URL failed, this source will be empty")
            continue

        html, final_url = res

        if not is_allowed_url(final_url, source):
            print(f"    SKIP redirected outside path: {final_url}")

            if is_start:
                print("    WARNING: start URL redirects outside allowed path, "
                      "update this source's url/path")
            continue

        # start URL redirected to a versioned URL -> pin that version
        if is_start and source.get("pin_regex"):
            m = re.match(source["pin_regex"], get_path(final_url))

            if m:
                source = {**source, "path": m.group(0)}
                print(f"    PINNED PATH: {source['path']}")

        if final_url != url:
            if final_url in global_seen:
                print(f"    SKIP duplicate after redirect: {final_url}")
                continue

            global_seen.add(final_url)
            local_seen.add(final_url)
            url = final_url

        data = extract_content(html, url)
        text = data["text"]

        if len(text) < 200:
            print(f"    SKIP tiny page: {url}")
            continue

        output_path = save_document(technology, url, data, used_names)
        pages_saved += 1

        metadata.append(
            {
                "technology": technology,
                "source": url,
                "file": str(output_path),
                "characters": len(text),
                "words": len(text.split()),
                "code_blocks": data["code_blocks"],
                "title": data["title"],
            }
        )

        print(f"    SAVED: {output_path}")
        print(
            f"    chars={len(text)} "
            f"words={len(text.split())} "
            f"code_blocks={data['code_blocks']}"
        )

        if pages_saved < limit:
            for link in sorted(find_links(html, url, source)):
                if (
                    link not in local_seen
                    and link not in global_seen
                    and len(queue) < limit * 3
                ):
                    queue.append(link)

        time.sleep(REQUEST_DELAY)

    return pages_saved


# ============================================================
# CRAWL TECHNOLOGY
# ============================================================

def crawl_technology(
    technology: str,
    sources: list,
    global_seen: set,
    metadata: list,
):
    max_pages = PAGE_LIMITS.get(technology, DEFAULT_MAX_PAGES)

    print()
    print("=" * 70)
    print(f"CRAWLING: {technology.upper()} (limit {max_pages} pages)")
    print("=" * 70)

    if CLEAN_BEFORE_CRAWL:
        shutil.rmtree(OUTPUT_DIR / technology, ignore_errors=True)

    used_names = set()
    total_pages = 0

    for source in sources:
        remaining = max_pages - total_pages

        if remaining <= 0:
            break

        limit = min(remaining, source.get("max_pages", remaining))

        saved = crawl_source(
            technology,
            source,
            global_seen,
            metadata,
            used_names,
            limit,
        )

        total_pages += saved

    print()
    print(f"{technology.upper()} COMPLETE")
    print(f"Pages saved: {total_pages}")


# ============================================================
# SAVE METADATA
# ============================================================

def save_metadata(metadata: list):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    metadata_path = OUTPUT_DIR / "sources.json"

    metadata_path.write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print()
    print(f"Metadata saved: {metadata_path}")


# ============================================================
# COMBINED DOCUMENT
# ============================================================

def build_combined_document():
    output_file = OUTPUT_DIR / "all_documents.txt"

    parts = []

    for technology in SOURCES.keys():
        technology_dir = OUTPUT_DIR / technology

        if not technology_dir.exists():
            continue

        for file_path in sorted(technology_dir.glob("*.txt")):
            try:
                content = file_path.read_text(encoding="utf-8")
            except Exception:
                continue

            parts.append(
                "\n".join(
                    [
                        "=" * 80,
                        f"TECHNOLOGY: {technology}",
                        f"FILE: {file_path.name}",
                        "=" * 80,
                        content,
                    ]
                )
            )

    output_file.write_text("\n\n".join(parts), encoding="utf-8")

    print(f"Combined document saved: {output_file}")


# ============================================================
# SUMMARY
# ============================================================

def print_summary(metadata: list):
    print()
    print("=" * 70)
    print("CRAWL SUMMARY")
    print("=" * 70)

    total_chars = 0
    total_words = 0
    total_code = 0
    by_technology = {t: 0 for t in SOURCES}

    for item in metadata:
        t = item["technology"]
        by_technology[t] = by_technology.get(t, 0) + 1

        total_chars += item["characters"]
        total_words += item["words"]
        total_code += item["code_blocks"]

    for t, count in by_technology.items():
        flag = "   <-- EMPTY, check URL/path" if count == 0 else ""
        print(f"{t:12} : {count} pages{flag}")

    print()
    print(f"Total pages      : {len(metadata)}")
    print(f"Total characters : {total_chars:,}")
    print(f"Total words      : {total_words:,}")
    print(f"Total code blocks: {total_code:,}")

    print()
    print(f"Knowledge base: {OUTPUT_DIR.resolve()}")


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 70)
    print("CodeMind AI - Developer Documentation Crawler")
    print("=" * 70)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    metadata = []
    global_seen = set()

    for technology, sources in SOURCES.items():
        crawl_technology(technology, sources, global_seen, metadata)

    save_metadata(metadata)
    build_combined_document()
    print_summary(metadata)

    print()
    print("=" * 70)
    print("DONE")
    print("=" * 70)


if __name__ == "__main__":
    main()