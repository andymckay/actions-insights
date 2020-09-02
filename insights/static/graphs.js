// Were we put graphs code.
document.addEventListener("DOMContentLoaded", function(){
    findGraphs();
})

function findGraphs() {
    let ctx = document.getElementById('runs-doughnut');
    if (ctx) {
        new Chart(ctx, {
            type: 'doughnut',
            data: JSON.parse(ctx.dataset.data)
        });
    }
}