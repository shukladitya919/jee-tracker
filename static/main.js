document.addEventListener('DOMContentLoaded', function() {
    initializeChapterCheckboxes();
    initializeRevisionButtons();
    initializeBookCheckboxes();
});

function initializeChapterCheckboxes() {
    const checkboxes = document.querySelectorAll('.chapter-checkbox');
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const id = this.getAttribute('data-id');
            const field = this.getAttribute('data-field');
            toggleChapter(id, field);
        });
    });
}

function initializeRevisionButtons() {
    const buttons = document.querySelectorAll('.revision-btn');
    buttons.forEach(button => {
        button.addEventListener('click', function() {
            const id = this.getAttribute('data-id');
            const action = this.getAttribute('data-action');
            toggleRevision(id, action);
        });
    });
}

function initializeBookCheckboxes() {
    const bookCheckboxes = document.querySelectorAll('input[data-subject]');
    bookCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const subject = this.getAttribute('data-subject');
            const field = this.getAttribute('data-field');
            toggleBook(subject, field);
        });
    });
}

function toggleChapter(id, field) {
    toggleRequest(id, field, 'toggle');
}

function toggleRevision(id, action) {
    toggleRequest(id, 'revision_count', action);
}

function toggleBook(subject, field) {
    fetch('/toggle', {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify({subject: subject, field: field})
    })
    .then(res => res.json())
    .then(data => {
        if (!data.ok) {
            console.error('Book toggle failed', data);
            alert('Error updating book status');
        }
    })
    .catch(e => {
        console.error('Error toggling book:', e);
        alert('Error updating book status');
    });
}

async function toggleRequest(id, field, action) {
    try {
        const res = await fetch('/toggle', {
            method: 'POST',
            headers: {'Content-Type':'application/json'},
            body: JSON.stringify({id: id, field: field, action: action})
        });
        const data = await res.json();
        if (!data.ok) {
            console.error('Toggle failed', data);
            alert('Error updating progress');
            return;
        }
        
        const subjBar = document.getElementById('subject-progress');
        if (subjBar && data.subject_percent !== undefined) {
            subjBar.style.width = data.subject_percent + '%';
            subjBar.textContent = data.subject_percent + '%';
        }
        
        const chapProg = document.getElementById('chapprog-' + id);
        const chapBar = document.getElementById('chapbar-' + id);
        if (chapProg && chapBar) {
            chapProg.textContent = data.chapter_progress + '/' + data.chapter_max;
            chapBar.style.width = (data.chapter_progress/data.chapter_max*100) + '%';
        }
        
        if (field === 'revision_count') {
            const revisionElement = document.getElementById('revision_' + id);
            if (revisionElement) {
                revisionElement.textContent = data.revision_count;
                const container = revisionElement.closest('.d-flex');
                if (container) {
                    const decrementBtn = container.querySelector('.btn-outline-danger');
                    if (decrementBtn) {
                        decrementBtn.disabled = data.revision_count === 0;
                    }
                }
            }
        }
        
        const chapterElement = document.querySelector(`input[data-id="${id}"]`);
        if (chapterElement) {
            const card = chapterElement.closest('.card');
            if (card) {
                const catProgressBar = card.querySelector('.cat-progress');
                if (catProgressBar && data.category_percent !== undefined) {
                    catProgressBar.style.width = data.category_percent + '%';
                    catProgressBar.textContent = data.category_percent + '%';
                }
            }
        }
        
    } catch (e) {
        console.error('Error toggling:', e);
        alert('Error updating progress. Please try again.');
    }
}
