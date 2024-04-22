# Import necessary libraries
from flask import Flask, request, render_template, redirect, url_for
import dash
from dash import dcc, html
import plotly.figure_factory as ff
import json
from Process import Process
from Scheduler import Scheduler
import time  # Import the time module
from SchedulingAlgorithm import FCFS as FCSF

# Initialize Flask app
app = Flask(__name__)

# Initialize Dash app within Flask app
dash_app = dash.Dash(__name__, server=app, url_base_pathname='/dashboard/')
dash_app.layout = html.Div(id='output')

# Define route for submitting jobs

#Shceduler should return : [proceses] [start_times] [durations]

@app.route('/schedule', methods=['POST'])
def schedule():
    job_data = request.json
    print(job_data)
    # Process job data (you can add your logic here)
    # For now, let's just assume job_data contains intervals for processes
    # Extract process names, start times, and durations from job data
    algorithm = job_data[-1]['algorithm']
    scheduler = Scheduler()
    if algorithm == 'FCFS':
        algo=FCSF()
        scheduler.set_algorithm(algo)
    job_data.pop()
    process_names = [job['pid'] for job in job_data]
    start_times = [job['arrival_time'] for job in job_data]
    durations = [job['burst_time'] for job in job_data]
    processes = [Process(name, start, duration) for name, start, duration in zip(process_names, start_times, durations)]
    print(processes)
    scheduler.set_processes(processes)
    #try:
    start_times, process_names,durations= scheduler.run()
    #except Exception as e:
    #    return str(e), 400
    #durations=[5,10,7,8,13,6,2]
    #start_times=[0,11,14,20,25,30,30]
    #process_names=['P1','P2','P3','P4','P5','P6','P1']
    tasks = []
    for name, start, duration in zip(process_names, start_times, durations):
        start = float(start)  # Convert start to float
        tasks.append({'Task': name, 'Start': start, 'Finish': start + float(duration), 'Resource': name})  # Add 'Resource' key for legend
    # Create Gantt chart using create_gantt() function
    fig = ff.create_gantt(tasks, index_col='Task', title='Job Schedule', group_tasks=True, show_colorbar=True)
    # Customize x-axis properties to remove time units and start from 0
    fig.update_layout(xaxis_type='linear')
    # Update Dash app layout with new Gantt chart
    dash_app.layout = html.Div([
        dcc.Graph(id='job-gantt-chart', figure=fig),
    ])

    return redirect(url_for('render_dashboard'))



@app.route('/')
def index():
    return render_template('index.html')


@app.route('/dashboard/')
def render_dashboard():
    return dash_app.index()

if __name__ == '__main__':
    app.run(debug=True)
