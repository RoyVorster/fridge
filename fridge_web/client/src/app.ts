import './style.css';
import axios from 'axios';
import Chart from 'chart.js/auto';

const canvas = <HTMLCanvasElement> document.getElementById("chart");

// Init chart
let chart = new Chart(canvas, {
    type: 'line',
    data: {
        labels: [0],
        datasets: [{
            data: [0],
            label: "Fridge temperature",
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

function updateChart(response) {
    const { time, data }: { time: number[]; data: number[] } = response;

    chart.data.labels = time;
    chart.data.datasets[0].data = data;

    chart.update();
}

// Get data from rpi every second
setInterval(getData, 1000); getData();
function getData() {
    const body = {
        interval: '10 seconds',
        n_points: 500,
        sensor_id: 0,
    };
    const headers = { 'Content-Type': 'application/json' };

    axios.post('http://80.114.174.200:5001/data', body, { headers })
        .then(({ data }) => updateChart(data));
}

