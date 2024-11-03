let ws = new WebSocket('ws://' + location.host + '/connect-websocket');
let maxLogNoRendered = 0;
window.onload = () => {
    const lastLogElement = document.querySelector("#lastLog");
    maxLogNoRendered = Number(lastLogElement.textContent) - 1;
}
ws.onopen = () => console.log('WebSocket connection opened');
ws.onclose = () => console.log('WebSocket connection closed');
ws.onmessage = event => {
    //console.log('Web socket data', event.data);
    const ulElement = document.querySelector("#logs");
    const dataAsObject = JSON.parse(event.data)
    Object.keys(dataAsObject.logs)
      .forEach(key => {
        const keyAsNum = Number(key)
        if (keyAsNum > maxLogNoRendered) {
            const li = document.createElement("li");
            li.appendChild(document.createTextNode(dataAsObject.logs[key]));
            ulElement.appendChild(li);
            maxLogNoRendered = keyAsNum;
        }
    });
    const lastLogElement = document.querySelector("#lastLog");
    lastLogElement.textContent = maxLogNoRendered;
}
ws.onerror = error => console.log('Web socket error', error);