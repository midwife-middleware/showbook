# ShowBook

> "They should make some kind of interface where you could surf through all the different options at once. Or maybe a book to tell you what's on where." — [@deepfates](https://x.com/deepfates)

A Python script that fetches the catalogs of every major streaming service and compiles them into a **PDF book** instead of any easily usable digital format.

You're welcome.

## What it does

1. Pulls movie and TV show catalogs from Netflix, Amazon Prime Video, Disney+, Hulu, Max, Apple TV+, Peacock, and Paramount+
2. Organizes everything by provider → movies/shows → alphabetical order
3. Outputs it as a PDF, like God intended

## Setup

```bash
pip install -r requirements.txt
```

You'll need a free TMDB API key: https://www.themoviedb.org/settings/api

## Usage

```bash
# Set your API key
export TMDB_API_KEY="your_key_here"

# Generate the book
python showbook.py

# Or pass the key directly
python showbook.py --api-key your_key_here

# Custom output path
python showbook.py -o streaming_guide_2026.pdf

# More titles (default 25 pages = ~500 titles per category)
python showbook.py --max-pages 100

# Different region
python showbook.py --region GB

# See available streaming providers
python showbook.py --list-providers
```

## The book contains

- **Title page** with the original quote
- **Table of contents** with title counts per service
- **Full alphabetical listings** per provider, split by movies and shows
- **A colophon**, because it's a *book*
- An immediate expiration date, because streaming catalogs change constantly

## Attribution

Streaming data provided by [TMDB](https://www.themoviedb.org/). This product uses the TMDB API but is not endorsed or certified by TMDB.
