const API_URL = "http://127.0.0.1:8000";


// ======================================================
// DOM ELEMENTS
// ======================================================

const totalStudentsEl =
    document.getElementById("totalStudents");

const presentTodayEl =
    document.getElementById("presentToday");

const absentTodayEl =
    document.getElementById("absentToday");

const attendanceRateEl =
    document.getElementById("attendanceRate");

const summaryPresentEl =
    document.getElementById("summaryPresent");

const summaryAbsentEl =
    document.getElementById("summaryAbsent");

const presentPercentageEl =
    document.getElementById("presentPercentage");

const absentPercentageEl =
    document.getElementById("absentPercentage");

const progressPercentageEl =
    document.getElementById("progressPercentage");

const progressPresentEl =
    document.getElementById("progressPresent");

const recentAttendanceTable =
    document.getElementById("recentAttendanceTable");

const chartPeriodSelect =
    document.getElementById("chartPeriod");


// ======================================================
// CHART VARIABLE
// ======================================================

let attendanceOverviewChart = null;


// ======================================================
// INDIA DATE
// ======================================================

function getIndiaDate() {

    return new Intl.DateTimeFormat(
        "en-CA",
        {
            timeZone: "Asia/Kolkata",
            year: "numeric",
            month: "2-digit",
            day: "2-digit"
        }
    ).format(new Date());

}


// ======================================================
// NORMALIZE DATE
// ======================================================

function normalizeDate(date) {

    if (!date) {
        return "";
    }

    return String(date).split("T")[0];

}


// ======================================================
// CREATE YYYY-MM-DD
// ======================================================

function makeISODate(date) {

    const year =
        date.getFullYear();

    const month =
        String(date.getMonth() + 1)
            .padStart(2, "0");

    const day =
        String(date.getDate())
            .padStart(2, "0");

    return `${year}-${month}-${day}`;

}


// ======================================================
// CHART DATE RANGE
// ======================================================

function getChartDateRange(period) {

    const today = new Date();

    today.setHours(
        0,
        0,
        0,
        0
    );

    let startDate;
    let endDate;


    // --------------------------------------------------
    // THIS WEEK
    // Monday → Today
    // --------------------------------------------------

    if (period === "This Week") {

        const day =
            today.getDay();

        const mondayOffset =
            day === 0
                ? 6
                : day - 1;

        startDate =
            new Date(today);

        startDate.setDate(
            today.getDate() -
            mondayOffset
        );

        endDate =
            new Date(today);

    }


    // --------------------------------------------------
    // LAST WEEK
    // Previous 7 days
    // --------------------------------------------------

    else if (period === "Last Week") {

        endDate =
            new Date(today);

        endDate.setDate(
            today.getDate() - 1
        );

        startDate =
            new Date(today);

        startDate.setDate(
            today.getDate() - 7
        );

    }


    // --------------------------------------------------
    // THIS MONTH
    // --------------------------------------------------

    else {

        startDate =
            new Date(
                today.getFullYear(),
                today.getMonth(),
                1
            );

        endDate =
            new Date(today);

    }


    return {
        startDate,
        endDate
    };

}


// ======================================================
// RENDER ATTENDANCE GRAPH
// ======================================================

function renderAttendanceChart(
    attendance,
    period = "This Week",
    totalStudents = 0
) {

    const canvas =
        document.getElementById(
            "attendanceOverviewChart"
        );


    // Canvas doesn't exist

    if (!canvas) {

        console.error(
            "attendanceOverviewChart not found."
        );

        return;

    }


    // Chart.js doesn't exist

    if (typeof Chart === "undefined") {

        console.error(
            "Chart.js is not loaded."
        );

        return;

    }


    const {
        startDate,
        endDate
    } =
        getChartDateRange(period);


    // ==================================================
    // COUNT PRESENT STUDENTS PER DATE
    // ==================================================

    const presentByDate = {};


    if (Array.isArray(attendance)) {

        attendance.forEach(
            function (record) {

                if (
                    !record.attendance_date ||
                    record.student_id === undefined ||
                    record.student_id === null
                ) {

                    return;

                }


                const status =
                    String(
                        record.status || ""
                    )
                    .trim()
                    .toLowerCase();


                if (status !== "present") {

                    return;

                }


                const date =
                    normalizeDate(
                        record.attendance_date
                    );


                if (!date) {

                    return;

                }


                if (!presentByDate[date]) {

                    presentByDate[date] =
                        new Set();

                }


                // Count each student only once

                presentByDate[date].add(
                    String(
                        record.student_id
                    )
                );

            }
        );

    }


    // ==================================================
    // CREATE LABELS AND VALUES
    // ==================================================

    const labels = [];

    const counts = [];

    const dates = [];


    let currentDate =
        new Date(startDate);


    while (
        currentDate <= endDate
    ) {

        const dateString =
            makeISODate(
                currentDate
            );


        const date =
            new Date(
                `${dateString}T00:00:00`
            );


        const dayName =
            date.toLocaleDateString(
                "en-IN",
                {
                    weekday: "short"
                }
            );


        const shortDate =
            date.toLocaleDateString(
                "en-IN",
                {
                    day: "numeric",
                    month: "short"
                }
            );


        labels.push(
            `${dayName} ${shortDate}`
        );


        dates.push(
            dateString
        );


        const count =
            presentByDate[dateString]
                ? presentByDate[dateString].size
                : 0;


        counts.push(count);


        currentDate.setDate(
            currentDate.getDate() + 1
        );

    }


    // ==================================================
    // DESTROY OLD CHART
    // ==================================================

    if (attendanceOverviewChart) {

        attendanceOverviewChart.destroy();

        attendanceOverviewChart = null;

    }


    // ==================================================
    // CREATE GRADIENT
    // ==================================================

    const ctx =
        canvas.getContext("2d");


    const gradient =
        ctx.createLinearGradient(
            0,
            0,
            0,
            320
        );


    gradient.addColorStop(
        0,
        "#60a5fa"
    );


    gradient.addColorStop(
        1,
        "#2563eb"
    );


    // ==================================================
    // VALUE LABEL PLUGIN
    // ==================================================

    const valueLabelsPlugin = {

        id: "attendanceValueLabels",

        afterDatasetsDraw(chart) {

            const {
                ctx
            } = chart;


            ctx.save();


            ctx.font =
                "600 12px Arial";


            ctx.fillStyle =
                "#334155";


            ctx.textAlign =
                "center";


            ctx.textBaseline =
                "bottom";


            const meta =
                chart.getDatasetMeta(0);


            meta.data.forEach(
                function (bar, index) {

                    const value =
                        chart.data
                            .datasets[0]
                            .data[index];


                    if (
                        value !== null &&
                        value !== undefined
                    ) {

                        ctx.fillText(
                            String(value),
                            bar.x,
                            bar.y - 8
                        );

                    }

                }
            );


            ctx.restore();

        }

    };


    // ==================================================
    // MAX Y AXIS
    // ==================================================

    let maxValue =
        Math.max(
            totalStudents || 0,
            ...counts,
            1
        );


    // Give graph some breathing space

    let suggestedMax =
        maxValue + 1;


    if (totalStudents > 0) {

        suggestedMax =
            Math.max(
                totalStudents,
                maxValue
            );

    }


    // ==================================================
    // CREATE CHART
    // ==================================================

    attendanceOverviewChart =
        new Chart(
            ctx,
            {

                type: "bar",


                data: {

                    labels: labels,

                    datasets: [

                        {

                            label:
                                "Present Students",

                            data:
                                counts,

                            backgroundColor:
                                gradient,

                            hoverBackgroundColor:
                                "#1d4ed8",

                            borderRadius:
                                10,

                            borderSkipped:
                                false,

                            borderWidth:
                                0,

                            maxBarThickness:
                                42,

                            categoryPercentage:
                                0.70,

                            barPercentage:
                                0.80

                        }

                    ]

                },


                plugins: [
                    valueLabelsPlugin
                ],


                options: {

                    responsive: true,

                    maintainAspectRatio:
                        false,


                    animation: {

                        duration: 700,

                        easing:
                            "easeOutQuart"

                    },


                    interaction: {

                        intersect: false,

                        mode: "index"

                    },


                    scales: {

                        y: {

                            beginAtZero:
                                true,

                            suggestedMax:
                                suggestedMax,

                            ticks: {

                                stepSize: 1,

                                precision: 0,

                                color:
                                    "#64748b",

                                font: {

                                    size: 11

                                },

                                padding: 8

                            },


                            title: {

                                display:
                                    true,

                                text:
                                    "Students Present",

                                color:
                                    "#64748b",

                                font: {

                                    size: 11,

                                    weight:
                                        "600"

                                }

                            },


                            grid: {

                                color:
                                    "rgba(148,163,184,0.15)",

                                drawBorder:
                                    false

                            },


                            border: {

                                display:
                                    false

                            }

                        },


                        x: {

                            ticks: {

                                color:
                                    "#64748b",

                                font: {

                                    size: 10,

                                    weight:
                                        "600"

                                },

                                maxRotation:
                                    0,

                                minRotation:
                                    0,

                                autoSkip:
                                    true,

                                maxTicksLimit:
                                    period === "This Month"
                                        ? 10
                                        : 7,

                                padding: 8

                            },


                            grid: {

                                display:
                                    false

                            },


                            border: {

                                display:
                                    false

                            }

                        }

                    },


                    plugins: {

                        legend: {

                            display:
                                false

                        },


                        tooltip: {

                            backgroundColor:
                                "#0f172a",

                            titleColor:
                                "#ffffff",

                            bodyColor:
                                "#e2e8f0",

                            padding:
                                12,

                            cornerRadius:
                                10,

                            displayColors:
                                false,


                            callbacks: {

                                title:
                                    function (
                                        tooltipItems
                                    ) {

                                        if (
                                            !tooltipItems.length
                                        ) {

                                            return "";

                                        }


                                        return (
                                            tooltipItems[0]
                                                .label
                                        );

                                    },


                                label:
                                    function (
                                        context
                                    ) {

                                        const value =
                                            context.raw ||
                                            0;


                                        return (
                                            `${value} student${
                                                value === 1
                                                    ? ""
                                                    : "s"
                                            } present`
                                        );

                                    }

                            }

                        }

                    }

                }

            }
        );

}


// ======================================================
// LOAD DASHBOARD
// ======================================================

async function loadDashboard() {

    try {

        console.log(
            "Loading dashboard..."
        );


        // ==================================================
        // GET STUDENTS
        // ==================================================

        const studentsResponse =
            await fetch(
                `${API_URL}/students`
            );


        if (!studentsResponse.ok) {

            throw new Error(
                "Unable to load students."
            );

        }


        const studentsResult =
            await studentsResponse.json();


        const students =
            Array.isArray(
                studentsResult.data
            )
                ? studentsResult.data
                : [];


        // ==================================================
        // GET ATTENDANCE
        // ==================================================

        const attendanceResponse =
            await fetch(
                `${API_URL}/attendance`
            );


        if (!attendanceResponse.ok) {

            throw new Error(
                "Unable to load attendance."
            );

        }


        const attendanceResult =
            await attendanceResponse.json();


        const attendance =
            Array.isArray(
                attendanceResult.data
            )
                ? attendanceResult.data
                : [];


        console.log(
            "Students:",
            students
        );


        console.log(
            "Attendance:",
            attendance
        );


        // ==================================================
        // TODAY
        // ==================================================

        const today =
            getIndiaDate();


        // ==================================================
        // TOTAL STUDENTS
        // ==================================================

        const totalStudents =
            students.length;


        // ==================================================
        // TODAY'S RECORDS
        // ==================================================

        const todayAttendance =
            attendance.filter(
                function (record) {

                    return (
                        normalizeDate(
                            record.attendance_date
                        ) === today
                    );

                }
            );


        // ==================================================
        // UNIQUE STUDENT RECORDS
        // ==================================================

        const attendanceMap =
            new Map();


        todayAttendance.forEach(
            function (record) {

                if (
                    record.student_id !==
                    undefined &&
                    record.student_id !==
                    null
                ) {

                    attendanceMap.set(
                        String(
                            record.student_id
                        ),
                        record
                    );

                }

            }
        );


        const uniqueAttendance =
            Array.from(
                attendanceMap.values()
            );


        // ==================================================
        // PRESENT
        // ==================================================

        const presentStudents =
            uniqueAttendance.filter(
                function (record) {

                    return (
                        String(
                            record.status ||
                            ""
                        )
                        .trim()
                        .toLowerCase()
                        ===
                        "present"
                    );

                }
            ).length;


        // ==================================================
        // ABSENT
        // ==================================================

        const absentStudents =
            uniqueAttendance.filter(
                function (record) {

                    return (
                        String(
                            record.status ||
                            ""
                        )
                        .trim()
                        .toLowerCase()
                        ===
                        "absent"
                    );

                }
            ).length;


        // ==================================================
        // ATTENDANCE RATE
        // ==================================================

        let attendanceRate =
            0;


        if (totalStudents > 0) {

            attendanceRate =
                Math.round(
                    (
                        presentStudents /
                        totalStudents
                    ) * 100
                );

        }


        // ==================================================
        // UPDATE STAT CARDS
        // ==================================================

        if (totalStudentsEl) {

            totalStudentsEl.textContent =
                totalStudents;

        }


        if (presentTodayEl) {

            presentTodayEl.textContent =
                presentStudents;

        }


        if (absentTodayEl) {

            absentTodayEl.textContent =
                absentStudents;

        }


        if (attendanceRateEl) {

            attendanceRateEl.textContent =
                `${attendanceRate}%`;

        }


        // ==================================================
        // SUMMARY
        // ==================================================

        if (summaryPresentEl) {

            summaryPresentEl.textContent =
                `${presentStudents} Students`;

        }


        if (summaryAbsentEl) {

            summaryAbsentEl.textContent =
                `${absentStudents} Students`;

        }


        // ==================================================
        // PERCENTAGES
        // ==================================================

        let presentPercentage =
            0;

        let absentPercentage =
            0;


        if (totalStudents > 0) {

            presentPercentage =
                Math.round(
                    (
                        presentStudents /
                        totalStudents
                    ) * 100
                );


            absentPercentage =
                Math.round(
                    (
                        absentStudents /
                        totalStudents
                    ) * 100
                );

        }


        if (presentPercentageEl) {

            presentPercentageEl.textContent =
                `${presentPercentage}%`;

        }


        if (absentPercentageEl) {

            absentPercentageEl.textContent =
                `${absentPercentage}%`;

        }


        if (progressPercentageEl) {

            progressPercentageEl.textContent =
                `${presentPercentage}%`;

        }


        if (progressPresentEl) {

            progressPresentEl.style.width =
                `${presentPercentage}%`;

        }


        // ==================================================
        // DRAW CHART
        // ==================================================

        const selectedPeriod =
            chartPeriodSelect
                ? (
                    chartPeriodSelect.value ||
                    "This Week"
                )
                : "This Week";


        renderAttendanceChart(
            attendance,
            selectedPeriod,
            totalStudents
        );


        // ==================================================
        // RECENT ATTENDANCE
        // ==================================================

        displayRecentAttendance(
            attendance
        );


        console.log(
            "Dashboard loaded successfully."
        );

    }


    catch (error) {

        console.error(
            "Dashboard Error:",
            error
        );


        if (totalStudentsEl) {

            totalStudentsEl.textContent =
                "0";

        }


        if (presentTodayEl) {

            presentTodayEl.textContent =
                "0";

        }


        if (absentTodayEl) {

            absentTodayEl.textContent =
                "0";

        }


        if (attendanceRateEl) {

            attendanceRateEl.textContent =
                "0%";

        }


        if (recentAttendanceTable) {

            recentAttendanceTable.innerHTML = `

                <tr>

                    <td
                        colspan="4"
                        style="
                            text-align:center;
                            padding:30px;
                            color:#dc2626;
                        "
                    >

                        <i
                            class="fa-solid
                            fa-triangle-exclamation"
                        ></i>

                        <br><br>

                        Failed to load attendance.

                        <br><br>

                        ${escapeHTML(
                            error.message
                        )}

                    </td>

                </tr>

            `;

        }

    }

}


// ======================================================
// RECENT ATTENDANCE TABLE
// ======================================================

function displayRecentAttendance(
    attendance
) {

    if (!recentAttendanceTable) {

        return;

    }


    if (
        !Array.isArray(attendance) ||
        attendance.length === 0
    ) {

        recentAttendanceTable.innerHTML = `

            <tr>

                <td
                    colspan="4"
                    style="
                        text-align:center;
                        padding:30px;
                        color:#64748b;
                    "
                >

                    No attendance records found.

                </td>

            </tr>

        `;

        return;

    }


    // ==================================================
    // SORT NEWEST FIRST
    // ==================================================

    const sortedAttendance =
        [...attendance].sort(
            function (a, b) {

                const dateA =
                    new Date(
                        a.created_at ||
                        `${normalizeDate(
                            a.attendance_date
                        )}T00:00:00`
                    );


                const dateB =
                    new Date(
                        b.created_at ||
                        `${normalizeDate(
                            b.attendance_date
                        )}T00:00:00`
                    );


                return dateB - dateA;

            }
        );


    // ==================================================
    // ONLY 10 RECORDS
    // ==================================================

    const recentRecords =
        sortedAttendance.slice(
            0,
            10
        );


    recentAttendanceTable.innerHTML =
        "";


    // ==================================================
    // CREATE TABLE ROWS
    // ==================================================

    recentRecords.forEach(
        function (record) {

            const row =
                document.createElement(
                    "tr"
                );


            const isPresent =
                String(
                    record.status ||
                    ""
                )
                .trim()
                .toLowerCase()
                ===
                "present";


            const statusClass =
                isPresent
                    ? "present"
                    : "absent";


            const statusIcon =
                isPresent
                    ? "fa-check"
                    : "fa-xmark";


            const statusText =
                isPresent
                    ? "Present"
                    : "Absent";


            row.innerHTML = `

                <td>

                    <strong>

                        ${escapeHTML(
                            record.student_name ||
                            "Unknown"
                        )}

                    </strong>

                </td>


                <td>

                    ${escapeHTML(
                        String(
                            record.student_id ||
                            "-"
                        )
                    )}

                </td>


                <td>

                    ${formatDate(
                        record.attendance_date
                    )}

                </td>


                <td>

                    <span
                        class="status-badge ${statusClass}"
                    >

                        <i
                            class="fa-solid
                            ${statusIcon}"
                        ></i>

                        ${statusText}

                    </span>

                </td>

            `;


            recentAttendanceTable.appendChild(
                row
            );

        }
    );

}


// ======================================================
// FORMAT DATE
// ======================================================

function formatDate(dateValue) {

    if (!dateValue) {

        return "-";

    }


    const normalized =
        normalizeDate(
            dateValue
        );


    const date =
        new Date(
            `${normalized}T00:00:00`
        );


    if (
        Number.isNaN(
            date.getTime()
        )
    ) {

        return "-";

    }


    return date.toLocaleDateString(
        "en-IN",
        {
            day: "2-digit",
            month: "short",
            year: "numeric"
        }
    );

}


// ======================================================
// ESCAPE HTML
// ======================================================

function escapeHTML(value) {

    return String(value)

        .replace(
            /&/g,
            "&amp;"
        )

        .replace(
            /</g,
            "&lt;"
        )

        .replace(
            />/g,
            "&gt;"
        )

        .replace(
            /"/g,
            "&quot;"
        )

        .replace(
            /'/g,
            "&#039;"
        );

}


// ======================================================
// TOTAL STUDENTS CARD → STUDENTS PAGE
// ======================================================

const totalStudentsCard =
    document.querySelector(
        ".total-students"
    );


if (totalStudentsCard) {

    totalStudentsCard.style.cursor =
        "pointer";


    totalStudentsCard.addEventListener(
        "click",
        function () {

            window.location.href =
                "students.html";

        }
    );

}


// ======================================================
// CHART DROPDOWN
// ======================================================

if (chartPeriodSelect) {

    chartPeriodSelect.addEventListener(
        "change",
        function () {

            console.log(
                "Selected chart period:",
                chartPeriodSelect.value
            );


            loadDashboard();

        }
    );

}


// ======================================================
// INITIAL LOAD
// ======================================================

document.addEventListener(
    "DOMContentLoaded",
    function () {

        loadDashboard();

    }
);


// ======================================================
// AUTO REFRESH
// ======================================================

setInterval(
    function () {

        loadDashboard();

    },
    5000
);
