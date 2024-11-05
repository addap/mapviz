const uploadBtn = document.getElementById("svg-file");
const colorPickers = document.getElementsByClassName("color-picker");
const preview = document.getElementById("img-box");
//let url = undefined;

const uploadBtnHandler = (e) => {
    console.log(uploadBtn.files);
    //if (url) {URL.revokeObjectURL(url)};
    //url = URL.createObjectURL(uploadBtn.files[0]);
    //preview.innerHTML = uploadBtn.files[0];
    const file = uploadBtn.files[0];
    file.text().then((s) => {
        preview.insertAdjacentHTML("afterbegin", s);
        const building = document.getElementsByClassName("mapviz-building");
        const initialColor = building[0].style.fill;

    });
};

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

uploadBtn.addEventListener("change", uploadBtnHandler);
for (const colorPicker of colorPickers) {
    colorPicker.addEventListener("change", generalHandler);
    colorPicker.value = "black";
}

function download(filename, str) {
    const fileBlob = new Blob([str], { type: 'image/svg+xml' });
    const url = URL.createObjectURL(fileBlob);

    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', filename);
    link.click()

    URL.revokeObjectURL(url)
}

function handleOut(e) {
    const str = svgContainer.innerHTML;
    download("map.svg", str);
}
