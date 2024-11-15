const sendMotorInit = (motorIndex) => { 
    fetch(`/api/motor/${motorIndex}/init`, {method: 'POST'})
    .then(res => {
        const feedbackElement = document.querySelector("#data");
        if (res.ok) {
            res.text().then(t => feedbackElement.textContent = t);
        } else {
            console.console.error(res);
            feedbackElement.textContent = "API error, see console";
        }
    }); 
};

const getMotorData = (motorIndex) => { 
    fetch(`/api/motor/${motorIndex}/data`, {method: 'GET'})
    .then(res => {
        const feedbackElement = document.querySelector("#data");
        if (res.ok) {
            res.text().then(t => feedbackElement.textContent = t);
        } else {
            console.console.error(res);
            feedbackElement.textContent = "API error, see console";
        }
    }); 
};

const sendMotorConfig = (motorIndex, steps, current) => { 
    console.log(`Sending config for motor ${motorIndex}: steps ${steps}, current ${current}`)
    fetch(`/api/motor/${motorIndex}/config/?steps=${steps}&current=${current}`, {method: 'POST'})
    .then(res => {
        const feedbackElement = document.querySelector("#data");
        if (res.ok) {
            res.text().then(t => feedbackElement.textContent = t);
        } else {
            console.console.error(res);
            feedbackElement.textContent = "API error, see console";
        }
    }); 
};

const moveMotor = (motorIndex, steps, direction, rpm) => { 
    console.log(`Sending config for move ${motorIndex}: steps ${steps}, direction ${direction}, speed ${rpm}`);
    apiSteps = (direction == "1") ? steps : -steps;
    fetch(`/api/motor/${motorIndex}/move/${apiSteps}/${rpm}`, {method: 'POST'})
    .then(res => {
        const feedbackElement = document.querySelector("#data");
        if (res.ok) {
            res.text().then(t => feedbackElement.textContent = t);
        } else {
            console.console.error(res);
            feedbackElement.textContent = "API error, see console";
        }
    }); 
};

const runMotor = (motorIndex, speed) => { 
    console.log(`Sending config for run ${motorIndex}: speed ${speed}`);
    fetch(`/api/motor/${motorIndex}/run/${speed}`, {method: 'POST'})
    .then(res => {
        const feedbackElement = document.querySelector("#data");
        if (res.ok) {
            res.text().then(t => feedbackElement.textContent = t);
        } else {
            console.console.error(res);
            feedbackElement.textContent = "API error, see console";
        }
    }); 
};

const sendMotorHold = (motorIndex, val) => { 
    console.log(`Sending motor ${(val) ? 'hold' : 'release'}`)
    fetch(`/api/motor/${motorIndex}/hold/${val}`, {method: 'POST'})
    .then(res => {
        const feedbackElement = document.querySelector("#data");
        if (res.ok) {
            res.text().then(t => feedbackElement.textContent = t);
        } else {
            console.console.error(res);
            feedbackElement.textContent = "API error, see console";
        }
    }); 
};