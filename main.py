from flask import Flask, request, render_template, redirect, url_for
import dash
from dash import dcc, html, dash_table
import pandas as pd
import plotly.figure_factory as ff
import plotly.colors
import json
import csv
from Process import Process
from Scheduler import Scheduler
from io import TextIOWrapper
import time  # Import the time module
import SchedulingAlgorithm 
from SchedulingAlgorithm import FCFS as FCFS
from SchedulingAlgorithm import SJF as SJF
from SchedulingAlgorithm import Priority as Priority
from SchedulingAlgorithm import PriorityRR as PriorityRR
from SchedulingAlgorithm import RR as RR
import hashlib
import dash_bootstrap_components as dbc
import plotly.graph_objs as go

PLOTLY_LOGO = "https://images.plot.ly/logo/new-branding/plotly-logomark.png"

# Initialize Flask app
app = Flask(__name__)

dash_app = dash.Dash(__name__, server=app, url_base_pathname='/dashboard/',external_stylesheets=[dbc.themes.BOOTSTRAP])
dash_app.layout = html.Div(id='output')

def generate_color(process_name):
    """
    Generate a color based on the process name.

    Args:
        process_name (str): The name of the process.

    Returns:
        str: Hexadecimal color code.
    """
    hash_object = hashlib.sha256(process_name.encode())
    hex_dig = hash_object.hexdigest()[:6]
    return '#' + hex_dig

def render_gantt_chart(processes, start_times, durations, app_layout,algorithm=None):
    """
    Render a Gantt chart visualizing the job scheduling.

    Args:
        processes (list): List of process names.
        start_times (list): List of start times for each process.
        durations (list): List of durations for each process.
        app_layout (list): List representing the layout of the Dash app.
        algorithm (str, optional): The scheduling algorithm used. Defaults to None.
    """
    tasks = []
    colors = [generate_color(process_name) for process_name in processes]
    color_dict = {process: color for process, color in zip(processes, colors)} 
    for name, start, duration, color in zip(processes, start_times, durations, colors):
        start = float(start)
        tasks.append({'Task': name, 'Start': start, 'Finish': start + float(duration), 'Resource': name})
    title='Job Scheduling Gantt Chart'
    fig = ff.create_gantt(tasks, index_col='Task', title=title, group_tasks=True, show_colorbar=True, colors=color_dict)
    fig.update_layout(xaxis_type='linear')
    app_layout.append(dcc.Graph(id='job-gantt-chart', figure=fig))

def render_turnaround_time_chart(processes, start_times, durations, arrival_times, app_layout):
    """
    Render a bar chart showing the turnaround time for each process.

    Args:
        processes (list): List of process names.
        start_times (list): List of start times for each process.
        durations (list): List of durations for each process.
        arrival_times (dict): Dictionary mapping process names to their arrival times.
        app_layout (list): List representing the layout of the Dash app.
    """
    termination_times={processes[i]:0 for i in range(len(processes))}
    for p in processes:
        for i in range(len(processes)):
            if processes[i]==p:
                termination_times[p]=max(start_times[i]+durations[i],termination_times[p])
    turnaround_times = {process: termination_times[process] - arrival_times[process] for process in processes}
    colors={process:generate_color(process) for process in processes}
    data = []
    for p in turnaround_times:
        data.append(go.Bar(name=p, x=[p], y=[turnaround_times[p]], marker_color=colors[p]))
    layout = go.Layout(
        title='Turnaround Time for Each Process',
        xaxis=dict(title='Process'),
        yaxis=dict(title='Turnaround Time'),
        barmode='group'
    )
    fig = go.Figure(data=data, layout=layout)
    app_layout.append(dcc.Graph(id='waiting-time-chart', figure=fig))

def render_waiting_time_chart(processes, start_times, durations, arrival_times, app_layout):
    """
    Render a bar chart showing the waiting time for each process.

    Args:
        processes (list): List of process names.
        start_times (list): List of start times for each process.
        durations (list): List of durations for each process.
        arrival_times (dict): Dictionary mapping process names to their arrival times.
        app_layout (list): List representing the layout of the Dash app.
    """
    waiting_times= {process: 0 for process in processes}
    for p in set(processes):
        last_run=arrival_times[p]
        for i in range(len(processes)):
            if processes[i]==p:
                waiting_times[p]+=(start_times[i]-last_run)
                last_run=start_times[i]+durations[i]
    colors={process:generate_color(process) for process in processes}
    data = []
    for p in waiting_times:
        data.append(go.Bar(name=p, x=[p], y=[waiting_times[p]], marker_color=colors[p]))
    layout = go.Layout(
        title='Waiting Time for Each Process',
        xaxis=dict(title='Process'),
        yaxis=dict(title='Waiting Time'),
        barmode='group'
    )
    fig = go.Figure(data=data, layout=layout)
    app_layout.append(dcc.Graph(id='waiting-time-chart', figure=fig))
    average_waiting_time = sum(waiting_times.values()) / len(waiting_times)
    app_layout.append(html.P(
        children=[
            html.Span("Average Waiting Time: ", style={"font-size": "1.25rem"}),  # Text with increased font size
            html.Span(
                f"{average_waiting_time:.2f}",  # Numerical value with two decimal places
                style={"font-size": "1.5rem", "color": "red", "margin-left": "8px"}  # Increased font size, red color, and margin between the text and numerical value
            )
        ],
        className="p-4"
    ))


def render_cpu_utilization_chart(processes, durations, app_layout):
    """
    Render a pie chart showing CPU utilization per process.

    Args:
        processes (list): List of process names.
        durations (list): List of durations for each process.
        app_layout (list): List representing the layout of the Dash app.
    """
    total_cpu_time = sum(durations)
    cpu_utilization = {process: 0 for process in processes}
    for i in range(len(processes)):
        cpu_utilization[processes[i]] += durations[i]
    cpu_utilization_percentage = {process: (time / total_cpu_time) * 100 for process, time in cpu_utilization.items()}
    labels = list(cpu_utilization_percentage.keys())
    values = list(cpu_utilization_percentage.values())
    colors = [generate_color(process) for process in labels]
    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.3, marker=dict(colors=colors))])
    fig.update_layout(title='CPU Utilization Per Process')
    app_layout.append(dcc.Graph(id='cpu-utilization-chart', figure=fig))

def render_process_table(processes, start_times, durations, arrival_times, app_layout):
    """
    Render a table showing process details.

    Args:
        processes (list): List of process names.
        start_times (list): List of start times for each process.
        durations (list): List of durations for each process.
        arrival_times (dict): Dictionary mapping process names to their arrival times.
        app_layout (list): List representing the layout of the Dash app.
    """
    start_time_dict = {process: start_times[i] for i, process in enumerate(processes)}
    durations_dict = {process: 0 for process in processes}
    for i, process in enumerate(processes):
        start_time_dict[process] = min(start_time_dict[process], start_times[i])
        durations_dict[process] += durations[i]
    termination_times={processes[i]:0 for i in range(len(processes))}
    for p in processes:
        for i in range(len(processes)):
            if processes[i]==p:
                termination_times[p]=max(start_times[i]+durations[i],termination_times[p])
    turnaround_times = {process: termination_times[process] - arrival_times[process] for process in processes}
    colors = {process: generate_color(process) for process in processes}
    processes = list(set(processes))
    data = {
        "Process": processes,
        "Arrival Time": [arrival_times[process] for process in processes],
        "Burst Time": [durations_dict[process] for process in processes],
        "Start Time": [start_time_dict[process] for process in processes],
        "Finish Time": [turnaround_times[process] + arrival_times[process] for process in processes],
        "Turnaround Time": [turnaround_times[process] for process in processes]
    }
    table = dbc.Table.from_dataframe(pd.DataFrame(data), striped=True, bordered=True, hover=True)
    app_layout.append(html.Div([
    html.Div(table, className="p-4"),  # Add padding
    html.P(
        children=[
            html.Span("Average Turnaround Time: ", style={"font-size": "1.25rem"}),  # Text with increased font size
            html.Span(
                f"{sum(turnaround_times.values()) / len(turnaround_times):.2f}",  # Numerical value with two decimal places
                style={"font-size": "1.5rem", "color": "red", "margin-left": "8px"}  # Increased font size, red color, and margin between the text and numerical value
            )
        ],
        className="p-4",
    ),
    ], className="container mt-4"))


def add_header(app_layout):
    """
    Add header to the layout.

    Args:
        app_layout (list): List representing the layout of the Dash app.
    """
    header = dbc.Navbar(
        dbc.Container(
            [
                html.A(
                    dbc.Row(
                        [
                            dbc.Col(dbc.NavbarBrand("Process Scheduling Algorithm", className="ms-2")),
                        ],
                        align="center",
                        className="g-0",
                    ),
                    href="/",
                    style={"textDecoration": "none"},
                ),
                dbc.NavbarToggler(id="navbar-toggler", n_clicks=0),
                dbc.Collapse(
                    id="navbar-collapse",
                    is_open=False,
                    navbar=True,
                    children=[
                        dbc.Nav(
                            [
                                dbc.NavItem(dbc.NavLink("Manualy generate", href="../manual",external_link=True)),
                                dbc.NavItem(dbc.NavLink("Randomly generate", href="/generate",external_link=True)),
                                dbc.NavItem(dbc.NavLink("File upload", href="/file",external_link=True)),
                                dbc.NavItem(dbc.NavLink("Compare algorithms", href="/compare",external_link=True)),
                                dbc.NavItem(dbc.NavLink("Documentation", href="/documentation",external_link=True)),
                            ],
                            navbar=True,
                        )
                    ]
                ),
            ]
        ),
        color="dark",
        dark=True,
    )
    app_layout.append(header)

def add_footer(app_layout):
    """
    Add footer to the layout.

    Args:
        app_layout (list): List representing the layout of the Dash app.
    """
    footer = html.Footer("Process Scheduling Visualizer 2024", className="footer text-center fixed-bottom bg-dark text-light")
    app_layout.append(footer)

def render(processes=[], start_times=[], durations=[], arrival_times={}):
    """
    Render the Dash app with the given process data.

    Args:
        processes (list): List of process names.
        start_times (list): List of start times for each process.
        durations (list): List of durations for each process.
        arrival_times (dict): Dictionary mapping process names to their arrival times.
    """
    app_layout = []
    add_header(app_layout)
    render_gantt_chart(processes, start_times, durations, app_layout)
    render_turnaround_time_chart(processes, start_times,durations,arrival_times, app_layout)
    render_process_table(processes, start_times, durations,arrival_times, app_layout)
    render_waiting_time_chart(processes, start_times, durations, arrival_times, app_layout)
    render_cpu_utilization_chart(processes, durations, app_layout)
    add_footer(app_layout)
    dash_app.layout = html.Div(app_layout)






@app.route('/schedule', methods=['POST'])
def schedule():
    """
    Endpoint to schedule processes.

    Returns:
        Response: Redirects to the dashboard.
    """
    job_data = request.json
    print(job_data)
    algorithm = job_data[-1]['algorithm']
    if(algorithm == 'RR' or algorithm == 'PriorityRR'):
        quantum = int(job_data[-1]['quantum'])
    scheduler = Scheduler()
    # Initialize the scheduling algorithm based on the selected algorithm
    if algorithm == 'FCFS':
        algo=FCFS()
    elif algorithm == 'SJF':
        algo=SJF()
    elif algorithm == 'Priority':
        algo=Priority()
    elif algorithm == 'RR':
         algo=RR(quantum)
    elif algorithm == 'PriorityRR':
        algo=PriorityRR(quantum)
    scheduler.set_algorithm(algo)
    job_data.pop()
    process_names = [job['pid'] for job in job_data]
    arrival_times = [job['arrival_time'] for job in job_data]
    arrival_time_dict = {name: arrival for name, arrival in zip(process_names, arrival_times)}
    durations = [job['burst_time'] for job in job_data]
    priorities = [job['priority'] for job in job_data]
    processes = [Process(name, int(arrival),int(duration)) for name, arrival, duration in zip(process_names, arrival_times, durations)]
    if algorithm == 'Priority' or algorithm == "PriorityRR":
        for process, priority in zip(processes, priorities):
            process.priority = int(priority)
    print(processes)
    scheduler.set_processes(processes)
    process_names,start_times,durations= scheduler.run()
    print(start_times)
    render(process_names, start_times, durations, arrival_time_dict)
    return redirect(url_for('render_dashboard'))

@app.route('/upload', methods=['POST'])
def processFile():
    """
    Process uploaded file.

    Returns:
        Response: Redirects to the dashboard.
    """
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    try:
        file_wrapper = TextIOWrapper(file, encoding='utf-8')

        # Read CSV file
        job_data = []
        csv_reader = csv.reader(file_wrapper)
        for row in csv_reader:
            try:
                if len(row) == 3:
                    pid, arrival_time, burst_time = row
                    job_data.append({'pid': pid, 'arrival_time': int(arrival_time), 'burst_time': int(burst_time), 'priority': None})
                else:
                    pid, arrival_time, burst_time, priority = row
                    priority = int(priority) if priority != 'None' else None
                    job_data.append({'pid': pid, 'arrival_time': int(arrival_time), 'burst_time': int(burst_time), 'priority': priority})
            except ValueError:
                return "Error: Incorrect data format in CSV file."
    except Exception as e:
        return f"Error: {str(e)}"
    algorithm = request.form['algorithm']
    scheduler = Scheduler()

    # Initialize the scheduling algorithm based on the selected algorithm
    if algorithm == 'FCFS':
        algorithm = FCFS()
    elif algorithm == 'SJF':
        algorithm = SJF()
    elif algorithm == 'Priority':
        algorithm = Priority()
    elif algorithm == 'RR':
        if request.form["quantum"]:
            quantum = int(request.form["quantum"])
        algorithm = RR(quantum)
    elif algorithm == 'PriorityRR':
        if request.form["quantum"]:
            quantum = int(request.form["quantum"])
        algorithm = PriorityRR(quantum)
    else:
        return algorithm
    scheduler.set_algorithm(algorithm)
    process_names = [job['pid'] for job in job_data]
    arrival_times = [job['arrival_time'] for job in job_data]
    arrival_time_dict = {name: arrival for name, arrival in zip(process_names, arrival_times)}
    durations = [job['burst_time'] for job in job_data]
    priorities = [job['priority'] for job in job_data]
    processes = [Process(name, int(arrival), int(duration), priority=priority) for name, arrival, duration, priority in zip(process_names, arrival_times, durations, priorities)]
    scheduler.set_processes(processes)
    process_names, start_times, durations = scheduler.run()
    print("Arrival Time Dict: ", arrival_time_dict)
    render(process_names, start_times, durations, arrival_time_dict)
    return redirect(url_for('render_dashboard'))

@app.route('/')
def index():
    """
    Endpoint for the index page.

    Returns:
        str: Rendered HTML page.
    """
    return render_template('documentation.html')

@app.route('/file')
def fileu():
    """
    Endpoint for the file upload page.

    Returns:
        str: Rendered HTML page.
    """
    return render_template('file.html')

@app.route('/manual')
def manual():
    """
    Endpoint for the manual input page.

    Returns:
        str: Rendered HTML page.
    """
    return render_template('manual.html')

@app.route('/generate')
def random():
    """
    Endpoint for the random generation page.

    Returns:
        str: Rendered HTML page.
    """
    return render_template('generate.html')

@app.route('/dashboard/')
def render_dashboard():
    """
    Endpoint for rendering the dashboard.

    Returns:
        str: Rendered dashboard.
    """
    return dash_app.index()

@app.route('/compare')
def compare():
    """
    Endpoint for the comparison page.

    Returns:
        str: Rendered HTML page.
    """
    return render_template('compare.html')

@app.route('/documentation')
def documentation():
    """
    Endpoint for the documentation page.

    Returns:
        str: Rendered HTML page.
    """
    return render_template('documentation.html')

def render_comparison_box(title, processes, start_times, durations, arrival_times, app_layout):
    """
    Render comparison box for each scheduling algorithm.

    Args:
        title (str): Title of the comparison box.
        processes (list): List of process names.
        start_times (list): List of start times for each process.
        durations (list): List of durations for each process.
        arrival_times (dict): Dictionary mapping process names to their arrival times.
        app_layout (list): List representing the layout of the Dash app.
    """
    termination_times = {processes[i]: 0 for i in range(len(processes))}
    waiting_times = {process: 0 for process in processes}
    start_time_dict = {process: start_times[i] for i, process in enumerate(processes)}
    durations_dict = {process: 0 for process in processes}

    for p in processes:
        for i in range(len(processes)):
            if processes[i] == p:
                termination_times[p] = max(start_times[i] + durations[i], termination_times[p])

    for p in set(processes):
        last_run = arrival_times[p]
        for i in range(len(processes)):
            if processes[i] == p:
                waiting_times[p] += (start_times[i] - last_run)
                last_run = start_times[i] + durations[i]

    for i, process in enumerate(processes):
        start_time_dict[process] = min(start_time_dict[process], start_times[i])
        durations_dict[process] += durations[i]

    turnaround_times = {process: termination_times[process] - arrival_times[process] for process in processes}

    # Calculate average waiting time and average turnaround time
    average_waiting_time = sum(waiting_times.values()) / len(waiting_times)
    average_turnaround_time = sum(turnaround_times.values()) / len(turnaround_times)

    if title == "FCFS":
        title = "First Come First Served (FCFS)"
    elif title == "SJF":
        title = "Shortest Job First (SJF)"
    elif title == "P":
        title = "Priority Scheduling"
    elif title == "RR":
        title = "Round Robin (RR)"
    else:
        title = "Priority Scheduling with Round Robin (PriorityRR)"

    # Add elements to the app layout
    app_layout.append(html.Div([
        html.H3(html.Strong(title), className="text-center mb-4 lead p-3"),
        html.Div([
            html.P(f"Average Turnaround Time: {average_turnaround_time}", className="lead p-3"),
            html.P(f"Average Waiting Time: {average_waiting_time}", className="lead p-3")
        ], className="text-center")
    ], className="border rounded p-4 mb-4", style={"margin": "16px 360px 16px 360px"}))


def renderComparison(processes={}, start_times={}, durations={}, arrival_times={}):
    """
    Render comparison page for different scheduling algorithms.

    Args:
        processes (dict): Dictionary of processes for each algorithm.
        start_times (dict): Dictionary of start times for each algorithm.
        durations (dict): Dictionary of durations for each algorithm.
        arrival_times (dict): Dictionary of arrival times for each algorithm.
    """
    app_layout = []
    add_header(app_layout)
    print(processes)
    for key in processes:
        render_comparison_box(key, processes[key], start_times[key], durations[key], arrival_times[key], app_layout)
    add_footer(app_layout)
    dash_app.layout = html.Div(app_layout)



@app.route('/comparison', methods=['POST'])
def comparison():
    """
    Endpoint to compare different scheduling algorithms.

    Returns:
        Response: Redirects to the dashboard.
    """
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    try:
        file_wrapper = TextIOWrapper(file, encoding='utf-8')

        # Read CSV file
        job_data = []
        csv_reader = csv.reader(file_wrapper)
        for row in csv_reader:
            try:
                if len(row) == 3:
                    pid, arrival_time, burst_time = row
                    job_data.append({'pid': pid, 'arrival_time': int(arrival_time), 'burst_time': int(burst_time), 'priority': None})
                else:
                    pid, arrival_time, burst_time, priority = row
                    priority = int(priority) if priority != 'None' else None
                    job_data.append({'pid': pid, 'arrival_time': int(arrival_time), 'burst_time': int(burst_time), 'priority': priority})
            except ValueError:
                return "Error: Incorrect data format in CSV file."
    except Exception as e:
        return f"Error: {str(e)}"

    schedulerFCFS = Scheduler()
    schedulerSJF = Scheduler()
    schedulerP = Scheduler()
    schedulerRR = Scheduler()
    schedulerPRR = Scheduler()

    fcfs = FCFS()
    sjf = SJF()
    priori = Priority()
    rr = RR(int(request.form["quantum"]))
    prioriRR = PriorityRR(int(request.form["quantum"]))

    processes2 = dict()
    start_times2 = dict()
    durations2 = dict()
    arrival_times2 = dict()

    schedulerFCFS.set_algorithm(fcfs)
    process_names = [job['pid'] for job in job_data]
    arrival_times = [job['arrival_time'] for job in job_data]
    arrival_time_dict = {name: arrival for name, arrival in zip(process_names, arrival_times)}
    durations = [job['burst_time'] for job in job_data]
    priorities = [job['priority'] for job in job_data]
    processes = [Process(name, int(arrival), int(duration), priority=priority) for name, arrival, duration, priority in zip(process_names, arrival_times, durations, priorities)]
    schedulerFCFS.set_processes(processes)
    process_names, start_times, durations = schedulerFCFS.run()
    processes2["FCFS"] = process_names
    start_times2["FCFS"] = start_times
    durations2["FCFS"] = durations
    arrival_times2["FCFS"] = arrival_time_dict
    print("Arrival Time Dict: ", arrival_time_dict)

    schedulerSJF.set_algorithm(sjf)
    process_names = [job['pid'] for job in job_data]
    arrival_times = [job['arrival_time'] for job in job_data]
    arrival_time_dict = {name: arrival for name, arrival in zip(process_names, arrival_times)}
    durations = [job['burst_time'] for job in job_data]
    priorities = [job['priority'] for job in job_data]
    processes = [Process(name, int(arrival), int(duration), priority=priority) for name, arrival, duration, priority in zip(process_names, arrival_times, durations, priorities)]
    schedulerSJF.set_processes(processes)
    process_names, start_times, durations = schedulerSJF.run()
    processes2["SJF"] = process_names
    start_times2["SJF"] = start_times
    durations2["SJF"] = durations
    arrival_times2["SJF"] = arrival_time_dict
    print("Arrival Time Dict: ", arrival_time_dict)

    schedulerP.set_algorithm(priori)
    process_names = [job['pid'] for job in job_data]
    arrival_times = [job['arrival_time'] for job in job_data]
    arrival_time_dict = {name: arrival for name, arrival in zip(process_names, arrival_times)}
    durations = [job['burst_time'] for job in job_data]
    priorities = [job['priority'] for job in job_data]
    processes = [Process(name, int(arrival), int(duration), priority=priority) for name, arrival, duration, priority in zip(process_names, arrival_times, durations, priorities)]
    schedulerP.set_processes(processes)
    process_names, start_times, durations = schedulerP.run()
    processes2["P"] = process_names
    start_times2["P"] = start_times
    durations2["P"] = durations
    arrival_times2["P"] = arrival_time_dict
    print("Arrival Time Dict: ", arrival_time_dict)

    schedulerRR.set_algorithm(rr)
    process_names = [job['pid'] for job in job_data]
    arrival_times = [job['arrival_time'] for job in job_data]
    arrival_time_dict = {name: arrival for name, arrival in zip(process_names, arrival_times)}
    durations = [job['burst_time'] for job in job_data]
    priorities = [job['priority'] for job in job_data]
    processes = [Process(name, int(arrival), int(duration), priority=priority) for name, arrival, duration, priority in zip(process_names, arrival_times, durations, priorities)]
    schedulerRR.set_processes(processes)
    process_names, start_times, durations = schedulerRR.run()
    processes2["RR"] = process_names
    start_times2["RR"] = start_times
    durations2["RR"] = durations
    arrival_times2["RR"] = arrival_time_dict
    print("Arrival Time Dict: ", arrival_time_dict)

    schedulerPRR.set_algorithm(prioriRR)
    process_names = [job['pid'] for job in job_data]
    arrival_times = [job['arrival_time'] for job in job_data]
    arrival_time_dict = {name: arrival for name, arrival in zip(process_names, arrival_times)}
    durations = [job['burst_time'] for job in job_data]
    priorities = [job['priority'] for job in job_data]
    processes = [Process(name, int(arrival), int(duration), priority=priority) for name, arrival, duration, priority in zip(process_names, arrival_times, durations, priorities)]
    schedulerPRR.set_processes(processes)
    process_names, start_times, durations = schedulerPRR.run()
    processes2["PRR"] = process_names
    start_times2["PRR"] = start_times
    durations2["PRR"] = durations
    arrival_times2["PRR"] = arrival_time_dict
    print("Arrival Time Dict: ", arrival_time_dict)

    renderComparison(processes2, start_times2, durations2, arrival_times2)
    return redirect(url_for('render_dashboard'))

if __name__ == '__main__':
    app.run(debug=True)
