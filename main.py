from flask import Flask, request, render_template, redirect, url_for
import dash
from dash import dcc, html, dash_table
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
    
    
    job_data.pop() # Remove the scheduling algorithm from the job data
    
    process_names = [job['pid'] for job in job_data]
    arrival_times = [job['arrival_time'] for job in job_data]
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
    print('done')
    render(process_names, start_times, durations, arrival_times)
    return redirect(url_for('render_dashboard'))

def generate_color(process_name):
    hash_object = hashlib.sha256(process_name.encode())
    hex_dig = hash_object.hexdigest()[:6]
    return '#' + hex_dig


def render_turnaround_time_chart(processes, start_times, durations, arrival_times, app_layout):
    turnaround_times = [abs(arrival - start) + duration for start, arrival, duration in zip(arrival_times, start_times, durations)]
    colors=[generate_color(process_name) for process_name in processes]
    print(colors)
    data = []
    for process, turnaround_time,color in zip(processes, turnaround_times,colors):
        data.append(go.Bar(x=[process], y=[turnaround_time], name=process, marker=dict(color=color)))
    layout = go.Layout(
        title='Turnaround Time for Each Process',
        xaxis=dict(title='Process'),
        yaxis=dict(title='Turnaround Time'),
        barmode='group'
    )
    fig = go.Figure(data=data, layout=layout)
    app_layout.append(dcc.Graph(id='waiting-time-chart', figure=fig))

    
    
    
def render_gantt_chart(processes, start_times, durations, app_layout):
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
    fig = ff.create_gantt(tasks, index_col='Task', title='Job Schedule', group_tasks=True, show_colorbar=True, colors=color_dict)
    fig.update_layout(xaxis_type='linear')
    app_layout.append(dcc.Graph(id='job-gantt-chart', figure=fig))
    
    
def render_process_table(processes, start_times, durations,arrival_times, app_layout):
    # Calculate turnaround times for each process
    turnaround_times = [abs(arrival - start) + duration for start, arrival, duration in zip(arrival_times, start_times, durations)]
    average_turnaround_time = sum(turnaround_times)/len(turnaround_times)
    data = {
        "Process": processes,
        "Start Time": start_times,
        "Duration": durations,
        "Arrival Time": arrival_times,
        "Turnaround Time": turnaround_times  # Include turnaround times in the data
    }
    
    table = dash_table.DataTable(
        id='process-table',
        columns=[{"name": i, "id": i} for i in data.keys()],
        data=[{k: v for k, v in zip(data.keys(), row)} for row in zip(*data.values())] # Modified line
    )
    
    app_layout.append(html.Div([
        table,
        html.P(f"Average Turnaround Time: {average_turnaround_time}")
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
                ),
            ]
        ),
        color="dark",
        dark=True,
    )
    app_layout.append(header)

def add_footer(app_layout):
    footer = html.Footer("2024", className="footer text-center")
    app_layout.append(footer)

def render(processes=[], start_times=[], durations=[], arrival_times=[]):
    app_layout = []
    add_header(app_layout)
    render_gantt_chart(processes, start_times, durations, app_layout)
    render_turnaround_time_chart(processes, start_times,durations,arrival_times, app_layout)
    render_process_table(processes, start_times, durations,arrival_times, app_layout)
    add_footer(app_layout)
    dash_app.layout = html.Div(app_layout)

@app.route('/upload', methods=['POST'])
def processFile():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    
    # Check if the file is empty
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
    durations = [job['burst_time'] for job in job_data]
    priorities = [job['priority'] for job in job_data]
    processes = [Process(name, int(arrival), int(duration), priority=priority) for name, arrival, duration, priority in zip(process_names, arrival_times, durations, priorities)]

    scheduler.set_processes(processes)

    process_names, start_times, durations = scheduler.run()
    render(process_names, start_times, durations, arrival_times)
    return redirect(url_for('render_dashboard'))




@app.route('/')
def index():
    return render_template('index.html')


@app.route('/manual')
def manual():
    return render_template('manual.html')


@app.route('/generate')
def random():
    return render_template('generate.html')

@app.route('/dashboard/')
def render_dashboard():
    return dash_app.index()

if __name__ == '__main__':
    app.run(debug=True)
