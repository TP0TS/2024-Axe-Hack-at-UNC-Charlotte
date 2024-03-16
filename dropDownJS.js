let chapterDropdown = document.getElementById('chapterDropdown');
let dropdownLabel = document.getElementById('dropdownLabel');

// Add an event listener to the dropdown
chapterDropdown.addEventListener('click', function(event) {
    // Check if the clicked item is a chapter link
    if (event.target.tagName === 'A') {
        // Update the label text with the selected chapter
        dropdownLabel.textContent = event.target.textContent;
    }
});