# ui/tabs/guests.py
import tkinter as tk
from tkinter import ttk, messagebox
from database.config import logger

class GuestsTab(ttk.Frame):
    def __init__(self, parent, db_connection):
        super().__init__(parent)
        self.db = db_connection
        self.setup_ui()
        self.load_guests()

    def setup_ui(self):
        # Create main frames
        self.form_frame = self.create_form_frame()
        self.list_frame = self.create_list_frame()

        # Layout frames
        self.form_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.list_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")

    def create_form_frame(self):
        frame = ttk.LabelFrame(self, text="Guest Information")

          # Add a variable to store the selected guest ID
    

        # Add the Search Guest button with the handler
       

        #first name
        ttk.Label(frame, text="First_name:").grid(row=0, column=0, padx=5, pady=5)
        self.first_name = ttk.Entry(frame, width=30)
        self.first_name.grid(row=0, column=1, padx=5, pady=5)

        # last name
        ttk.Label(frame, text="Last_name:").grid(row=1, column=0, padx=5, pady=5)
        self.last_name = ttk.Entry(frame, width=30)
        self.last_name.grid(row=1, column=1, padx=5, pady=5)

        # Email
        ttk.Label(frame, text="Email:").grid(row=2, column=0, padx=5, pady=5)
        self.email = ttk.Entry(frame, width=30)
        self.email.grid(row=2, column=1, padx=5, pady=5)

        # Phone
        ttk.Label(frame, text="Phone:").grid(row=3, column=0, padx=5, pady=5)
        self.phone = ttk.Entry(frame, width=30)
        self.phone.grid(row=3, column=1, padx=5, pady=5)

        # Address
        ttk.Label(frame, text="Address:").grid(row=4, column=0, padx=5, pady=5)
        self.address = tk.Text(frame, height=3, width=30)
        self.address.grid(row=4, column=1, padx=5, pady=5)

        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=10)

        ttk.Button(button_frame, text="Add Guest", command=self.add_guest).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Update Guest", command=self.update_guest).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Delete Guest", command=self.delete_guest).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear Form", command=self.clear_form).pack(side=tk.LEFT, padx=5)

        return frame

    def create_list_frame(self):
        frame = ttk.LabelFrame(self, text="Guest List")

        
        # Create Treeview
        columns = ('id', 'first_name', 'last_name', 'email', 'phone', 'address')
        self.tree = ttk.Treeview(frame, columns=columns, show='headings')
        
        # Define column headings
        self.tree.heading('id', text='ID')
        self.tree.heading('first_name', text='First_name')
        self.tree.heading('last_name', text='Last_name')
        self.tree.heading('email', text='Email')
        self.tree.heading('phone', text='Phone')
        self.tree.heading('address', text='Address')
        
        # Configure column widths
        self.tree.column('id', width=50)
        self.tree.column('first_name', width=150)
        self.tree.column('last_name', width=150)
        self.tree.column('email', width=200)
        self.tree.column('phone', width=100)
        self.tree.column('address', width=250)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Bind select event
        self.tree.bind('<<TreeviewSelect>>', self.on_select)
        
        # Layout
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        return frame
    
    
    def load_guests(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM guests ORDER BY first_name, last_name")
                guests = cursor.fetchall()
                for guest in guests:
                    # Convert tuple to list of strings
                    values = [str(value) if value is not None else "" for value in guest]
                    self.tree.insert('', tk.END, values=values)
        except Exception as e:
            logger.error(f"Error loading guests: {str(e)}")
            messagebox.showerror("Error", "Failed to load guest list")

    def clear_form(self):
        """Clear all form fields"""
        self.first_name.delete(0, tk.END)
        self.last_name.delete(0, tk.END)
        self.email.delete(0, tk.END)
        self.phone.delete(0, tk.END)
        self.address.delete('1.0', tk.END)
        # Deselect any selected item in the treeview
        if self.tree.selection():
            self.tree.selection_remove(self.tree.selection())

    def validate_form(self):
        """Validate form inputs"""
        if not self.first_name.get().strip():
            messagebox.showwarning("Validation Error", "first_name is required")
            return False
        if not self.email.get().strip():
            messagebox.showwarning("Validation Error", "Email is required")
            return False
        return True

    def get_form_data(self):
        """Get data from form fields"""
        return {
            'first_name': self.first_name.get().strip(),
            'last_name': self.last_name.get().strip(),
            'email': self.email.get().strip(),
            'phone': self.phone.get().strip(),
            'address': self.address.get('1.0', tk.END).strip()
        }

    def add_guest(self):
        """Add a new guest to the database"""
        if not self.validate_form():
            return
            
        data = self.get_form_data()
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO guests (first_name, last_name, email, phone, address)
                    VALUES (?, ?, ?, ?, ?)
                """, (data['first_name'], data['last_name'], data['email'], data['phone'], data['address']))
                conn.commit()
            
            messagebox.showinfo("Success", "Guest added successfully")
            self.clear_form()
            self.load_guests()
        except Exception as e:
            logger.error(f"Error adding guest: {str(e)}")
            messagebox.showerror("Error", "Failed to add guest")

    def update_guest(self):
        """Update selected guest in the database"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a guest to update")
            return
            
        if not self.validate_form():
            return
            
        guest_id = self.tree.item(selection[0])['values'][0]
        data = self.get_form_data()
        
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE guests 
                    SET first_name=?, last_name=?, email=?, phone=?, address=?
                    WHERE id=?
                """, (data['first_name'],(data['last_name']), data['email'], data['phone'], data['address'], guest_id))
                conn.commit()
            
            messagebox.showinfo("Success", "Guest updated successfully")
            self.clear_form()
            self.load_guests()
        except Exception as e:
            logger.error(f"Error updating guest: {str(e)}")
            messagebox.showerror("Error", "Failed to update guest")

    def delete_guest(self):
        """Delete selected guest from the database"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a guest to delete")
            return
            
        if not messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this guest?"):
            return
            
        guest_id = self.tree.item(selection[0])['values'][0]
        
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM guests WHERE id=?", (guest_id,))
                conn.commit()
            
            messagebox.showinfo("Success", "Guest deleted successfully")
            self.clear_form()
            self.load_guests()
        except Exception as e:
            logger.error(f"Error deleting guest: {str(e)}")
            messagebox.showerror("Error", "Failed to delete guest")


    def on_select(self, event):
        """Handle treeview selection"""
        selection = self.tree.selection()
        if not selection:
            return
            
        # Get the selected item's values
        values = self.tree.item(selection[0])['values']
        
        # Clear form and populate with selected guest's data
        self.clear_form()
        self.first_name.insert(0, values[1])
        self.last_name.insert(0, values[2])
        self.email.insert(0, values[3])
        self.phone.insert(0, values[4])
        self.address.insert('1.0', values[5])