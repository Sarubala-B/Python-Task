import json
import os
import re
from tabulate import tabulate
from dataclasses import dataclass

# Directory to store task files
DATA_FOLDER = "data"
TODO_FILE = os.path.join(DATA_FOLDER, "tasks.json")


@dataclass(frozen=True)
class TaskStatus:
    PENDING: int = 0
    IN_PROGRESS: int = 1
    COMPLETED: int = 2

    @staticmethod
    def get_status_name(code: int) -> str:
        status_map = {
            None: "Not Assigned",  # If the status is None, show "Not Assigned"
            TaskStatus.PENDING: "Pending",
            TaskStatus.IN_PROGRESS: "In Progress",
            TaskStatus.COMPLETED: "Completed"
        }
        return status_map.get(code, "Unknown Status")



class FileHandler:
    @staticmethod
    def ensure_folder_exists():
        if not os.path.exists(DATA_FOLDER):
            os.makedirs(DATA_FOLDER)

    @staticmethod
    def load_tasks(filename):
        FileHandler.ensure_folder_exists()  # Ensure folder exists before accessing the file
        if not os.path.exists(filename):
            return []
        try:
            with open(filename, "r") as file:
                tasks = json.load(file)
                return tasks if isinstance(tasks, list) else []
        except (json.JSONDecodeError, ValueError):
            return []

    @staticmethod
    def save_tasks(filename, tasks):
        FileHandler.ensure_folder_exists()  # Ensure folder exists before writing
        with open(filename, "w") as file:
            json.dump(tasks, file, indent=4)


class TaskValidator:
    @staticmethod
    def validate_input(prompt, is_taskname=False, is_description=False):
        while True:
            value = input(prompt).strip()
            if not value:
                print("Input cannot be empty. Please enter a valid value.")
                continue

            if is_taskname and not re.match(r"^[A-Za-z0-9 ]{1,20}$", value):
                print("Error: Task name can only contain letters, numbers, and spaces (max 20 characters).")
                continue

            if is_description and not re.search(r"[A-Za-z0-9]", value):
                print("Error: Description must contain at least one letter or number.")
                continue
            return value


class TaskManager:
    def __init__(self, filename=TODO_FILE):
        self.filename = filename
        self.tasks = FileHandler.load_tasks(self.filename)

    def save_tasks(self):
        FileHandler.save_tasks(self.filename, self.tasks)

    def get_next_task_id(self):
        return max([task["taskid"] for task in self.tasks], default=0) + 1

    def add_task(self):
        taskname = TaskValidator.validate_input("Task Name: ", is_taskname=True)
        description = TaskValidator.validate_input("Description: ", is_description=True)
        task_id = self.get_next_task_id()

        self.tasks.append({
            "taskid": task_id,
            "taskname": taskname,
            "description": description,
             "status": None
        })
        self.save_tasks()
        print(f"\nTask '{taskname}' added with Task ID {task_id}.\n")

    def view_all_tasks(self):
        if not self.tasks:
            print("\nNo tasks available.\n")
            return

        print("\n Overall Task List:\n")
        table_data = [
            [task["taskid"], task["taskname"], task["description"], TaskStatus.get_status_name(task["status"])]
            for task in self.tasks
        ]
        print(tabulate(table_data, headers=["Task ID", "Task Name", "Description", "Status"], tablefmt="grid"))
        print("\n" + "=" * 50 + "\n")

    def view_tasks_by_name(self):
        if not self.tasks:
            print("\nNo tasks available.\n")
            return

        task_name_groups = {}
        for task in self.tasks:
            task_name_groups.setdefault(task["taskname"], []).append(task)

        print("\n Tasks Grouped by Task Name:\n")
        for taskname, tasks in task_name_groups.items():
            print(f"🔹 Task Name: '{taskname}'")
            table_data = [
                [task["taskid"], task["description"], TaskStatus.get_status_name(task["status"])]
                for task in tasks
            ]
            print(tabulate(table_data, headers=["Task ID", "Description", "Status"], tablefmt="grid"))
            print("\n" + "=" * 50 + "\n")

    def view_tasks_by_status(self):
        if not self.tasks:
            print("\nNo tasks available.\n")
            return

        status_groups = {}
        for task in self.tasks:
            status_groups.setdefault(task["status"], []).append(task)

        print("\n Tasks Grouped by Status:\n")
        for status, tasks in status_groups.items():
            print(f"🔹 Status: '{TaskStatus.get_status_name(status)}'")
            table_data = [
                [task["taskid"], task["taskname"], task["description"]]
                for task in tasks
            ]
            print(tabulate(table_data, headers=["Task ID", "Task Name", "Description"], tablefmt="grid"))
            print("\n" + "=" * 50 + "\n")

    def update_task(self):
        if not self.tasks:
            print("\nNo tasks available to update.\n")
            return

        try:
            task_id = int(input("Enter Task ID to update: ").strip())
        except ValueError:
            print("\nInvalid Task ID. Please enter a valid number.\n")
            return

        task = next((t for t in self.tasks if t["taskid"] == task_id), None)
        if not task:
            print("\nTask ID not found.\n")
            return

        new_taskname = input("Enter new task name (leave empty to keep current name): ").strip()
        if new_taskname:
            task["taskname"] = new_taskname

        new_description = input("Enter new description (leave empty to keep current description): ").strip()
        if new_description:
            task["description"] = new_description

        print("\nSelect new status:")
        for status_code in [TaskStatus.PENDING, TaskStatus.IN_PROGRESS, TaskStatus.COMPLETED]:
            print(f"{status_code}: {TaskStatus.get_status_name(status_code)}")

        try:
            new_status = int(input("Enter status code (0-2): ").strip())
            if new_status in [TaskStatus.PENDING, TaskStatus.IN_PROGRESS, TaskStatus.COMPLETED]:
                task["status"] = new_status
                self.save_tasks()
                print("\nTask Updated Successfully.\n")
            else:
                print("\nInvalid status code! Please enter 0, 1, or 2.\n")
        except ValueError:
            print("\nInvalid input! Please enter a number (0-2).\n")

    def delete_task(self):
        if not self.tasks:
            print("\nNo tasks available to delete.\n")
            return

        try:
            task_id = int(input("Enter Task ID to delete: ").strip())
        except ValueError:
            print("\nInvalid Task ID. Please enter a valid number.\n")
            return

        task = next((t for t in self.tasks if t["taskid"] == task_id), None)
        if not task:
            print("\nTask ID not found.\n")
            return

        if task["status"] != TaskStatus.COMPLETED:
            print("\nTask cannot be deleted because it is not completed.\n")
            return

        self.tasks.remove(task)
        self.save_tasks()
        print(f"\nTask ID {task_id} deleted successfully.\n")


class ToDoApp:
    def __init__(self):
        self.task_manager = TaskManager()

    def main(self):
        options = {
            "1": self.task_manager.add_task,
            "2": self.task_manager.view_all_tasks,
            "3": self.task_manager.view_tasks_by_name,
            "4": self.task_manager.view_tasks_by_status,
            "5": self.task_manager.update_task,
            "6": self.task_manager.delete_task,
            "7": lambda: exit("\nExiting the program. Have a great day!\n")
        }

        while True:
            print("\nTo-Do List Menu")
            for k, v in options.items():
                print(f"{k}. {v.__name__.replace('_', ' ').title()}")
            choice = input("Enter your choice: ").strip()
            options.get(choice, lambda: print("\nInvalid choice!"))()


if __name__ == "__main__":
    ToDoApp().main()
