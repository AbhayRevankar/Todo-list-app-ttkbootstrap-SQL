import tkinter as tk
import ttkbootstrap as ttk  # type: ignore
from ttkbootstrap.scrolled import ScrolledFrame # type: ignore
from ttkbootstrap.widgets import Separator  # type: ignore
import sqlite3
from todo_func_vari import DATA_BASE_FILE,TODAY_STRING, convert, STYLE, STYLE_OUTLINE

        
class Task_frame(ttk.Frame):
	def __init__(self, parent, data, check_func,delete_func, edit_btn):
		super().__init__(parent)

		self.delete_func = delete_func
		self.check_func = check_func
		self.edit_btn = edit_btn
		self.create_widget(data)
		self.pack(fill='x', padx=10, pady=5)

	def create_widget(self, data):
		task, date, priority, check_color, strike, overdue = data 
		ch_var = tk.IntVar(value=5)

		self.columnconfigure(0, weight=4, uniform='a')
		self.columnconfigure((1,2,3,4), weight=1, uniform='a')
		self.rowconfigure(0, weight=1, uniform='a')
		
		check_btn = ttk.Checkbutton(self, text=task, variable=ch_var, onvalue=10, offvalue=5, bootstyle=check_color)
		overdue_lab = ttk.Label(self, text="Overdue")
		date_lab = ttk.Label(self, text= date)
		btn_del = ttk.Button(self, text="Delete",bootstyle = STYLE)
		btn_edit = ttk.Button(self, text="Edit",bootstyle = STYLE_OUTLINE)

		check_btn.grid(row=0, column=0, sticky='nsew', padx=5)
		btn_edit.grid(row=0, column=3, sticky='nsew', padx=5)
		btn_del.grid(row=0, column=4, sticky='nsew', padx=5)
	
		if date:
			if convert(date) < convert(TODAY_STRING) and overdue == 1:
				overdue_lab.grid(row=0, column=1)
				date_lab.grid(row=0, column=2, sticky='nsew', padx=5)

			elif convert(date) > convert(TODAY_STRING):
				date_lab.grid(row=0, column=2, sticky='nsew', padx=5)

		else:
			pass
		check_btn.config(command=lambda task=task, date=date, priority = priority: self.check_func(task, date, priority))
		btn_del.config(command=lambda task=task, priority = priority: self.delete_func(task, priority))
		btn_edit.config(command=lambda task=task, date=date, priority = priority, check_color = check_color: self.edit_btn(task,date,priority, check_color))

		
class Tab_frame(ttk.Frame):
	def __init__(self, parent, tab, data, check_func,delete_func,edit_btn, blank_txt):
		super().__init__(parent)

		self.data = data
		self.frm1 = ttk.Frame(tab)
		self.scroll_frame = ScrolledFrame(self.frm1)
	
		if self.data:
			for row in self.data:
				Task_frame(self.scroll_frame, row, check_func, delete_func, edit_btn)
				ttk.Separator(self.scroll_frame, bootstyle="dark").pack(expand=True, fill='x', padx=15, pady=4)
			self.scroll_frame.pack(fill='both', expand=True)	
		else:
			ttk.Label(self.frm1, text=blank_txt,font=("Arial", 15)).pack(expand=True, fill='both', padx=200, pady=100)
		
		self.frm1.pack(fill='both', expand=True)


def overdue_tsk():
	"""Marks all the overdue tasks"""
	conn = sqlite3.connect(DATA_BASE_FILE)
	cursor = conn.cursor()
	cursor.execute("SELECT * FROM alltasks WHERE date !=?",("",))

	data = cursor.fetchall()
	for row in data:
		if convert(row[1]) < convert(TODAY_STRING):
			cursor.execute("UPDATE alltasks SET overdue =1, priority =1, color='warning' WHERE date=?",(row[1],))
			conn.commit()
		else:
			cursor.execute("UPDATE alltasks SET overdue =0 WHERE date=?",(row[1],))
			conn.commit()

	conn.close()
        
def auto_delete():
	"""Delete tasks marked as complete and overdue from the database."""
	conn = sqlite3.connect(DATA_BASE_FILE)
	cursor = conn.cursor()
	cursor.execute("SELECT * FROM alltasks")
	data = cursor.fetchall()
	for row in data:
		if row[1]:
			if convert(row[1]) < convert(TODAY_STRING):
				cursor.execute("DELETE FROM alltasks WHERE task=? AND strike=1",(row[0],))
			else:
				pass
	conn.commit()
	conn.close()

def progress_bar_func():
	"""Calculates the progress by striking the tasks and returns the persentage."""
	conn = sqlite3.connect(DATA_BASE_FILE)
	cursor = conn.cursor()

	cursor.execute("SELECT COUNT(*) FROM alltasks WHERE strike=1")
	done = cursor.fetchone()[0]
	cursor.execute("SELECT COUNT(*) FROM alltasks WHERE date=?",(TODAY_STRING,))
	total_tasks = cursor.fetchone()[0]

	per = (done/total_tasks)*100 if done else 0
	conn.close()
	return round(per,1)