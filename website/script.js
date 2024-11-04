const svgIn = document.getElementById("svg-input");
const svgOut = document.getElementById("svg-output");
const svgContainer = document.getElementById("svg-container");

function handleIn(e) {
    const file = svgIn.files[0];

    file.text().then((s) => {
        svgContainer.insertAdjacentHTML("afterbegin", s);

        const buildings = document.getElementsByClassName("mapviz-building");
        for (const building of buildings) {
            building.style.fill = "#00ff00";
        }
    });
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

svgIn.addEventListener("change", handleIn);
svgOut.addEventListener("click", handleOut);
console.log("script finished")