import os
import getpass
import oracledb
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


# ============================================================
# DATABASE CONFIGURATION
# ============================================================

DB_USER = "water_user"
DB_DSN = "localhost:1521/FREEPDB1"


# ============================================================
# REPORT FOLDER
# ============================================================

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORT_FOLDER = os.path.join(PROJECT_ROOT, "reports")

os.makedirs(REPORT_FOLDER, exist_ok=True)


# ============================================================
# DATABASE CONNECTION
# ============================================================

def connect_database(password):
    try:
        connection = oracledb.connect(
            user=DB_USER,
            password=password,
            dsn=DB_DSN
        )

        print("\nDatabase connection successful.")
        return connection

    except oracledb.Error as error:
        print("\nDatabase connection failed.")
        print("Error:", error)
        return None


# ============================================================
# LOAD DATA
# ============================================================

def load_data(connection):

    query = """
        SELECT
            incident_id,
            location,
            leak_start,
            repair_time,
            duration_hours,
            loss_rate,
            water_loss,
            leak_type,
            priority
        FROM leakage_records
        ORDER BY incident_id
    """

    dataframe = pd.read_sql(
        query,
        connection
    )

    return dataframe


# ============================================================
# DISPLAY SUMMARY
# ============================================================

def display_summary(df):

    print("\n")
    print("=" * 65)
    print("             WATER LEAKAGE ANALYSIS REPORT")
    print("=" * 65)

    total_incidents = len(df)

    total_water_loss = df["WATER_LOSS"].sum()

    average_water_loss = df["WATER_LOSS"].mean()

    average_duration = df["DURATION_HOURS"].mean()

    average_loss_rate = df["LOSS_RATE"].mean()

    highest_loss = df["WATER_LOSS"].max()

    highest_loss_incident = df.loc[
        df["WATER_LOSS"].idxmax(),
        "INCIDENT_ID"
    ]

    print(f"Total incidents       : {total_incidents}")
    print(f"Total water loss      : {total_water_loss:,.2f} Liters")
    print(f"Average water loss    : {average_water_loss:,.2f} Liters")
    print(f"Average leak duration : {average_duration:.2f} Hours")
    print(f"Average loss rate     : {average_loss_rate:,.2f} L/hour")
    print(f"Highest water loss    : {highest_loss:,.2f} Liters")
    print(f"Highest-loss incident : {highest_loss_incident}")

    print("=" * 65)


# ============================================================
# GRAPH 1
# WATER LOSS BY LOCATION
# ============================================================

def graph_water_loss_by_location(df):

    location_data = (
        df.groupby("LOCATION")["WATER_LOSS"]
        .sum()
        .sort_values(ascending=False)
    )

    plt.figure(figsize=(10, 6))

    sns.barplot(
        x=location_data.values,
        y=location_data.index
    )

    plt.title(
        "Total Water Loss by Location",
        fontsize=16,
        fontweight="bold"
    )

    plt.xlabel("Water Loss (Liters)")
    plt.ylabel("Location")

    plt.tight_layout()

    filename = os.path.join(
        REPORT_FOLDER,
        "01_water_loss_by_location.png"
    )

    plt.savefig(
        filename,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

    print(f"Created: {filename}")


# ============================================================
# GRAPH 2
# WATER LOSS BY INCIDENT
# ============================================================

def graph_water_loss_by_incident(df):

    plt.figure(figsize=(11, 6))

    sns.barplot(
        data=df,
        x="INCIDENT_ID",
        y="WATER_LOSS"
    )

    plt.title(
        "Water Loss by Incident",
        fontsize=16,
        fontweight="bold"
    )

    plt.xlabel("Incident ID")
    plt.ylabel("Water Loss (Liters)")

    plt.tight_layout()

    filename = os.path.join(
        REPORT_FOLDER,
        "02_water_loss_by_incident.png"
    )

    plt.savefig(
        filename,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

    print(f"Created: {filename}")


# ============================================================
# GRAPH 3
# PRIORITY DISTRIBUTION
# ============================================================

def graph_priority_distribution(df):

    priority_counts = df["PRIORITY"].value_counts()

    plt.figure(figsize=(7, 7))

    plt.pie(
        priority_counts.values,
        labels=priority_counts.index,
        autopct="%1.1f%%",
        startangle=90
    )

    plt.title(
        "Leakage Incident Priority Distribution",
        fontsize=16,
        fontweight="bold"
    )

    plt.tight_layout()

    filename = os.path.join(
        REPORT_FOLDER,
        "03_priority_distribution.png"
    )

    plt.savefig(
        filename,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

    print(f"Created: {filename}")


# ============================================================
# GRAPH 4
# LOSS RATE VS WATER LOSS
# ============================================================

def graph_loss_rate_vs_water_loss(df):

    plt.figure(figsize=(10, 6))

    sns.scatterplot(
        data=df,
        x="LOSS_RATE",
        y="WATER_LOSS",
        s=120
    )

    plt.title(
        "Leakage Rate vs Water Loss",
        fontsize=16,
        fontweight="bold"
    )

    plt.xlabel("Leakage Rate (Liters/Hour)")
    plt.ylabel("Water Loss (Liters)")

    plt.tight_layout()

    filename = os.path.join(
        REPORT_FOLDER,
        "04_loss_rate_vs_water_loss.png"
    )

    plt.savefig(
        filename,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

    print(f"Created: {filename}")


# ============================================================
# GRAPH 5
# DURATION VS WATER LOSS
# ============================================================

def graph_duration_vs_water_loss(df):

    plt.figure(figsize=(10, 6))

    sns.scatterplot(
        data=df,
        x="DURATION_HOURS",
        y="WATER_LOSS",
        s=120
    )

    plt.title(
        "Leak Duration vs Water Loss",
        fontsize=16,
        fontweight="bold"
    )

    plt.xlabel("Leak Duration (Hours)")
    plt.ylabel("Water Loss (Liters)")

    plt.tight_layout()

    filename = os.path.join(
        REPORT_FOLDER,
        "05_duration_vs_water_loss.png"
    )

    plt.savefig(
        filename,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

    print(f"Created: {filename}")


# ============================================================
# GRAPH 6
# AVERAGE WATER LOSS BY LEAK TYPE
# ============================================================

def graph_loss_by_leak_type(df):

    leak_type_data = (
        df.groupby("LEAK_TYPE")["WATER_LOSS"]
        .mean()
        .sort_values(ascending=False)
    )

    plt.figure(figsize=(10, 6))

    sns.barplot(
        x=leak_type_data.values,
        y=leak_type_data.index
    )

    plt.title(
        "Average Water Loss by Leak Type",
        fontsize=16,
        fontweight="bold"
    )

    plt.xlabel("Average Water Loss (Liters)")
    plt.ylabel("Leak Type")

    plt.tight_layout()

    filename = os.path.join(
        REPORT_FOLDER,
        "06_average_loss_by_leak_type.png"
    )

    plt.savefig(
        filename,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

    print(f"Created: {filename}")


# ============================================================
# MAIN PROGRAM
# ============================================================

def main():

    print("=" * 65)
    print("       WATER LEAKAGE ANALYZER - PROJECT REPORT")
    print("=" * 65)

    password = getpass.getpass(
        "Enter Oracle password: "
    )

    connection = connect_database(password)

    if connection is None:
        return

    try:

        print("\nLoading leakage data...")

        df = load_data(connection)

        if df.empty:
            print("\nNo leakage records found in the database.")
            return

        print(
            f"{len(df)} leakage records loaded successfully."
        )

        # Display statistics
        display_summary(df)

        print("\nGenerating visualizations...")
        print("-" * 65)

        # Generate all graphs
        graph_water_loss_by_location(df)

        graph_water_loss_by_incident(df)

        graph_priority_distribution(df)

        graph_loss_rate_vs_water_loss(df)

        graph_duration_vs_water_loss(df)

        graph_loss_by_leak_type(df)

        print("-" * 65)

        print("\nAll visualizations generated successfully.")

        print("\nReport folder:")
        print(REPORT_FOLDER)

        print("\nFiles created:")

        print("1. 01_water_loss_by_location.png")
        print("2. 02_water_loss_by_incident.png")
        print("3. 03_priority_distribution.png")
        print("4. 04_loss_rate_vs_water_loss.png")
        print("5. 05_duration_vs_water_loss.png")
        print("6. 06_average_loss_by_leak_type.png")

        print("\nYou can insert these PNG files directly into your project report.")

    except Exception as error:

        print("\nAn error occurred while generating the report.")
        print("Error:", error)

    finally:

        connection.close()

        print("\nDatabase connection closed.")


# ============================================================
# PROGRAM START
# ============================================================

if __name__ == "__main__":
    main()