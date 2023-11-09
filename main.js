const slider1 = document.getElementById("slider1");
const modSlider1 = document.getElementById("modSlider1");

let isDragging1 = false;
let isModDragging1 = false;
let power = 0;
let currentBrightness = 0;
let currentWarmth = 0;

slider1.addEventListener("touchstart", startDragging);
modSlider1.addEventListener("touchstart", startModDragging);
document.addEventListener("touchmove", handleDrag);

var clickTimer = null;

function sliderTapHandler() {// source: https://stackoverflow.com/a/26809354
    if (clickTimer == null) {
        clickTimer = setTimeout(function () {
            clickTimer = null;
        }, 500)
    } else {
        clearTimeout(clickTimer);
        clickTimer = null;
        if(power){
            powerOff()
        } else{
            powerOn()
        }
    }
}

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
    sliderTapHandler();
    if (e.type === "touchstart") {
        isDragging1 = e.target === slider1 || slider1.contains(e.target);
    }
}

function startModDragging(e) {
    e.preventDefault();
    if (e.type === "touchstart") {
        isModDragging1 = e.target === modSlider1 || modSlider1.contains(e.target);
    }
}

function powerOn(){
    power=1
    document.body.classList.remove('_power_off');
    updateSliders(currentBrightness,currentWarmth)
    sendData('pwrOn');
}
function powerOff(){
    power=0
    document.body.classList.add('_power_off');
    sendData('pwrOff');
    updateSliders(0,50);
}


function handleDrag(e) {
    console.log(power)
    if ((isDragging1 || isModDragging1 )&& power===1) {
        const mouseY = e.clientY || e.touches[0].clientY;
        const slider1Rect = slider1.getBoundingClientRect();
        const modSlider1Rect = modSlider1.getBoundingClientRect();
        if(document.getElementById('slider1').style.transition == 'all 0.5s ease'){ //remove transitions to directly move to cursor
            document.getElementById('slider1').style.transition = 'none';
            for (const i of document.getElementsByClassName('handle')){
                i.style.transition = 'none';
            }
        }
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
            if(newPosition===0){ //if the slider is brought to 0%, turn off
                power=0;
            }
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

        const valslider1 = getComputedStyle(document.documentElement).getPropertyValue('--slider1').trim().replace('%','');
        const valModSlider1 = getComputedStyle(document.documentElement).getPropertyValue('--modSlider1').trim().replace('%','');
        const percentageArray = `[${Math.ceil(valslider1* 100) / 100},${Math.ceil(valModSlider1* 100) / 100},${power}]`;
         
        if(power){
            sendDataThrottled('Set' + percentageArray)
        }else{
            powerOff()
        }
    }
}

document.addEventListener("touchend", stopDragging);

function stopDragging() {
    isDragging1 = false;
    isModDragging1 = false;
}

var teleporturl = ""
if(window.location.href.includes(":5500")){
  teleporturl = window.location.href.split(":5500")[0] + ":8080/teleport"; //automatically reconstructs the server URL if the admin url is through a Five Server environment
} else{
  teleporturl = window.location.href + "/teleport";
}

setInterval(function() {
    const currentTime = Date.now();
    if(currentTime - lastSendTime >= 1000){
        sendData("Ping");
    }
}, 500);

function updateSliders(val1, val2){
    document.getElementById('slider1').style.transition = 'all 0.5s ease'//apply transition temporarily
    for (const i of document.getElementsByClassName('handle')){
        i.style.transition = 'all 0.5s ease';
    }
    document.documentElement.style.setProperty("--slider1", val1 + "%");
    document.documentElement.style.setProperty("--modSlider1", val2 + "%");
    setTimeout(function() {
        document.getElementById('slider1').style.transition = 'none';
        for (const i of document.getElementsByClassName('handle')){
            i.style.transition = 'none';
        }
    }, 500);
}

function sendData(data) {
    var xhr = new XMLHttpRequest();
    xhr.open('POST', teleporturl, true); // Modify the URL as per your server configuration

    xhr.onreadystatechange = function () {
        if (xhr.readyState === XMLHttpRequest.DONE) {
            if (xhr.status === 200) {
                resp = String(xhr.responseText.trim()) //removes the request header.
                console.log('Received POST data: ' + resp); //process received responses here
                if (resp.includes("Cur[")) {
                    current = JSON.parse(resp.replace('Cur',''));
                    currentBrightness = current[0]
                    currentWarmth = current[1]
                    power=current[2]

                    if(power===1){
                        document.body.classList.remove('_power_off');
                        
                        if ((current[0] !== parseFloat(getComputedStyle(document.documentElement).getPropertyValue("--slider1")) || current[1] !== parseFloat(getComputedStyle(document.documentElement).getPropertyValue("--modSlider1")))) {
                            updateSliders(current[0],current[1]);
                        }
                    }
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
function sendDataThrottled(data) { //rate limit to avoid flooding server
    const currentTime = Date.now();
    if (currentTime - lastSendTime >= sendInterval) {
        lastSendTime = currentTime;
        sendData(data);
    }
}