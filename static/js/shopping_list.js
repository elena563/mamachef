import { setupDynamicFields } from './recipe_form.js';



function updateDisabledBtn(btn, items) {
    const isEmpty = items.length === 0;
    
    btn.classList.toggle('opacity-50', isEmpty);
    btn.classList.toggle('cursor-not-allowed', isEmpty);
    btn.classList.toggle('cursor-pointer', !isEmpty);
}

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

    const removeBoughtBtn = document.querySelector('.remove_bought_btn');
    const items = document.querySelectorAll('.item-cont')

    items.forEach((item) => {
        const label = item.querySelector('.item-label')
        const view = item.querySelector('.view-mode')
        const edit = item.querySelector('.edit-mode')
        label.addEventListener('click', () => {
            view.classList.add('hidden')
            edit.classList.remove('hidden');
        })

        const checkbox = item.querySelector('.item-checkbox')
        checkbox.addEventListener('change', async () => {
            item.classList.toggle('bought');
            label.classList.toggle('line-through')

            const itemId = item.dataset.itemId;
            try {
                await fetch(`/shopping-list/item/${itemId}/bought/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken'),
                    },
                    body: JSON.stringify({ bought: checkbox.closest('input').checked }),
                });

                // if there's at least one bought item, remove bought btn enabled
                const boughtItems = document.querySelectorAll('.item-cont.bought');
                removeBoughtBtn.disabled = boughtItems.length === 0;
                updateDisabledBtn(removeBoughtBtn, boughtItems);
            } catch (err) {
                item.classList.toggle('bought');
                label.classList.toggle('line-through');
                console.error(err);
            }
        })
    })


    const clearBtn = document.querySelector('.clear_btn');

    clearBtn.addEventListener('click', () => {
        items.forEach(item => item.remove());
    })

    removeBoughtBtn.addEventListener('click', () => {
        items.forEach((item) => {
            if (item.classList.contains('bought')) {
                item.remove();
            }
        })
    })
});



function getCookie(name) {
    return document.cookie
        .split('; ')
        .find(row => row.startsWith(name + '='))
        ?.split('=')[1];
}