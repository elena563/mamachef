document.addEventListener('submit', async (event) => {
  const form = event.target.closest('[data-favorite-form]');
  if (!form) return;
  event.preventDefault();

  const recipeId = form.dataset.recipeId;
  const token = form.querySelector('input[name="csrfmiddlewaretoken"]').value;

  try {
    const res = await fetch(form.action, {
      method: 'POST',
      headers: { 'X-CSRFToken': token },
      credentials: 'same-origin',
    });
    const data = await res.json();
    if (!data.success) return;

    setFavoritesState(recipeId, data.favorited);
    syncFavoritesGrid(recipeId, data.favorited, form);
  } catch (err) {
    console.error(err);
  }
});

function setFavoritesState(recipeId, favorited) {
  document.querySelectorAll(`[data-favorite-card][data-recipe-id="${recipeId}"]`).forEach((card) => {
    const icon = card.querySelector('[data-favorite-icon]');
    if (icon) icon.setAttribute('fill', favorited ? 'currentColor' : 'none');
  });
}

function syncFavoritesGrid(recipeId, favorited, form) {
  const grid = document.getElementById('favorites-grid');
  if (!grid) return;

  const empty = document.getElementById('favorites-empty');
  const existing = grid.querySelector(`[data-favorite-card][data-recipe-id="${recipeId}"]`);

  if (favorited) {
    if (!existing) {
      const source = form.closest('[data-favorite-card]');
      if (source) {
        grid.appendChild(source.cloneNode(true));
      }
    }
  } else if (existing) {
    existing.remove();
  }

  const hasCards = grid.querySelectorAll('[data-favorite-card]').length > 0;
  grid.classList.toggle('hidden', !hasCards);
  if (empty) empty.classList.toggle('hidden', hasCards);
}
