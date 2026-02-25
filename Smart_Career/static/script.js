
document.addEventListener('DOMContentLoaded', function() {
    const select = document.getElementById('vacancy-select');
    const modal = document.getElementById('vacancyModal');
    const modalTitle = document.getElementById('modalTitle');
    const modalDesc = document.getElementById('modalDesc');
    const closeBtn = document.getElementById('closeModal');
    const btnSecondary = document.getElementById('btnSecondaryClose');

    select.addEventListener('change', function() {
        const selectedOption = this.options[this.selectedIndex];
        

        if (this.value !== "") {
            modalTitle.innerText = selectedOption.getAttribute('data-title');
            modalDesc.innerText = selectedOption.getAttribute('data-desc');
            

            modal.style.display = "block";
        }
    });

    function closeModal() {
        modal.style.display = "none";
        select.value = ""; 
    }

    closeBtn.onclick = closeModal;
    btnSecondary.onclick = closeModal;

    window.onclick = function(event) {
        if (event.target == modal) {
            closeModal();
        }
    };

    window.onload = function() {
    const select = document.getElementById('vacancy-select');
    if (select) {
        select.value = "";
    }
    };
});