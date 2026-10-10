const API_URL = "http://127.0.0.1:8000";


// ==========================================
// GET HTML ELEMENTS
// ==========================================

const studentList = document.getElementById("studentList");

const totalCount = document.getElementById("totalCount");
const presentCount = document.getElementById("presentCount");
const absentCount = document.getElementById("absentCount");

const markAllPresent = document.getElementById("markAllPresent");
const markAllAbsent = document.getElementById("markAllAbsent");

const saveAttendance = document.getElementById("saveAttendance");
const resetAttendance = document.getElementById("resetAttendance");

const modifyAttendance = document.getElementById("modifyAttendance");

const attendanceDate = document.getElementById("attendanceDate");
const currentDate = document.getElementById("currentDate");


// ==========================================
// VARIABLES
// ==========================================

let attendanceRecords = [];

let modifyMode = false;


// ==========================================
// GET INDIA DATE
// ==========================================

function getIndiaDate() {

    const now = new Date();

    const indiaDate = new Intl.DateTimeFormat(
        "en-CA",
        {
            timeZone: "Asia/Kolkata",
            year: "numeric",
            month: "2-digit",
            day: "2-digit"
        }
    ).format(now);

    return indiaDate;
}


const todayDate = getIndiaDate();


// ==========================================
// DISPLAY CURRENT DATE
// ==========================================

if (currentDate) {

    const today = new Date();

    currentDate.textContent =
        today.toLocaleDateString(
            "en-IN",
            {
                timeZone: "Asia/Kolkata",
                day: "2-digit",
                month: "long",
                year: "numeric"
            }
        );

}


// ==========================================
// SET DEFAULT DATE
// ==========================================

if (attendanceDate) {

    attendanceDate.value = todayDate;

}


// ==========================================
// NORMALIZE DATE
// ==========================================

function normalizeDate(dateValue) {

    if (!dateValue) {

        return "";

    }

    return String(dateValue).split("T")[0];

}


// ==========================================
// GET SELECTED DATE
// ==========================================

function getSelectedDate() {

    if (
        attendanceDate &&
        attendanceDate.value
    ) {

        return attendanceDate.value;

    }

    return todayDate;

}


// ==========================================
// DISABLE EDIT BUTTONS
// ==========================================

function disableEditing() {

    const buttons = document.querySelectorAll(
        ".present-btn, .absent-btn"
    );

    buttons.forEach(function (button) {

        button.disabled = true;

    });

}


// ==========================================
// ENABLE EDIT BUTTONS
// ==========================================

function enableEditing() {

    const buttons = document.querySelectorAll(
        ".present-btn, .absent-btn"
    );

    buttons.forEach(function (button) {

        button.disabled = false;

    });

}


// ==========================================
// SHOW EMPTY SCREEN
// ==========================================

function showEmptyMessage(message) {

    if (!studentList) {

        return;

    }

    studentList.innerHTML = `

        <div class="empty-attendance">

            <i class="fa-solid fa-camera"></i>

            <h3>
                ${message}
            </h3>

            <p>
                Click "Modify Attendance"
                to load attendance records.
            </p>

        </div>

    `;

    updateCounts();

}


// ==========================================
// LOAD ATTENDANCE
// ==========================================

async function loadAttendance(
    selectedDate = getSelectedDate()
) {

    try {

        if (studentList) {

            studentList.innerHTML = `

                <div class="empty-attendance">

                    <i class="fa-solid fa-spinner fa-spin"></i>

                    <h3>
                        Loading Attendance...
                    </h3>

                    <p>
                        Please wait.
                    </p>

                </div>

            `;

        }


        // ==================================
        // GET ATTENDANCE BY DATE
        // ==================================

        const response = await fetch(

            `${API_URL}/attendance/date/${selectedDate}`

        );


        if (!response.ok) {

            throw new Error(
                "Could not load attendance."
            );

        }


        const result = await response.json();


        if (!result.success) {

            throw new Error(
                result.detail ||
                "Unable to load attendance."
            );

        }


        attendanceRecords =
            result.data || [];


        // ==================================
        // DISPLAY
        // ==================================

        displayAttendance(
            attendanceRecords
        );


    }

    catch (error) {

        console.error(
            "Attendance Error:",
            error
        );


        if (studentList) {

            studentList.innerHTML = `

                <div class="empty-attendance">

                    <i
                        class="fa-solid fa-triangle-exclamation"
                        style="color:#dc2626;"
                    ></i>

                    <h3>
                        Failed to Load Attendance
                    </h3>

                    <p>
                        ${error.message}
                    </p>

                </div>

            `;

        }

    }

}


// ==========================================
// DISPLAY ATTENDANCE
// ==========================================

function displayAttendance(records) {

    if (!studentList) {

        return;

    }


    // ======================================
    // NO RECORDS
    // ======================================

    if (
        !records ||
        records.length === 0
    ) {

        studentList.innerHTML = `

            <div class="empty-attendance">

                <i class="fa-solid fa-calendar-xmark"></i>

                <h3>
                    No Attendance Found
                </h3>

                <p>
                    No attendance records exist
                    for ${getSelectedDate()}.
                </p>

            </div>

        `;

        updateCounts();

        return;

    }


    // ======================================
    // CLEAR OLD DATA
    // ======================================

    studentList.innerHTML = "";


    // ======================================
    // CREATE STUDENT ROWS
    // ======================================

    records.forEach(
        function (record, index) {

            const displayNumber =
                String(index + 1)
                .padStart(2, "0");


            const studentRow =
                document.createElement("div");


            studentRow.className =
                "student-row";


            // ==================================
            // STORE DATA
            // ==================================

            studentRow.dataset.recordId =
                record.id || "";

            studentRow.dataset.studentId =
                record.student_id || "";

            studentRow.dataset.studentName =
                record.student_name || "";

            studentRow.dataset.status =
                record.status || "Absent";


            // ==================================
            // STATUS
            // ==================================

            const isPresent =
                String(record.status)
                .toLowerCase()
                ===
                "present";


            const presentClass =
                isPresent
                ? "active"
                : "";


            const absentClass =
                !isPresent
                ? "active"
                : "";


            // ==================================
            // HTML
            // ==================================

            studentRow.innerHTML = `

                <div class="student-details">

                    <div class="student-number">

                        ${displayNumber}

                    </div>


                    <div>

                        <h3>
                            ${record.student_name || "Unknown"}
                        </h3>


                        <p>

                            Student ID:
                            ${record.student_id || "-"}

                        </p>

                    </div>

                </div>


                <div class="attendance-buttons">


                    <button
                        type="button"
                        class="present-btn ${presentClass}"
                    >

                        <i class="fa-solid fa-check"></i>

                        Present

                    </button>


                    <button
                        type="button"
                        class="absent-btn ${absentClass}"
                    >

                        <i class="fa-solid fa-xmark"></i>

                        Absent

                    </button>


                </div>

            `;


            studentList.appendChild(
                studentRow
            );

        }
    );


    // ======================================
    // ADD BUTTON EVENTS
    // ======================================

    addAttendanceButtonEvents();


    // ======================================
    // ENABLE ONLY IN MODIFY MODE
    // ======================================

    if (modifyMode) {

        enableEditing();

    }

    else {

        disableEditing();

    }


    updateCounts();

}


// ==========================================
// UPDATE LOCAL STATUS
// ==========================================

function updateLocalStatus(
    studentId,
    status
) {

    attendanceRecords =
        attendanceRecords.map(
            function (record) {

                if (
                    String(record.student_id)
                    ===
                    String(studentId)
                ) {

                    record.status =
                        status;

                }

                return record;

            }
        );

}


// ==========================================
// PRESENT / ABSENT EVENTS
// ==========================================

function addAttendanceButtonEvents() {

    const studentRows =
        document.querySelectorAll(
            ".student-row"
        );


    studentRows.forEach(
        function (row) {

            const presentButton =
                row.querySelector(
                    ".present-btn"
                );


            const absentButton =
                row.querySelector(
                    ".absent-btn"
                );


            // ==================================
            // PRESENT
            // ==================================

            presentButton.addEventListener(
                "click",
                function () {

                    if (!modifyMode) {

                        return;

                    }


                    row.dataset.status =
                        "Present";


                    presentButton.classList.add(
                        "active"
                    );


                    absentButton.classList.remove(
                        "active"
                    );


                    updateLocalStatus(
                        row.dataset.studentId,
                        "Present"
                    );


                    updateCounts();

                }
            );


            // ==================================
            // ABSENT
            // ==================================

            absentButton.addEventListener(
                "click",
                function () {

                    if (!modifyMode) {

                        return;

                    }


                    row.dataset.status =
                        "Absent";


                    absentButton.classList.add(
                        "active"
                    );


                    presentButton.classList.remove(
                        "active"
                    );


                    updateLocalStatus(
                        row.dataset.studentId,
                        "Absent"
                    );


                    updateCounts();

                }
            );

        }
    );

}


// ==========================================
// UPDATE COUNTS
// ==========================================

function updateCounts() {

    const studentRows =
        document.querySelectorAll(
            ".student-row"
        );


    const totalStudents =
        studentRows.length;


    let presentStudents = 0;

    let absentStudents = 0;


    studentRows.forEach(
        function (row) {

            if (
                row.dataset.status
                ===
                "Present"
            ) {

                presentStudents++;

            }

            else {

                absentStudents++;

            }

        }
    );


    if (totalCount) {

        totalCount.textContent =
            totalStudents;

    }


    if (presentCount) {

        presentCount.textContent =
            presentStudents;

    }


    if (absentCount) {

        absentCount.textContent =
            absentStudents;

    }

}


// ==========================================
// MARK ALL PRESENT
// ==========================================

if (markAllPresent) {

    markAllPresent.addEventListener(
        "click",
        function () {

            if (!modifyMode) {

                alert(
                    "First click Modify Attendance."
                );

                return;

            }


            const studentRows =
                document.querySelectorAll(
                    ".student-row"
                );


            if (
                studentRows.length === 0
            ) {

                alert(
                    "No attendance records available."
                );

                return;

            }


            studentRows.forEach(
                function (row) {

                    row.dataset.status =
                        "Present";


                    row.querySelector(
                        ".present-btn"
                    ).classList.add(
                        "active"
                    );


                    row.querySelector(
                        ".absent-btn"
                    ).classList.remove(
                        "active"
                    );


                    updateLocalStatus(
                        row.dataset.studentId,
                        "Present"
                    );

                }
            );


            updateCounts();

        }
    );

}


// ==========================================
// MARK ALL ABSENT
// ==========================================

if (markAllAbsent) {

    markAllAbsent.addEventListener(
        "click",
        function () {

            if (!modifyMode) {

                alert(
                    "First click Modify Attendance."
                );

                return;

            }


            const studentRows =
                document.querySelectorAll(
                    ".student-row"
                );


            if (
                studentRows.length === 0
            ) {

                alert(
                    "No attendance records available."
                );

                return;

            }


            studentRows.forEach(
                function (row) {

                    row.dataset.status =
                        "Absent";


                    row.querySelector(
                        ".absent-btn"
                    ).classList.add(
                        "active"
                    );


                    row.querySelector(
                        ".present-btn"
                    ).classList.remove(
                        "active"
                    );


                    updateLocalStatus(
                        row.dataset.studentId,
                        "Absent"
                    );

                }
            );


            updateCounts();

        }
    );

}


// ==========================================
// MODIFY ATTENDANCE
// ==========================================

if (modifyAttendance) {

    modifyAttendance.addEventListener(
        "click",
        async function () {

            // ==============================
            // ENABLE MODIFY MODE
            // ==============================

            modifyMode = true;


            const selectedDate =
                getSelectedDate();


            modifyAttendance.disabled =
                true;


            modifyAttendance.innerHTML = `

                <i class="fa-solid fa-spinner fa-spin"></i>

                Loading...

            `;


            try {

                await loadAttendance(
                    selectedDate
                );


                if (
                    attendanceRecords.length > 0
                ) {

                    enableEditing();


                    alert(

                        "Attendance loaded successfully!\n\n" +

                        "You can now modify Present / Absent status."

                    );

                }

                else {

                    alert(

                        `No attendance found for ${selectedDate}.`

                    );

                }

            }

            catch (error) {

                console.error(error);

            }

            finally {

                modifyAttendance.disabled =
                    false;


                modifyAttendance.innerHTML = `

                    <i class="fa-solid fa-pen-to-square"></i>

                    Modify Attendance

                `;

            }

        }
    );

}


// ==========================================
// DATE CHANGE
// ==========================================

if (attendanceDate) {

    attendanceDate.addEventListener(
        "change",
        function () {

            // ==================================
            // IMPORTANT:
            // DATE CHANGE DOES NOT LOAD DATA
            // ==================================

            // If user has not clicked Modify,
            // keep attendance hidden.

            if (!modifyMode) {

                showEmptyMessage(
                    "Click Modify Attendance"
                );

                return;

            }


            // ==================================
            // IF MODIFY MODE IS ON
            // LOAD NEW DATE
            // ==================================

            loadAttendance(
                attendanceDate.value
            );

        }
    );

}


// ==========================================
// SAVE ATTENDANCE
// ==========================================

if (saveAttendance) {

    saveAttendance.addEventListener(
        "click",
        async function () {

            // ==================================
            // MUST BE IN MODIFY MODE
            // ==================================

            if (!modifyMode) {

                alert(
                    "First click Modify Attendance."
                );

                return;

            }


            const studentRows =
                document.querySelectorAll(
                    ".student-row"
                );


            if (
                studentRows.length === 0
            ) {

                alert(
                    "No attendance records available."
                );

                return;

            }


            try {

                saveAttendance.disabled =
                    true;


                saveAttendance.innerHTML = `

                    <i class="fa-solid fa-spinner fa-spin"></i>

                    Saving Changes...

                `;


                const selectedDate =
                    getSelectedDate();


                // ==================================
                // UPDATE EVERY STUDENT
                // ==================================

                for (
                    const row
                    of studentRows
                ) {

                    const studentId =
                        row.dataset.studentId;


                    const newStatus =
                        row.dataset.status;


                    const response =
                        await fetch(

                            `${API_URL}/attendance/${studentId}`,

                            {

                                method: "PUT",

                                headers: {

                                    "Content-Type":
                                        "application/json"

                                },

                                body:
                                    JSON.stringify({

                                        status:
                                            newStatus,

                                        attendance_date:
                                            selectedDate

                                    })

                            }

                        );


                    if (!response.ok) {

                        let errorMessage =
                            "Failed to update attendance.";


                        try {

                            const errorResult =
                                await response.json();


                            errorMessage =
                                errorResult.detail
                                ||
                                errorMessage;

                        }

                        catch (error) {

                            console.error(error);

                        }


                        throw new Error(
                            errorMessage
                        );

                    }

                }


                // ==================================
                // SUCCESS
                // ==================================

                alert(
                    "Attendance saved successfully!"
                );


                // ==================================
                // IMPORTANT:
                // HIDE ATTENDANCE AFTER SAVE
                // ==================================

                attendanceRecords = [];


                modifyMode = false;


                showEmptyMessage(
                    "Attendance Saved Successfully"
                );


                updateCounts();


            }

            catch (error) {

                console.error(
                    "Save Error:",
                    error
                );


                alert(

                    "Failed to save changes:\n\n" +
                    error.message

                );

            }

            finally {

                saveAttendance.disabled =
                    false;


                saveAttendance.innerHTML = `

                    <i class="fa-solid fa-floppy-disk"></i>

                    Save Attendance Changes

                `;

            }

        }
    );

}


// ==========================================
// RESET ATTENDANCE
// ==========================================

if (resetAttendance) {

    resetAttendance.addEventListener(
        "click",
        async function () {

            const selectedDate =
                getSelectedDate();


            const confirmReset =
                confirm(

                    `Are you sure you want to reset attendance for ${selectedDate}?\n\n` +

                    "All attendance records for this date will be deleted."

                );


            if (!confirmReset) {

                return;

            }


            try {

                resetAttendance.disabled =
                    true;


                resetAttendance.innerHTML = `

                    <i class="fa-solid fa-spinner fa-spin"></i>

                    Resetting...

                `;


                const response =
                    await fetch(

                        `${API_URL}/attendance/reset/${selectedDate}`,

                        {

                            method: "DELETE"

                        }

                    );


                if (!response.ok) {

                    const errorResult =
                        await response.json();


                    throw new Error(

                        errorResult.detail
                        ||
                        "Failed to reset attendance."

                    );

                }


                attendanceRecords = [];


                modifyMode = false;


                showEmptyMessage(
                    "Attendance Reset Successfully"
                );


                alert(
                    "Attendance reset successfully!"
                );

            }

            catch (error) {

                console.error(
                    "Reset Error:",
                    error
                );


                alert(

                    "Failed to reset attendance:\n\n" +
                    error.message

                );

            }

            finally {

                resetAttendance.disabled =
                    false;


                resetAttendance.innerHTML = `

                    <i class="fa-solid fa-rotate-left"></i>

                    Reset Attendance

                `;

            }

        }
    );

}


// ==========================================
// START APPLICATION
// ==========================================

// IMPORTANT:
// DO NOT LOAD ATTENDANCE AUTOMATICALLY

showEmptyMessage(
    "Click Modify Attendance"
);