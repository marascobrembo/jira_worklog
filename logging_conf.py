import logging
import customtkinter


class TextHandler(logging.Handler):
    """This class allows you to log to a Tkinter Text or ScrolledText widget."""

    def __init__(self, text: customtkinter.CTkTextbox):
        # run the regular Handler __init__
        logging.Handler.__init__(self)
        # Store a reference to the Text it will log to
        self.text: customtkinter.CTkTextbox = text

    def emit(self, record) -> None:
        msg: str = self.format(record)

        def append() -> None:
            self.text.configure(state="normal")
            self.text.insert(customtkinter.END, msg + "\n")
            self.text.configure(state="disabled")

            # Autoscroll to the bottom
            self.text.yview(customtkinter.END)

        # This is necessary because we can't modify the Text from other threads
        self.text.after(0, append)


logger: logging.Logger = logging.getLogger()


def setup_logging() -> None:
    # Basic logger configuration
    logging.basicConfig(
        filename="issue_not_map.log",
        filemode="w",
        level=logging.INFO,
    )
