# Process Scheduling Algorithm

## Overview
This project implements various process scheduling algorithms using Flask, a Python web framework. It allows users to upload CSV files containing process data, manually input process information, or generate random processes for testing purposes. Users can then choose from different scheduling algorithms to analyze and compare their performance.

## How to Run
1. **Install Python:** Make sure you have Python installed on your system. You can download it from the [official Python website](https://www.python.org/downloads/).

2. **Install Flask:** Flask is required to run the web application. You can install it via pip by executing the following command in your terminal:
    ```bash
    pip install flask
    ```

3. **Install Plotly:** Plotly is used for data visualization in the application. You can install it via pip by executing the following command:
    ```bash
    pip install plotly
    ```

4. **Install Dash:** Dash is a Python framework for building analytical web applications. Install it via pip using the following command:
    ```bash
    pip install dash
    ```

5. **Install other dependencies:** Additional dependencies may be required. You can install them by executing:
    ```bash
    pip install pandas
    ```

6. **Run the Application:** Once the dependencies are installed, you can run the application by executing the following command in your terminal:
    ```bash
    python main.py
    ```

7. **Access the Application:** After running the application, you can access it by opening your web browser and navigating to `http://127.0.0.1:5000`.

## How to Use
1. **File Upload:** Navigate to the "File upload" section to submit a CSV file containing process data. Each line of the CSV should be in one of the following two forms:
    - `process_id,arrival_time,burst_time`
    - `process_id,arrival_time,burst_time,priority` (for priority-based algorithms)
   After uploading the file, choose one of the five available scheduling algorithms: First Come First Served (FCFS), Shortest Job First (SJF), Priority Scheduling, Round Robin, or Priority with Round Robin. If you choose Round Robin or Priority with Round Robin, you'll need to specify the time quantum.

2. **Manual Upload:** If you prefer, you can manually enter process data in the "Manual Upload" section. Enter information regarding processes (process_id, arrival_time, burst_time, priority) manually. To add a process, click on the "Add Process" button. Once you have entered all the required process information and selected your algorithm, click the "Submit" button to process the data.

3. **Randomly Generate:** Use the "Randomly Generate" section to create random process data for testing purposes. Specify the number of random processes to be generated, then click the "Generate Processes" button. After generating the processes, choose your algorithm and press the "Submit" button to process the data.

4. **Compare Algorithms:**
    
    1. **Upload CSV File:** Upload a CSV file containing process data to compare the performance of different scheduling algorithms. Each line of the CSV should follow the format: `process_id,arrival_time,burst_time,priority`.
    
    2. **Choose Time Quantum**

    3. **Submit**
    
    4. **View Comparison Results:** Once the comparison is complete, the results will be displayed in a new page, showing the performance metrics for each algorithm.

5. **Documentation:** Takes you to this page where you can read how to use the app.

## Algorithm Description and Complexity Analysis
- **First Come First Served (FCFS):** Simplest scheduling algorithm where processes are executed in the order they arrive.
    - Complexity: O(nlogn) in the worst case due to sorting based on arrival time.

- **Shortest Job First (SJF):** Selects the process with the shortest burst time to execute next.
    - Complexity: O(nlogn) due to sorting based on burst time.

- **Priority Scheduling:** Executes processes based on their priority, with lower priority processes executed first.
    - Complexity: O(n^2) (naive implementation which is the one we used), O(nlogn) (using priority queue).

- **Round Robin:** Preemptive scheduling where each process is assigned a fixed time slice (quantum) to execute.
    - Complexity: O(n*(MaxBurstTime/quantum)+nlogn) assuming processes are not sorted by arrival time. 

- **Priority with Round Robin:** Combines Priority Scheduling and Round Robin.
    - Complexity: O(n*(MaxBurstTime/quantum)+nlogn) (worst-case time complexity).


## References
- [Flask Documentation](https://flask.palletsprojects.com/en/2.0.x/)
- [Plotly Documentation](https://plotly.com/python/)
- [Dash Documentation](https://dash.plotly.com/)

© 2024 Process Scheduling Algorithms
