import sys
import traceback
from datetime import date
from warnings import warn

import pyexcel as pe
import numpy as np
import requests
from scipy.optimize import curve_fit


def process_data_file(filename,
                      dot_class: str,
                      dot_ignore_class: str,
                      excluded_indices_total: set[int],
                      excluded_indices_bench: set[int],
                      excluded_indices_deadlift: set[int],
                      excluded_indices_squat: set[int]):
    np.set_printoptions(threshold=sys.maxsize)
    graph_offset = 2

    print("Reading ods file")

    def read_ods_file():
        book = pe.get_book(file_name=filename)
        sheet = book[sheet_name_data]
        data = sheet.to_array()
        numpy_array = np.array(data)
        return numpy_array

    sheet_name_data = "data_desu"
    sheet_name_stats = "stats"
    table_data = read_ods_file()

    stats_book = pe.get_book(file_name=filename)
    stats_sheet = stats_book[sheet_name_stats]
    stats_data = stats_sheet.to_array()

    max_bench_value = stats_data[1][0]
    max_deadlift_value = stats_data[1][1]
    max_squat_value = stats_data[1][2]
    max_bench_c_value = stats_data[1][3]
    max_deadlift_c_value = stats_data[1][4]
    max_squat_c_value = stats_data[1][5]
    max_bench_m_value = stats_data[1][6]
    max_deadlift_m_value = stats_data[1][7]
    max_squat_m_value = stats_data[1][8]
    max_total_value = stats_data[1][9]
    max_total_c_value = stats_data[1][10]

    # FIT_INV_EXPONENT__________________________________________________________________________________________________

    # get values closest to today_______________________________________________________________________________________
    target_date = date.today()

    print("Finding values")

    def nearest(items, pivot):
        pivot = pivot.toordinal()
        return min([i for i in items if isinstance(i, date) and i.toordinal() <= pivot],
                   key=lambda x: abs((x.toordinal() - pivot)))

    closest_row = nearest(table_data[1:, 0], target_date)
    index = np.where(table_data[:, 0] == closest_row)[0][0]
    current_week = table_data[index, 1]

    attendance_total_value = float(table_data[index, -1])
    try:
        weight_value = float(table_data[index, -4])
    except ValueError:
        if filename == "data.ods":
            warn(f"Weight not found in {filename}")
        else:
            print(f"No weight data in {filename}")
        weight_value = 0

    print("Generating points")

    # generate points for graphs____________________________________________________________________________________
    # MAIN______________________________________________________________________________________________________________
    weeks_and_totals = [
        (int(row[1]), float(row[15]), float(row[16]))
        for row in table_data[1:]
        if row[1] != '' and row[15] != '' and float(row[15]) != 0 and row[16] != '' and float(row[16]) != 0
    ]

    # Finding the smallest and largest week and week_total values individually
    min_week = min(weeks_and_totals, key=lambda x: x[0])[0]
    min_week_total = min(weeks_and_totals, key=lambda x: x[1])[1]
    min_week_total_m = min(weeks_and_totals, key=lambda x: x[2])[2]

    max_week = max(weeks_and_totals, key=lambda x: x[0])[0]
    max_week_total = max(weeks_and_totals, key=lambda x: x[1])[1]
    max_week_total_m = max(weeks_and_totals, key=lambda x: x[2])[2]

    power_lvl_points = ""
    x_data_total = np.array([])
    y_data_total = np.array([])

    for idx, row in enumerate(table_data[1:], start=1):
        week, week_total, week_total_m = row[1], row[15], row[16]

        if week == '' or week_total == '' or float(week_total) == 0 or week_total_m == '' or float(week_total_m) == 0:
            continue

        week = int(week)
        week_total = float(week_total)
        week_total_m = float(week_total_m)

        percentage_week = (week - min_week) / (max_week - min_week) * 100
        percentage_week_total = (week_total - min_week_total) / (max_week_total - min_week_total) * 100
        percentage_week_total_m = (week_total_m - min_week_total_m) / (max_week_total_m - min_week_total_m) * 100

        formatted_text = f"""Date: {row[0]}
        Week: {row[1]}
        Bench: {row[2]:.1f} {row[3]:.0f} rep est: {row[4]:.1f} bw: {row[5]:.2f}
        Deadlift: {row[6]:.1f} {row[7]:.0f} rep est: {row[8]:.1f} bw: {row[9]:.2f}
        Squat: {row[10]:.1f} {row[11]:.0f} rep est: {row[12]:.1f} bw: {row[13]:.2f}
        BW: {row[14]:.1f} kg
        Total-est: {row[15]:.1f} bw. {row[16]:.2f}
        """

        # Check if the current index is not in the excluded set
        if idx not in excluded_indices_total:
            x_data_total = np.append(x_data_total, graph_offset + (percentage_week / 100) * (100 - 2 * graph_offset))
            y_data_total = np.append(y_data_total,
                                     graph_offset + (percentage_week_total / 100) * (100 - 2 * graph_offset))
            power_lvl_points += \
                (
                    f'<circle class="{dot_class}" cx="{graph_offset + (percentage_week / 100) * (100 - 2 * graph_offset)}%" '
                    f'cy="{graph_offset + ((100 - percentage_week_total_m) / 100) * (100 - 2 * graph_offset)}%">'
                    f'<title>{formatted_text}</title></circle>\n')
        else:
            power_lvl_points += \
                (
                    f'<circle class="{dot_ignore_class}" cx="{graph_offset + (percentage_week / 100) * (100 - 2 * graph_offset)}%" '
                    f'cy="{graph_offset + ((100 - percentage_week_total_m) / 100) * (100 - 2 * graph_offset)}%">'
                    f'<title>{formatted_text}</title></circle>\n')

    # BENCH_____________________________________________________________________________________________________________
    week_and_bench_c_values = [
        (int(row[1]), float(row[4]))
        for row in table_data[1:]
        if row[1] != '' and row[4] != '' and row[4] is not None and float(row[4]) != 0
    ]

    min_week = min(week_and_bench_c_values, key=lambda x: x[0])[0]
    max_week = max(week_and_bench_c_values, key=lambda x: x[0])[0]
    min_bench_c = min(week_and_bench_c_values, key=lambda x: x[1])[1]
    max_bench_c = max(week_and_bench_c_values, key=lambda x: x[1])[1]

    power_lvl_points_bench_c = ""
    x_data_bench_c = np.array([])
    y_data_bench_c = np.array([])

    for idx, row in enumerate(table_data[1:], start=1):
        week, bench_c = row[1], row[4]

        if week == '' or bench_c == '' or bench_c is None or float(bench_c) == 0:
            continue

        week = int(week)

        try:
            bench_c = float(bench_c)
        except ValueError:
            continue

        percentage_week = (week - min_week) / (max_week - min_week) * 100
        percentage_bench_c = (bench_c - min_bench_c) / (max_bench_c - min_bench_c) * 100

        formatted_text_bench_c = f"""Date: {row[0]}
        Week: {row[1]}
        Bench estimated: {row[4]:.2f} kg
        BW ratio: {row[5]:.2f} : {row[3]:.0f} rep(s) at {row[2]:.1f} kg
        """
        if idx not in excluded_indices_bench:
            x_data_bench_c = np.append(x_data_bench_c,
                                       graph_offset + (percentage_week / 100) * (100 - 2 * graph_offset))
            y_data_bench_c = np.append(y_data_bench_c,
                                       graph_offset + (percentage_bench_c / 100) * (100 - 2 * graph_offset))
            power_lvl_points_bench_c += \
                (
                    f'<circle class="{dot_class}" cx="{graph_offset + (percentage_week / 100) * (100 - 2 * graph_offset)}%" '
                    f'cy="{graph_offset + ((100 - percentage_bench_c) / 100) * (100 - 2 * graph_offset)}%">'
                    f'<title>{formatted_text_bench_c}</title></circle>\n')
        else:
            power_lvl_points_bench_c += \
                (
                    f'<circle class="{dot_ignore_class}" cx="{graph_offset + (percentage_week / 100) * (100 - 2 * graph_offset)}%" '
                    f'cy="{graph_offset + ((100 - percentage_bench_c) / 100) * (100 - 2 * graph_offset)}%">'
                    f'<title>{formatted_text_bench_c}</title></circle>\n')

    # DEADLIFT__________________________________________________________________________________________________________
    week_and_deadlift_c_values = [
        (int(row[1]), float(row[8]))
        for row in table_data[1:]
        if row[1] != '' and row[8] != '' and row[8] is not None and float(row[8]) != 0
    ]

    min_week = min(week_and_deadlift_c_values, key=lambda x: x[0])[0]
    max_week = max(week_and_deadlift_c_values, key=lambda x: x[0])[0]
    min_deadlift_c = min(week_and_deadlift_c_values, key=lambda x: x[1])[1]
    max_deadlift_c = max(week_and_deadlift_c_values, key=lambda x: x[1])[1]

    power_lvl_points_deadlift_c = ""
    x_data_deadlift_c = np.array([])
    y_data_deadlift_c = np.array([])

    for idx, row in enumerate(table_data[1:], start=1):
        week, deadlift_c = row[1], row[8]

        if week == '' or deadlift_c == '' or deadlift_c is None or float(deadlift_c) == 0:
            continue

        week = int(week)

        try:
            deadlift_c = float(deadlift_c)
        except ValueError:
            continue

        percentage_week = (week - min_week) / (max_week - min_week) * 100
        percentage_deadlift_c = (deadlift_c - min_deadlift_c) / (max_deadlift_c - min_deadlift_c) * 100

        formatted_text_deadlift_c = f"""Date: {row[0]}
        Week: {row[1]}
        Deadlift estimated: {row[8]:.2f} kg
        BW ratio: {row[9]:.2f} : {row[7]:.0f} rep(s) at {row[6]:.1f} kg
        """
        if idx not in excluded_indices_deadlift:
            x_data_deadlift_c = np.append(x_data_deadlift_c,
                                          graph_offset + (percentage_week / 100) * (100 - 2 * graph_offset))
            y_data_deadlift_c = np.append(y_data_deadlift_c,
                                          graph_offset + (percentage_deadlift_c / 100) * (100 - 2 * graph_offset))
            power_lvl_points_deadlift_c += \
                (
                    f'<circle class="{dot_class}" cx="{graph_offset + (percentage_week / 100) * (100 - 2 * graph_offset)}%" '
                    f'cy="{graph_offset + ((100 - percentage_deadlift_c) / 100) * (100 - 2 * graph_offset)}%">'
                    f'<title>{formatted_text_deadlift_c}</title></circle>\n')
        else:
            power_lvl_points_deadlift_c += \
                (
                    f'<circle class="{dot_ignore_class}" cx="{graph_offset + (percentage_week / 100) * (100 - 2 * graph_offset)}%" '
                    f'cy="{graph_offset + ((100 - percentage_deadlift_c) / 100) * (100 - 2 * graph_offset)}%">'
                    f'<title>{formatted_text_deadlift_c}</title></circle>\n')

    # SQUAT_____________________________________________________________________________________________________________
    week_and_squat_c_values = [
        (int(row[1]), float(row[13]))
        for row in table_data[1:]
        if row[1] != '' and row[13] != '' and row[13] is not None and float(row[13]) != 0
    ]

    min_week = min(week_and_squat_c_values, key=lambda x: x[0])[0]
    max_week = max(week_and_squat_c_values, key=lambda x: x[0])[0]
    min_squat_c = min(week_and_squat_c_values, key=lambda x: x[1])[1]
    max_squat_c = max(week_and_squat_c_values, key=lambda x: x[1])[1]

    power_lvl_points_squat_c = ""
    x_data_squat_c = np.array([])
    y_data_squat_c = np.array([])

    for idx, row in enumerate(table_data[1:], start=1):
        week, squat_c = row[1], row[13]

        if week == '' or squat_c == '' or squat_c is None or float(squat_c) == 0:
            continue

        week = int(week)

        try:
            squat_c = float(squat_c)
        except ValueError:
            continue

        percentage_week = (week - min_week) / (max_week - min_week) * 100
        percentage_squat_c = (squat_c - min_squat_c) / (max_squat_c - min_squat_c) * 100

        formatted_text_squat_c = f"""Date: {row[0]}
        Week: {row[1]}
        Squat estimated: {row[12]:.2f} kg
        BW ratio: {row[13]:.2f} : {row[11]:.0f} rep(s) at {row[10]:.1f} kg
        """
        if idx not in excluded_indices_squat:
            x_data_squat_c = np.append(x_data_squat_c,
                                       graph_offset + (percentage_week / 100) * (100 - 2 * graph_offset))
            y_data_squat_c = np.append(y_data_squat_c,
                                       graph_offset + ((percentage_squat_c) / 100) * (100 - 2 * graph_offset))
            power_lvl_points_squat_c += (f'<circle class=' + dot_class + ''
                                                                         f' cx="{graph_offset + (percentage_week / 100) * (100 - 2 * graph_offset)}%"'
                                                                         f' cy="{graph_offset + ((100 - percentage_squat_c) / 100) *
                                                                                 (100 - 2 * graph_offset)}%"><title>{formatted_text_squat_c}</title>'
                                                                         f'</circle>\n')
        else:
            power_lvl_points_squat_c += (f'<circle class=' + dot_ignore_class + ''
                                                                                f' cx="{graph_offset + (percentage_week / 100) * (100 - 2 * graph_offset)}%"'
                                                                                f' cy="{graph_offset + ((100 - percentage_squat_c) / 100) *
                                                                                        (100 - 2 * graph_offset)}%"><title>{formatted_text_squat_c}</title>'
                                                                                f'</circle>\n')

    # WEIGHT________________________________________________________________________________________________________________
    week_and_weight_values = [
        (int(row[1]), float(row[14]))
        for row in table_data[1:]
        if row[1] != '' and row[14] != '' and row[14] is not None and float(row[14]) != 0
    ]

    min_week = min(week_and_weight_values, key=lambda x: x[0])[0]
    max_week = max(week_and_weight_values, key=lambda x: x[0])[0]
    min_weight = min(week_and_weight_values, key=lambda x: x[1])[1]
    max_weight = max(week_and_weight_values, key=lambda x: x[1])[1]

    power_lvl_points_weight = ""
    for row in table_data[1:]:
        week, weight = row[1], row[14]

        if week == '' or weight == '' or weight is None or float(weight) == 0:
            continue

        week = int(week)

        try:
            weight = float(weight)
        except ValueError:
            continue

        percentage_week = (week - min_week) / (max_week - min_week) * 100
        percentage_weight = (weight - min_weight) / (max_weight - min_weight) * 100

        formatted_text_weight = f"""Date: {row[0]}
        Weight: {row[14]} kg
        """

        power_lvl_points_weight += (f'<circle class=' + dot_class + ' '
                                                                    f'cx="{graph_offset + (percentage_week / 100) * (100 - 2 * graph_offset)}%" '
                                                                    f'cy="{graph_offset + ((100 - percentage_weight) / 100) *
                                                                           (100 - 2 * graph_offset)}%"><title>{formatted_text_weight}</title>'
                                                                    f'</circle>\n')

    return {
        "x_data_total": x_data_total,
        "y_data_total": y_data_total,
        "power_lvl_points": power_lvl_points,
        "max_total_value": max_total_value,
        "weight_value": weight_value,
        "attendance_total_value": attendance_total_value,
        "max_total_c_value": max_total_c_value,
        "x_data_deadlift_c": x_data_deadlift_c,
        "y_data_deadlift_c": y_data_deadlift_c,
        "power_lvl_points_deadlift_c": power_lvl_points_deadlift_c,
        "max_deadlift_value": max_deadlift_value,
        "max_deadlift_c_value": max_deadlift_c_value,
        "max_deadlift_m_value": max_deadlift_m_value,
        "x_data_squat_c": x_data_squat_c,
        "y_data_squat_c": y_data_squat_c,
        "power_lvl_points_squat_c": power_lvl_points_squat_c,
        "max_squat_value": max_squat_value,
        "max_squat_c_value": max_squat_c_value,
        "max_squat_m_value": max_squat_m_value,
        "x_data_bench_c": x_data_bench_c,
        "y_data_bench_c": y_data_bench_c,
        "power_lvl_points_bench_c": power_lvl_points_bench_c,
        "max_bench_value": max_bench_value,
        "max_bench_c_value": max_bench_c_value,
        "max_bench_m_value": max_bench_m_value,
        "power_lvl_points_weight": power_lvl_points_weight,
        "current_week": current_week,
    }


def fivepl_with_benefits(x, a, b, c, d, e, f):
    return ((a - d) / ((1 + ((x / c) ** b)) ** e)) + d + f * x


def fit_inv_exp(x_data, y_data):
    print("Fitting the line")
    params, covariance = curve_fit(fivepl_with_benefits, x_data, y_data, maxfev=10000000)
    a_fit, b_fit, c_fit, d_fit, e_fit, f_fit = params

    x_fit = np.linspace(min(x_data), max(x_data), 60)
    # y_fit = inverted_exponential(x_fit, a_fit, b_fit, c_fit)
    y_fit = fivepl_with_benefits(x_fit, a_fit, b_fit, c_fit, d_fit, e_fit, f_fit)

    print(f"Fitted parameters: a = {a_fit}, b = {b_fit}, c = {c_fit}, d = {d_fit}, e = {e_fit}, f = {f_fit}")
    return x_fit, y_fit


def svg_html_line(x_data, y_data):
    x_fit, y_fit = fit_inv_exp(x_data, y_data)
    y_fit = [100 - y for y in y_fit]

    lines = ''
    for i in range(len(x_fit) - 1):
        x1, y1 = x_fit[i], y_fit[i]
        x2, y2 = x_fit[i + 1], y_fit[i + 1]
        lines += f'<line class="line_avg" x1="{x1}%" y1="{y1}%" x2="{x2}%" y2="{y2}%"> </line>\n'

    return lines


def svg_event_line(event_week, current_week, text):
    """Generates SVG markup for a vertical line and text representing an event at a specific week

    :param event_week: The week number of the event.
    :param current_week: The current week number, representing the end of the graph's time scale.
    :param text: The text content to display next to the line.
    :return: SVG markup string for the event line and text.
    """
    # Calculate the percentage position of the event on the x-axis.
    percentage_position = (float(event_week) / current_week) * 100

    # Define the SVG line element with a stroke-width of 20px.
    line_element = f'<line x1="{percentage_position}%" y1="0%" x2="{percentage_position}%" y2="100%" style="stroke:var(--dark-scarlet);stroke-width:3px" />\n'

    background_rect = f'<rect x="{float(percentage_position) - 5}%" y="95%" width="10%" height="5%" fill="black" />\n'
    text_element = f'<text x="{percentage_position}%" y="98%" text-anchor="middle" style="font-size: 12px; font-family: ImpactuDesu; fill: var(--egg-white);">{text}</text>\n'

    # Combine the line and text elements into a single SVG markup string.
    svg_markup = line_element + background_rect + text_element

    return svg_markup


def download_file(url, local_filename):
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    return local_filename


if __name__ == "__main__":
    # get my data
    my_data = process_data_file("data.ods",
                                "dot",
                                "dot_ignore",
                                excluded_indices_total={14, 15, 29, 69, 73, 74, 75},
                                excluded_indices_bench={29},
                                excluded_indices_deadlift={15, 29, 30, 117},
                                excluded_indices_squat={14, 15, 27, 29, 69, 73, 74, 75, 115}
                                )

    dieta_line = svg_event_line(66, my_data["current_week"], "CUTTING")
    suplements = svg_event_line(74, my_data["current_week"], "SUPPLEMENTS")
    milestones = dieta_line + suplements

    # # get baczek data
    # baczek_site = "https://baczek.me/fit.ods"
    # local_file_name = "fit.ods"
    # try:
    #     pass # download_file(baczek_site, local_file_name)
    # except requests.exceptions.RequestException as e:
    #     print(f"Failed to download the file: {e}")
    # except Exception as e:
    #     print(f"An unexpected error occurred during the download: {e}")
    # else:
    #     try:
    #         baczek_data = process_data_file(local_file_name,
    #                                         "dot_baczek",
    #                                         "dot_ignore_baczek",
    #                                         {0},
    #                                         {0},
    #                                         {0},
    #                                         {0})
    #     except FileNotFoundError as e:
    #         print(f"Bączek się opierdala: File not found: {e}\nTraceback: {traceback.format_exc()}")
    #     except ValueError as e:
    #         print(f"Bączek się opierdala: Value error during processing: {e}\nTraceback: {traceback.format_exc()}")
    #     except Exception as e:
    #         print(
    #             f"Bączek się opierdala: An unexpected error occurred during processing: {e}\nTraceback: {traceback.format_exc()}")
    #
    # # TODO: add Baczek failsafe to include the dots

    html_content = (f"""
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
            <p>Total lift normalised by bodyweight over time (hover for details)</p>
            <svg id="strength_stats" >
                """ + milestones + svg_html_line(my_data["x_data_total"], my_data["y_data_total"]) + ' ' +
                    my_data["power_lvl_points"] + f"""
            </svg>

            <div class="stats">
                <div class="stat">
                    <p>Lifting for</p>
                    <p id="daysCounter" class="big-font">69 days</p>
                </div>
                <div class="stat">
                    <p>Max total lift</p>
                    <p class="big-font">{round(my_data["max_total_value"], 1)} kg</p>
                </div>
                <div class="stat">
                    <p>Body-weight</p>
                    <p class="big-font">{round(my_data["weight_value"], 1)} kg</p>
                </div>
                <div class="stat">
                    <p>Attendance</p>
                    <p class="big-font">{round(my_data["attendance_total_value"], 2)} %</p>
                </div>
                <div class="stat">
                    <p>Estimated max lift</p>
                    <p class="big-font">{round(my_data["max_total_c_value"], 1)} kg</p>
                </div>
            </div>

            <br><br><br><br>
            <p>Deadlift progress - max estimated from set (hover for details)</p>
            <svg id="deadlift_stats">
                """ + milestones + svg_html_line(my_data["x_data_deadlift_c"], my_data["y_data_deadlift_c"]) + ' ' +
                    my_data["power_lvl_points_deadlift_c"] + f"""
            </svg>

            <div class="stats">
                <div class="stat">
                    <p>Max deadlift 1RM</p>
                    <p class="big-font">{round(my_data["max_deadlift_value"], 1)} kg</p>
                </div>
                <div class="stat">
                    <p>Max estimated deadlift</p>
                    <p class="big-font">{round(my_data["max_deadlift_c_value"], 1)} kg</p>
                </div>
                <div class="stat">
                    <p>Max est. lift/BW</p>
                    <p class="big-font">{round(my_data["max_deadlift_m_value"], 2)}</p>
                </div>
            </div>

            <br><br><br><br>
            <p>Squat progress - max estimated from set (hover for details)</p>
            <svg id="squat_stats">
                """ + milestones + svg_html_line(my_data["x_data_squat_c"], my_data["y_data_squat_c"]) + ' ' +
                    my_data["power_lvl_points_squat_c"] + f"""
            </svg>

            <div class="stats">
                <div class="stat">
                    <p>Max squat 1RM</p>
                    <p class="big-font">{round(my_data["max_squat_value"], 1)} kg</p>
                </div>
                <div class="stat">
                    <p>Max estimated squat</p>
                    <p class="big-font">{round(my_data["max_squat_c_value"], 1)} kg</p>
                </div>
                <div class="stat">
                    <p>Max est. lift/BW</p>
                    <p class="big-font">{round(my_data["max_squat_m_value"], 2)}</p>
                </div>
            </div>

            <br><br><br><br>
            <p>Bench progress - max estimated from set (hover for details)</p>
            <svg id="bench_stats">
                """ + milestones + svg_html_line(my_data["x_data_bench_c"], my_data['y_data_bench_c']) + ' '
                    + my_data["power_lvl_points_bench_c"] + f"""
            </svg>

            <div class="stats">
                <div class="stat">
                    <p>Max bench 1RM</p>
                    <p class="big-font">{round(my_data["max_bench_value"], 1)} kg</p>
                </div>
                <div class="stat">
                    <p>Max estimated bench</p>
                    <p class="big-font">{round(my_data["max_bench_c_value"], 1)} kg</p>
                </div>
                <div class="stat">
                    <p>Max est. lift/BW</p>
                    <p class="big-font">{round(my_data["max_bench_m_value"], 2)}</p>
                </div>
            </div>

            <br><br><br><br>
            <p>Bodyweight timeline</p>
            <svg id="weight_stats">
                """ + milestones + my_data["power_lvl_points_weight"] + f"""
            </svg>

            <p>The formula used to calculate the statistics in "Main power level" graph is a Landers formula (1985):
                ( 100 * Weight ) / ( 101.3 - ( 2.67123 * repetitions ) ). There are also: The Brzycki (1993),
                The Baechle (2000) and The Epley (1985) formulas but this one works fine for me.</p>

            <p>The fitting of the curve was carried out by using 
            <a href="https://en.wikipedia.org/wiki/Generalised_logistic_function">generalised logistic function</a>
                which in some cases worked out just fine but in some failed as other tried formulas. This can be either 
                due to too poor dataset or the fact that I am not a machine :) </p>

            <p>The fitting equation employed is given by: <span style="color:var(--dark-scarlet);">((a - d) / ((1 + 
            ((x / c) ** b)) ** e)) + d + f * x </span>
            I took the liberty of adding the linear function to the equation, which resulted in a slight improvement. 
            The grayed-out points are not considered in the fit calculation.</p>

            <div style="height: 30vh;"></div>

        </div>

      <script type="text/javascript" src="plot.js"></script>

      <script type="text/javascript" src="../scripts/transition.js"></script>
      </body>

    </html>
    """)

    with open("strength.html", "w") as file:
        file.write(html_content)