import os, sys, getpass


# change working directory
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# script path
script_path = script_dir+"/b3_trading_signals_task_scheduler"

# script time
script_hour = "12:00"

# task name in Windows Task Scheduler
task_name = "b3_trading_signals_bot"

# command to create the scheduled task
task_command = f'schtasks /Create /SC DAILY /TN "{task_name}" /TR "{sys.executable} {script_path}" /ST {script_hour} /F'

# execute command
result = os.system(task_command)

if result == 0:
    print("Task successfully created.")
else:
    print("Error creating the task.")