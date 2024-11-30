import tkinter as tk
from tkinter import ttk, filedialog
import random


class FlightManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Flight Manager")
        self.root.geometry("900x600")
        self.flights = []  # Store flights as dictionaries
        self.used_squawk_codes = set()  # To track already used squawk codes

        # Colors
        self.bg_color = "#1B3B6F"  # Background color (dark blue)
        self.text_color = "#000000"  # Text color (white)
        self.button_color = "#4A90E2"  # Button color (light blue)
        self.highlight_color = "#D6E4F0"  # Highlight color (very light blue)

        # Apply background color
        self.root.configure(bg=self.bg_color)

        # Create UI
        self.create_ui()

    def create_ui(self):
        # Title
        title_label = tk.Label(
            self.root,
            text="Flight Manager",
            font=("Arial", 24, "bold"),
            bg=self.bg_color,
            fg=self.text_color
        )
        title_label.pack(fill="x", pady=10)

        # Input Frame (for entering flight details manually)
        input_frame = tk.Frame(self.root, bg=self.bg_color)
        input_frame.pack(fill="x", pady=10, padx=10)

        self.fields = ["Username", "Callsign", "Aircraft", "Flight Rules", "Departing", "Arriving", "Route", "Flight Level"]
        self.input_entries = {}

        for idx, field in enumerate(self.fields):
            label = tk.Label(input_frame, text=field, font=("Arial", 12), bg=self.bg_color, fg=self.text_color)
            label.grid(row=0, column=idx, padx=5, pady=5)
            entry = ttk.Entry(input_frame, font=("Arial", 12), width=12)
            entry.grid(row=1, column=idx, padx=5, pady=5)
            self.input_entries[field] = entry

        # Buttons
        button_frame = tk.Frame(self.root, bg=self.bg_color)
        button_frame.pack(fill="x", pady=10)

        button_style = ttk.Style()
        button_style.configure("TButton", background=self.button_color, foreground=self.text_color, padding=6, font=("Arial", 11, "bold"))
        button_style.map("TButton", background=[("active", "#3566A8")])  # Button hover effect

        ttk.Button(button_frame, text="Add Flight", command=self.add_flight).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Edit Selected", command=self.edit_selected_flight).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Delete Selected", command=self.delete_flight).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Move Up", command=lambda: self.move_flight(-1)).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Move Down", command=lambda: self.move_flight(1)).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Download Log", command=self.download_log).pack(side="left", padx=5)

        # Auto-paste Flight Textbox
        paste_label = tk.Label(self.root, text="Auto-Paste Flight Details (Copy-Paste below):", font=("Arial", 12), bg=self.bg_color, fg=self.text_color)
        paste_label.pack(pady=10)

        self.paste_text = tk.Text(self.root, height=8, width=80, font=("Arial", 12), bg="#F0F8FF", fg="black", highlightbackground=self.bg_color)
        self.paste_text.pack(pady=5)

        ttk.Button(self.root, text="Auto-Paste Flight", command=self.auto_paste_flight).pack(pady=5)

        # Flight List (Including Squawk column)
        self.fields.append("Squawk")  # Add Squawk to fields list
        tree_frame = tk.Frame(self.root, bg=self.bg_color)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.tree = ttk.Treeview(tree_frame, columns=self.fields, show="headings", height=15)
        self.tree.pack(fill="both", expand=True, side="left")

        for col in self.fields:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=100)

        # Add vertical scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

    def add_flight(self):
        flight = {field: self.input_entries[field].get().strip() for field in self.fields if field != "Squawk"}
        if any(value == "" for value in flight.values()):
            self.display_message("All fields must be filled!")
            return
        
        # Generate and add squawk code
        squawk_code = self.generate_squawk_code(flight["Flight Rules"])
        flight["Squawk"] = squawk_code
        
        self.flights.append(flight)
        self.update_tree()
        self.clear_inputs()

    def generate_squawk_code(self, flight_rules):
        if flight_rules == "VFR":
            return "1200"
        else:
            # Generate a random squawk code between 1000 and 7777
            while True:
                squawk_code = str(random.randint(1000, 7777))
                # Ensure the squawk code is not 7500, 7600, or 7700 and hasn't been used
                if squawk_code not in {"7500", "7600", "7700"} and squawk_code not in self.used_squawk_codes:
                    self.used_squawk_codes.add(squawk_code)
                    return squawk_code

    def edit_selected_flight(self):
        selected_item = self.tree.selection()
        if not selected_item:
            self.display_message("Please select a flight to edit.")
            return

        index = self.tree.index(selected_item[0])
        flight = self.flights[index]

        # Populate input fields with selected flight details
        for field, value in flight.items():
            self.input_entries[field].delete(0, tk.END)
            self.input_entries[field].insert(0, value)

    def delete_flight(self):
        selected_item = self.tree.selection()
        if not selected_item:
            self.display_message("Please select a flight to delete.")
            return

        index = self.tree.index(selected_item[0])
        del self.flights[index]
        self.update_tree()

    def move_flight(self, direction):
        selected_item = self.tree.selection()
        if not selected_item:
            self.display_message("Please select a flight to move.")
            return

        index = self.tree.index(selected_item[0])
        new_index = index + direction
        if 0 <= new_index < len(self.flights):
            self.flights[index], self.flights[new_index] = self.flights[new_index], self.flights[index]
            self.update_tree()
            self.tree.selection_set(self.tree.get_children()[new_index])

    def update_tree(self):
        # Clear Treeview
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Add Flights to Treeview
        for flight in self.flights:
            self.tree.insert("", "end", values=tuple(flight[field] for field in self.fields))

    def download_log(self):
        if not self.flights:
            self.display_message("No flights to log.")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")], title="Save Log File")
        if not file_path:  # User canceled
            return

        try:
            with open(file_path, "w") as file:
                for flight in self.flights:
                    for key, value in flight.items():
                        file.write(f"{key}: {value}\n")
                    file.write("\n")  # Add a blank line between flights
            self.display_message(f"Log saved successfully to {file_path}")
        except Exception as e:
            self.display_message(f"Error saving log: {str(e)}")

    def auto_paste_flight(self):
        raw_input = self.paste_text.get("1.0", "end-1c").strip()
        if not raw_input:
            self.display_message("Please paste flight details to import.")
            return

        try:
            details = self.parse_flight_input(raw_input)
            # Generate and add squawk code
            squawk_code = self.generate_squawk_code(details["Flight Rules"])
            details["Squawk"] = squawk_code
            self.flights.append(details)
            self.update_tree()
            self.paste_text.delete(1.0, "end")
            self.display_message("Flight added successfully!")
        except ValueError as e:
            self.display_message(f"Error: {str(e)}")

    def parse_flight_input(self, raw_input):
        """Parses the pasted flight details into a dictionary."""
        details = {}
        try:
            lines = raw_input.strip().split("\n")
            for line in lines:
                key, value = line.split(":", 1)
                key = key.strip()
                value = value.strip()
                details[key] = value

            # Ensure all required keys are present
            required_keys = ["Username", "Callsign", "Aircraft", "Flight Rules", "Departing", "Arriving", "Route", "Flight Level"]
            for key in required_keys:
                if key not in details:
                    raise ValueError(f"Missing required field: {key}")

            return details
        except Exception as e:
            raise ValueError("Invalid format. Please ensure the input matches the required format.") from e

    def display_message(self, message):
        """Displays a message below the input fields."""
        message_label = tk.Label(self.root, text=message, font=("Arial", 12), bg=self.bg_color, fg="red")
        message_label.pack(pady=5, after=self.tree)
        self.root.after(3000, message_label.destroy)  # Remove after 3 seconds

    def clear_inputs(self):
        for field in self.fields:
            self.input_entries[field].delete(0, tk.END)


# Run the Application
if __name__ == "__main__":
    root = tk.Tk()
    app = FlightManagerApp(root)
    root.mainloop()