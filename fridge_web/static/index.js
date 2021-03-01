var socket = io();

const n = 10000;
const data = {
    type: 'line',
    labels: [...Array(n).keys()],
    datasets: [{
        label: 'Temperature data',
        data: [...Array(n).fill(0)],
        fill: false,
    }],
};

const options = {
    responsive: true,
    plugins: {
        zoom: {
            pan: {
                enabled: true,
            },
            zoom: {
                enabled: true,
            }
        }
    }
};

let ctx = document.getElementById('plot');
var temperaturePlot = new Chart(ctx, {
    type: 'line',
    data: data,
    options: options
});

function updatePlot(newDataPoint) {
    temperaturePlot.data.datasets[0].data.push(newDataPoint);
    temperaturePlot.data.datasets[0].data.shift();

    temperaturePlot.update();
};

socket.on('temperature', (data) => updatePlot(data.data));

