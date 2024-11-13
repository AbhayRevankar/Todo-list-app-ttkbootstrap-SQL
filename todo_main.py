import ttkbootstrap as ttk  # type: ignore
from ttkbootstrap.widgets import DateEntry, Floodgauge # type: ignore
from ttkbootstrap.tooltip import ToolTip # type: ignore
import tkinter as tk
from tkinter import messagebox 
import sqlite3
from todo_tab_tsk import *
from todo_func_vari import *

class Main(ttk.Window):
    def __init__(self, title, size):

        # main setup
        super().__init__(themename = detect_theme_mode())
        self.title(title)
        self.geometry(f'{size[0]}x{size[1]}')
        self.resizable(False, False)
        self.iconbitmap(ICON)

        # widgets 
        self.main_frame = Main_frame(self)

        # run 
        self.mainloop()
		
class Main_frame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.progress_int = tk.DoubleVar() 
        self.prog_str = tk.StringVar()

        self.notebook = ttk.Notebook(self)
        self.tab1 = ttk.Frame(self.notebook)
        self.tab2 = ttk.Frame(self.notebook)
        self.tab3 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab1, text = 'Today')
        self.notebook.add(self.tab2, text = 'Upcoming')
        self.notebook.add(self.tab3, text = 'No Date')

        #grid
        self.columnconfigure(0, weight=1,uniform='a')
        self.rowconfigure((0,1,2,3,4,5,6),weight=1, uniform='a')

        #topframe
        Top_frame(self, self.progress_int, self.prog_str).grid(column=0, row=0, sticky='nsew')

        #middle frame
        self.notebook.grid(column=0, row=1,rowspan=5 ,sticky='nsew')
        self.fetch_data()
        #bottom frame
        Bottom_frame(self).grid(column=0, row=6, sticky='nsew')

        self.pack(fill="both", expand=True, padx=5, pady=5)

    def fetch_data(self):
        """Fetches the tasks on one of the three tabs based on date (today/upcoming/no date)."""
        overdue_tsk()
        auto_delete()
        self.progress_int.set(progress_bar_func())
        self.prog_str.set(f"{self.progress_int.get()} %")

        conn = sqlite3.connect(DATA_BASE_FILE)
        cursor = conn.cursor()

        #today
        today_t = cursor.execute("SELECT * FROM alltasks WHERE date = ? AND strike = 0 OR overdue=1", (TODAY_STRING,))
        data_t = today_t.fetchall() 
        sort_data_t = sorted(data_t, key=lambda x: x[2])
        self.add_tabs(self.tab1, sort_data_t, TODAY_BLANK_TXT)

        #upcoming
        Upcoming_t = cursor.execute("SELECT * FROM alltasks WHERE date != ? AND date != ? AND strike = 0 AND overdue=0", (TODAY_STRING ,"",)) 
        data_u = Upcoming_t.fetchall()
        sort_data_u = sorted(data_u, key=lambda x: convert(x[1])) 
        self.add_tabs(self.tab2, sort_data_u,UPCOMING_BLANK_TXT)

        #nodate
        nodate_t = cursor.execute("SELECT * FROM alltasks WHERE date = ? AND strike = 0 AND overdue=0", ("",))
        data_n = nodate_t.fetchall()
        self.add_tabs(self.tab3, data_n, NODATE_BLANK_TXT)

    def add_tabs(self, tab, sorted_list, blank_txt):
        """Reloads the tabs"""
        for widgets in tab.winfo_children():
            widgets.destroy()
            
        Tab_frame(self, tab, sorted_list, self.check_btn, self.delete_btn, self.edit_btn,blank_txt)

    def check_btn(self,task, date, priority):
        """Delete or updates the database after clicking on the checkbutton."""
        conn = sqlite3.connect(DATA_BASE_FILE)
        cursor = conn.cursor()
        if date:
            if convert(date) == convert(TODAY_STRING ):
                cursor.execute("UPDATE alltasks SET strike =1 WHERE task =? AND date =?",(task, date,)) 
            else:
                cursor.execute("DELETE FROM alltasks WHERE task=? AND date=?", (task, date,))
        else:
            cursor.execute("DELETE FROM alltasks WHERE task=? AND priority=?", (task, priority,))

        conn.commit()
        conn.close()
        self.fetch_data()
		
    def edit_btn(self,task,date,priority,check_color):
        """Places the edit frame after clicking on the "edit" button."""
        Edit_frame(self.master,task,date,priority,check_color, self)


    def delete_btn(self,task, priority):
        """Deletes the task from the datanase"""
        delete_box = messagebox.askquestion("Delete task", f"Do you want to delete '{task}'?")
        if delete_box == 'yes':
            conn = sqlite3.connect(DATA_BASE_FILE)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM alltasks WHERE task=? AND priority=?", (task, priority,))
            conn.commit()
            conn.close()
            self.fetch_data()
            task_add_del_notification(task, 'deleted')

class Top_frame(ttk.Frame):
    def __init__(self, parent, progress_int, prog_str):
        super().__init__(parent)
        
        self.progress = ttk.Progressbar(self, bootstyle = f'{STYLE}-striped', value=100, variable=progress_int)
        self.lab = ttk.Label(self, textvariable= prog_str, text="0.0 %",font=("Arial", 18, 'bold'))
        self.lab_t = ttk.Label(self, text=f"Today - {TODAY_LABEL}",font=("Arial", 12, 'bold'))

        self.columnconfigure((0,1,2,3,4,5), weight=1,uniform='a')
        self.rowconfigure((0,1),weight=1, uniform='a')

        self.lab_t.grid(column=0, row=0, sticky='sw',padx=10,columnspan=2)
        self.lab.grid(column=5, row=0, sticky='se', padx=10)
        self.progress.grid(column=0, row=1, columnspan=6, sticky='ew', padx=10)

class Add_frame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bootstyle = 'dark')
        self.parent = parent
        self.priority_str = tk.StringVar(value=PRIORITY_LAVELS[3])

        self.close_btn = ttk.Button(self, text='✕',bootstyle=STYLE_OUTLINE, command=self.close_frm)
        ToolTip(self.close_btn, text = 'Close', bootstyle = STYLE_INVERSE)
        self.close_btn.place(relx = 0.95, rely=0)

        self.ent_tsk = ttk.Entry(self, bootstyle = STYLE)#task
        ToolTip(self.ent_tsk, text = 'Task name', bootstyle = STYLE_INVERSE)
        self.ent_tsk.pack(side='left',padx=20, pady=5)

        self.ent_date = DateEntry(self,bootstyle = STYLE)#date entry
        self.ent_date.pack(side='left',padx=10, pady=5)

        self.comb_prt = ttk.Combobox(self,textvariable = self.priority_str, values=PRIORITY_LAVELS,bootstyle = STYLE).pack(side='left',padx=20, pady=5)
        self.insert_btn = ttk.Button(self, text="   Insert   ",bootstyle = STYLE, command=self.insert_data).pack(side='left',padx=10, pady=5)
        
        self.place(relx=RELX, rely=RELY, relwidth=RELWIDTH, relheight=RELHEIGHT)

    def close_frm(self):
        for widgets in self.winfo_children():
            widgets.destroy()
        self.place_forget()

    def insert_data(self):
        """Inserts the new tasks in the database."""
        tsk = self.ent_tsk.get()
        date = str(self.ent_date.entry.get())
        priority = self.priority_str.get()
        strike = 0
        overdue = 0
        priority_val = 0
        check_color = STYLE 
        is_valid_date = validate_date(date)
        is_valid_tsk = validate_task(tsk)

        if is_valid_tsk == True and is_valid_tsk == True:
            for pos,val in enumerate(PRIORITY_LAVELS):
                if val == priority:
                    priority_val = pos+1
            
            match priority_val:
                case 1:
                    check_color =PRIORITY_1
                case 2:
                    check_color =PRIORITY_2
                case 3:
                    check_color =PRIORITY_3

            con = sqlite3.connect(DATA_BASE_FILE)
            cursor = con.cursor()
            cursor.execute("CREATE TABLE IF NOT EXISTS alltasks (task TEXT, date TEXT, priority INTEGER, color TEXT,strike INTEGER, overdue INTEGER)")
            cursor.execute("INSERT INTO alltasks VALUES (?, ?, ?, ?, ?, ?)", (tsk, date, priority_val, check_color, strike, overdue))
            con.commit()
            con.close()

            self.ent_tsk.delete(0, tk.END)
            self.priority_str.set(PRIORITY_LAVELS[3])
            Main_frame.fetch_data(self.parent)
            task_add_del_notification(tsk, 'created')
        
        else:
            if is_valid_tsk == False:
                messagebox.showerror("Something went wrong", "Please enter the task name.") 
            elif is_valid_date == False:
                messagebox.showerror("Something went wrong", "Invalid date.")

class Edit_frame(ttk.Frame):
    def __init__(self, parent,task,date,priority,check_color,main_frame):
        super().__init__(parent,bootstyle = 'dark')
        self.main_frame = main_frame
        self.task = task
        self.date = date
        self.priority_o = priority
        self.check_color = check_color
        self.priority_str = tk.StringVar()

        for pos, pri in enumerate(PRIORITY_LAVELS):
            if pos+1 == self.priority_o:
                self.priority_str.set(pri)

        self.close_btn = ttk.Button(self, text='✕',bootstyle=STYLE_OUTLINE, command= self.close_frm)
        ToolTip(self.close_btn, text = 'Close', bootstyle = STYLE_INVERSE)
        self.close_btn.place(relx = 0.95, rely=0)

        self.ent_tsk = ttk.Entry(self, bootstyle = STYLE)#task
        self.ent_tsk.pack(side='left',padx=20, pady=5)

        self.ent_date = DateEntry(self,bootstyle = STYLE, startdate = convert(self.date))#date entry
        self.ent_date.pack(side='left',padx=10, pady=5)

        self.comb_prt = ttk.Combobox(self,textvariable = self.priority_str, values= PRIORITY_LAVELS,bootstyle = STYLE).pack(side='left',padx=20, pady=5)
        self.insert_btn = ttk.Button(self, text="   Done   ",bootstyle = STYLE, command=self.edit_data).pack(side='left',padx=10, pady=5)
        
        self.ent_tsk.insert(0,self.task)

        self.place(relx=RELX, rely=RELY, relwidth=RELWIDTH, relheight=RELHEIGHT)       
        

    def close_frm(self):
        for widgets in self.winfo_children():
            widgets.destroy()
        self.place_forget()
    
    def edit_data(self):
        """Update the data (task name/date/priority)"""
        conn = sqlite3.connect(DATA_BASE_FILE)
        cursor = conn.cursor()
        task_new = self.ent_tsk.get()
        date_new = self.ent_date.entry.get()
        priority_new = 0
        check_color_new = STYLE
        is_valid_date = validate_date(date_new)
        is_valid_tsk = validate_task(task_new)
        
        if is_valid_date == True and is_valid_tsk == True:
            for pos, val in enumerate(PRIORITY_LAVELS):
                if val == self.priority_str.get():
                    priority_new = pos+1

            match priority_new:
                case 1:
                    check_color_new =PRIORITY_1
                case 2:
                    check_color_new =PRIORITY_2
                case 3:
                    check_color_new =PRIORITY_3
            
            cursor.execute("SELECT * FROM alltasks WHERE task=? AND date=?",(self.task,self.date))
            cursor.execute("UPDATE alltasks SET task =?, date =?, priority=?, color=? WHERE task=? AND date=?", (task_new, date_new, priority_new, check_color_new,self.task, self.date))
            conn.commit()
                
            conn.close()
            Main_frame.fetch_data(self.main_frame)
            task_add_del_notification(self.task, 'edited')
            self.close_frm()    
        else:
            if is_valid_tsk == False:
                messagebox.showerror("Something went wrong", "Please enter the task name.") 
            elif is_valid_date == False:
                messagebox.showerror("Something went wrong", "Invalid date.") 

class Bottom_frame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        self.add_button = ttk.Button(self, text='Add',bootstyle = STYLE, command =self.print_btn, width=30)
        ToolTip(self.add_button, text = 'Add task', bootstyle = STYLE_INVERSE)
        self.add_button.pack(padx = 10, pady= 10)

    def print_btn(self):
        Add_frame(self.master)


if __name__=='__main__':
    Main('My To-DO', (800,500))