# Playwright Playground

Just familiarizing myself with how playwright works, with video recording.

This is a uv project, but you also need to install the playwright browsers:

```
$ uv sync
$ uv run playwright install
```

From there you can then do a:

```
$ uv run main.py -h
```

This will go to a given url, and make a video clicking all the links on the page. It will then live in videos/