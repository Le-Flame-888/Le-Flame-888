import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import datetime, timedelta
import sqlite3
from database.config import logger


class ReservationsTab(ttk.Frame):
    def __init__(self, parent, db_connection):
        super().__init__(parent)
        self.db = db_connection.get_connection()
        self.setup_ui()
        self.num_adults = tk.StringVar()
        self.num_children = tk.StringVar()
        self.special_requests = tk.Text(self)
        self.load_room_list()
        self.refresh_reservations()

    def setup_ui(self):
        """Initialize all UI components"""
        # Create main frames
        self.filters_frame = ttk.LabelFrame(self, text="Reservation Filters")
        self.form_frame = ttk.LabelFrame(self, text="New Reservation")
        self.list_frame = ttk.LabelFrame(self, text="Reservations List")
        self.details_frame = ttk.LabelFrame(self, text="Reservation Details")
        
        # Layout frames
        self.filters_frame.grid(row=0, column=0, columnspan=2, padx=20, pady=10, sticky="ew")
        self.form_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.list_frame.grid(row=1, column=1, padx=20, pady=10, sticky="nsew")
        self.details_frame.grid(row=2, column=0, columnspan=2, padx=20, pady=10, sticky="nsew")
        
        # Configure grid weights
        self.grid_columnconfigure(1, weight=1)
        
        # Setup individual frames
        self.setup_filters_frame()
        self.setup_form_frame()
        self.setup_list_frame()
        self.setup_details_frame()

    def setup_filters_frame(self):
        """Setup the filters section"""
        # Date range filters
        ttk.Label(self.filters_frame, text="From:").grid(row=0, column=0, padx=5, pady=5)
        self.filter_date_from = DateEntry(self.filters_frame, width=12)
        self.filter_date_from.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(self.filters_frame, text="To:").grid(row=0, column=2, padx=5, pady=5)
        self.filter_date_to = DateEntry(self.filters_frame, width=12)
        self.filter_date_to.grid(row=0, column=3, padx=5, pady=5)
        
        # Status filter
        ttk.Label(self.filters_frame, text="Status:").grid(row=0, column=4, padx=5, pady=5)
        self.filter_status = ttk.Combobox(self.filters_frame, values=[
            "All",
            "Reserved",
            "Checked In",
            "Checked Out",
            "Cancelled"
        ])
        self.filter_status.set("All")
        self.filter_status.grid(row=0, column=5, padx=5, pady=5)
        
        # Search
        ttk.Label(self.filters_frame, text="Search:").grid(row=0, column=6, padx=5, pady=5)
        self.search_entry = ttk.Entry(self.filters_frame, width=30)
        self.search_entry.grid(row=0, column=7, padx=5, pady=5)
        
        # Buttons
        ttk.Button(self.filters_frame, text="Apply Filters", 
                  command=self.apply_filters).grid(row=0, column=8, padx=5, pady=5)
        ttk.Button(self.filters_frame, text="Reset", 
                  command=self.reset_filters).grid(row=0, column=9, padx=5, pady=5)

    def setup_form_frame(self):
        """Setup the reservation form"""
        # Guest Information
        guest_frame = ttk.LabelFrame(self.form_frame, text="Guest Information")
        guest_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(guest_frame, text="Guest:*").grid(row=0, column=0, padx=5, pady=5)
        self.guest_search = ttk.Entry(guest_frame, width=30)
        self.guest_search.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(guest_frame, text="Search Guest", 
                  command=self.search_guest).grid(row=0, column=2, padx=5, pady=5)
        
        # Room Selection
        room_frame = ttk.LabelFrame(self.form_frame, text="Room Selection")
        room_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(room_frame, text="Room Type:").grid(row=0, column=0, padx=5, pady=5)
        self.room_type = ttk.Combobox(room_frame)
        self.room_type.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(room_frame, text="Room Number:*").grid(row=1, column=0, padx=5, pady=5)
        self.room_number = ttk.Combobox(room_frame)
        self.room_number.grid(row=1, column=1, padx=5, pady=5)
        
        # Dates
        dates_frame = ttk.LabelFrame(self.form_frame, text="Dates")
        dates_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(dates_frame, text="Check-in:*").grid(row=0, column=0, padx=5, pady=5)
        self.check_in_date = DateEntry(dates_frame, width=12)
        self.check_in_date.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(dates_frame, text="Check-out:*").grid(row=0, column=2, padx=5, pady=5)
        self.check_out_date = DateEntry(dates_frame, width=12)
        self.check_out_date.grid(row=0, column=3, padx=5, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(self.form_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(button_frame, text="Create Reservation", 
                  command=self.create_reservation).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear Form", 
                  command=self.clear_form).pack(side=tk.LEFT, padx=5)

    def setup_list_frame(self):
        """Setup the reservations list"""
        # Create Treeview
        columns = ('ID', 'Guest', 'Room', 'Check-in', 'Check-out', 'Status')
        self.tree = ttk.Treeview(self.list_frame, columns=columns, show='headings')
        
        # Add column headings
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        
        # Add scrollbars
        vsb = ttk.Scrollbar(self.list_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(self.list_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Grid layout
        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
        # Configure grid weights
        self.list_frame.grid_rowconfigure(0, weight=1)
        self.list_frame.grid_columnconfigure(0, weight=1)
        
        # Bind selection event
        self.tree.bind('<<TreeviewSelect>>', self.on_reservation_select)

    def setup_details_frame(self):
        """Setup the reservation details section"""
        # Status management
        status_frame = ttk.Frame(self.details_frame)
        status_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(status_frame, text="Current Status:").pack(side=tk.LEFT, padx=5)
        self.current_status = ttk.Label(status_frame, text="")
        self.current_status.pack(side=tk.LEFT, padx=5)
        
        self.check_in_button = ttk.Button(status_frame, text="Check In", 
                                        command=self.check_in_guest)
        self.check_in_button.pack(side=tk.LEFT, padx=5)
        
        self.check_out_button = ttk.Button(status_frame, text="Check Out", 
                                         command=self.check_out_guest)
        self.check_out_button.pack(side=tk.LEFT, padx=5)
        
        self.cancel_button = ttk.Button(status_frame, text="Cancel Reservation", 
                                      command=self.cancel_reservation)
        self.cancel_button.pack(side=tk.LEFT, padx=5)

    def load_reservations(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT r.id, g.first_name || ' ' || g.last_name as guest_name, 
                        r.room_number, r.check_in_date, r.check_out_date
                    FROM reservations r
                    JOIN guests g ON r.guest_id = g.id
                    ORDER BY r.check_in_date
                """)
                for row in cursor.fetchall():
                    self.tree.insert('', tk.END, values=row)
        except Exception as e:
            logger.error(f"Error loading reservations: {str(e)}")
            messagebox.showerror("Error", "Failed to load reservations")


    def create_reservation(self):
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO reservations (guest_id, room_number, check_in_date, check_out_date)
                    VALUES (?, ?, ?, ?)
                """, (self.selected_guest_id, self.room_number.get(), 
                    self.check_in_date.get(), self.check_out_date.get()))
                conn.commit()
                self.load_reservations()
                self.clear_form()
                messagebox.showinfo("Success", "Reservation created successfully")
        except Exception as e:
            logger.error(f"Error creating reservation: {str(e)}")
            messagebox.showerror("Error", "Failed to create reservation")

    # [Rest of the methods (load_room_list, refresh_reservations, etc.) remain the same]

    def load_room_list(self):
        try:
            # Use cursor for database operations
            cursor = self.db.cursor()
            
            # Load room types
            cursor.execute("SELECT DISTINCT room_type FROM rooms ORDER BY room_type")
            room_types = [row[0] for row in cursor.fetchall()]
            self.room_type['values'] = room_types
            
            # Load room numbers
            cursor.execute("SELECT room_number FROM rooms ORDER BY room_number")
            room_numbers = [row[0] for row in cursor.fetchall()]
            self.room_number['values'] = room_numbers
            
        except sqlite3.Error as e:
            tk.messagebox.showerror("Database Error", f"Failed to load room list: {str(e)}")

    def search_guest(self):
        search_text = self.guest_search.get()
        if not search_text:
            tk.messagebox.showerror("Validation Error", "Please enter a guest name to search")
            return

        try:
            cursor = self.db.cursor()
            query = """
            SELECT id, first_name, last_name 
            FROM guests 
            WHERE first_name LIKE ? OR last_name LIKE ?
            """
            search_pattern = f"%{search_text}%"
            cursor.execute(query, (search_pattern, search_pattern))
            guests = cursor.fetchall()

            if not guests:
                tk.messagebox.showinfo("No Results", "No guests found matching the search criteria")
                return

            # Display search results in a new window
            search_window = tk.Toplevel(self)
            search_window.title("Search Results")
            search_window.geometry("400x300")

            tree = ttk.Treeview(search_window, columns=("ID", "First Name", "Last Name"), show='headings')
            tree.heading("ID", text="ID")
            tree.heading("First Name", text="First Name")
            tree.heading("Last Name", text="Last Name")
            tree.column("ID", width=50)
            tree.column("First Name", width=150)
            tree.column("Last Name", width=150)
            tree.pack(fill=tk.BOTH, expand=True)

            for guest in guests:
                tree.insert('', 'end', values=(guest[0], guest[1], guest[2]))

            def on_select(event):
                selected_item = tree.selection()
                if selected_item:
                    guest_id, first_name, last_name = tree.item(selected_item[0])['values']
                    self.current_guest_id = guest_id
                    self.guest_search.delete(0, tk.END)
                    self.guest_search.insert(0, f"{first_name} {last_name}")
                    search_window.destroy()

            tree.bind('<<TreeviewSelect>>', on_select)

        except sqlite3.Error as e:
            tk.messagebox.showerror("Database Error", f"Failed to search guests: {str(e)}")

    def refresh_reservations(self):
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        try:
            cursor = self.db.cursor()
            
            # Apply filters if they exist
            where_clauses = []
            params = []
            
            if self.filter_status.get() != "All":
                where_clauses.append("r.status = ?")
                params.append(self.filter_status.get())
                
            if self.filter_date_from.get_date():
                where_clauses.append("r.check_in_date >= ?")
                params.append(self.filter_date_from.get_date())
                
            if self.filter_date_to.get_date():
                where_clauses.append("r.check_out_date <= ?")
                params.append(self.filter_date_to.get_date())
                
            search_text = self.search_entry.get()
            if search_text:
                where_clauses.append("""
                    (g.name LIKE ? OR r.room_number LIKE ? OR r.status LIKE ?)
                """)
                search_pattern = f"%{search_text}%"
                params.extend([search_pattern] * 3)
                
            # Construct query
            query = """
            SELECT r.id, g.name, r.room_number, 
                   r.check_in_date, r.check_out_date, r.status
            FROM reservations r
            JOIN guests g ON r.guest_id = g.id
            """
            
            if where_clauses:
                query += " WHERE " + " AND ".join(where_clauses)
                
            query += " ORDER BY r.check_in_date DESC"
            
            # Execute query and populate treeview
            cursor.execute(query, params)
            for row in cursor.fetchall():
                self.tree.insert('', 'end', values=(
                    row[0],
                    row[1],  # guest name is already combined
                    row[2],
                    row[3],
                    row[4],
                    row[5]
                ))
                
        except sqlite3.Error as e:
            tk.messagebox.showerror("Database Error", f"Failed to refresh reservations: {str(e)}")

    def check_room_availability(self):
        try:
            cursor = self.db.cursor()
            room = self.room_number.get()
            check_in = self.check_in_date.get_date()
            check_out = self.check_out_date.get_date()
            
            query = """
            SELECT COUNT(*) FROM reservations
            WHERE room_number = ? 
            AND status != 'Cancelled'
            AND (
                (check_in_date BETWEEN ? AND ?) OR
                (check_out_date BETWEEN ? AND ?) OR
                (check_in_date <= ? AND check_out_date >= ?)
            )
            """
            
            cursor.execute(query, (
                room, check_in, check_out, 
                check_in, check_out,
                check_in, check_out
            ))
            count = cursor.fetchone()[0]
            return count == 0
        except sqlite3.Error as e:
            tk.messagebox.showerror("Database Error", f"Failed to check room availability: {str(e)}")
            return False

    # ... [rest of the methods remain the same, but use cursor = self.db.cursor() for database operations] ...

    def validate_reservation(self):
        # Check required fields
        if not hasattr(self, 'current_guest_id'):
            tk.messagebox.showerror("Validation Error", "Please select a guest")
            return False
            
        if not self.room_number.get():
            tk.messagebox.showerror("Validation Error", "Please select a room")
            return False
            
        # Validate dates
        check_in = self.check_in_date.get_date()
        check_out = self.check_out_date.get_date()
        
        if check_in >= check_out:
            tk.messagebox.showerror("Validation Error", "Check-out date must be after check-in date")
            return False
            
        if check_in < datetime.now().date():
            tk.messagebox.showerror("Validation Error", "Check-in date cannot be in the past")
            return False
            
        return True

    def clear_form(self):
        self.guest_search.delete(0, tk.END)
        if hasattr(self, 'current_guest_id'):
            del self.current_guest_id
        self.room_type.set('')
        self.room_number.set('')
        self.check_in_date.set_date(datetime.now())
        self.check_out_date.set_date(datetime.now() + timedelta(days=1))
        self.num_adults.set(1)
        self.num_children.set(0)
        self.special_requests.delete('1.0', tk.END)

    def refresh_reservations(self):
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        try:
            # Apply filters if they exist
            where_clauses = []
            params = []
            
            if self.filter_status.get() != "All":
                where_clauses.append("r.status = ?")
                params.append(self.filter_status.get())
                
            if self.filter_date_from.get_date():
                where_clauses.append("r.check_in_date >= ?")
                params.append(self.filter_date_from.get_date())
                
            if self.filter_date_to.get_date():
                where_clauses.append("r.check_out_date <= ?")
                params.append(self.filter_date_to.get_date())
                
            search_text = self.search_entry.get()
            if search_text:
                where_clauses.append("""
                    (g.first_name LIKE ? OR g.last_name LIKE ? OR 
                     r.room_number LIKE ? OR r.status LIKE ?)
                """)
                search_pattern = f"%{search_text}%"
                params.extend([search_pattern] * 4)
                
            # Construct query
            query = """
            SELECT r.id, g.first_name, g.last_name, r.room_number, 
                   r.check_in_date, r.check_out_date, r.status
            FROM reservations r
            JOIN guests g ON r.guest_id = g.id
            """
            
            if where_clauses:
                query += " WHERE " + " AND ".join(where_clauses)
                
            query += " ORDER BY r.check_in_date DESC"
            
            # Execute query and populate treeview
            cursor = self.db.execute(query, params)
            for row in cursor.fetchall():
                self.tree.insert('', 'end', values=(
                    row[0],
                    f"{row[1]} {row[2]}",
                    row[3],
                    row[4],
                    row[5],
                    row[6]
                ))
                
        except sqlite3.Error as e:
            tk.messagebox.showerror("Database Error", f"Failed to refresh reservations: {str(e)}")

    def apply_filters(self):
        self.refresh_reservations()

    def reset_filters(self):
        self.filter_status.set("All")
        self.filter_date_from.set_date(datetime.now())
        self.filter_date_to.set_date(datetime.now() + timedelta(days=30))
        self.search_entry.delete(0, tk.END)
        self.refresh_reservations()

    def on_reservation_select(self, event):
        selected_items = self.tree.selection()
        if not selected_items:
            return
            
        try:
            # Get reservation details
            reservation_id = self.tree.item(selected_items[0])['values'][0]
            query = """
            SELECT r.*, g.first_name, g.last_name
            FROM reservations r
            JOIN guests g ON r.guest_id = g.id
            WHERE r.id = ?
            """
            
            cursor = self.db.execute(query, (reservation_id,))
            reservation = cursor.fetchone()
            
            if reservation:
                # Update status display
                self.current_status.config(text=reservation['status'])
                
                # Update button states based on current status
                if reservation['status'] == 'Reserved':
                    self.check_in_button.config(state='normal')
                    self.check_out_button.config(state='disabled')
                    self.cancel_button.config(state='normal')
                elif reservation['status'] == 'Checked In':
                    self.check_in_button.config(state='disabled')
                    self.check_out_button.config(state='normal')
                    self.cancel_button.config(state='disabled')
                else:
                    self.check_in_button.config(state='disabled')
                    self.check_out_button.config(state='disabled')
                    self.cancel_button.config(state='disabled')
                
        except sqlite3.Error as e:
            tk.messagebox.showerror("Database Error", f"Failed to load reservation details: {str(e)}")

    def update_reservation_status(self, reservation_id, new_status):
        try:
            self.db.execute(
                "UPDATE reservations SET status = ? WHERE id = ?",
                (new_status, reservation_id)
            )
            self.db.commit()
            self.refresh_reservations()
        except sqlite3.Error as e:
            tk.messagebox.showerror("Database Error", f"Failed to update reservation status: {str(e)}")

    def check_in_guest(self):
        selected_items = self.tree.selection()
        if not selected_items:
            return
            
        reservation_id = self.tree.item(selected_items[0])['values'][0]
        self.update_reservation_status(reservation_id, 'Checked In')
        tk.messagebox.showinfo("Success", "Guest has been checked in")

    def check_out_guest(self):
        selected_items = self.tree.selection()
        if not selected_items:
            return
            
        reservation_id = self.tree.item(selected_items[0])['values'][0]
        self.update_reservation_status(reservation_id, 'Checked Out')
        tk.messagebox.showinfo("Success", "Guest has been checked out")

    def cancel_reservation(self):
        selected_items = self.tree.selection()
        if not selected_items:
            return
            
        if tk.messagebox.askyesno("Confirm Cancellation", 
                                 "Are you sure you want to cancel this reservation?"):
            reservation_id = self.tree.item(selected_items[0])['values'][0]
            self.update_reservation_status(reservation_id, 'Cancelled')
            tk.messagebox.showinfo("Success", "Reservation has been cancelled")