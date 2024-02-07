import tkinter as tk
from tkinter import StringVar, filedialog

import jira_log_manager as jm

MONTHS: dict[str, int] = {
    "January": 1,
    "February": 2,
    "March": 3,
    "April": 4,
    "May": 5,
    "June": 6,
    "July": 7,
    "August": 8,
    "September": 9,
    "October": 10,
    "November": 11,
    "December": 12,
}

PERSONS: list[str] = [
    "Longoni Samuele",
    "Papi Lorenzo",
    "Perrino Francesco",
    "Di Palma Federico",
    "Marasco Leonardo",
    "Iuculano Matilde",
    "Panzeri Samuele",
]


def select_file(file_path_string: StringVar) -> None:
    file_path: str = filedialog.askopenfilename(
        filetypes=[("Excel File", "*.xlsx;*.xls")]
    )
    file_path_string.set(file_path)


def load_worklog_handler(file_entry, month_var, person_var) -> None:
    file_path: str = file_entry.get()
    selected_month: int = MONTHS[month_var.get()]
    selected_person = person_var.get()

    print("Excel file path:", file_path)
    print("Selected month:", selected_month)
    print("Selected person:", selected_person)

    jm.load_worklog(file_path, selected_month, selected_person)

    print("Worklog loaded!")


def main() -> None:
    root = tk.Tk()
    root.title("Jira Support Tool")

    # Label for Excel file
    file_label = tk.Label(root, text="Select Excel File:")
    file_label.pack(pady=10)

    # Entry for displaying the file path (read-only)
    file_path = StringVar()
    file_entry = tk.Entry(root, width=40, state="readonly", textvariable=file_path)
    file_entry.pack(pady=10)

    # Button to select the Excel file
    file_button = tk.Button(root, text="Browse", command=lambda: select_file(file_path))
    file_button.pack(pady=10)

    # Label for month
    month_label = tk.Label(root, text="Select the Month:")
    month_label.pack(pady=10)

    # Dropdown menu to select the month
    month_var = tk.StringVar(root)
    month_var.set(list(MONTHS.keys())[0])  # Set the default month
    month_menu = tk.OptionMenu(root, month_var, *list(MONTHS.keys()))
    month_menu.pack(pady=10)

    # Label for person
    person_label = tk.Label(root, text="Select the Person:")
    person_label.pack(pady=10)

    # Dropdown menu to select the person
    person_var = tk.StringVar(root)
    person_var.set(PERSONS[0])  # Set the default person
    person_menu = tk.OptionMenu(root, person_var, *PERSONS)
    person_menu.pack(pady=10)

    # Button to load the worklog
    load_button = tk.Button(
        root,
        text="Load Worklog",
        command=lambda: load_worklog_handler(file_entry, month_var, person_var),
    )
    load_button.pack(pady=20)

    root.mainloop()


if __name__ == "__main__":
    main()
