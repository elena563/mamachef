import { setupDynamicFields } from './recipe_form.js';

document.addEventListener('DOMContentLoaded', () => {
    setupDynamicFields('.add_btn', 'items-container', 'item-template');

    const listName = document.getElementById('listName');
    const listNameInput = document.querySelector('input[name="list_name"]');
    if (listName && listNameInput) {
        listName.addEventListener('click', () => {
            listName.classList.add('hidden');
            listNameInput.classList.remove('hidden');
            listNameInput.focus();
    });
    }
});