from pathlib import Path

import pandas as pd
from pandas import Series
from scipy.signal import savgol_filter

from docs.static.strength.get_data import get_strength_data


def generate_svg_plot(df: pd.DataFrame, y_col: str) -> str:
    padding = 1
    svg_width_px = 1050
    svg_height_px = 450

    def normalize(s: Series) -> Series:
        if s.max() > s.min():
            normalized: Series = padding + (s - s.min()) / (s.max() - s.min()) * (
                100 - 2 * padding
            )
            return normalized
        return pd.Series([50.0] * len(s))

    # Normalise the data for plotting
    x_pct = normalize(df["week"])
    y_pct = normalize(df[y_col])

    # Generate dots for the plot
    svg_points = ""
    for i in range(len(df)):
        row = df.iloc[i]
        xi = x_pct.iloc[i]
        yi = y_pct.iloc[i]

        if pd.isna(xi) or pd.isna(yi):
            continue

        date_str = pd.to_datetime(row["date"]).strftime("%Y-%m-%d")
        tooltip = f"Date: {date_str}\nWeek: {row['week']}\n{y_col}: {row[y_col]}"
        svg_points += f'<circle class="dot" cx="{xi}%" cy="{100 - yi}%" r="3"><title>{tooltip}</title></circle>\n'

    # Generate average line (Savitzky–Golay filter)
    valid_mask = ~(x_pct.isna() | y_pct.isna())
    x_pixels = x_pct[valid_mask].to_numpy() / 100 * svg_width_px
    y_pixels = (100 - y_pct[valid_mask].to_numpy()) / 100 * svg_height_px
    y_smooth = savgol_filter(y_pixels, window_length=10, polyorder=2)
    polyline_points = " ".join(
        f"{x_pixels[i]},{y_smooth[i]}" for i in range(len(x_pixels))
    )
    svg_polyline = (
        f'<polyline class="line_avg" fill="none" points="{polyline_points}" />\n'
    )

    svg = f'<svg viewBox="0 0 {svg_width_px} {svg_height_px}" >\n'
    svg += svg_points
    svg += svg_polyline
    svg += "</svg>"

    return svg


if __name__ == "__main__":
    df = get_strength_data()
    total_orm = generate_svg_plot(df, y_col="total_orm")
    bench_orm = generate_svg_plot(df, y_col="bench_orm")
    deadlift_orm = generate_svg_plot(df, y_col="deadlift_orm")
    squat_orm = generate_svg_plot(df, y_col="squat_orm")
    weight = generate_svg_plot(df, y_col="weight")

    html_content = (
        """
    <!DOCTYPE html>
    <html>
      <head>
        <title>Strength stats</title>
        <link rel="icon" href="../graphics/icon.png" type="image/x-icon">
        <meta charset="UTF-8">
        <link rel="stylesheet" href="../styles/fonts.css">
        <link rel="stylesheet" href="../styles/transitions.css">
        <link rel="stylesheet" href="../styles/global.css">
        <link rel="stylesheet" href="strength.css">
        <script type="text/javascript" src="../scripts/global.js"></script>
      </head>
      <body id="strength_body">
        <audio id="hover" src="../sounds/hover.wav"></audio>
        <audio id="click" src="../sounds/click.wav"></audio>

        <div class="transition transition-1 is-active"></div>
        <div id="home"><img src="../graphics/home.svg"
        onmouseenter="handleHover()" onmousedown='clickWaitGo(event, "/")'></div>

        <div id="strength_content">

            <p class="big-font">My weightlifting adventure</p>
            <br><br><br><br>
            <p>ORM total lift over time (hover for details)</p>
            """
        + total_orm
        + f"""

            <div class="stats">
                <div class="stat">
                    <p>Lifting for</p>
                    <p id="daysCounter" class="big-font">69 days</p>
                </div>
                <div class="stat">
                    <p>Max total</p>
                    <p class="big-font">{round(df['deadlift'].max() + df['squat'].max() + df['bench'].max(), 1)} kg</p>
                </div>
                <div class="stat">
                    <p>Body-weight</p>
                    <p class="big-font">{round(df["weight"].dropna().iloc[-1], 1)} kg</p>
                </div>
                <div class="stat">
                    <p>Attendance (last 45days)</p>
                    <p class="big-font">{round(df["attendance_last_45d"].iloc[-1], 2)} %</p>
                </div>
                <div class="stat">
                    <p>Max estimated total</p>
                    <p class="big-font">{round(df['total_orm'].max(), 1)} kg</p>
                </div>
            </div>
            <br><br><br><br>
            <p>Deadlift progress - max estimated from set (hover for details)</p>
            """
        + deadlift_orm
        + f"""

            <div class="stats">
                <div class="stat">
                    <p>Max deadlift 1RM</p>
                    <p class="big-font">{round(df["deadlift"].max(), 1)} kg</p>
                </div>
                <div class="stat">
                    <p>Max estimated deadlift</p>
                    <p class="big-font">{round(df["deadlift_orm"].max(), 1)} kg</p>
                </div>
                <div class="stat">
                    <p>Max est. lift/BW</p>
                    <p class="big-font">{round(df["deadlift_rel"].max(), 2)}</p>
                </div>
            </div>

            <br><br><br><br>
            <p>Squat progress - max estimated from set (hover for details)</p>
            """
        + squat_orm
        + f"""

            <div class="stats">
                <div class="stat">
                    <p>Max squat 1RM</p>
                    <p class="big-font">{round(df["squat"].max(), 1)} kg</p>
                </div>
                <div class="stat">
                    <p>Max estimated squat</p>
                    <p class="big-font">{round(df["squat_orm"].max(), 1)} kg</p>
                </div>
                <div class="stat">
                    <p>Max est. lift/BW</p>
                    <p class="big-font">{round(df["squat_rel"].max(), 2)}</p>
                </div>
            </div>

            <br><br><br><br>
            <p>Bench progress - max estimated from set (hover for details)</p>
            """
        + bench_orm
        + f"""

            <div class="stats">
                <div class="stat">
                    <p>Max bench 1RM</p>
                    <p class="big-font">{round(df["bench"].max(), 1)} kg</p>
                </div>
                <div class="stat">
                    <p>Max bench squat</p>
                    <p class="big-font">{round(df["bench_orm"].max(), 1)} kg</p>
                </div>
                <div class="stat">
                    <p>Max est. lift/BW</p>
                    <p class="big-font">{round(df["bench_rel"].max(), 2)}</p>
                </div>
            </div>

            <p>Body-weight timeline</p>
            """
        + weight
        + f"""

             <div class="stats">
                <div class="stat">
                    <p>Max weight</p>
                    <p class="big-font">{round(df["weight"].max(), 1)} kg</p>
                </div>
                <div class="stat">
                    <p>Avg weight</p>
                    <p class="big-font">{round(df["weight"].mean(), 1)} kg</p>
                </div>
                <div class="stat">
                    <p>Min weight</p>
                    <p class="big-font">{round(df["weight"].min(), 1)} kg</p>
                </div>
            </div>

            <br><br><br><br>
            <p>*The formula used to calculate one rep max is a Landers formula (1985):
                ( 100 * Weight ) / ( 101.3 - ( 2.67123 * repetitions ) ).</p>

            <p>The average line is generated by applying a Savitzky–Golay filter (10 points window).</p>

            <div style="height: 30vh;"></div>

        </div>

      <script type="text/javascript" src="plot.js"></script>

      <script type="text/javascript" src="../scripts/transition.js"></script>
      </body>

    </html>
    """
    )
    html_path = Path(__file__).parent / "strength.html"
    with open(html_path, "w") as file:
        file.write(html_content)


# TODO
#             <p>The fitting equation employed is given by: <span style="color:var(--dark-scarlet);">((a - d) / ((1 +
#             ((x / c) ** b)) ** e)) + d + f * x </span>
#             I took the liberty of adding the linear function to the equation, which resulted in a slight improvement.
#             The grayed-out points are not considered in the fit calculation.</p>
