const ctx = document.getElementById("tenantStatusChart").getContext("2d");
const tenantStatusChart = new Chart(ctx, {
    type: "doughnut",
    data: {
        labels: ["Aktif", "Tidak Aktif"],
        datasets: [
            {
                data: [87, 13],
                backgroundColor: ["#0d6efd", "#e9ecef"],
                borderWidth: 0,
                cutout: "70%",
            },
        ],
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: { display: false },
            tooltip: { enabled: true },
        },
    },
});