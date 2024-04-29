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
    hash_object = hashlib.sha256(process_name.encode())
    hex_dig = hash_object.hexdigest()[:6]
    return '#' + hex_dig




def render_gantt_chart(processes, start_times, durations, app_layout,algorithm=None):
    tasks = []
    # Generate a custom color for each process name
    #unique_process_names = set(processes)
    colors = [generate_color(process_name) for process_name in processes]
    color_dict = {process: color for process, color in zip(processes, colors)} 
    print(colors)
    for name, start, duration, color in zip(processes, start_times, durations, colors):
        start = float(start)  # Convert start to float
        tasks.append({'Task': name, 'Start': start, 'Finish': start + float(duration), 'Resource': name})
    # Update the color attribute to use custom colors
    title='Job Scheduling Gantt Chart'
    fig = ff.create_gantt(tasks, index_col='Task', title=title, group_tasks=True, show_colorbar=True, colors=color_dict)
    fig.update_layout(xaxis_type='linear')
    app_layout.append(dcc.Graph(id='job-gantt-chart', figure=fig))



def render_turnaround_time_chart(processes, start_times, durations, arrival_times, app_layout):

    print("########################################")
    print("turnaround time chart info:")
    print(processes)
    print(start_times)
    print(durations)
    print(arrival_times)
    print("########################################")

    termination_times={processes[i]:0 for i in range(len(processes))}
    for p in processes:
        for i in range(len(processes)):
            if processes[i]==p:
                termination_times[p]=max(start_times[i]+durations[i],termination_times[p])
    print(termination_times)
    print(arrival_times)
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
        app_layout.append(html.P(f"Average Waiting Time: {average_waiting_time}", className="p-4"))
        

def render_cpu_utilization_chart(processes, start_times, durations, app_layout):
    pass

def render_process_table(processes, start_times, durations, arrival_times, app_layout):

    print("########################################")
    print("process table info:")
    print("########################################")
    # Calculate start times and durations for each process
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

    # Calculate turnaround times for each process
    turnaround_times = {process: termination_times[process] - arrival_times[process] for process in processes}

    # Generate colors for each process
    colors = {process: generate_color(process) for process in processes}

    processes = list(set(processes))

    # Prepare data for the table
    data = {
        "Process": processes,
        "Arrival Time": [arrival_times[process] for process in processes],
        "Burst Time": [durations_dict[process] for process in processes],
        "Start Time": [start_time_dict[process] for process in processes],
        "Finish Time": [turnaround_times[process] + arrival_times[process] for process in processes],
        "Turnaround Time": [turnaround_times[process] for process in processes]
    }

    # Create the DataTable with Bootstrap stripped table and padding
    table = dbc.Table.from_dataframe(pd.DataFrame(data), striped=True, bordered=True, hover=True)

    # Append the table and average turnaround time to the layout
    app_layout.append(html.Div([
        html.Div(table, className="p-4"),  # Add padding
        html.P(f"Average Turnaround Time: {sum(turnaround_times.values()) / len(turnaround_times)}", className="p-4")
    ]))




def add_header(app_layout):
    header = dbc.Navbar(
        dbc.Container(
            [
                html.A(
                    dbc.Row(
                        [
                            dbc.Col(html.Img(src=PLOTLY_LOGO, height="30px")),
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
                                dbc.NavItem(dbc.NavLink("Manualy generate", href="/manual")),
                                dbc.NavItem(dbc.NavLink("Randomly generate", href="/manual")),
                                dbc.NavItem(dbc.NavLink("File upload", href="/upload")),
                                dbc.NavItem(dbc.NavLink("Compare algorithms", href="/compare")),
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
    footer = html.Footer("Process Scheduling Visualizer 2024", className="footer text-center fixed-bottom bg-dark text-light")
    app_layout.append(footer)


def render(processes=[], start_times=[], durations=[], arrival_times={}):
    app_layout = []
    add_header(app_layout)
    render_gantt_chart(processes, start_times, durations, app_layout)
    render_turnaround_time_chart(processes, start_times,durations,arrival_times, app_layout)
    render_process_table(processes, start_times, durations,arrival_times, app_layout)
    render_waiting_time_chart(processes, start_times, durations, arrival_times, app_layout)
    add_footer(app_layout)
    dash_app.layout = html.Div(app_layout)





#Shceduler should return : [proceses] [start_times] [durations]
@app.route('/schedule', methods=['POST'])
def schedule():
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
    return render_template('documentation.html')

@app.route('/file')
def fileu():
    return render_template('file.html')

@app.route('/manual')
def manual():
    return render_template('manual.html')

@app.route('/generate')
def random():
    return render_template('generate.html')

@app.route('/dashboard/')
def render_dashboard():
    return dash_app.index()

@app.route('/compare')
def compare():
    return render_template('compare.html')

@app.route('/documentation')
def documentation():
    return render_template('documentation.html')


def render_comparison_box(title, processes, start_times, durations, arrival_times, app_layout):
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
    app_layout = []
    add_header(app_layout)
    print(processes)
    for key in processes:
        render_comparison_box(key, processes[key], start_times[key], durations[key], arrival_times[key], app_layout)
    add_footer(app_layout)
    dash_app.layout = html.Div(app_layout)



@app.route('/comparison', methods=['POST'])
def comparison():
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
