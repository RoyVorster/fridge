import './style.scss';
import axios from 'axios';
import Chart from 'chart.js/auto';

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
    const headers = { 'Content-Type': 'application/json' };

    // Access via wireguard VPN
    axios.post('http://192.168.0.180:5001/data', body, { headers })
        .then(({ data: response }) => {
            const { time, data }: { time: number[]; data: number[] } = response;

            chart.data.labels = time;
            chart.data.datasets[0].data = data;

            chart.update();
        });
}

