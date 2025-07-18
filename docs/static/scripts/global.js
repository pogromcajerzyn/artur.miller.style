function handleHover() {
    return new Promise(res=>{
    var clickSound = document.getElementById("hover")
    clickSound.volume = 0.15;
    clickSound.currentTime = 0;
    clickSound.play();
    clickSound.onended = res;
    })
}


function handleClick() {
    return new Promise(res=>{
    var clickSound = document.getElementById("click")
    clickSound.volume = 0.07;
    clickSound.currentTime = 0;
    clickSound.play();
    clickSound.onended = res;
    })
}

function clickWaitGo(event, address){

    handleClick();
    event.stopPropagation();
    const transition_el = document.querySelector('.transition');
    transition_el.classList.add('is-active');

    setTimeout(() => {
        window.open(address, "_self");
    }, 500);

}