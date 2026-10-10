const API_URL = "http://127.0.0.1:8000";

let attendanceRecords = [];


// ==========================================
// LOAD ATTENDANCE RECORDS
// ==========================================

async function loadAttendance() {

    const attendanceTable =
        document.getElementById("attendanceTable");

    try {

        attendanceTable.innerHTML =
            '<tr><td colspan="5">Loading attendance records...</td></tr>';


        const response = await fetch(
            API_URL + "/attendance"
        );


        if (!response.ok) {

            throw new Error(
                "Failed to fetch attendance records."
            );

        }


        const result = await response.json();


        console.log(
            "Attendance data:",
            result
        );


        if (!result.success) {

            throw new Error(
                result.error ||
                "Unable to load attendance."
            );

        }


        attendanceRecords = result.data;


        // UPDATE STATISTICS

        updateStatistics(
            attendanceRecords
        );


        // DISPLAY TABLE

        displayAttendance(
            attendanceRecords
        );

    }

    catch (error) {

        console.error(
            "Attendance Error:",
            error
        );


        attendanceTable.innerHTML =
            '<tr>' +
                '<td colspan="5" style="color:red;">' +
                    'Failed to load attendance records.' +
                '</td>' +
            '</tr>';

    }

}


// ==========================================
// UPDATE STATISTICS
// ==========================================

function updateStatistics(records) {

    const totalRecords =
        records.length;


    const totalPresent =
        records.filter(function (record) {

            return record.status === "Present";

        }).length;


    const totalAbsent =
        records.filter(function (record) {

            return record.status === "Absent";

        }).length;


    document.getElementById(
        "totalRecords"
    ).textContent =
        totalRecords;


    document.getElementById(
        "totalPresent"
    ).textContent =
        totalPresent;


    document.getElementById(
        "totalAbsent"
    ).textContent =
        totalAbsent;

}


// ==========================================
// DISPLAY ATTENDANCE TABLE
// ==========================================

function displayAttendance(records) {

    const attendanceTable =
        document.getElementById(
            "attendanceTable"
        );


    // NO RECORDS

    if (records.length === 0) {

        attendanceTable.innerHTML =
            '<tr>' +
                '<td colspan="5">' +
                    'No attendance records found.' +
                '</td>' +
            '</tr>';

        return;

    }


    // CLEAR TABLE

    attendanceTable.innerHTML = "";


    // CREATE ROWS

    records.forEach(
        function (record, index) {


            const row =
                document.createElement("tr");


            // STATUS CLASS

            let statusClass = "";


            if (record.status === "Present") {

                statusClass =
                    "status-present";

            }

            else {

                statusClass =
                    "status-absent";

            }


            // TABLE DATA

            row.innerHTML =
                '<td>' +

                    (index + 1) +

                '</td>' +


                '<td>' +

                    record.student_id +

                '</td>' +


                '<td>' +

                    record.student_name +

                '</td>' +


                '<td>' +

                    '<span class="' +

                        statusClass +

                    '">' +

                        record.status +

                    '</span>' +

                '</td>' +


                '<td>' +

                    record.attendence_date +

                '</td>';


            attendanceTable.appendChild(
                row
            );


        }
    );

}


// ==========================================
// SEARCH ATTENDANCE
// ==========================================

document.addEventListener(
    "DOMContentLoaded",
    function () {


        // LOAD DATA

        loadAttendance();


        // GET SEARCH BOX

        const searchInput =
            document.getElementById(
                "searchAttendance"
            );


        // SEARCH EVENT

        searchInput.addEventListener(
            "input",
            function () {


                const searchValue =
                    this.value
                        .toLowerCase()
                        .trim();


                const filteredRecords =
                    attendanceRecords.filter(
                        function (record) {


                            const studentName =
                                String(
                                    record.student_name || ""
                                ).toLowerCase();


                            const studentId =
                                String(
                                    record.student_id || ""
                                ).toLowerCase();


                            return (

                                studentName.includes(
                                    searchValue
                                )

                                ||

                                studentId.includes(
                                    searchValue
                                )

                            );


                        }
                    );


                displayAttendance(
                    filteredRecords
                );


            }
        );


    }
);