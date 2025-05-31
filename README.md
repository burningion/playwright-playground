# Playwright Playground

Just familiarizing myself with how playwright works, with video recording.

This is a uv project, but you also need to install the playwright browsers:

```
$ uv sync
$ uv run playwright install
```

From there you can then do a:

```
$ uv run main.py --help
Usage: main.py [OPTIONS]

  Main function to run the link clicker

Options:
  -u, --url TEXT  URL to visit and click all links on
  -h, --headless  Run in headless mode (no visible browser)
  --help          Show this message and exit.
```

This will go to a given url, and make a video clicking all the links on the page. It will then live in `videos/` as .webm files.