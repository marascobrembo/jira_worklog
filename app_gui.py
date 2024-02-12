import logging
import customtkinter as ctk
from PIL import Image
from CTkMessagebox import CTkMessagebox

from app_data import AppData
from app_logic import AppLogic

from constants import MONTHS, USERS_LIST, JIRA_ICON_PATH, CHECK_ICON_PATH, CROSS_ICON_PATH
import text_handler as th


def select_file(excel_file_path: ctk.StringVar) -> None:
    file_path: str = ctk.filedialog.askopenfilename(
        filetypes=[("Excel File", "*.xlsx;*.xls")],
        initialdir=excel_file_path.get()
    )
    if file_path:
        excel_file_path.set(file_path)


class App:
    def __init__(self, data: AppData, app_logic: AppLogic):
        self.api_validity_icon = None
        self._app_data = data
        self._app_logic = app_logic
        self._gui = self.create_gui()
        # Collega la funzione on_closing all'evento di chiusura della finestra
        self._gui.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        # Salva la configurazione prima di chiudere
        self._app_data.save_config()
        # Chiudi la finestra
        self._gui.destroy()

    def create_gui(self):
        main_window = ctk.CTk()
        main_window.title("Jira workload logging tool")

        ctk.set_appearance_mode(self._app_data.appearance_theme)
        main_window.geometry("550x670")
        main_window.resizable(width=False, height=False)
        main_window.iconbitmap(True, JIRA_ICON_PATH)

        self._app_data.instantiate_view_variables()

        # Box for user and month selection
        user_month_selection_box = ctk.CTkFrame(main_window)
        user_month_selection_box.pack(pady=10, ipadx=10)

        # Label to ask to select user
        user_selection_label = ctk.CTkLabel(user_month_selection_box, text="Select user:")
        user_selection_label.grid(row=0, column=0, padx=10)

        # Dropdown menu to select the user
        user_selection_menu = ctk.CTkComboBox(user_month_selection_box,
                                              variable=self._app_data.selected_user_var,
                                              values=USERS_LIST,
                                              state="readonly")
        user_selection_menu.grid(row=0, column=1, padx=0, pady=10)

        # Label to ask to select month on which log hours
        month_selection_label = ctk.CTkLabel(
            user_month_selection_box, text="Select the month:")
        month_selection_label.grid(row=1, column=0, padx=10)

        month_selection_menu = ctk.CTkComboBox(user_month_selection_box,
                                               variable=self._app_data.selected_month_var,
                                               values=list(MONTHS.keys()),
                                               state="readonly")
        month_selection_menu.grid(row=1, column=1, padx=0, pady=10)

        # Box for Excel file selection
        excel_file_selection_box = ctk.CTkFrame(main_window)
        excel_file_selection_box.pack(pady=10, ipadx=30, ipady=10)

        # Label for Excel file
        excel_file_selection_label = ctk.CTkLabel(excel_file_selection_box, text="Select Excel File:")
        excel_file_selection_label.pack(pady=5)

        # Entry for displaying the file path (read-only)
        excel_file_selection_entry = ctk.CTkEntry(excel_file_selection_box, width=300, state="readonly",
                                                  textvariable=self._app_data.selected_file_path_var)
        excel_file_selection_entry.pack(pady=5)

        # Button to select the Excel file
        browse_excel_file_button = ctk.CTkButton(excel_file_selection_box, text="Browse File",
                                                 command=lambda: select_file(self._app_data.selected_file_path_var))
        browse_excel_file_button.pack(pady=5)

        # Box for API token setting
        api_setting_box = ctk.CTkFrame(main_window)
        api_setting_box.pack(pady=5, ipady=5)

        api_validity_label = ctk.CTkLabel(api_setting_box, text="API valid:")
        api_validity_label.grid(row=0, column=0, padx=10, pady=10)

        self.api_validity_icon = ctk.CTkLabel(api_setting_box)
        self.api_validity_icon.grid(row=0, column=1, padx=10, pady=10)
        self.update_api_status_icon()  # Function called in order to initialize icon at app launch

        set_api_token_button = ctk.CTkButton(api_setting_box, text="Set Jira API Token",
                                             command=self.open_token_window)
        set_api_token_button.grid(row=1, column=0, columnspan=2, padx=30, pady=10)

        # Button to start the worklog
        # TODO: enable/disable start button
        start_worklog_load_button = ctk.CTkButton(
            main_window,
            text="Load Worklog",
            command=self._app_logic.load_worklog_handler
        )
        start_worklog_load_button.pack(pady=20)

        # Text Logger box
        log_text = ctk.CTkTextbox(main_window, height=200, width=500, state="disabled", activate_scrollbars=True)
        log_text.pack(pady=10)

        # Create textLogger
        text_handler = th.TextHandler(log_text)

        # Add the handler to logger
        logger = logging.getLogger()
        logger.addHandler(text_handler)

        return main_window

    def update_api_status_icon(self):
        image_path = CHECK_ICON_PATH if self._app_data.is_api_token_valid else CROSS_ICON_PATH
        ctk_image = ctk.CTkImage(Image.open(image_path), size=(20, 20))
        self.api_validity_icon.configure(image=ctk_image, text="")

    def open_token_window(self):
        token_window = ctk.CTkToplevel(self._gui)
        token_window.wm_attributes("-topmost", True)
        token_window.title("Set Jira API Token")

        width = 330
        height = 100
        x = self._gui.winfo_rootx() + (self._gui.winfo_width() - width) // 2
        y = self._gui.winfo_rooty() + (self._gui.winfo_height() - height) // 2
        token_window.geometry(f"{width}x{height}+{x}+{y}")

        token_window.resizable(width=False, height=False)
        token_window.focus_set()

        token_label = ctk.CTkLabel(token_window, text="API token:")
        token_label.grid(row=0, column=0, padx=10, pady=10)

        _token_input = ctk.StringVar()
        token_entry = ctk.CTkEntry(token_window, textvariable=_token_input)
        token_entry.grid(row=0, column=1, padx=10, pady=10)
        if self._app_data.api_key_token:
            token_entry.insert(0, self._app_data.api_key_token)

        ok_button = ctk.CTkButton(token_window, text="OK",
                                  command=lambda: self.save_token(token_window, _token_input.get()))
        ok_button.grid(row=1, column=0, padx=10, pady=10)

        cancel_button = ctk.CTkButton(token_window, text="Cancel", command=token_window.destroy)
        cancel_button.grid(row=1, column=1, padx=10, pady=10)

    def save_token(self, token_window: ctk.CTkToplevel, token_value: str) -> None:
        token_window.destroy()
        if token_value is not None:
            self._app_data.api_key_token = token_value
            self._app_logic.check_api_token_validity()
            if self._app_data.is_api_token_valid:
                CTkMessagebox(title="Success",
                              message="Valid token, login successfully completed.",
                              icon="check")
        else:
            CTkMessagebox(title="Error",
                          message="Invalid token. Please, try again.",
                          icon="cancel")
        self.update_api_status_icon()

    def show_window(self):
        self._gui.mainloop()
