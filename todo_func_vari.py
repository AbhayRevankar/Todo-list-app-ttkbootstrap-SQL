import datetime
import darkdetect # type: ignore
from ttkbootstrap.toast import ToastNotification # type: ignore


def convert(date):
	"""Converts a date string in 'dd-mm-YYYY' format to a datetime.date object."""
	if date:
		con = datetime.datetime.strptime(date, DATE_FROMAT)
		return con.date()
	else:
		return None	
	
def validate_task(task):
	"""Returns True if the task name is valid else returns False"""
	if task:
		if task.isspace():
			return False
		else:
			return True
	return False

def validate_date(date):
	"""Returns True if the date is valid else returns False"""
	if date:
		try:
			convert(date)
			return True
		except ValueError:
			return False
	
def detect_theme_mode():
	"""Returns a theme based on the system's light/dark mode."""
	try:
		return "solar" if darkdetect.isDark() else "journal_by_abhay"
	except Exception as e:
		return "journal_by_abhay"

def task_add_del_notification(task, key, duration=4000, title="My To-do says:"):
	"""Display a toast notification for task actions (add/delete/edit)"""
	theme = 'dark' if darkdetect.isDark() else 'light'
	message=f"The task by name \"{task}\" have been {key} successfully."

	toast = ToastNotification(
	bootstyle = theme,
	title=title,
	icon = '',
	message=message,
	duration=duration,
)
	toast.show_toast()

DATA_BASE_FILE = "tasks.db"
ICON = "checked_icon.ico"
DATE_FROMAT = '%d-%m-%Y'
TODAY = datetime.date.today()
TODAY_STRING = str(TODAY.strftime(DATE_FROMAT)) 
TODAY_LABEL = str(TODAY.strftime("%a, %b %d"))
PRIORITY_LAVELS = ('Priority - 1','Priority - 2','Priority - 3','Priority - 4')
RELX = 0.05
RELY = 0.7
RELWIDTH = 0.9
RELHEIGHT = 0.25
TODAY_BLANK_TXT = "There is nothing to strike today.\nClick on the \"Add\" button to create tasks."
UPCOMING_BLANK_TXT = "There are no future tasks yet,so you can\nadd one. Click the \"Add\" button to get\nstarted."
NODATE_BLANK_TXT ="There are no tasks with blank dates."
STYLE = 'success'
STYLE_OUTLINE = f'{STYLE}-outline'
STYLE_INVERSE = f'{STYLE}-inverse'
PRIORITY_1 = 'warning'
PRIORITY_2 = 'primary'
PRIORITY_3 = 'info'
