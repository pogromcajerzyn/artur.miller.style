
// function about_toggle() {
//
//     const textToType = `Welcome to my creative hub!
//
//     From a young age, my aspiration has consistently revolved around the pursuit of becoming a deviser. Despite evolving interests in collateral fields over the years, the core motivation has always remained constant: the innate desire to create.
//
//     I'm passionate about sailing, engaging in DIY projects (in physics, electronics, and mechanics), exploring the art of cooking, practicing photography, teaming up with friends in video games like Destiny 2 and CS: GO, and weightlifting.
//
//     Driven by curiosity, my background in physics and mechatronics is consistently guided by a dedicated commitment to the art of creation.`;
//
//     handleClick();
//     var para = document.getElementById("about_me");
//     var myTextSpan = document.getElementById("my_text");
//
//     if (!para.classList.contains("expanded_about_me")) {
//         myTextSpan.textContent = "";
//         var index = 0;
//
//         typeSound = document.getElementById("key")
//         typeSound.volume = 0.07;
//         typeSound.currentTime = 0;
//
//         function type() {
//             typeSound.play();
//             const currentText = textToType.slice(0, index + 1);
//             myTextSpan.textContent = currentText;
//             index++;
//
//             if (index < textToType.length) {
//                 setTimeout(type, 5);
//             }
//         }
//         type();
//     }
//     para.classList.toggle("expanded_about_me");
// }
//
//
// function more_toggle() {
//     handleClick();
//     var para = document.getElementById("more");
//     para.classList.toggle("expanded_more");
// }

function handleClickBlog(clickedElement) {
    handleClick();

    var doc = document.documentElement.style

    var borders = 2* parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--small-edges'));
    var thumbnailWidth = clickedElement.clientWidth;

    doc.setProperty('--thumbnail-width-now', thumbnailWidth+borders+'px');
    doc.setProperty('--thumbnail-height-now', (thumbnailWidth/4)*3+borders+'px');

    var postSpaceWidth = document.getElementById('post_space').clientWidth;
    doc.setProperty('--post_space_width_now', postSpaceWidth + 'px');

    if (postSpaceWidth > thumbnailWidth + borders){

        doc.setProperty('--post-preview-predicted-height', (thumbnailWidth/4)*3+borders+'px');
        doc.setProperty('--content-offset-left', thumbnailWidth+'px');
        doc.setProperty('--content-offset-top', 0 + 'px');

    } else{
        doc.setProperty('--post-preview-predicted-height', (thumbnailWidth/2)*3+borders+'px');
        doc.setProperty('--content-offset-left', 0+'px');
        doc.setProperty('--content-offset-top', (thumbnailWidth/4)*3+'px');
    }

    clickedElement.classList.toggle('expanded_post_block');

    var childContainers = clickedElement.querySelectorAll('.thumbnail_wrapper');
    childContainers.forEach(function(childContainer) {
        childContainer.classList.toggle('expended_thumbnail_wrapper');
    });



    var containers = document.querySelectorAll('.post_block');
    containers.forEach(function(container) {
        if (container !== clickedElement) {
            container.classList.remove('expanded_post_block');

            var otherChildContainers = container.querySelectorAll('.thumbnail_wrapper');
            otherChildContainers.forEach(function(otherChildContainer) {
                otherChildContainer.classList.remove('expended_thumbnail_wrapper');
            });
        }
    });
}
