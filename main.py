import tkinter
from tkinter import ttk
from dotenv import load_dotenv
from poller import Poller
from datetime import datetime
import os
from sl_api import check_sl

load_dotenv()
CALENDAR_ID = os.getenv("CALENDAR_ID")

class App(tkinter.Tk):
    def __init__(self):
        super().__init__()
        self.title("Stonify Watcher")
        self.iconbitmap("eye_icon.ico")
        self.geometry("500x500")
        self.attributes("-topmost", True)
        self.resizable(False, False)
        self.configure(bg="#0d1117")

        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TLabel", background="#0d1117", foreground="#e6edf3")
        style.configure("TButton", background="#1f6feb", foreground="#e6edf3")
        style.map("TButton", background=[("active", "#388bfd")])
        style.configure("TEntry", background="#161b22", fieldbackground="#161b22", foreground="#e6edf3", bordercolor="#161b22")
        style.configure("Treeview", background="#161b22", fieldbackground="#161b22", foreground="#e6edf3")
        style.configure("Treeview.Heading", background="#0d1117", foreground="#8b949e")

        lbl_token = ttk.Label(self, text="Session Token")
        lbl_token.pack(pady=5)

        self.entry_token = ttk.Entry(self, width=50, show="*")
        self.entry_token.pack(pady=5)

        lbl_btoken = ttk.Label(self, text="SpeedLabel Token")
        lbl_btoken.pack(pady=5)

        self.entry_btoken = ttk.Entry(self, width=50, show="*")
        self.entry_btoken.pack(pady=5)

        lbl_interval = ttk.Label(self, text="Interval: (minutes)")
        lbl_interval.pack(pady=5)

        self.entry_interval = ttk.Entry(self, width=10)
        self.entry_interval.pack(pady=5)

        self.btn_start = ttk.Button(self, text="Start", command=self.start_polling)
        self.btn_start.pack(pady=10)

        self.btn_update = ttk.Button(self, text="Refresh", command=self.force_update)
        self.btn_update.pack(pady=10)

        self.lbl_update = ttk.Label(self, text="Last Update: ")
        self.lbl_update.pack(pady=5)

        self.tree = ttk.Treeview(self, columns=("Project", "CAD Tech", "Description", "SpeedLabel"), show="headings")
        self.tree.heading("Project", text="Project")
        self.tree.column("Project", width=80)
        self.tree.heading("CAD Tech", text="CAD Tech")
        self.tree.column("CAD Tech", width=100)
        self.tree.heading("Description", text="Description")
        self.tree.column("Description", width=150)
        self.tree.heading("SpeedLabel", text="SpeedLabel?")
        self.tree.column("SpeedLabel", width=80)
        self.tree.pack(fill="both", expand=True)
        self.tree.tag_configure("new", background="#388bfd", foreground="#0d1117")

        self.known_jobs = set()

        self.poller = None

    def start_polling(self):
        token = self.entry_token.get()
        secs = int(self.entry_interval.get()) * 60
        self.poller = Poller(token, CALENDAR_ID, secs, on_update=self.update_display)
        self.poller.start()

    def force_update(self):
        if self.poller:
            self.poller._tick()

    def update_display(self, jobs):
        self.tree.delete(*self.tree.get_children())
        lst_update = datetime.now().strftime("%H:%M:%S")
        self.lbl_update.config(text=f"Last Update: {lst_update} ")
        current_ids = {job["project"] for job in jobs}
        new_ids = current_ids.difference(self.known_jobs)
        b_token = self.entry_btoken.get()

        for job in jobs:
            description = f"{(job['description'] or '').replace('\n', ' ')}"

            if job["project"] in new_ids:
                if check_sl(job["project"], b_token) == False:
                    status = "Missing"
                else:
                    status = "Good"
                self.tree.insert("", "end", values=(job["project"], job["assignee"], description, status), tags=("new",))
                self.known_jobs.add(job["project"])
            else:
                self.tree.insert("", "end", values=(job["project"], job["assignee"], description, ""))
        self.known_jobs = current_ids

app = App()
app.mainloop()
