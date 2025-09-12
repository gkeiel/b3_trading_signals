import os, sys

"""
This script automatically creates a Windows Task Scheduler entry 
to run b3_trading_signals_bot.py daily at a specified time.
"""

# change working directory
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# script path
script_path = script_dir+"/b3_trading_signals_bot.py"

# script time
script_hour = "19:03"

# task name in Windows Task Scheduler
task_name = "b3_trading_signals_bot"

# command to create the scheduled task:
# /F overwrite current task
# /TR command to be executed 
task_command = f'schtasks /Create /SC DAILY /TN "{task_name}" /TR "{sys.executable} {script_path}" /ST {script_hour} /F'

# execute
result = os.system(task_command)

if result == 0:
    print("Task successfully created.")
else:
    print("Error creating the task.")