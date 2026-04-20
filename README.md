# Durham County Civic Hub

A free, nonpartisan civic information resource for Durham County, NC residents — modeled after [Peak News Network](https://peaknewsnetwork.org/) (Apex, NC).

Maintained as a public service by Commissioner Nida Allam's office.

## What's Included

- **Latest News** — curated Durham County news with tag filtering and search
- **Budget Explorer** — interactive FY2025 budget breakdown by department, revenue sources, and key investments
- **Public Meetings** — upcoming Board of Commissioners, DPS Board, and Planning Commission meetings
- **Commissioner Districts** — who represents you and how to reach them
- **Civic Tools** — 12 direct links to county services (voter registration, property records, public records requests, etc.)

## Files

```
index.html   — Main page
budget.html  — Full budget explorer
styles.css   — All styles
app.js       — Search, filtering, budget charts
README.md    — This file
```

## Deploying to GitHub Pages

1. **Create a GitHub repository**
   - Go to [github.com](https://github.com) → New repository
   - Name it `durham-civic-hub` (or any name you prefer)
   - Set it to **Public**
   - Do NOT initialize with a README (you already have one)

2. **Push these files**
   ```bash
   cd durham-news-network
   git init
   git add .
   git commit -m "Initial commit: Durham County Civic Hub"
   git branch -M main
   git remote add origin https://github.com/YOUR-USERNAME/durham-civic-hub.git
   git push -u origin main
   ```

3. **Enable GitHub Pages**
   - Go to your repository → **Settings** → **Pages**
   - Under "Source", select **Deploy from a branch**
   - Branch: `main` · Folder: `/ (root)`
   - Click **Save**

4. **Your site will be live at:**
   ```
   https://YOUR-USERNAME.github.io/durham-civic-hub/
   ```
   (Takes 1–2 minutes to go live after first deploy)

## Updating Content

### Adding a news story
In `index.html`, add a new `<article>` block inside `#storiesGrid`:
```html
<article class="story-card" data-tags="commissioners budget">
  <div class="story-meta">
    <span class="story-tag">Commissioners</span>
    <time datetime="2026-04-15">April 15, 2026</time>
  </div>
  <h3 class="story-title"><a href="LINK-TO-ARTICLE">Your Headline Here</a></h3>
  <p class="story-excerpt">Brief summary of the story (2–3 sentences).</p>
  <div class="story-footer">
    <span class="story-source">Source Name</span>
    <a href="LINK-TO-ARTICLE" class="story-read-more">Read more →</a>
  </div>
</article>
```

Available tags: `commissioners`, `budget`, `schools`, `housing`, `public-safety`, `environment`, `transit`

### Adding a meeting
In `index.html`, add a new `.meeting-row` inside `.meetings-list`:
```html
<div class="meeting-row">
  <div class="meeting-date-col">
    <span class="m-month">APR</span>
    <span class="m-day">28</span>
  </div>
  <div class="meeting-body">
    <div class="meeting-name">Meeting Name</div>
    <div class="meeting-where">Day · Time · Location</div>
    <div class="meeting-links">
      <a href="AGENDA-URL" target="_blank" class="m-link">Agenda</a>
    </div>
  </div>
  <div class="meeting-type-badge">Type</div>
</div>
```

### Updating budget numbers
Budget data lives in `app.js` — update the `SPENDING`, `REVENUE`, and `DEPARTMENTS` arrays at the top of the file when new budget figures are released.

## Custom Domain (Optional)

To use a custom domain like `durhamcivichub.org`:
1. Buy the domain from any registrar (Namecheap, Google Domains, etc.)
2. In your repo, create a file named `CNAME` containing just your domain:
   ```
   durhamcivichub.org
   ```
3. Point your domain's DNS to GitHub Pages (see [GitHub Pages docs](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site))

## License

This project is released into the public domain. Reuse, fork, and adapt freely.
