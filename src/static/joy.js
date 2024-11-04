const sendJoyCommand = (command) => { 
    fetch('/api/joy/'+command, {method: 'POST'})
    .then(res => {
        const feedbackElement = document.querySelector("#feedback");
        if (res.ok) {
            res.text().then(t => feedbackElement.textContent = t);
        } else {
            console.console.error(res);
            feedbackElement.textContent = "API error, see console";
        }
    }); 
};

const getJoyData = () => { 
    const buttonConvert = val => (val >>> 0).toString(2).split('').join(' ');
    fetch('/api/joy', {method: 'GET'})
    .then(res => {
        const posElement = document.querySelector("#positions");
        posElement.innerHTML = '';
        if (res.ok) {
            res.json().then(data => {
                ['x', 'y', 'z', 'rx', 'ry', 'rz', 'buttons'].forEach(k => {
                    const parent = document.createElement("div");
                    const val = (k == 'buttons') ? buttonConvert(data[k]) : data[k];
                    parent.appendChild(document.createTextNode(`${k}: ${val}`));
                    posElement.appendChild(parent);
                })
            });
        } else {
            console.console.error(res);
            posElement.textContent = "API error, see console";
        }
    }); 
};