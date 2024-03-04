document.addEventListener('DOMContentLoaded', () => {
    const navList = document.getElementById('navList');
    const content = document.getElementById('content');
    // Initialize the page with the 'upload' content
    loadContent('upload');

    const uploadButton = document.getElementById('uploadDataButton');

    uploadButton.addEventListener('click', function () {
        document.getElementById('uploadInput').click();
    });

    navList.addEventListener('click', (event) => {
        let target = event.target;
        if (target.tagName.toLowerCase() === 'li') {
            const targetId = target.getAttribute('data-target');
            setActiveTab(targetId);
            loadContent(targetId);
        }
    });

    document.querySelectorAll('#navList li').forEach(li => {
        li.addEventListener('mouseover', function () {
            this.classList.add('hover');
        });

        li.addEventListener('mouseout', function () {
            this.classList.remove('hover');
        });
    });

    function setActiveTab(targetId) {
        document.querySelectorAll('#navList li').forEach(li => {
            li.classList.remove('active');
        });
        document.querySelector(`#navList li[data-target="${targetId}"]`).classList.add('active');
    }
})