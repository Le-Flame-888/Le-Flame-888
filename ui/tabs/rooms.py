# ui/tabs/rooms.py
import tkinter as tk
from tkinter import ttk, messagebox
from database.config import logger

class RoomsTab(ttk.Frame):
    def __init__(self, parent, db_connection):
        super().__init__(parent)
        self.db = db_connection
        self.setup_ui()
        self.load_rooms()

    def setup_ui(self):
        # Create main frames
        self.form_frame = self.create_form_frame()
        self.list_frame = self.create_list_frame()

        # Layout frames
        self.form_frame.grid(row=0, column=0, padx=20, pady=10, sticky="nsew")
        self.list_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")

    def create_form_frame(self):
        frame = ttk.LabelFrame(self, text="Room Management")

        # Room Number
        ttk.Label(frame, text="Room Number:").grid(row=0, column=0, padx=5, pady=5)
        self.room_number = ttk.Entry(frame)
        self.room_number.grid(row=0, column=1, padx=5, pady=5)

        # Room Type
        ttk.Label(frame, text="Room Type:").grid(row=1, column=0, padx=5, pady=5)
        self.room_type = ttk.Combobox(frame, values=["Standard", "Deluxe", "Suite"])
        self.room_type.grid(row=1, column=1, padx=5, pady=5)

        # Rate
        ttk.Label(frame, text="Rate ($):").grid(row=2, column=0, padx=5, pady=5)
        self.rate = ttk.Entry(frame)
        self.rate.grid(row=2, column=1, padx=5, pady=5)

        # Description
        ttk.Label(frame, text="Description:").grid(row=3, column=0, padx=5, pady=5)
        self.description = tk.Text(frame, height=3, width=30)
        self.description.grid(row=3, column=1, padx=5, pady=5)

        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)

        ttk.Button(button_frame, text="Add Room", command=self.add_room).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Update Room", command=self.update_room).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Delete Room", command=self.delete_room).pack(side=tk.LEFT, padx=5)

        return frame

    def create_list_frame(self):
        frame = ttk.LabelFrame(self, text="Room List")

        # Create Treeview
        columns = ('Room Number', 'Type', 'Rate', 'Status', 'Description')
        self.tree = ttk.Treeview(frame, columns=columns, show='headings')

        # Add column headings
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)

        # Add scrollbars
        vsb = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        # Grid layout
        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')

        # Configure grid weights
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(0, weight=1)

        # Bind select event
        self.tree.bind('<<TreeviewSelect>>', self.on_select)

        return frame

    def add_room(self):
        """Add a new room to the database"""
        try:
            # Validate inputs
            if not self.validate_inputs():
                return

            cursor = self.db.get_connection().cursor()
            cursor.execute("""
                INSERT INTO rooms (room_number, room_type, rate, description)
                VALUES (?, ?, ?, ?)
            """, (
                self.room_number.get(),
                self.room_type.get(),
                float(self.rate.get()),
                self.description.get("1.0", tk.END).strip()
            ))
            self.db.get_connection().commit()
            
            messagebox.showinfo("Success", "Room added successfully!")
            self.clear_form()
            self.load_rooms()
            
        except Exception as e:
            logger.error(f"Error adding room: {str(e)}")
            messagebox.showerror("Error", f"Failed to add room: {str(e)}")

    def update_room(self):
        """Update selected room"""
        if not self.tree.selection():
            messagebox.showwarning("Warning", "Please select a room to update")
            return

        try:
            if not self.validate_inputs():
                return

            cursor = self.db.get_connection().cursor()
            cursor.execute("""
                UPDATE rooms 
                SET room_type = ?, rate = ?, description = ?
                WHERE room_number = ?
            """, (
                self.room_type.get(),
                float(self.rate.get()),
                self.description.get("1.0", tk.END).strip(),
                self.room_number.get()
            ))
            self.db.get_connection().commit()
            
            messagebox.showinfo("Success", "Room updated successfully!")
            self.load_rooms()
            
        except Exception as e:
            logger.error(f"Error updating room: {str(e)}")
            messagebox.showerror("Error", f"Failed to update room: {str(e)}")

    def delete_room(self):
        """Delete selected room"""
        if not self.tree.selection():
            messagebox.showwarning("Warning", "Please select a room to delete")
            return

        if messagebox.askyesno("Confirm", "Are you sure you want to delete this room?"):
            try:
                cursor = self.db.get_connection().cursor()
                cursor.execute("DELETE FROM rooms WHERE room_number = ?", 
                             (self.room_number.get(),))
                self.db.get_connection().commit()
                
                messagebox.showinfo("Success", "Room deleted successfully!")
                self.clear_form()
                self.load_rooms()
                
            except Exception as e:
                logger.error(f"Error deleting room: {str(e)}")
                messagebox.showerror("Error", f"Failed to delete room: {str(e)}")

    def load_rooms(self):
        """Load rooms into treeview"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            cursor = self.db.get_connection().cursor()
            cursor.execute("SELECT * FROM rooms ORDER BY room_number")
            
            for row in cursor.fetchall():
                self.tree.insert('', 'end', values=(
                    row['room_number'],
                    row['room_type'],
                    f"${row['rate']:.2f}",
                    row['status'],
                    row['description']
                ))
                
        except Exception as e:
            logger.error(f"Error loading rooms: {str(e)}")
            messagebox.showerror("Error", f"Failed to load rooms: {str(e)}")

    def on_select(self, event):
        """Handle room selection"""
        selected_item = self.tree.selection()
        if not selected_item:
            return

        # Get the selected room's values
        values = self.tree.item(selected_item[0])['values']
        
        # Update form fields
        self.room_number.delete(0, tk.END)
        self.room_number.insert(0, values[0])
        
        self.room_type.set(values[1])
        
        self.rate.delete(0, tk.END)
        self.rate.insert(0, values[2].replace('$', ''))
        
        self.description.delete("1.0", tk.END)
        self.description.insert("1.0", values[4] if values[4] else "")

    def validate_inputs(self):
        """Validate form inputs"""
        if not self.room_number.get().strip():
            messagebox.showerror("Error", "Please enter a room number")
            return False

        if not self.room_type.get():
            messagebox.showerror("Error", "Please select a room type")
            return False

        try:
            rate = float(self.rate.get())
            if rate <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid rate")
            return False

        return True

    def clear_form(self):
        """Clear all form inputs"""
        self.room_number.delete(0, tk.END)
        self.room_type.set('')
        self.rate.delete(0, tk.END)
        self.description.delete("1.0", tk.END)