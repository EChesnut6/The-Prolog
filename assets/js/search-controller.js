document.addEventListener('DOMContentLoaded', () => {
  const searchInput = document.querySelector("#dedicated-movie-search");
  const resultsGrid = document.querySelector("#dedicated-results-grid");
  const statusText = document.querySelector("#dedicated-search-status");
  const paginationControls = document.querySelector("#pagination-controls");

  if (!searchInput || !resultsGrid || !statusText || !paginationControls) {
    return;
  }

  const movies = window.movies || [];
  let currentPage = 1;
  const pageSize = 40;
  let currentMatches = [...movies];

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
      resultsGrid.innerHTML = '<div class="no-results">No movies found matching your search.</div>';
      statusText.textContent = "No results found";
      paginationControls.innerHTML = "";
      return;
    }

    const start = (currentPage - 1) * pageSize;
    const end = start + pageSize;
    const pageItems = matches.slice(start, end);

    resultsGrid.innerHTML = pageItems.map(m => `
      <article class="mini-card">
        <a href="reviews/${m.slug}.html">
          <img src="${m.poster}" alt="${m.title} poster">
          <div class="mini-card__copy">
            <h3>
              ${m.title}
              ${m.reviewed ? '<span class="review-icon" title="Reviewed">★</span>' : ''}
            </h3>
            <p class="mini-card__meta">${m.year} · ${m.director}</p>
          </div>
        </a>
      </article>
    `).join("");
    
    statusText.textContent = `${matches.length} movie${matches.length === 1 ? "" : "s"} found`;
    renderPagination(matches.length);
  }

  function performSearch() {
    const query = searchInput.value.trim().toLowerCase();
    
    if (!query) {
      renderResults(movies);
      statusText.textContent = "Showing all movies";
      return;
    }

    // Filter by Title first, then Director as requested
    const titleMatches = movies.filter(m => m.title.toLowerCase().includes(query));
    const directorMatches = movies.filter(m => 
      !titleMatches.includes(m) && m.director.toLowerCase().includes(query)
    );

    renderResults([...titleMatches, ...directorMatches]);
  }

  searchInput.addEventListener("input", performSearch);
  
  // Initial render
  renderResults(movies);
});
