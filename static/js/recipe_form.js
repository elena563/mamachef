function setupDynamicFields(addSelector, containerId, templateId) {
    const addBtn = document.querySelector(addSelector);
    const container = document.getElementById(containerId);
    const template = document.getElementById(templateId);

    if (!addBtn || !container || !template) return;

    addBtn.addEventListener('click', () => {
        const newEl = template.content.firstElementChild.cloneNode(true);
        container.appendChild(newEl);
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
    // Setup dynamic fields for ingredients and steps
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

    // Handle ingredient checkboxes
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

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeForm);
} else {
    initializeForm();
}
