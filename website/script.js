const uploadBtn = document.getElementById("svg-file");
// const colorPickers = document.getElementsByClassName("color-picker");
const preview = document.getElementById("img-box");
const downloadBtn = document.getElementById("download-btn");
const sideMenu = document.getElementById("side-menu");
const btnContainer = document.getElementById("btn-container");
//let url = undefined;

const generalHandler = (e) => {
    console.log(e);
    const color = e.target.value;
    const layerClass = e.target.getAttribute("data-class");

    console.log(layerClass);
    
    const objects = document.getElementsByClassName(layerClass);
    for (const object of objects) {
        object.style.fill = color;
    }
}

const createColorPicker = (colorPickerInfo) => {

    const input = document.createElement("input");
    input.setAttribute("data-class", colorPickerInfo.layerClass);
    input.classList.add("color-picker");
    input.setAttribute("type", "color");
    input.value = colorPickerInfo.color;
    input.addEventListener("change", generalHandler);
    input.id = colorPickerInfo.layerName;

    const label = document.createElement("label");
    label.innerText = colorPickerInfo.name;
    label.htmlFor = input.id;

    const div = document.createElement("div");
    div.classList.add("menu-layer");

    div.appendChild(label);
    div.appendChild(input);

    sideMenu.insertBefore(div, btnContainer);
};

function analyzeSVGEl(element) {

    const layerClass = element.classList[0];
    const color = element.getAttribute("fill");
    const layerName = layerClass.substring(7);
    const name = layerName.charAt(0).toUpperCase() + layerName.slice(1);

    return {
        "layerClass": layerClass,
        "layerName": layerName,
        "name": name,
        "color": color
    };
};

function analyzeSVG (svg) {
    //
    let svgInfo = {};
    
    for (const element of svg.children) {
        const elInfo = analyzeSVGEl(element);
        svgInfo[elInfo.layerClass] = elInfo;
    };

    return svgInfo;
};

const uploadBtnHandler = (e) => {
    // console.log(uploadBtn.files);
    //if (url) {URL.revokeObjectURL(url)};
    //url = URL.createObjectURL(uploadBtn.files[0]);
    //preview.innerHTML = uploadBtn.files[0];
    const file = uploadBtn.files[0];
    file.text().then((s) => {
        if (preview.children.length > 0) {
            preview.removeChild(preview.children[0]);
        }

        /* adrian: Here it is very important to make an array out of the HTMLCollection 
         * returned by getElementsByClassName because the HTMLCollection gets updated whenever
         * the DOM is changed. So when we delete an element in the for loop below, the 
         * oldColorPickers variable is updated and then the for loop gets completely confused 
         * and we end up skipping elements. I hate javascript so much. 
         * ref: https://developer.mozilla.org/en-US/docs/Web/API/HTMLCollection
         */
        const oldColorPickers = Array.from(document.getElementsByClassName("menu-layer"));
        console.log(oldColorPickers);
        for (const colorPicker of oldColorPickers) {
            colorPicker.remove();
        }

        preview.insertAdjacentHTML("afterbegin", s);
        const svgEl = document.getElementsByClassName("mapviz-map")[0];
        const svgInfo = analyzeSVG(svgEl);
        console.log(svgInfo);        

        for (const colorPickerInfo of Object.values(svgInfo)) {
            createColorPicker(colorPickerInfo);
        }

        //const building = document.getElementsByClassName("mapviz-building");
        //const initialColor = building[0].style.fill;
        downloadBtn.parentElement.classList.remove("hide");
    });
};

function download(filename, str) {
    const fileBlob = new Blob([str], { type: 'image/svg+xml' });
    const url = URL.createObjectURL(fileBlob);

    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', filename);
    link.click();

    URL.revokeObjectURL(url);
}

function downloadSVG(e) {
    const str = preview.innerHTML;
    download("map.svg", str);
}

//event listeners

uploadBtn.addEventListener("change", uploadBtnHandler);
downloadBtn.addEventListener("click", downloadSVG);