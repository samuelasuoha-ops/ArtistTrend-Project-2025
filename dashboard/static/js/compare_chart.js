document.addEventListener("DOMContentLoaded", function () {
    const labels = window.barLabels || [];
    const data1  = window.barData1 || [];
    const data2  = window.barData2 || [];
    const artist1Name = window.artist1Name || "Artist 1";
    const artist2Name = window.artist2Name || "Artist 2";

    console.log("Bar chart data:", { labels, data1, data2 });

    const canvas = document.getElementById("compareBarChart");
    if (!canvas) {
        console.log("No canvas with id 'compareBarChart' found.");
        return;
    }

    if (!labels.length || !data1.length || !data2.length) {
        console.log("Not enough data to draw bar chart.");
        return;
    }

    const ctx = canvas.getContext("2d");

    new Chart(ctx, {
        type: "bar",
        data: {
            labels: labels,  // ["Popularity", "Followers (M)"]
            datasets: [
                {
                    label: artist1Name,
                    data: data1,
                    borderWidth: 1
                },
                {
                    label: artist2Name,
                    data: data2,
                    borderWidth: 1
                }
            ]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true,
                    title: { display: true, text: "Value" }
                }
            }
        }
    });
});
