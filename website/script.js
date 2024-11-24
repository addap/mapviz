const uploadBtn = document.getElementById("svg-file");
// const colorPickers = document.getElementsByClassName("color-picker");
const preview = document.getElementById("img-box");
const downloadBtn = document.getElementById("download-btn");
const sideMenu = document.getElementById("side-menu");
const btnContainer = document.getElementById("btn-container");
//let url = undefined;
let svgInfo = undefined;

const redrawLayer = (layerClass) => {
    const objects = document.getElementsByClassName(layerClass);
    const colors = svgInfo[layerClass].colors;
    for (const object of objects) {
        let i = Math.floor(Math.random() * colors.length);
        object.style.fill = colors[i];
    }
};

const generalHandler = (e) => {
    console.log(e);
    const color = e.target.value;
    const layerClass = e.target.getAttribute("data-class");
    const index = e.target.getAttribute("data-index");
    svgInfo[layerClass].colors[index] = color;
    redrawLayer(layerClass);

    console.log(layerClass);
}

function addColorPicker(layerClass) {
    const elInfo = svgInfo[layerClass];
    elInfo.colors.push(elInfo.colors[elInfo.colors.length - 1]);
    svgInfo[layerClass] = elInfo;
}

const createColorPicker = (colorPickerInfo) => {
    
    const cpDiv = document.createElement("div");
    cpDiv.classList.add("cp-container");

    let i = 0;
    for (const color of colorPickerInfo.colors) {
        const input = document.createElement("input");
        input.setAttribute("data-class", colorPickerInfo.layerClass);
        input.setAttribute("data-index", i);
        i += 1;
        input.classList.add("color-picker");
        input.setAttribute("type", "color");
        input.value = color;
        input.addEventListener("change", generalHandler); 
        cpDiv.appendChild(input);
    };
    
    const plusBtn = document.createElement("button");
    plusBtn.value = "+";
    plusBtn.addEventListener("click", () => addColorPicker(colorPickerInfo.layerClass));

    
    const label = document.createElement("label");
    label.innerText = colorPickerInfo.name;
    //label.htmlFor = input.id;

    const div = document.createElement("div");
    div.classList.add("menu-layer");

    div.appendChild(label);
    div.appendChild(cpDiv);

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
        "colors": new Set([color])
    };
};

function analyzeSVG (svg) {
    //
    let svgInfo = {};
    
    for (const element of svg.children) {
        const elInfo = analyzeSVGEl(element);

        if (elInfo.layerClass in svgInfo) {
            svgInfo[elInfo.layerClass].colors = svgInfo[elInfo.layerClass].colors.union(elInfo.colors);
        } else {
            svgInfo[elInfo.layerClass] = elInfo;
        }
    };

    for (const key in svgInfo) {svgInfo[key].colors = Array.from(svgInfo[key].colors)};

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
        svgInfo = analyzeSVG(svgEl);
        console.log(svgInfo);  
        const elInfos = Object.values(svgInfo);
        elInfos.sort((i1, i2) => {
            if (i1.name < i2.name) { return -1; }
            else if (i1.name > i2.name) { return 1; }
            else { return 0; }
        });      


        for (const colorPickerInfo of elInfos) {
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