document.addEventListener('DOMContentLoaded', () => {
    const transition_el = document.querySelector('.transition');

    const removeIsActiveClass = () => {
        transition_el.classList.remove('is-active');
    };

    setTimeout(removeIsActiveClass, 500);

    window.addEventListener('pageshow', (event) => {
        if (event.persisted) {
            setTimeout(removeIsActiveClass, 500);
        }
    });
});