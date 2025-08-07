const searchInput = document.getElementById('teacher-search');
const autocompleteList = document.getElementById('autocomplete-list');
const form = document.getElementById('teacher-form');
const teacherIdInput = document.getElementById('teacher-id');

let debounceTimeout;

searchInput.addEventListener('input', () => {
    const query = searchInput.value.trim();

    clearTimeout(debounceTimeout);
    debounceTimeout = setTimeout(() => {
        if (query.length < 2) {
            autocompleteList.innerHTML = '';
            return;
        }

        fetch(`/search_teachers?q=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(data => {
                autocompleteList.innerHTML = '';
                data.forEach(teacher => {
                    const li = document.createElement('li');
                    li.textContent = teacher.name;
                    li.dataset.id = teacher.id;
                    li.addEventListener('click', () => {
                        teacherIdInput.value = teacher.id;
                        form.submit();
                    });
                    autocompleteList.appendChild(li);
                });
            });
    }, 200); // Debounce to avoid spamming the server
});

// Hide suggestions when clicking outside
document.addEventListener('click', e => {
    if (!form.contains(e.target)) {
        autocompleteList.innerHTML = '';
    }
});