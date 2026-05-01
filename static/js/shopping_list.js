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
        listNameInput.addEventListener('blur', () => {
            listNameInput.classList.add('hidden');
            listName.textContent = listNameInput.value || 'Untitled List';
            listName.classList.remove('hidden');
        });
    }

    const items = document.querySelectorAll('#item-cont')
    console.log(items)
    items.forEach((item) => {
        const view = item.querySelector('.view-mode')
        const edit = item.querySelector('.edit-mode')
        item.addEventListener('click', () => {
            view.classList.add('hidden')
            edit.classList.remove('hidden');
        })
    })
});