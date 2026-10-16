
import tkinter as tk
from tkinter import messagebox
import oracledb
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.ticker import FuncFormatter


DB_USER = "water_user"
DB_DSN = "localhost:1521/FREEPDB1"

# Light blue and white dashboard palette
COLORS = {
    "background": "#F3F7FC",
    "white": "#FFFFFF",
    "blue": "#2563EB",
    "blue_dark": "#173B70",
    "blue_light": "#DBEAFE",
    "text": "#172B4D",
    "muted": "#64748B",
    "grid": "#E5ECF5",
    "high": "#DC5252",
    "medium": "#E9A23B",
    "low": "#16A085",
    "unknown": "#94A3B8",
}

PRIORITY_COLORS = {
    "High": COLORS["high"],
    "Medium": COLORS["medium"],
    "Low": COLORS["low"],
    "Unknown": COLORS["unknown"],
}


def load_data(password):
    """Read existing incident data from Oracle without modifying it."""
    connection = None

    try:
        connection = oracledb.connect(
            user=DB_USER,
            password=password,
            dsn=DB_DSN
        )

        cursor = connection.cursor()
        cursor.execute("""
            SELECT incident_id, location, duration_hours,
                   loss_rate, water_loss, leak_type, priority
            FROM leakage_records
            ORDER BY incident_id
        """)

        columns = [item[0] for item in cursor.description]
        rows = cursor.fetchall()

        df = pd.DataFrame(rows, columns=columns)
        cursor.close()

        if not df.empty:
            df["LOCATION"] = (
                df["LOCATION"]
                .fillna("Unknown")
                .astype(str)
                .str.strip()
                .str.title()
            )

            df["PRIORITY"] = (
                df["PRIORITY"]
                .fillna("Unknown")
                .astype(str)
                .str.strip()
                .str.title()
            )

            for column in [
                "INCIDENT_ID", "DURATION_HOURS",
                "LOSS_RATE", "WATER_LOSS"
            ]:
                df[column] = pd.to_numeric(
                    df[column], errors="coerce"
                )

        return df

    finally:
        if connection is not None:
            connection.close()


def format_number(value):
    return f"{value:,.2f}"


def style_axis(ax, title, xlabel, ylabel):
    """Apply consistent formatting to each chart."""
    ax.set_title(
        title,
        loc="left",
        fontsize=12,
        fontweight="bold",
        color=COLORS["text"],
        pad=13
    )

    ax.set_xlabel(xlabel, fontsize=9, color=COLORS["muted"])
    ax.set_ylabel(ylabel, fontsize=9, color=COLORS["muted"])

    ax.set_facecolor(COLORS["white"])
    ax.grid(
        axis="x",
        color=COLORS["grid"],
        linewidth=0.8
    )
    ax.set_axisbelow(True)

    ax.tick_params(
        axis="both",
        labelsize=8,
        colors=COLORS["muted"]
    )

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(COLORS["grid"])
    ax.spines["bottom"].set_color(COLORS["grid"])


def show_dashboard(password):
    """Open a separate, refreshable analytics dashboard."""

    try:
        df = load_data(password)
    except Exception as error:
        messagebox.showerror(
            "Database Connection Error",
            "Unable to load Oracle data.\n\n"
            f"{error}"
        )
        return

    if df.empty:
        messagebox.showinfo(
            "No Data",
            "There are no leakage incidents to display."
        )
        return

    root = tk.Tk()
    root.title("Water Leakage & Loss Analyzer")
    root.geometry("1280x860")
    root.minsize(1050, 700)
    root.configure(bg=COLORS["background"])

    current = {"figure": None, "canvas": None}

    # ---------------- HEADER ----------------

    header = tk.Frame(root, bg=COLORS["white"])
    header.pack(fill="x")

    heading_area = tk.Frame(header, bg=COLORS["white"])
    heading_area.pack(
        side="left", fill="x", expand=True,
        padx=28, pady=19
    )

    tk.Label(
        heading_area,
        text="Water Leakage & Loss Analyzer",
        font=("Segoe UI", 21, "bold"),
        bg=COLORS["white"],
        fg=COLORS["blue_dark"]
    ).pack(anchor="w")

    tk.Label(
        heading_area,
        text="INCIDENT ANALYTICS  |  ORACLE DATABASE",
        font=("Segoe UI", 9, "bold"),
        bg=COLORS["white"],
        fg=COLORS["muted"]
    ).pack(anchor="w", pady=(5, 0))

    refresh_button = tk.Button(
        header,
        text="↻  Refresh Data",
        font=("Segoe UI", 10, "bold"),
        bg=COLORS["blue"],
        fg="white",
        activebackground=COLORS["blue_dark"],
        activeforeground="white",
        relief="flat",
        cursor="hand2",
        padx=16,
        pady=10
    )
    refresh_button.pack(side="right", padx=28, pady=22)

    # ---------------- CONTENT ----------------

    content = tk.Frame(root, bg=COLORS["background"])
    content.pack(fill="both", expand=True, padx=22, pady=18)

    metrics_frame = tk.Frame(
        content, bg=COLORS["background"]
    )
    metrics_frame.pack(fill="x", pady=(0, 16))

    chart_frame = tk.Frame(
        content,
        bg=COLORS["white"],
        highlightbackground="#E1E9F3",
        highlightthickness=1
    )
    chart_frame.pack(fill="both", expand=True)

    footer = tk.Label(
        root,
        text="Source: Oracle FREEPDB1  •  Charts use stored incident records",
        font=("Segoe UI", 9),
        bg=COLORS["background"],
        fg=COLORS["muted"],
        pady=8
    )
    footer.pack(fill="x")

    def render_dashboard(data):
        # Remove the previous cards and charts on refresh.
        for widget in metrics_frame.winfo_children():
            widget.destroy()

        for widget in chart_frame.winfo_children():
            widget.destroy()

        if current["figure"] is not None:
            plt.close(current["figure"])

        total_incidents = len(data)
        total_loss = data["WATER_LOSS"].fillna(0).sum()
        avg_duration = data["DURATION_HOURS"].mean()
        high_count = int((data["PRIORITY"] == "High").sum())

        avg_text = (
            f"{avg_duration:.2f} hrs"
            if pd.notna(avg_duration) else "N/A"
        )

        metrics = [
            ("TOTAL INCIDENTS", f"{total_incidents}", COLORS["blue"]),
            ("TOTAL WATER LOSS", f"{total_loss:,.2f} L", "#087EAA"),
            ("AVERAGE DURATION", avg_text, "#5267C9"),
            ("HIGH PRIORITY", f"{high_count}", COLORS["high"]),
        ]

        # ---------------- SUMMARY CARDS ----------------

        for title, value, accent in metrics:
            card = tk.Frame(
                metrics_frame,
                bg=COLORS["white"],
                highlightbackground="#E1E9F3",
                highlightthickness=1
            )
            card.pack(
                side="left", fill="both", expand=True,
                padx=(0, 10)
            )

            tk.Frame(
                card, bg=accent, height=4
            ).pack(fill="x")

            tk.Label(
                card,
                text=title,
                font=("Segoe UI", 9, "bold"),
                bg=COLORS["white"],
                fg=COLORS["muted"]
            ).pack(anchor="w", padx=15, pady=(13, 5))

            tk.Label(
                card,
                text=value,
                font=("Segoe UI", 17, "bold"),
                bg=COLORS["white"],
                fg=COLORS["text"],
                wraplength=240
            ).pack(anchor="w", padx=15, pady=(0, 14))

        # ---------------- CHARTS ----------------

        fig = Figure(
            figsize=(12, 7.0),
            dpi=100,
            facecolor=COLORS["white"]
        )

        ax1, ax2, ax3, ax4 = fig.subplots(2, 2).flatten()

        fig.subplots_adjust(
            left=0.10, right=0.97,
            top=0.93, bottom=0.11,
            wspace=0.30, hspace=0.42
        )

        number_formatter = FuncFormatter(
            lambda value, position: f"{value:,.0f}"
        )

        # Chart 1: Total loss by location.
        location_loss = (
            data.groupby("LOCATION")["WATER_LOSS"]
            .sum()
            .dropna()
            .sort_values(ascending=True)
        )

        if not location_loss.empty:
            ax1.barh(
                location_loss.index,
                location_loss.values,
                color=COLORS["blue"],
                height=0.62
            )

            # A symmetric-log scale preserves the real values
            # while making smaller locations visible beside outliers.
            if (
                location_loss.max() > 0
                and location_loss.max()
                / max(location_loss[location_loss > 0].min(), 1)
                >= 100
            ):
                ax1.set_xscale("symlog", linthresh=100)
                ax1.text(
                    0.99, 0.02,
                    "Symlog scale; values remain in litres",
                    transform=ax1.transAxes,
                    ha="right", va="bottom",
                    fontsize=7, color=COLORS["muted"]
                )
            else:
                ax1.xaxis.set_major_formatter(number_formatter)

            style_axis(
                ax1, "Water Loss by Location",
                "Total water loss (litres)", ""
            )
        else:
            ax1.text(
                0.5, 0.5, "No water-loss data",
                ha="center", va="center"
            )
            style_axis(ax1, "Water Loss by Location", "", "")

        # Chart 2: Priority distribution.
        priority_counts = (
            data["PRIORITY"]
            .value_counts()
            .reindex(["High", "Medium", "Low", "Unknown"], fill_value=0)
        )
        priority_counts = priority_counts[priority_counts > 0]

        if not priority_counts.empty:
            pie_colors = [
                PRIORITY_COLORS.get(label, COLORS["unknown"])
                for label in priority_counts.index
            ]

            wedges, _ = ax2.pie(
                priority_counts.values,
                colors=pie_colors,
                startangle=90,
                counterclock=False,
                wedgeprops={"width": 0.36, "edgecolor": "white"}
            )

            ax2.text(
                0, 0.08, str(int(priority_counts.sum())),
                ha="center", va="center",
                fontsize=22, fontweight="bold",
                color=COLORS["text"]
            )
            ax2.text(
                0, -0.16, "INCIDENTS",
                ha="center", va="center",
                fontsize=8, color=COLORS["muted"]
            )

            ax2.legend(
                wedges,
                [
                    f"{label}  ·  {count} "
                    f"({count / priority_counts.sum():.0%})"
                    for label, count in priority_counts.items()
                ],
                loc="lower center",
                bbox_to_anchor=(0.5, -0.08),
                ncol=2,
                frameon=False,
                fontsize=8
            )

        ax2.set_title(
            "Incident Priority Distribution",
            loc="left", fontsize=12,
            fontweight="bold", color=COLORS["text"],
            pad=13
        )
        ax2.set_aspect("equal")

        # Chart 3: Duration versus water loss.
        scatter_data = data.dropna(
            subset=["DURATION_HOURS", "WATER_LOSS"]
        )

        for priority, color in PRIORITY_COLORS.items():
            group = scatter_data[
                scatter_data["PRIORITY"] == priority
            ]
            if not group.empty:
                ax3.scatter(
                    group["DURATION_HOURS"],
                    group["WATER_LOSS"],
                    s=65,
                    color=color,
                    label=priority,
                    alpha=0.85,
                    edgecolors="white",
                    linewidths=0.7
                )

        if not scatter_data.empty:
            positive_losses = scatter_data["WATER_LOSS"].dropna()

            if (positive_losses > 0).all() and (
                positive_losses.max()
                / max(positive_losses.min(), 1)
                >= 100
            ):
                ax3.set_yscale("log")
                ax3.text(
                    0.99, 0.02,
                    "Log scale on vertical axis",
                    transform=ax3.transAxes,
                    ha="right", va="bottom",
                    fontsize=7, color=COLORS["muted"]
                )

            ax3.yaxis.set_major_formatter(number_formatter)
            ax3.legend(
                frameon=False, fontsize=8,
                loc="best", title="Priority",
                title_fontsize=8
            )

        style_axis(
            ax3, "Leak Duration vs Water Loss",
            "Duration (hours)", "Water loss (litres)"
        )

        # Chart 4: Individual incidents.
        incident_data = (
            data.dropna(subset=["WATER_LOSS"])
            .sort_values("WATER_LOSS", ascending=True)
        )

        if not incident_data.empty:
            bar_colors = [
                PRIORITY_COLORS.get(p, COLORS["unknown"])
                for p in incident_data["PRIORITY"]
            ]

            ax4.barh(
                incident_data["INCIDENT_ID"].map(
                    lambda value: f"Incident {int(value)}"
                    if pd.notna(value) else "Unknown"
                ),
                incident_data["WATER_LOSS"],
                color=bar_colors,
                height=0.62
            )

            loss_values = incident_data["WATER_LOSS"]
            positive = loss_values[loss_values > 0]

            if (
                not positive.empty
                and loss_values.max() / max(positive.min(), 1) >= 100
            ):
                ax4.set_xscale("symlog", linthresh=100)
                ax4.text(
                    0.99, 0.02,
                    "Symlog scale; values remain in litres",
                    transform=ax4.transAxes,
                    ha="right", va="bottom",
                    fontsize=7, color=COLORS["muted"]
                )
            else:
                ax4.xaxis.set_major_formatter(number_formatter)

        style_axis(
            ax4, "Water Loss by Incident",
            "Water loss (litres)", ""
        )

        canvas = FigureCanvasTkAgg(fig, master=chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(
            fill="both", expand=True, padx=12, pady=10
        )

        current["figure"] = fig
        current["canvas"] = canvas

        footer.config(
            text=(
                f"Oracle FREEPDB1  •  {len(data)} records loaded  •  "
                "Refresh to reload the latest saved data"
            )
        )

    def refresh():
        refresh_button.config(state="disabled", text="Loading...")
        root.update_idletasks()

        try:
            updated_data = load_data(password)

            if updated_data.empty:
                messagebox.showinfo(
                    "No Data",
                    "No leakage records were found.",
                    parent=root
                )
                return

            render_dashboard(updated_data)

        except Exception as error:
            messagebox.showerror(
                "Refresh Failed",
                f"Could not refresh Oracle data.\n\n{error}",
                parent=root
            )
        finally:
            refresh_button.config(
                state="normal", text="↻  Refresh Data"
            )

    refresh_button.config(command=refresh)

    render_dashboard(df)
    root.mainloop()
