import json
import os
from tabulate import tabulate

# File to store tasks
TODO_FILE = "tasks.json"

STATUS_CODES = {
    0: "Pending",
    1: "In Progress",
    2: "Completed"
}

def load_tasks():
    if not os.path.exists(TODO_FILE):  
        return {}  # Return empty dictionary if file doesn't exist
    try:
        with open(TODO_FILE, "r") as file:
            tasks = json.load(file)
            return tasks if isinstance(tasks, dict) else {}  # Ensure data is a dictionary
    except (json.JSONDecodeError, ValueError):
        return {}  # Return empty dictionary if file is corrupted
    

def save_tasks(tasks):
    with open(TODO_FILE, "w") as file:
        json.dump(tasks, file, indent=4)  


def get_next_task_id(tasks):
    if tasks:
        return max(map(int, tasks.keys())) + 1  # Get max ID and increment
    return 1


def validate_input(prompt):
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("Input cannot be empty. Please enter a valid value.")


def add_task():
    tasks = load_tasks()  
    
    while True:
        taskname = validate_input("Task Name: ")
        if any(task["taskname"].lower() == taskname.lower() for task in tasks.values()):
            print("\n Error: Task name already exists. Please enter a different task name.\n")
        else:
            break  # Exit loop if task name is unique

    description = validate_input("Description: ")

    task_id = get_next_task_id(tasks)  # Generate new task ID
    tasks[str(task_id)] = {  # Store task with ID as key
        "taskid": task_id,
        "taskname": taskname,
        "description": description,
        "status": 0  
    }
    save_tasks(tasks)  
    print(f"\n Task '{taskname}' added with Task ID {task_id}.\n")


# def view_tasks():
#     tasks = load_tasks()
#     if tasks:
#         task_list = list(tasks.values())  
#         print("\n Task List:\n")
#         print(json.dumps(task_list, indent=4))  
#     else:
#         print("\n No tasks available.\n")

def view_tasks():
    tasks = load_tasks()
    if not tasks:
        print("\n No tasks available.\n")
        return
    
    # print("\nTask List:\n")
    # for task in tasks.values():
    #     print(f"Task ID    : {task['taskid']}")
    #     print(f"Task Name  : {task['taskname']}")
    #     print(f"Description: {task['description']}")
    #     print(f"Status     : {STATUS_CODES[task['status']]}")
    #     print("-" * 50)
    table_data = [[task["taskid"], task["taskname"], task["description"], STATUS_CODES[task["status"]]] for task in tasks.values()]
    
    print("\n" + tabulate(table_data, headers=["Task ID", "Task Name", "Description", "Status"], tablefmt="grid"))



def update_task_status():
    tasks = load_tasks()
    if not tasks:
        print("\n No tasks available to update.\n")
        return
    try:
        task_id = input("Enter Task ID to update status: ").strip()
        if task_id not in tasks:
            print("\n Task ID not found.\n")
            return

        print("\nSelect new status:")
        for code, status in STATUS_CODES.items():
            print(f"{code}: {status}")
        
        new_status = int(input("Enter status code (0-2): ").strip())
        if new_status not in STATUS_CODES:
            print("\n Invalid status code! Please enter 0, 1, or 2.\n")
            return

        # Update task status
        tasks[task_id]["status"] = new_status
        save_tasks(tasks)

        # Print updated task details
        updated_task = tasks[task_id]
        print("\n Task Updated Successfully:")
        print(f"Task ID    : {updated_task['taskid']}")
        print(f"Task Name  : {updated_task['taskname']}")
        print(f"Description: {updated_task['description']}")
        print(f"Status     : {STATUS_CODES[new_status]}\n")

    except ValueError:
        print("\n Invalid input! Please enter a number (0-2).\n")



def delete_task():
    tasks = load_tasks()
    if not tasks:
        print("\n No tasks available to delete.\n")
        return

    task_id = input("Enter Task ID to delete: ").strip()
    
    if task_id not in tasks:
        print("\n Task ID not found.\n")
        return

    confirmation = input(f"Are you sure you want to delete Task ID {task_id}? (yes/no): ").strip().lower()
    if confirmation == "yes":
        del tasks[task_id]  
        save_tasks(tasks)  
        print(f"\n Task ID {task_id} deleted successfully.\n")
    else:
        print("\n Task deletion canceled.\n")


def main():
    while True:
        print("\n To-Do List Menu")
        print("1. Add Task")
        print("2. View Tasks")
        print("3. Update Task Status")
        print("4. Delete Task") 
        print("5. Exit")
        choice = input("Enter your choice: ").strip()

        if choice == "1":
            add_task()
        elif choice == "2":
            view_tasks()
        elif choice == "3":
            update_task_status()
        elif choice == "4":
            delete_task()  
        elif choice == "5":
            print("\n Exiting the program. Have a great day!\n")
            break
        else:
            print("\n Invalid choice! Please enter a valid option (1-5).\n")


# Run the program
if __name__ == "__main__":
    main()
