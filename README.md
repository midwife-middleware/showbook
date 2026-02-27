# ShowBook

> "They should make some kind of interface where you could surf through all the different options at once. Or maybe a book to tell you what's on where." — [@deepfates](https://x.com/deepfates)

A Python script that fetches the catalogs of every major streaming service and compiles them into a **KDP-ready paperback PDF** instead of any easily usable digital format.

Yes. A physical book. That you can sell on Amazon. You're welcome.

## What it does

1. Pulls movie and TV show catalogs from Netflix, Amazon Prime Video, Disney+, Hulu, Max, Apple TV+, Peacock, and Paramount+
2. Caches the data as JSON so you don't burn API calls every time
3. Organizes everything by provider → movies/shows → alphabetical order
4. Outputs a 6"x9" KDP-ready paperback PDF with proper margins, alternating gutter, and page numbers

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

You'll need a free TMDB API key: https://www.themoviedb.org/settings/api

## Usage

```bash
export TMDB_API_KEY="your_key_here"

# Fetch data + generate PDF in one shot
python showbook.py

# Just fetch and cache the data (no PDF yet)
python showbook.py --fetch-only

# Generate PDF from cached data (iterate on formatting without re-fetching)
python showbook.py --from-cache catalog-US-2026-02-27.json

# Quick mode for cowards (~100 titles per category)
python showbook.py --quick

# Different region
python showbook.py --region GB

# See available streaming providers
python showbook.py --list-providers
```

## The book contains

- **Title page**: *The Show and Movie Catalogue: YYYY/MM/DD Edition*
- **Index** with title counts per service
- **Full alphabetical listings** per provider, split by movies and shows
- **A colophon**, because it's a *book*
- An immediate expiration date, because streaming catalogs change constantly

## KDP specs

- **Trim size:** 6" x 9" (standard US paperback)
- **Margins:** 0.75" gutter, 0.5" outside/top/bottom
- **Alternating gutter** for proper left/right page binding
- **Even page count** (padded if needed)
- **Max 828 pages** (warns if exceeded)

Upload to [KDP](https://kdp.amazon.com/) and let Amazon print your streaming guide on demand. Each copy will be outdated by the time it ships.

## Attribution

Streaming data provided by [TMDB](https://www.themoviedb.org/). This product uses the TMDB API but is not endorsed or certified by TMDB.
