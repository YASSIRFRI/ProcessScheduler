from flask import Flask, request, render_template, redirect, url_for
import dash
from dash import dcc, html
import plotly.figure_factory as ff
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

# Initialize Flask app
app = Flask(__name__)


dash_app = dash.Dash(__name__, server=app, url_base_pathname='/dashboard/')
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
    #try:
    process_names,start_times,durations= scheduler.run()
    print(start_times)
    print('done')
    #tasks = []
    #for name, start, duration in zip(process_names, start_times, durations):
        #start = float(start)  # Convert start to float
        #tasks.append({'Task': name, 'Start': start, 'Finish': start + float(duration), 'Resource': name})  # Add 'Resource' key for legend
    ## Create Gantt chart using create_gantt() function
    #fig = ff.create_gantt(tasks, index_col='Task', title='Job Schedule', group_tasks=True, show_colorbar=True)
    ## Customize x-axis properties to remove time units and start from 0
    #fig.update_layout(xaxis_type='linear')
    ## Update Dash app layout with new Gantt chart
    #dash_app.layout = html.Div([
        #dcc.Graph(id='job-gantt-chart', figure=fig),
    #])
    render(process_names, start_times, durations)
    return redirect(url_for('render_dashboard'))

def render_gantt_chart(processes, start_times, durations,app_layout):
    tasks = []
    for name, start, duration in zip(processes, start_times, durations):
        start = float(start)  # Convert start to float
        tasks.append({'Task': name
            , 'Start': start
            , 'Finish': start + float(duration)
            , 'Resource': name})
    fig = ff.create_gantt(tasks, index_col='Task', title='Job Schedule', group_tasks=True, show_colorbar=True)
    fig.update_layout(xaxis_type='linear')
    app_layout.append(dcc.Graph(id='job-gantt-chart', figure=fig))
    
def add_header(app_layout):
    header = html.H1("results", style={'color': 'blue', 'font-size': '32px', 'text-align': 'center'})
    app_layout.append(header)

def add_footer( app_layout):
    footer = html.Footer("2024", style={'text-align': 'center', 'margin-top': '20px'})
    app_layout.append(footer)

def render(processes=[], start_times=[], durations=[]):
    app_layout = []
    add_header(app_layout)
    render_gantt_chart(processes, start_times, durations, app_layout)
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

        # Handle if CSV file has trailing newline characters
    except Exception as e:
        return f"Error: {str(e)}"

    algorithm = request.form['algorithm']
    scheduler = Scheduler()

    print("")
    print("")
    print("")
    print(job_data)
    print("")
    print("")
    print("")

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
    render(process_names, start_times, durations)
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
