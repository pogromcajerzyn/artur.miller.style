const postsPath = '/static/posts';

function updateFontSize() {
    const container = document.querySelector('#middle_column');
    const post_block = document.querySelector('.post_thumbnail');

    if (container) {
        const containerWidth = container.offsetWidth;
        const fontScaler = containerWidth * 0.004;
        document.documentElement.style.setProperty('--font-scaler', fontScaler);
    }

    if (post_block) {
        const postContainerWidth = post_block.offsetWidth;
        const postFontScaler = postContainerWidth * 0.004;
        document.documentElement.style.setProperty('--post-font-scaler', postFontScaler);
    }
}

function append_post(title1, title2, id, date, description){
    var article = document.createElement("article");
    article.classList.add("post_block");
    article.setAttribute("onmouseenter", "handleHover()");
    article.setAttribute("onmousedown", "handleClickBlog(this)");

    var contentWrapper = document.createElement("div");
    contentWrapper.classList.add("content_wrapper");

    var contentWrapperText = document.createElement("div");
    contentWrapperText.classList.add("content_wrapper_text");
    var paragraph = document.createElement("p");
    paragraph.style.textAlign = "left";
    paragraph.style.margin = "0";
    paragraph.innerHTML = id + " - " + title1 + " " + title2 + "<span style='float:right; margin: 0;'>"+date+"</span>";
    contentWrapperText.appendChild(paragraph);
    contentWrapperText.innerHTML += "<p style='max-height: calc(var(--thumbnail-height-now)/2); '>" + description +"</p>";

    contentWrapper.appendChild(contentWrapperText);

    var moreDiv = document.createElement("div");
    moreDiv.classList.add("more");
    moreDiv.setAttribute("onmouseenter", "handleHover()");
    moreDiv.setAttribute("onmousedown", "clickWaitGo(event, '/static/posts/" + id + "/post.html')");
    moreDiv.innerHTML = "MORE...";

    article.appendChild(contentWrapper);
    article.appendChild(moreDiv);

    var thumbnailWrapper = document.createElement("div");
    thumbnailWrapper.classList.add("thumbnail_wrapper");

    var postThumbnailBackground = document.createElement("img");
    postThumbnailBackground.classList.add("post_thumbnail_background");
    postThumbnailBackground.src = "/static/posts/" + id + "/thumbnail.jpg";

    var postThumbnail = document.createElement("img");
    postThumbnail.classList.add("post_thumbnail");
    postThumbnail.src = "/static/posts/" + id + "/thumbnail.jpg";

    var postThumbnailOverlay = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    postThumbnailOverlay.classList.add("post_thumbnail_overlay");

    var overlaySquare = document.createElementNS("http://www.w3.org/2000/svg", "rect");
    overlaySquare.classList.add("post_thumbnail_overlay_square");
    overlaySquare.setAttribute("height", "100%");
    overlaySquare.setAttribute("width", "100%");

    var overlayText1 = document.createElementNS("http://www.w3.org/2000/svg", "text");
    overlayText1.classList.add("post_thumbnail_overlay_text");
    overlayText1.setAttribute("x", "50%");
    overlayText1.setAttribute("y", "40%");

    overlayText1.innerHTML = title1;

    var overlayText2 = document.createElementNS("http://www.w3.org/2000/svg", "text");
    overlayText2.classList.add("post_thumbnail_overlay_text");
    overlayText2.setAttribute("x", "50%");
    overlayText2.setAttribute("y", "60%");

    overlayText2.innerHTML = title2;

    postThumbnailOverlay.appendChild(overlaySquare);
    postThumbnailOverlay.appendChild(overlayText1);
    postThumbnailOverlay.appendChild(overlayText2);

    thumbnailWrapper.appendChild(postThumbnailBackground);
    thumbnailWrapper.appendChild(postThumbnail);
    thumbnailWrapper.appendChild(postThumbnailOverlay);

    article.appendChild(thumbnailWrapper);

    document.getElementById("post_space").appendChild(article);
    }



async function fetchFolderList() {
    // // debug without flask
    // const response = await fetch(`http://localhost:63342/miller.style/miller/artur/static/posts/post_list.json`);
    // return await response.json();

    const response = await fetch(`${postsPath}/post_list.json`);
    return await response.json();
}

async function readJson(folder) {
    // // debug without flask
    // const response = await fetch(`http://localhost:63342/miller.style/miller/artur/static/posts/${folder}/short.json`);
    // return await response.json();

    const response = await fetch(`${postsPath}/${folder}/short.json`);
    return await response.json();
}


async function processFolders() {
  const folderList = await fetchFolderList();

  for (let i = folderList.length - 1; i >= 0; i--) {
    const folder = folderList[i];
    const json = await readJson(folder);

    append_post(
      json.title1,
      json.title2,
      json.id,
      json.date,
      json.description,
    );
    updateFontSize();
  }
}




document.addEventListener('DOMContentLoaded', updateFontSize);
window.addEventListener('resize', updateFontSize);

document.documentElement.style.setProperty('--max-width', "calc(" + document.getElementById('middle_column').offsetWidth + 'px - var(--main-borders))');
console.log(document.getElementById('middle_column').offsetWidth);

processFolders();
