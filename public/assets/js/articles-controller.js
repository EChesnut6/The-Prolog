document.addEventListener('DOMContentLoaded', () => {
  const searchInput = document.querySelector("#dedicated-article-search");
  const resultsGrid = document.querySelector("#dedicated-results-grid");
  const statusText = document.querySelector("#dedicated-search-status");
  const paginationControls = document.querySelector("#pagination-controls");

  if (!searchInput || !resultsGrid || !statusText || !paginationControls) {
    return;
  }

  const articles = window.articles || [];
  let currentPage = 1;
  const pageSize = 12; // Fewer articles than movies, so 12 per page is great for a grid
  let currentMatches = [...articles];

  function renderPagination(totalItems) {
    const totalPages = Math.ceil(totalItems / pageSize);
    if (totalPages <= 1) {
      paginationControls.innerHTML = "";
      return;
    }

    let html = `
      <button class="page-button" ${currentPage === 1 ? 'disabled' : ''} onclick="goToPage(${currentPage - 1})">Previous</button>
      <span class="page-info">Page ${currentPage} of ${totalPages}</span>
      <button class="page-button" ${currentPage === totalPages ? 'disabled' : ''} onclick="goToPage(${currentPage + 1})">Next</button>
    `;
    
    paginationControls.innerHTML = html;
  }

  window.goToPage = function(page) {
    currentPage = page;
    renderResults(currentMatches, false);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  function renderResults(matches, resetPagination = true) {
    if (resetPagination) {
      currentPage = 1;
      currentMatches = matches;
    }

    if (matches.length === 0) {
      resultsGrid.innerHTML = '<div class="no-results" style="grid-column: 1/-1; text-align: center; color: var(--text-muted); padding: 40px;">No articles found matching your search.</div>';
      statusText.textContent = "No results found";
      paginationControls.innerHTML = "";
      return;
    }

    const start = (currentPage - 1) * pageSize;
    const end = start + pageSize;
    const pageItems = matches.slice(start, end);

    resultsGrid.innerHTML = pageItems.map(art => `
      <article class="collection-card">
        <a href="articles/${art.slug}.html">
          <div class="collection-card__content">
            <div class="meta" style="margin-bottom: 12px; margin-top: 0; justify-content: flex-start; gap: 8px;">
              <span style="font-size: 0.75rem; color: var(--text-muted);">${art.date}</span>
            </div>
            <h3>${art.title}</h3>
            <p>${art.teaser}</p>
            <div class="meta">
              <span>By ${art.author}</span>
              <span>Read Article →</span>
            </div>
          </div>
        </a>
      </article>
    `).join("");
    
    statusText.textContent = `${matches.length} article${matches.length === 1 ? "" : "s"} found`;
    renderPagination(matches.length);
  }

  function performSearch() {
    const query = searchInput.value.trim().toLowerCase();
    
    if (!query) {
      renderResults(articles);
      statusText.textContent = "Showing all articles";
      return;
    }

    // Filter by Title first, then author/teaser/keywords
    const titleMatches = articles.filter(art => art.title.toLowerCase().includes(query));
    const otherMatches = articles.filter(art => 
      !titleMatches.includes(art) && 
      (art.author.toLowerCase().includes(query) || 
       art.teaser.toLowerCase().includes(query) || 
       art.keywords.toLowerCase().includes(query))
    );

    renderResults([...titleMatches, ...otherMatches]);
  }

  searchInput.addEventListener("input", performSearch);
  
  // Initial render
  renderResults(articles);
});
