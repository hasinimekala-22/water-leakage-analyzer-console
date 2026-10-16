
import math
import re
import oracledb
from datetime import datetime, timedelta
from getpass import getpass

from dashboard import show_dashboard
# ============================================================
# WATER LEAKAGE AND LOSS ANALYZER
# Python + Oracle Database
# ============================================================

DB_USER = "water_user"
DB_DSN = "localhost:1521/FREEPDB1"


# -------------------- DATABASE CONNECTION --------------------

def connect_db(password):
    """Connect to the Oracle database."""
    try:
        connection = oracledb.connect(
            user=DB_USER,
            password=password,
            dsn=DB_DSN
        )
        return connection

    except oracledb.Error as error:
        print("\nDatabase connection failed:", error)
        return None


# -------------------- DISPLAY UTILITIES --------------------

def print_header(title):
    """Display a formatted heading."""
    print("\n" + "=" * 72)
    print(title.center(72))
    print("=" * 72)


def display_table(headers, rows):
    """Display database results in an aligned table."""
    if not rows:
        print("\nNo records found.")
        return

    formatted_rows = [
        [
            "-" if value is None else str(value)
            for value in row
        ]
        for row in rows
    ]

    widths = []

    for index, header in enumerate(headers):
        maximum = len(str(header))

        for row in formatted_rows:
            maximum = max(maximum, len(row[index]))

        widths.append(maximum)

    separator = "+-" + "-+-".join(
        "-" * width for width in widths
    ) + "-+"

    print(separator)

    print(
        "| " +
        " | ".join(
            str(headers[i]).ljust(widths[i])
            for i in range(len(headers))
        ) +
        " |"
    )

    print(separator)

    for row in formatted_rows:
        print(
            "| " +
            " | ".join(
                row[i].ljust(widths[i])
                for i in range(len(headers))
            ) +
            " |"
        )

    print(separator)
    print("Total records:", len(rows))


def confirm_action(prompt):
    """Accept y/yes as confirmation."""
    answer = input(prompt).strip().lower()
    return answer in ("y", "yes")


# -------------------- INPUT VALIDATION --------------------

def read_time(prompt):
    """Read a valid time strictly in HH:MM format."""
    while True:
        value = input(prompt).strip()

        if not re.fullmatch(r"\d{2}:\d{2}", value):
            print("Invalid format. Use HH:MM, for example 09:30.")
            continue

        try:
            return datetime.strptime(value, "%H:%M").time()

        except ValueError:
            print("Invalid time. Enter a valid time such as 09:30.")


def read_positive_number(prompt):
    """Read a positive, finite numeric value."""
    while True:
        try:
            value = float(input(prompt).strip())

            if not math.isfinite(value):
                print("Enter a finite numeric value.")
                continue

            if value <= 0:
                print("Value must be greater than zero.")
                continue

            return value

        except ValueError:
            print("Invalid input. Enter a numeric value.")


# -------------------- ADD LEAKAGE INCIDENT --------------------

def add_incident(password):
    """Collect incident details, calculate water loss and save."""

    print_header("ADD LEAKAGE INCIDENT")

    location = input("Enter location: ").strip()

    if not location:
        print("Location cannot be empty.")
        return

    print("\nEnter time in 24-hour HH:MM format.")

    start_time = read_time("Leak start time: ")
    repair_time = read_time("Repair time: ")

    today = datetime.now().date()

    start = datetime.combine(today, start_time)
    repair = datetime.combine(today, repair_time)

    # A repair time earlier than the start time means
    # the repair occurred after midnight.
    if repair < start:
        repair += timedelta(days=1)

    duration = (repair - start).total_seconds() / 3600

    if duration <= 0:
        print(
            "\nStart time and repair time cannot be identical. "
            "Please enter a positive-duration incident."
        )
        return

    print("\nLeak Types")
    print("-" * 30)
    print("1. Pipe Leakage")
    print("2. Tap Leakage")
    print("3. Main Pipeline Leakage")

    leak_types = {
        "1": "Pipe Leakage",
        "2": "Tap Leakage",
        "3": "Main Pipeline Leakage"
    }

    while True:
        choice = input("Choose leak type (1-3): ").strip()

        if choice in leak_types:
            leak_type = leak_types[choice]
            break

        print("Invalid choice. Please select 1, 2, or 3.")

    loss_rate = read_positive_number(
        "Estimated water loss rate (litres/hour): "
    )

    if loss_rate > 10000:
        print("\nWARNING: This leakage rate is unusually high.")
        print("Please verify the entered value.")

        if not confirm_action(
            "Save this rate anyway? (y/yes or n/no): "
        ):
            print("Incident cancelled. No record was saved.")
            return

    water_loss = duration * loss_rate

    if water_loss >= 500:
        priority = "High"
    elif water_loss >= 200:
        priority = "Medium"
    else:
        priority = "Low"

    print_header("INCIDENT SUMMARY")

    print(f"Location        : {location}")
    print(f"Leak type       : {leak_type}")
    print(f"Leak started    : {start}")
    print(f"Repair time     : {repair}")
    print(f"Duration        : {duration:.2f} hours")
    print(f"Loss rate       : {loss_rate:.2f} litres/hour")
    print(f"Total water loss: {water_loss:.2f} litres")
    print(f"Priority        : {priority}")

    if not confirm_action(
        "\nSave this incident? (y/yes or n/no): "
    ):
        print("Incident cancelled. No record was saved.")
        return

    connection = connect_db(password)

    if connection is None:
        print("Incident was not saved because the database is unavailable.")
        return

    cursor = None

    try:
        cursor = connection.cursor()

        # Retains the existing table and schema.
        # MAX + 1 is suitable only for a single-user demonstration.
        # An Oracle sequence is preferable for concurrent users.
        cursor.execute(
            """
            INSERT INTO leakage_records
            (
                incident_id,
                location,
                leak_start,
                repair_time,
                duration_hours,
                loss_rate,
                water_loss,
                leak_type,
                priority
            )
            VALUES
            (
                (SELECT NVL(MAX(incident_id), 0) + 1
                 FROM leakage_records),
                :location,
                :leak_start,
                :repair_time,
                :duration,
                :loss_rate,
                :water_loss,
                :leak_type,
                :priority
            )
            """,
            {
                "location": location,
                "leak_start": start,
                "repair_time": repair,
                "duration": round(duration, 2),
                "loss_rate": round(loss_rate, 2),
                "water_loss": round(water_loss, 2),
                "leak_type": leak_type,
                "priority": priority
            }
        )

        connection.commit()

        print("\nIncident saved successfully!")

    except oracledb.Error as error:
        connection.rollback()
        print("\nError saving incident:", error)
        print("The transaction was rolled back.")

    finally:
        if cursor is not None:
            cursor.close()

        connection.close()


# -------------------- REPORT DEFINITIONS --------------------

REPORTS = {
    "1": (
        "ALL LEAKAGE RECORDS",
        """
        SELECT incident_id,
               location,
               duration_hours,
               ROUND(water_loss, 2),
               priority
        FROM leakage_records
        ORDER BY incident_id
        """,
        [
            "ID",
            "Location",
            "Duration (hrs)",
            "Water Loss (L)",
            "Priority"
        ]
    ),

    "2": (
        "WATER LOSS BY LOCATION",
        """
        SELECT LOWER(TRIM(location)),
               COUNT(*),
               ROUND(SUM(water_loss), 2)
        FROM leakage_records
        GROUP BY LOWER(TRIM(location))
        ORDER BY SUM(water_loss) DESC
        """,
        [
            "Location",
            "Incidents",
            "Total Loss (L)"
        ]
    ),

    "3": (
        "RECURRING LEAKAGE LOCATIONS",
        """
        SELECT LOWER(TRIM(location)),
               COUNT(*)
        FROM leakage_records
        GROUP BY LOWER(TRIM(location))
        HAVING COUNT(*) > 1
        ORDER BY COUNT(*) DESC
        """,
        [
            "Location",
            "Incident Count"
        ]
    ),

    "4": (
        "HIGH-PRIORITY INCIDENTS",
        """
        SELECT incident_id,
               location,
               ROUND(water_loss, 2),
               duration_hours
        FROM leakage_records
        WHERE priority = 'High'
        ORDER BY water_loss DESC
        """,
        [
            "ID",
            "Location",
            "Water Loss (L)",
            "Duration (hrs)"
        ]
    ),

    "5": (
        "MAINTENANCE RECOMMENDATIONS",
        """
        SELECT LOWER(TRIM(location)),
               COUNT(*),
               ROUND(SUM(water_loss), 2),
               CASE
                   WHEN COUNT(*) > 1
                       THEN 'URGENT - RECURRING'
                   WHEN SUM(water_loss) >= 500
                       THEN 'HIGH'
                   ELSE 'NORMAL'
               END
        FROM leakage_records
        GROUP BY LOWER(TRIM(location))
        ORDER BY
            CASE
                WHEN COUNT(*) > 1 THEN 1
                WHEN SUM(water_loss) >= 500 THEN 2
                ELSE 3
            END,
            SUM(water_loss) DESC
        """,
        [
            "Location",
            "Incidents",
            "Total Loss (L)",
            "Recommendation"
        ]
    )
}


# -------------------- ANALYSIS REPORTS --------------------

def show_reports(password):
    """Display the five analytical reports."""

    while True:
        print_header("LEAKAGE ANALYSIS REPORTS")

        print("1. View All Leakage Records")
        print("2. Water Loss by Location")
        print("3. Find Recurring Locations")
        print("4. High-Priority Incidents")
        print("5. Maintenance Recommendations")
        print("6. Return to Main Menu")

        choice = input("\nEnter your choice (1-6): ").strip()

        if choice == "6":
            return

        if choice not in REPORTS:
            print("Invalid choice. Please select 1-6.")
            continue

        title, query, headers = REPORTS[choice]

        connection = connect_db(password)

        if connection is None:
            input("\nPress Enter to return to the report menu...")
            continue

        cursor = None

        try:
            cursor = connection.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()

            print_header(title)
            display_table(headers, rows)

        except oracledb.Error as error:
            print("\nUnable to generate report:", error)

        finally:
            if cursor is not None:
                cursor.close()

            connection.close()

        input("\nPress Enter to continue...")


# -------------------- MAIN MENU --------------------

def main():
    """Start and control the application."""

    print_header("WATER LEAKAGE AND LOSS ANALYZER")
    print("Python + Oracle Database")

    print("\nConnecting to Oracle...")

    password = getpass("Enter Oracle password: ")

    connection = connect_db(password)

    if connection is None:
        print("\nPlease verify your credentials and database service.")
        return

    connection.close()

    print("Database connection successful!")

   
    while True:
        print_header("MAIN MENU")

        print("1. Add Leakage Incident")
        print("2. View Analysis Reports")
        print("3. Open Visual Dashboard")
        print("4. Exit")

        choice = input("\nEnter your choice (1-4): ").strip()

        if choice == "1":
            add_incident(password)

        elif choice == "2":
            show_reports(password)

        elif choice == "3":
            try:
                show_dashboard(password)
            except Exception as error:
                print("\nUnable to open the dashboard:", error)
                input("Press Enter to return to the main menu...")

        elif choice == "4":
            print_header("APPLICATION CLOSED")
            print("Thank you for using Water Leakage and Loss Analyzer.")
            print("Exiting safely...")
            break

        else:
            print("Invalid choice. Please select 1, 2, 3, or 4.")

# -------------------- PROGRAM ENTRY POINT --------------------

if __name__ == "__main__":
    try:
        main()

    except KeyboardInterrupt:
        print("\n\nApplication interrupted. Goodbye!")
