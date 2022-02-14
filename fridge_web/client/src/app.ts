import './style.scss';
import axios from 'axios';
import Chart from 'chart.js/auto';

const ip = 'http://192.168.0.180:5001'; // Local IP, use wireguard VPN
const headers = { 'Content-Type': 'application/json' };

// Quick and dirty settings
const intervalIn = <HTMLInputElement> document.getElementById("interval-in");
const npointsIn = <HTMLInputElement> document.getElementById("npoints-in");

let interval: string = '2 minutes'; let n_points: number = 1000;
intervalIn.value = interval; npointsIn.value = n_points.toString();

intervalIn.addEventListener('input', () => {
    interval = intervalIn.value; update();
});

npointsIn.addEventListener('input', () => {
    const parsed: number = parseInt(npointsIn.value);
    if (!isNaN(parsed)) {
        n_points = parsed; update();
    }
});

// Turn on/off command
const tsleepIn = <HTMLInputElement> document.getElementById("tsleep-in");
const commandOut = <HTMLSpanElement> document.getElementById("command");

tsleepIn.value = '23:59';
tsleepIn.addEventListener('input', () => get_command());

// Init chart
const canvas = <HTMLCanvasElement> document.getElementById("chart");
let chart = new Chart(canvas, {
    type: 'line',
    data: {
        labels: [0],
        datasets: [{
            data: [0],
            label: "Temperature",
            borderColor: 'rgb(3, 98, 252)',
        }],
    },
    options: {
        plugins: {
            title: {
                display: true,
                text: "Amazing right",
            },
        }
    },
});

// Get data from RPI every five seconds
setInterval(update, 5000); update();
function update() {
    const body = {
        interval,
        n_points,
        sensor_id: 0,
    };

    axios.post(`${ip}/data`, body, { headers })
        .then(({ data: response }) => {
            const { time, data }: { time: number[]; data: number[] } = response;

            chart.data.labels = time;
            chart.data.datasets[0].data = data;

            chart.update();
        });
}

setInterval(get_command, 60000); get_command();
function get_command() {
    const body = { t_sleep: tsleepIn.value };

    axios.post(`${ip}/command`, body, { headers })
        .then(({ data: response }) => {
            const { command }: { command: string } = response;

            commandOut.textContent = command;
        });
}
