import argparse
import socket
import time
from typing import Dict, List, Optional
from tkinter import LEFT, Canvas, Frame, Label, Listbox, Tk

from db import DB
from server import ResourceServer


BG = "#101418"
PANEL = "#182027"
PANEL_SOFT = "#202a33"
TEXT = "#eef4f7"
MUTED = "#8fa1ad"
GRID = "#2d3942"
CPU = "#38bdf8"
RAM = "#f59e0b"
DISK = "#a3e635"
NET = "#f472b6"
OK = "#34d399"
WARN = "#fb7185"


class MetricCard(Frame):
    def __init__(self, parent, title: str, color: str, unit: str = "%"):
        super().__init__(parent, bg=PANEL, highlightthickness=1, highlightbackground=GRID)
        self.color = color
        self.unit = unit
        self.values: List[float] = []
        self.max_value = 100.0

        self.columnconfigure(0, weight=1)
        Label(self, text=title.upper(), bg=PANEL, fg=MUTED, font=("DejaVu Sans", 10, "bold")).grid(
            row=0, column=0, sticky="w", padx=14, pady=(12, 0)
        )
        self.value_label = Label(
            self,
            text="--",
            bg=PANEL,
            fg=TEXT,
            font=("DejaVu Sans", 26, "bold"),
            anchor="w",
        )
        self.value_label.grid(row=1, column=0, sticky="ew", padx=14, pady=(2, 0))
        self.detail_label = Label(
            self,
            text="Waiting for data",
            bg=PANEL,
            fg=MUTED,
            font=("DejaVu Sans", 9),
            anchor="w",
        )
        self.detail_label.grid(row=2, column=0, sticky="ew", padx=14)
        self.canvas = Canvas(self, height=72, bg=PANEL, highlightthickness=0)
        self.canvas.grid(row=3, column=0, sticky="ew", padx=10, pady=(4, 10))
        self.canvas.bind("<Configure>", lambda _event: self.draw())

    def update_metric(
        self,
        current: Optional[float],
        values: List[float],
        max_value: float,
        detail: str,
        unit: Optional[str] = None,
    ) -> None:
        self.values = values[-60:]
        self.max_value = max(max_value, 1)
        display_unit = unit if unit is not None else self.unit
        self.value_label.configure(text=format_value(current, display_unit))
        self.detail_label.configure(text=detail)
        self.draw()

    def draw(self) -> None:
        self.canvas.delete("all")
        width = max(self.canvas.winfo_width(), 10)
        height = max(self.canvas.winfo_height(), 10)

        for ratio in (0.25, 0.5, 0.75):
            y = height * ratio
            self.canvas.create_line(0, y, width, y, fill=GRID)

        if len(self.values) < 2:
            return

        denominator = max(self.max_value, max(self.values), 1)
        step = width / (len(self.values) - 1)
        points = []
        for index, value in enumerate(self.values):
            x = index * step
            y = height - ((max(value, 0) / denominator) * (height - 8)) - 4
            points.extend((x, y))

        self.canvas.create_line(points, fill=self.color, width=3, smooth=True)


class Dashboard:
    def __init__(self, root: Tk, db_path: str, server: ResourceServer):
        self.root = root
        self.db = DB(db_path)
        self.server = server
        self.selected_ip: Optional[str] = None
        self.client_rows: List[Dict] = []

        root.title("Resource Monitor")
        root.configure(bg=BG)
        root.geometry("800x480")
        root.minsize(800, 480)
        root.protocol("WM_DELETE_WINDOW", self.close)

        self._build_layout()
        self.server.start_in_thread()
        self.refresh()

    def _build_layout(self) -> None:
        self.root.columnconfigure(0, weight=0, minsize=220)
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(1, weight=1)

        header = Frame(self.root, bg=BG)
        header.grid(row=0, column=0, columnspan=2, sticky="ew", padx=16, pady=(14, 8))
        header.columnconfigure(0, weight=1)

        Label(
            header,
            text="Resource Monitor",
            bg=BG,
            fg=TEXT,
            font=("DejaVu Sans", 22, "bold"),
            anchor="w",
        ).grid(row=0, column=0, sticky="w")
        self.status_label = Label(
            header,
            text=f"Listening on {socket.gethostname()}:{self.server.port}",
            bg=BG,
            fg=MUTED,
            font=("DejaVu Sans", 10),
            anchor="e",
        )
        self.status_label.grid(row=0, column=1, sticky="e")

        sidebar = Frame(self.root, bg=PANEL_SOFT, highlightthickness=1, highlightbackground=GRID)
        sidebar.grid(row=1, column=0, sticky="nsew", padx=(16, 8), pady=(0, 16))
        sidebar.rowconfigure(1, weight=1)
        sidebar.columnconfigure(0, weight=1)

        Label(
            sidebar,
            text="CLIENTS",
            bg=PANEL_SOFT,
            fg=MUTED,
            font=("DejaVu Sans", 10, "bold"),
            anchor="w",
        ).grid(row=0, column=0, sticky="ew", padx=12, pady=(12, 6))
        self.client_list = Listbox(
            sidebar,
            bg=PANEL_SOFT,
            fg=TEXT,
            selectbackground=CPU,
            selectforeground="#071014",
            activestyle="none",
            highlightthickness=0,
            bd=0,
            font=("DejaVu Sans", 11),
        )
        self.client_list.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 8))
        self.client_list.bind("<<ListboxSelect>>", self.on_client_select)
        self.client_detail = Label(
            sidebar,
            text="No clients connected",
            bg=PANEL_SOFT,
            fg=MUTED,
            font=("DejaVu Sans", 9),
            justify=LEFT,
            anchor="w",
        )
        self.client_detail.grid(row=2, column=0, sticky="ew", padx=12, pady=(0, 12))

        content = Frame(self.root, bg=BG)
        content.grid(row=1, column=1, sticky="nsew", padx=(8, 16), pady=(0, 16))
        for row in range(2):
            content.rowconfigure(row, weight=1, uniform="cards")
        for col in range(2):
            content.columnconfigure(col, weight=1, uniform="cards")

        self.cpu_card = MetricCard(content, "CPU", CPU)
        self.ram_card = MetricCard(content, "Memory", RAM)
        self.disk_card = MetricCard(content, "Disk", DISK)
        self.net_card = MetricCard(content, "Network", NET, "B/s")

        self.cpu_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8), pady=(0, 8))
        self.ram_card.grid(row=0, column=1, sticky="nsew", padx=(8, 0), pady=(0, 8))
        self.disk_card.grid(row=1, column=0, sticky="nsew", padx=(0, 8), pady=(8, 0))
        self.net_card.grid(row=1, column=1, sticky="nsew", padx=(8, 0), pady=(8, 0))

    def on_client_select(self, _event=None) -> None:
        selection = self.client_list.curselection()
        if selection:
            self.selected_ip = self.client_rows[selection[0]].get("client_ip")
            self.refresh()

    def refresh(self) -> None:
        self.client_rows = self.db.list_clients()
        if self.selected_ip and not any(
            row.get("client_ip") == self.selected_ip for row in self.client_rows
        ):
            self.selected_ip = None

        if not self.selected_ip and self.client_rows:
            self.selected_ip = self.client_rows[0].get("client_ip")

        self._refresh_client_list()
        latest = self.db.get_latest_client_data(self.selected_ip) if self.selected_ip else None
        history = self.db.get_client_data(self.selected_ip, 60) if self.selected_ip else []
        self._refresh_metrics(latest, history)
        self.root.after(1000, self.refresh)

    def _refresh_client_list(self) -> None:
        current_selection = self.selected_ip
        self.client_list.delete(0, "end")
        for index, row in enumerate(self.client_rows):
            name = row.get("client_hostname") or "Unknown"
            ip = row.get("client_ip") or "No IP"
            age = time.time() - float(row.get("observed_at") or 0)
            marker = "*" if age <= 5 else " "
            self.client_list.insert("end", f"{marker} {name}  {ip}")
            if ip == current_selection:
                self.client_list.selection_set(index)

    def _refresh_metrics(self, latest: Optional[Dict], history: List[Dict]) -> None:
        if not latest:
            self.status_label.configure(text="Listening for clients on port 4000", fg=MUTED)
            self.client_detail.configure(text="Run: python client.py <pi-ip>")
            for card in (self.cpu_card, self.ram_card, self.disk_card, self.net_card):
                card.update_metric(None, [], 100, "Waiting for data")
            return

        age = time.time() - float(latest.get("observed_at") or 0)
        status_color = OK if age <= 5 else WARN
        status_text = "Live" if age <= 5 else f"Last update {int(age)}s ago"
        self.status_label.configure(text=status_text, fg=status_color)

        name = latest.get("client_hostname") or "Unknown"
        ip = latest.get("client_ip") or "No IP"
        iface = latest.get("ip_type") or "unknown"
        self.client_detail.configure(text=f"{name}\n{ip} via {iface}")

        cpu_values = [float(row.get("cpu_usage") or 0) for row in history]
        ram_values = [float(row.get("memory_usage") or 0) for row in history]
        disk_values = [float(row.get("disk_usage") or 0) for row in history]
        net_values = [
            float(row.get("net_sent_rate") or 0) + float(row.get("net_recv_rate") or 0)
            for row in history
        ]

        total_memory = float(latest.get("total_memory") or max(ram_values or [1]))
        total_disk = float(latest.get("total_disk") or max(disk_values or [1]))
        net_current = net_values[-1] if net_values else 0

        self.cpu_card.update_metric(
            float(latest.get("cpu_usage") or 0),
            cpu_values,
            100,
            "Processor load over the last minute",
        )
        self.ram_card.update_metric(
            float(latest.get("memory_usage") or 0),
            ram_values,
            total_memory,
            f"of {total_memory:.1f} GB",
            "GB",
        )
        self.disk_card.update_metric(
            float(latest.get("disk_usage") or 0),
            disk_values,
            total_disk,
            f"of {total_disk:.1f} GB",
            "GB",
        )
        self.net_card.update_metric(
            net_current,
            net_values,
            max(max(net_values or [1]), 1),
            "Combined send and receive rate",
            "B/s",
        )

    def close(self) -> None:
        self.server.stop()
        self.db.close()
        self.root.destroy()


def format_value(value: Optional[float], unit: str) -> str:
    if value is None:
        return "--"
    if unit == "%":
        return f"{value:.0f}%"
    if unit == "GB":
        return f"{value:.1f} GB"
    if unit == "B/s":
        return format_rate(value)
    return f"{value:.1f} {unit}"


def format_rate(value: float) -> str:
    units = ["B/s", "KB/s", "MB/s", "GB/s"]
    rate = float(value)
    for unit in units:
        if rate < 1024 or unit == units[-1]:
            return f"{rate:.1f} {unit}" if unit != "B/s" else f"{rate:.0f} {unit}"
        rate /= 1024
    return f"{rate:.0f} B/s"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the Raspberry Pi resource monitor GUI.")
    parser.add_argument("--host", default="")
    parser.add_argument("--port", type=int, default=4000)
    parser.add_argument("--db", default="resources.db")
    parser.add_argument("--fullscreen", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    server = ResourceServer(args.host, args.port, args.db)
    root = Tk()
    if args.fullscreen:
        root.attributes("-fullscreen", True)
        root.bind("<Escape>", lambda _event: root.attributes("-fullscreen", False))
    Dashboard(root, args.db, server)
    root.mainloop()


if __name__ == "__main__":
    main()
