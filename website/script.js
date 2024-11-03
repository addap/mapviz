const svgIpt = document.getElementById("svg-input");
const svgContainer = document.getElementById("svg-container");

function handle(e) {
    const file = svgIpt.files[0];
    console.log(file);

    // if (svg) {
    //     svg.remove();
    //     svg = undefined;
    // }

    file.text().then((s) => {
        // svg = document.createElement("div");
        // svg.id = "svg-container-inner";
        // svgContainer.insertAdjacentElement("afterbegin", svg);
        svgContainer.insertAdjacentHTML("afterbegin", s);
        svgIpt.style.display = "none";
    });
}

svgIpt.addEventListener("change", handle);
console.log("script finished")