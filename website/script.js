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
    const layer = e.target.id;
    const cls = `mapviz-${layer}`;

    console.log(cls);
    
    const objects = document.getElementsByClassName(cls);
    for (const object of objects) {
        object.style.fill = color;
    }

    console.log(objects);
}

const createColorPicker = (colorPickerInfo) => {
    const label = document.createElement("label");
    label.setAttribute("for", colorPickerInfo.layer);
    label.innerText = colorPickerInfo.name;

    const input = document.createElement("input");
    input.setAttribute("id", colorPickerInfo.layer);
    input.classList.add("color-picker");
    input.setAttribute("type", "color");
    input.value = colorPickerInfo.color;
    input.addEventListener("change", generalHandler);

    const div = document.createElement("div");
    div.classList.add("menu-layer");
    div.appendChild(label);
    div.appendChild(input);

    sideMenu.insertBefore(div, btnContainer);
};

function analyzeSVGEl(element) {

    const cls = element.classList[0];
    const color = element.getAttribute("fill");
    const layer = cls.substring(7);
    const name = layer.charAt(0).toUpperCase() + layer.slice(1);

    return {
        "layer": layer,
        "name": name,
        "color": color
    };
};

function analyzeSVG (svg) {
    //
    let svgInfo = {};
    
    for (const element of svg.children) {
        const elInfo = analyzeSVGEl(element);
        svgInfo[elInfo.layer] = elInfo;
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

        const oldColorPickers = document.getElementsByClassName("menu-layer");
        console.log(oldColorPickers);
        for (const colorPicker of oldColorPickers) {
            console.log("deleting " + colorPicker.id)
            sideMenu.removeChild(colorPicker);
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