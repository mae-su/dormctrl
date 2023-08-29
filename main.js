const slider1 = document.getElementById("slider1");
const slider2 = document.getElementById("slider2");
const modSlider1 = document.getElementById("modSlider1");
const modSlider2 = document.getElementById("modSlider2");

let isDragging1 = false;
let isDragging2 = false;
let isModDragging1 = false;
let isModDragging2 = false;

slider1.addEventListener("mousedown", startDragging);
slider2.addEventListener("mousedown", startDragging);
modSlider1.addEventListener("mousedown", startModDragging);
modSlider2.addEventListener("mousedown", startModDragging);

slider1.addEventListener("touchstart", startDragging);
slider2.addEventListener("touchstart", startDragging);
modSlider1.addEventListener("touchstart", startModDragging);
modSlider2.addEventListener("touchstart", startModDragging);

function getElement(s) {
    return document.getElementById(s)
}
function setDocProperty(p, v) {
    document.documentElement.style.setProperty(p, v)
}
function rmBodyClass(c) {
    if (typeof c === 'string' || c instanceof String) {
        document.body.classList.remove(c)
    }
    else {
        for (const i in c) {
            document.body.classList.remove(c[i])
        }
    }
}

function addBodyClass(c) {
    if (typeof c === 'string' || c instanceof String) {
        document.body.classList.add(c)
    }
    else {
        for (const i in c) {
            document.body.classList.add(c[i])
        }
    }
}

function startDragging(e) {
    e.preventDefault();
    if (e.type === "mousedown") {
        isDragging1 = e.target === slider1;
        isDragging2 = e.target === slider2;
    } else if (e.type === "touchstart") {
        isDragging1 = e.target === slider1 || slider1.contains(e.target);
        isDragging2 = e.target === slider2 || slider2.contains(e.target);
    }
}

function startModDragging(e) {
    e.preventDefault();
    if (e.type === "mousedown") {
        isModDragging1 = e.target === modSlider1;
        isModDragging2 = e.target === modSlider2;
    } else if (e.type === "touchstart") {
        isModDragging1 = e.target === modSlider1 || modSlider1.contains(e.target);
        isModDragging2 = e.target === modSlider2 || modSlider2.contains(e.target);
    }
}

document.addEventListener("touchmove", handleDrag);

function handleDrag(e) {
    if (isDragging1 || isDragging2 || isModDragging1 || isModDragging2) {
        e.preventDefault();
        const mouseY = e.clientY || e.touches[0].clientY;
        const slider1Rect = slider1.getBoundingClientRect();
        const slider2Rect = slider2.getBoundingClientRect();
        const modSlider1Rect = modSlider1.getBoundingClientRect();
        const modSlider2Rect = modSlider2.getBoundingClientRect();

        if (isDragging1) {
            const newPosition = Math.min(
                100,
                Math.max(0, ((slider1Rect.bottom - mouseY) / slider1Rect.height) * 100)
            );
            document.documentElement.style.setProperty(
                "--slider1",
                newPosition + "%"
            );
            slider1.querySelector(
                ".handle"
            ).style.top = `calc(95% - calc(var(--slider1)* .9))`;
        }

        if (isDragging2) {
            const newPosition = Math.min(
                100,
                Math.max(0, ((slider2Rect.bottom - mouseY) / slider2Rect.height) * 100)
            );
            document.documentElement.style.setProperty(
                "--slider2",
                newPosition + "%"
            );
            slider2.querySelector(
                ".handle"
            ).style.top = `calc(95% - calc(var(--slider2)* .9))`;
        }

        if (isModDragging1) {
            const newPosition = Math.min(
                100,
                Math.max(
                    0,
                    ((modSlider1Rect.bottom - mouseY) / modSlider1Rect.height) * 100
                )
            );
            document.documentElement.style.setProperty(
                "--modSlider1",
                newPosition + "%"
            );
            modSlider1.querySelector(
                ".handle"
            ).style.top = `calc(95% - calc(var(--modSlider1)* .9))`;
        }

        if (isModDragging2) {
            const newPosition = Math.min(
                100,
                Math.max(
                    0,
                    ((modSlider2Rect.bottom - mouseY) / modSlider2Rect.height) * 100
                )
            );
            document.documentElement.style.setProperty(
                "--modSlider2",
                newPosition + "%"
            );
            modSlider2.querySelector(
                ".handle"
            ).style.top = `calc(95% - calc(var(--modSlider2)* .9))`;
        }
        const valslider1 = getComputedStyle(document.documentElement).getPropertyValue('--slider1').trim().replace('%','');
        const valModSlider1 = getComputedStyle(document.documentElement).getPropertyValue('--modSlider1').trim().replace('%','');
        const valSlider2 = getComputedStyle(document.documentElement).getPropertyValue('--slider2').trim().replace('%','');
        const valModSlider2 = getComputedStyle(document.documentElement).getPropertyValue('--modSlider2').trim().replace('%','');
        const percentageArray = `[${Math.round(valslider1)},${Math.round(valModSlider1)},${Math.round(valSlider2)},${Math.round(valModSlider2)}]`;
        sendDataThrottled('Set' + percentageArray)

    }
}

document.addEventListener("mouseup", stopDragging);
document.addEventListener("touchend", stopDragging);

function stopDragging() {
    isDragging1 = false;
    isDragging2 = false;
    isModDragging1 = false;
    isModDragging2 = false;
}

var teleporturl = ""
if(window.location.href.includes(":5500")){
  teleporturl = window.location.href.split(":5500")[0] + ":8080/teleport"; //automatically reconstructs the server URL if the admin url is through a Five Server environment
} else{
  teleporturl = window.location.href + "/teleport";
}

setInterval(function() {
    sendData("Ping");
}, 500);

function sendData(data) {
    var xhr = new XMLHttpRequest();
    xhr.open('POST', teleporturl, true); // Modify the URL as per your server configuration

    // Set the appropriate headers if you need to send data other than plain text
    // xhr.setRequestHeader('Content-Type', 'application/json');
    // xhr.setRequestHeader('Authorization', 'Bearer myToken');

    xhr.onreadystatechange = function () {
        if (xhr.readyState === XMLHttpRequest.DONE) {
            if (xhr.status === 200) {
                resp = String(xhr.responseText.trim()) //removes the request header.
                console.log('Received POST data: ' + resp); //process received responses here

                if (resp.includes("Cur[")) {
                    current = JSON.parse(resp.replace('Cur',''));
                    document.documentElement.style.setProperty("--slider1", current[0] + "%");
                    document.documentElement.style.setProperty("--modSlider1", current[1] + "%");
                    document.documentElement.style.setProperty("--slider2", current[2] + "%");
                    document.documentElement.style.setProperty("--modSlider2", current[3] + "%");
                }
            }
            else {
                console.error('Error:', xhr.status);
            }
        }
    };
    xhr.send(data);
    console.log("Sent " + String(data))
}

let lastSendTime = 0;
const sendInterval = 10;

function sendDataThrottled(data) { //rate limit
    const currentTime = Date.now();
    if (currentTime - lastSendTime >= sendInterval) {
        lastSendTime = currentTime;
        sendData(data);
    } else {
        console.log('sendData throttled - too soon');
    }
}