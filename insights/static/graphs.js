// Were we put graphs code.
document.addEventListener("DOMContentLoaded", function(){
    findGraphs();
})

function findGraphs() {
    let canvas = document.getElementById('runs-doughnut');
    if (canvas) {
        new Chart(canvas, {
            type: 'doughnut',
            data: JSON.parse(canvas.dataset.data)
        });
    }

    const timeFormat = 'YYYY-MM-DD';

    canvas = document.getElementById('daily-run-count');
    if (canvas) {
        console.log(JSON.parse(canvas.dataset.data))

        new Chart(canvas, {
            type: 'line',
            data: JSON.parse(canvas.dataset.data),
            options: {
                xAxes: [{
                    type: 'time',
                    time: {
                        parser: timeFormat,
                        // round: 'day'
                        tooltipFormat: 'll HH:mm'
                    },
                    scaleLabel: {
                        display: true,
                        labelString: 'Date'
                    }
                }]
            }
        });
    }
}