To add your next review, the project flow is:

  1. Create a new Markdown file in content/movies/.

  Use the existing review as the template:

  cp content/movies/the-lighthouse.md content/movies/my-movie-slug.md

  2. Update the front matter at the top:

  ---
  title: Movie Title
  slug: movie-title
  tmdb_title: Movie Title
  year: 2024
  enjoyment_rating: 8
  filmmaking_rating: 8
  teaser: One short sentence that appears on the homepage and review hero.
  ---

  The slug controls the generated URL:

  public/reviews/movie-title.html

  3. Fill in the required sections:

  ## Primer

  Spoiler-light context for someone before watching.

  ## Technical Footnotes

  - Aspect ratio, format, sound, production note, useful viewing lens, etc.

  ## Review

  Your full critique.

  ## Gallery

  - Visual reference
  - Production still idea
  - Related artwork or image category

  4. Build the site:

  python3 src/build.py
