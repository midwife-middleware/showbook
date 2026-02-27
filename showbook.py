#!/usr/bin/env python3
"""
ShowBook — The Complete Streaming Guide
A PDF book of every show and movie on every streaming service.
Because someone said they should make a book for that. So we did.
"""

import argparse
import os
import sys
import time
from collections import OrderedDict
from datetime import date

import requests
from fpdf import FPDF

# TMDB caps discover results at 500 pages (10,000 titles per query).
# We default to ALL of them. This is the point.
TMDB_MAX_PAGES = 500


TMDB_BASE = "https://api.themoviedb.org/3"

# Major US streaming providers (TMDB watch provider IDs)
PROVIDERS = OrderedDict([
    (8, "Netflix"),
    (9, "Amazon Prime Video"),
    (337, "Disney+"),
    (15, "Hulu"),
    (384, "Max"),
    (350, "Apple TV+"),
    (386, "Peacock"),
    (531, "Paramount+"),
])

REQUEST_DELAY = 0.26  # ~4 req/s, well under TMDB's 40/10s limit


def get_api_key(cli_key=None):
    key = cli_key or os.environ.get("TMDB_API_KEY")
    if not key:
        print("Error: TMDB API key required.")
        print("  Set TMDB_API_KEY env var or pass --api-key KEY")
        print("  Get a free key at https://www.themoviedb.org/settings/api")
        sys.exit(1)
    return key


def tmdb_get(endpoint, api_key, params=None):
    """Make a TMDB API request with basic error handling."""
    params = params or {}
    params["api_key"] = api_key
    resp = requests.get(f"{TMDB_BASE}{endpoint}", params=params, timeout=30)
    if resp.status_code == 401:
        print("Error: Invalid API key.")
        sys.exit(1)
    resp.raise_for_status()
    return resp.json()


def list_providers(api_key, region):
    """Fetch and display available watch providers from TMDB."""
    data = tmdb_get("/watch/providers/movie", api_key, {"watch_region": region})
    providers = sorted(data.get("results", []), key=lambda p: p["provider_name"])
    print(f"\nAvailable streaming providers in {region}:\n")
    print(f"  {'ID':>6}  Provider")
    print(f"  {'--':>6}  --------")
    for p in providers:
        marker = " <--" if p["provider_id"] in PROVIDERS else ""
        print(f"  {p['provider_id']:>6}  {p['provider_name']}{marker}")
    print(f"\n  Providers marked with <-- are included by default.")


def fetch_titles(api_key, provider_id, media_type, region, max_pages, label=""):
    """Fetch all titles for a provider/media_type from TMDB discover."""
    titles = []
    page = 1
    total_pages = "?"

    while page <= max_pages:
        data = tmdb_get(f"/discover/{media_type}", api_key, {
            "with_watch_providers": provider_id,
            "watch_region": region,
            "with_watch_monetization_types": "flatrate",
            "sort_by": "popularity.desc",
            "page": page,
        })

        api_total = min(data.get("total_pages", 1), max_pages)
        total_pages = api_total

        for item in data.get("results", []):
            name = item.get("title") or item.get("name") or "Unknown"
            year = None
            release = item.get("release_date") or item.get("first_air_date") or ""
            if release:
                year = release[:4]
            titles.append((name, year))

        # Live progress
        print(f"\r    {label}: page {page}/{total_pages}"
              f" ({len(titles)} titles)", end="", flush=True)

        if page >= data.get("total_pages", 1):
            break
        page += 1
        time.sleep(REQUEST_DELAY)

    print()  # newline after progress

    # Deduplicate and sort alphabetically
    seen = set()
    unique = []
    for name, year in titles:
        key = name.lower()
        if key not in seen:
            seen.add(key)
            unique.append((name, year))
    return sorted(unique, key=lambda t: t[0].casefold())


def safe(text):
    """Make text safe for built-in PDF fonts (latin-1)."""
    return text.encode("latin-1", errors="replace").decode("latin-1")


class ShowBook(FPDF):
    """The sacred text."""

    def header(self):
        if self.page_no() > 1:
            self.set_font("Helvetica", "I", 8)
            self.cell(0, 8, safe("ShowBook \u2014 The Complete Streaming Guide"), align="C")
            self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")

    def title_page(self):
        self.add_page()
        self.set_font("Helvetica", "B", 52)
        self.cell(0, 70, "", ln=True)
        self.cell(0, 20, "ShowBook", ln=True, align="C")
        self.ln(5)
        self.set_font("Helvetica", "", 18)
        self.cell(0, 12, safe("The Complete Streaming Guide"), ln=True, align="C")
        self.ln(20)
        self.set_font("Helvetica", "I", 11)
        self.multi_cell(0, 6, safe(
            '"Crazy when you get a new streaming service and see all\n'
            'these shows and movies you forgot existed. Like oh that\'s\n'
            'where these were. They should make some kind of interface\n'
            'where you could surf through all the different options at once.\n'
            'Or maybe a book to tell you what\'s on where."\n'
            '\n'
            '\u2014 @deepfates'
        ), align="C")
        self.ln(15)
        self.set_font("Helvetica", "", 12)
        self.cell(0, 8, safe("So here's your book."), ln=True, align="C")
        self.cell(0, 8, safe("You're welcome."), ln=True, align="C")
        self.ln(30)
        self.set_font("Helvetica", "", 10)
        self.cell(0, 6, safe(f"Generated {date.today().strftime('%B %d, %Y')}"), ln=True, align="C")
        self.cell(0, 6, safe("(Already out of date.)"), ln=True, align="C")

    def toc_page(self, catalog):
        self.add_page()
        self.set_font("Helvetica", "B", 28)
        self.cell(0, 18, "Table of Contents", ln=True)
        self.ln(8)
        self.set_font("Helvetica", "", 13)
        for provider_name, sections in catalog.items():
            n_movies = len(sections["Movies"])
            n_shows = len(sections["Shows"])
            line = f"{provider_name}  \u2014  {n_movies} movies, {n_shows} shows"
            self.cell(0, 9, safe(line), ln=True)
        self.ln(15)
        total = sum(
            len(s["Movies"]) + len(s["Shows"]) for s in catalog.values()
        )
        self.set_font("Helvetica", "B", 13)
        self.cell(0, 9, safe(f"Total: {total} titles"), ln=True)

    def provider_section(self, provider_name, movies, shows):
        self.add_page()
        self.set_font("Helvetica", "B", 32)
        self.cell(0, 18, safe(provider_name), ln=True)
        y = self.get_y()
        self.line(10, y, 200, y)
        self.ln(8)

        self._title_list("Movies", movies)
        self.ln(6)
        self._title_list("Shows", shows)

    def _title_list(self, heading, titles):
        self.set_font("Helvetica", "B", 16)
        self.cell(0, 10, safe(f"{heading} ({len(titles)})"), ln=True)
        self.ln(2)
        self.set_font("Helvetica", "", 9)
        for name, year in titles:
            if self.get_y() > 272:
                self.add_page()
            suffix = f" ({year})" if year else ""
            self.cell(0, 4.8, safe(f"  {name}{suffix}"), ln=True)

    def back_matter(self):
        self.add_page()
        self.set_font("Helvetica", "", 10)
        self.cell(0, 90, "", ln=True)
        self.set_font("Helvetica", "B", 14)
        self.cell(0, 8, "Colophon", ln=True, align="C")
        self.ln(5)
        self.set_font("Helvetica", "", 10)
        self.multi_cell(0, 6, safe(
            "Generated by ShowBook\n"
            "github.com/midwife-middleware/showbook\n"
            "\n"
            "Streaming data provided by TMDB (themoviedb.org).\n"
            "This product uses the TMDB API but is not\n"
            "endorsed or certified by TMDB.\n"
            "\n"
            "You could have just scrolled through the apps,\n"
            "but no. You wanted a book.\n"
            "Here's your book."
        ), align="C")


def generate_pdf(catalog, output_path):
    pdf = ShowBook()
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=False)

    pdf.title_page()
    pdf.toc_page(catalog)

    for provider_name, sections in catalog.items():
        pdf.provider_section(provider_name, sections["Movies"], sections["Shows"])

    pdf.back_matter()
    pdf.output(output_path)
    return output_path


def main():
    parser = argparse.ArgumentParser(
        description="ShowBook: A PDF book of every streaming catalog. "
                    "Because a PDF is clearly the best format for this.",
    )
    parser.add_argument(
        "--api-key",
        help="TMDB API key (or set TMDB_API_KEY env var)",
    )
    parser.add_argument(
        "-o", "--output",
        default="showbook.pdf",
        help="Output PDF path (default: showbook.pdf)",
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=TMDB_MAX_PAGES,
        help=f"Max result pages per query, 20 titles/page (default: {TMDB_MAX_PAGES} — everything)",
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Quick mode: only 5 pages per query (~100 titles each). For cowards.",
    )
    parser.add_argument(
        "--region",
        default="US",
        help="Watch region code (default: US)",
    )
    parser.add_argument(
        "--list-providers",
        action="store_true",
        help="List available streaming providers and exit",
    )
    args = parser.parse_args()

    if args.quick:
        args.max_pages = 5

    api_key = get_api_key(args.api_key)

    if args.list_providers:
        list_providers(api_key, args.region)
        return

    catalog = OrderedDict()
    total_movies = 0
    total_shows = 0

    print("ShowBook - The Complete Streaming Guide")
    print("=" * 42)
    if args.max_pages == TMDB_MAX_PAGES:
        print("  Mode: EVERYTHING (this is going to take a while)")
        print(f"  Fetching up to {TMDB_MAX_PAGES} pages per query across"
              f" {len(PROVIDERS)} providers...")
        print("  Go make coffee. Or read a physical book. The irony is free.")
    elif args.quick:
        print("  Mode: quick (--quick). Coward mode engaged.")
    else:
        print(f"  Mode: {args.max_pages} pages per query")

    for provider_id, provider_name in PROVIDERS.items():
        print(f"\n  {provider_name}")

        movies = fetch_titles(
            api_key, provider_id, "movie", args.region, args.max_pages,
            label="Movies",
        )

        shows = fetch_titles(
            api_key, provider_id, "tv", args.region, args.max_pages,
            label="Shows ",
        )

        if not movies and not shows:
            print(f"    (no results — provider ID {provider_id} may be wrong,")
            print(f"     try --list-providers to find the correct ID)")

        catalog[provider_name] = {"Movies": movies, "Shows": shows}
        total_movies += len(movies)
        total_shows += len(shows)

    print(f"\n  Generating PDF: {total_movies} movies + {total_shows} shows "
          f"= {total_movies + total_shows} titles")

    output = generate_pdf(catalog, args.output)

    print(f"\n  Done! Your book is ready: {output}")
    print(f"  Now go read your PDF instead of just opening the apps.")


if __name__ == "__main__":
    main()
