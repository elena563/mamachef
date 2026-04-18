function setupDynamicFields(addSelector, containerId, templateId) {
    const addBtn = document.querySelector(addSelector);
    const container = document.getElementById(containerId);
    const template = document.getElementById(templateId);

    if (!addBtn || !container || !template) return;

    addBtn.addEventListener('click', () => {
        const newEl = template.content.firstElementChild.cloneNode(true);
        container.appendChild(newEl);
        setupIngredientAutocomplete(newEl.querySelector('input[name="ingredient"]'));
    });

    container.addEventListener('click', (e) => {
        if (e.target.classList.contains('remove_btn')) {
            e.target.parentElement.remove();
        }
    });
}

function swapSteps(step1, step2) {
    const temp = document.createElement('div');
    step1.parentNode.insertBefore(temp, step1);
    step2.parentNode.insertBefore(step1, step2);
    temp.parentNode.insertBefore(step2, temp);
    temp.remove();
}

function initializeForm() {
    setupDynamicFields('.add_btn', 'ingredients-container', 'ingredient-template');
    setupDynamicFields('.add_btn', 'steps-container', 'step-template');

    const form = document.querySelector('form');
    if (form) {
        form.addEventListener('submit', (e) => {
            // Update all hidden fields
            document.querySelectorAll('.step-wrapper').forEach((wrapper) => {
                const hiddenInput = wrapper.querySelector('.used-ingredients-hidden');
                const checkedBoxes = wrapper.querySelectorAll('input[type="checkbox"]:checked');
                const ingredients = Array.from(checkedBoxes).map(cb => cb.value).filter(v => v);
                if (hiddenInput) {
                    hiddenInput.value = ingredients.join(',');
                }
            });
            
            const stepDivs = document.querySelectorAll('#steps-container > .step-wrapper');
            stepDivs.forEach((div, index) => {
                const orderInput = div.querySelector('input[name="order"]');
                if (orderInput) {
                    orderInput.value = index;
                }
            });
        });
    }

    // Handle step reordering (up/down buttons)
    document.addEventListener('click', (e) => {
        if (e.target.classList.contains('up_btn')) {
            const stepWrapper = e.target.closest('.step-wrapper');
            const prevStep = stepWrapper?.previousElementSibling;
            if (prevStep && prevStep.classList.contains('step-wrapper')) {
                swapSteps(stepWrapper, prevStep);
            }
        } else if (e.target.classList.contains('down_btn')) {
            const stepWrapper = e.target.closest('.step-wrapper');
            const nextStep = stepWrapper?.nextElementSibling;
            if (nextStep && nextStep.classList.contains('step-wrapper')) {
                swapSteps(stepWrapper, nextStep);
            }
        }
    });

    document.addEventListener('change', (e) => {
        const checkbox = e.target;
        
        if (checkbox.type === 'checkbox') {
            const stepWrapper = checkbox.closest('.step-wrapper');
            if (!stepWrapper) return;
            
            const hiddenInput = stepWrapper.querySelector('.used-ingredients-hidden');
            if (!hiddenInput) return;
            
            // Get all checked checkboxes in this step wrapper
            const checkedBoxes = stepWrapper.querySelectorAll('input[type="checkbox"]:checked');
            const ingredients = Array.from(checkedBoxes).map(cb => cb.value).filter(v => v);
            
            hiddenInput.value = ingredients.join(',');
        }
    });
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeForm);
} else {
    initializeForm();
}


function setupIngredientSuggestions(inputElement) {
    let timeout = null;
    let suggestionsDiv = null;
    
    inputElement.addEventListener('input', function(e) {
        const query = e.target.value.trim();
        
        if (suggestionsDiv) {
            suggestionsDiv.remove();
        }
        
        if (query.length < 1) return;
        
        // Debounce: wait 300ms
        clearTimeout(timeout);
        timeout = setTimeout(() => {
            fetch(`/api/ingredients/autocomplete/?q=${encodeURIComponent(query)}`)
                .then(response => response.json())
                .then(data => {
                    if (data.ingredients.length > 0) {
                        showSuggestions(inputElement, data.ingredients);
                    }
                });
        }, 300);
    });
    
    function showSuggestions(input, suggestions) {
        suggestionsDiv = document.createElement('div');
        suggestionsDiv.className = 'bg-base-50 border-2 border-light-blue rounded-md shadow-lg fixed z-50 max-h-48 overflow-y-auto';

        const rect = input.getBoundingClientRect();
        suggestionsDiv.style.top = `${rect.bottom +2}px`;
        suggestionsDiv.style.left = `${rect.left}px`;
        suggestionsDiv.style.width = `${rect.width}px`;
        
        suggestions.forEach(ingredient => {
            const item = document.createElement('div');
            item.className = 'px-4 py-2 bg-white rounded-sm hover:bg-blue-100 cursor-pointer z-50';
            item.textContent = ingredient;
            
            item.addEventListener('click', () => {
                input.value = ingredient;
                suggestionsDiv.remove();
            });
            
            suggestionsDiv.appendChild(item);
        });
        
        document.body.appendChild(suggestionsDiv);
    }
    
    // remove when clicking outside or scrolling
    document.addEventListener('click', (e) => {
        if (suggestionsDiv && !inputElement.contains(e.target)) {
            suggestionsDiv.remove();
        }
    });

    window.addEventListener('scroll', () => {
        if (suggestionsDiv) {
            suggestionsDiv.remove();
        }
    }, true);
}

document.querySelectorAll('input[name="ingredient"]').forEach(input => {
    setupIngredientSuggestions(input);
});
