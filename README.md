# Michael Harmon's website

This repo holds the content for [your site]. Every time you change a file here, Netlify automatically rebuilds and redeploys (about a minute).

You never need to touch HTML or CSS. You edit text files and upload images — that's it.

---

## How the folders work

Each page on the site has its own folder:

| Folder | Page | What's in it |
|---|---|---|
| `home/` | Homepage | Bio + hero banner + portrait photo |
| `stories/` | Stories | Intro text + list of articles in `stories.yml` |
| `photos/` | Photos | Intro text + image grid |
| `newsletter/` | Newsletter | Placeholder until you set `substack_url` in `config.yml` |
| `contact/` | Contact | Email + optional photo |

Inside each folder:
- **`text.md`** — the words on that page
- **`images/`** — images for that page

---

## Editing text

1. Click into a page folder (e.g. `home/`)
2. Click `text.md`
3. Click the pencil icon (top right) to edit
4. Make your changes
5. Scroll down and click **Commit changes**

### Formatting cheatsheet

```
Leave a blank line between paragraphs.

Like this — that's a new paragraph.

Make a [link](https://example.com) with brackets and parentheses.
Use **double stars** for bold.
Use *single stars* for italic.
```

---

## Adding a new story (the main thing you'll do)

1. Open `stories/stories.yml`
2. Click the pencil icon to edit
3. Add a new block at the **top** of the list (newest stories appear first):

```yaml
- kicker: Travel
  title: A Headline About Somewhere Far Away
  dek: A one- or two-sentence summary of what the piece is about, in the same voice as an NYT dek.
  publication: The New York Times
  date: November 12, 2025
  link: https://www.nytimes.com/2025/11/12/travel/...
  image: bali.jpg
```

4. (Optional) Upload an image for the story to `stories/images/` and reference it by filename in the `image:` field
5. **Commit changes**

### What each field is for

- `kicker` — a short label that appears in red above the headline (e.g. "TRAVEL", "FOOD", "NEW YORK")
- `title` — the headline of the article
- `dek` — the summary that appears under the headline
- `publication` — usually "The New York Times"
- `date` — when it was published
- `link` — the URL to the article on nytimes.com (or wherever)
- `image` — filename of the cover image in `stories/images/` (optional but recommended)
- `featured: true` — add this line to make a story the big one at the top of the page; only one story should be featured at a time

### Watch out

If any value contains a colon, wrap it in double quotes:

```yaml
title: "After the Flood: A Town Rebuilds"
```

---

## Adding photos to the Photos page

1. Open `photos/images/`
2. Click **Add file → Upload files**
3. Drag in your photos
4. **Commit changes**

Photos are sorted by filename. Name them `01.jpg`, `02.jpg`, `03.jpg`... to control the order.

---

## Changing the homepage hero or portrait

- Hero banner: replace `home/images/hero.jpg` with your image (any image named `hero.*` works — `.jpg`, `.png`, etc.)
- Portrait: replace `home/images/portrait.jpg` with your photo

---

## Turning on the Substack subscribe form

When you start a Substack:

1. Open `config.yml`
2. Find the line `substack_url: ""`
3. Paste your Substack URL between the quotes, e.g. `substack_url: "https://mikeharmon.substack.com"`
4. **Commit changes**

The Newsletter page will switch from a placeholder to an embedded subscribe form automatically.

You can also edit `newsletter/text.md` to change the intro copy on that page.

---

## Site-wide settings

Edit `config.yml` to change:
- The site name in the header (`site_name`)
- The big nameplate on the homepage (`home_heading`)
- The tagline under the nameplate (`tagline`)
- The Substack URL (`substack_url`)
- The navigation menu order

---

## Did something break?

If the site stops updating after a change:

1. Go to [app.netlify.com](https://app.netlify.com) and check the latest deploy — it shows an error message if the build failed
2. The most common cause is a typo in `stories.yml` — usually a missing colon, a missing quote around a title with a colon in it, or wrong indentation
3. Every change is saved in git history, so nothing is ever lost — you can always click **History** on any file to see previous versions and restore them
