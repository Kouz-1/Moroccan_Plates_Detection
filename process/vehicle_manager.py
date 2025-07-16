import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from process.check_plate_status import check_plate_status

MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'vehicules_parking'
}

def fetch_all_vehicles():
    conn = mysql.connector.connect(**MYSQL_CONFIG)
    cursor = conn.cursor()
    cursor.execute("SELECT id, Number, Charactere, Region, arrived_at FROM vehicules")
    rows = cursor.fetchall()
    conn.close()
    return rows

def delete_vehicle(vehicle_id):
    conn = mysql.connector.connect(**MYSQL_CONFIG)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM vehicules WHERE id = %s", (vehicle_id,))
    conn.commit()
    conn.close()

def show_vehicle_admin_window():
    window = tk.Toplevel()
    window.title("Vehicle Records Management")
    window.geometry("800x500")
    window.configure(bg="white")

    tk.Label(window, text="All Detected Vehicles", font=("Helvetica", 14, "bold"), bg="white").pack(pady=10)

    table_frame = tk.Frame(window)
    table_frame.pack(pady=10)

    cols = ("ID", "Number", "Charactere", "Region", "Arrived At")
    tree = ttk.Treeview(table_frame, columns=cols, show='headings', height=15)
    for col in cols:
        tree.heading(col, text=col)
        tree.column(col, width=140, anchor='center')
    tree.pack()

    def refresh_table():
        for row in tree.get_children():
            tree.delete(row)
        for vehicle in fetch_all_vehicles():
            tree.insert('', 'end', values=vehicle)

    refresh_table()

    # Button frame
    btn_frame = tk.Frame(window, bg="white")
    btn_frame.pack(pady=20)

    # Connect to the second database
    def is_vehicle_suspect(number, char, region):
        try:
            conn = mysql.connector.connect(
                host='localhost',
                user='root',
                password='',
                database='vehicules_recherchees'
            )
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM vehicules
                WHERE Number = %s AND Charactere = %s AND Region = %s
            """, (number, char, region))
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            return result is not None
        except mysql.connector.Error as e:
            return False

    def delete_selected():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select a vehicle to delete.")
            return
        vehicle_id = tree.item(selected[0])['values'][0]
        delete_vehicle(vehicle_id)
        messagebox.showinfo("Deleted", "Vehicle deleted.")
        refresh_table()

    def check_selected():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select a vehicle to check.")
            return
        vehicle = tree.item(selected[0])['values']
        is_suspect = is_vehicle_suspect(vehicle[1], vehicle[2], vehicle[3])
        if is_suspect:
            messagebox.showwarning("Suspect Vehicle", f"{vehicle[1]}-{vehicle[2]}-{vehicle[3]} is marked as stolen/suspect.")
        else:
            messagebox.showinfo("Status", "Vehicle is clean.")


    def check_all():
        suspicious = []
        for vehicle in fetch_all_vehicles():
            if is_vehicle_suspect(vehicle[1], vehicle[2], vehicle[3]):
                suspicious.append(f"{vehicle[1]}-{vehicle[2]}-{vehicle[3]} (ID {vehicle[0]})")
        if suspicious:
            messagebox.showwarning("Suspected Vehicles", "\n".join(suspicious))
        else:
            messagebox.showinfo("Result", "No suspected vehicles found.")


    ttk.Button(btn_frame, text="Delete Vehicle", width=20, command=delete_selected).grid(row=0, column=0, padx=10)
    ttk.Button(btn_frame, text="Check One Vehicle", width=20, command=check_selected).grid(row=0, column=1, padx=10)
    ttk.Button(btn_frame, text="Check All Vehicles", width=20, command=check_all).grid(row=0, column=2, padx=10)

if __name__ == '__main__':
    root = tk.Tk()
    root.withdraw()
    show_vehicle_admin_window()
    root.mainloop()
