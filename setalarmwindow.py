import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gtk
from gi.repository import Gdk
import datetime
import subprocess
import share
import datetime
import locale
loc = locale.getlocale()
locale.setlocale(locale.LC_ALL, loc)

filepath = 'sinoamarelo.svg'

class SetAlarmWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Erinnerung erstellen")
        #Sets the position beginig with CENTER for non-supporting systems
        self.set_position(Gtk.WindowPosition.CENTER)
        #self.set_gravity(Gdk.Gravity.NORTH_EAST)
        self.move(Gdk.Screen.width() - self.get_size().width,0)

        # set dialog measures and spacing
        #self.set_default_size(150, 100)

        # set icon
        self.set_icon_from_file(filepath)

        self.connect('destroy', self.quit_window)
        box = Gtk.Box()

        box.set_orientation(Gtk.Orientation.VERTICAL)
        box.set_border_width(10)
        box.set_spacing(6)

        # create a label
        task_label = Gtk.Label()
        task_label.set_text('Text der angezeigt werden soll: ')
        box.add(task_label)

        # create a field to input the task description
        self.task_field = Gtk.Entry()
        self.task_field.set_text("Text hier eingeben ...")
        box.add(self.task_field)

        # Calculate the datetime for NOW + 5 minutes
        localtime = datetime.datetime.now()
        localtime_plus_5_min = localtime + datetime.timedelta(minutes=1)
 
        # create calendar
        self.cal = Gtk.Calendar()
        box.add(self.cal)

        # Setting correct calendar date -> month is between 0 and 11
        self.cal.select_day(localtime_plus_5_min.day)
        self.cal.select_month(  localtime_plus_5_min.month - 1,
                                localtime_plus_5_min.year )
        
        # create time fields
        time_hbox = Gtk.HBox()
        hour_adjustment = Gtk.Adjustment(00, 00, 23, 1, 10, 0)
        minute_adjustment = Gtk.Adjustment(00, 00, 59, 1, 10, 0)
        self.hours_field = Gtk.SpinButton()
        self.minutes_field = Gtk.SpinButton()
        self.hours_field.set_adjustment(hour_adjustment)
        self.minutes_field.set_adjustment(minute_adjustment)
        self.hours_field.connect('output', self.show_leading_zeros)
        self.minutes_field.connect('output', self.show_leading_zeros)
        
        # Setting correct time values
        self.hours_field.set_value(localtime_plus_5_min.hour)
        self.minutes_field.set_value(localtime_plus_5_min.minute)

        # creates a : separator between the two SpinButtons
        time_sep_label = Gtk.Label()
        time_sep_label.set_text(' : ')

        # add time fields to the box
        time_hbox.add(self.hours_field)
        time_hbox.add(time_sep_label)
        time_hbox.add(self.minutes_field)

        # add time box to calendar box
        box.add(time_hbox)

        # add OK button
        button_set_alarm = Gtk.Button("OK")
        button_set_alarm.connect('clicked', self.button_set_alarm_cliked)
        box.add(button_set_alarm)
        self.add(box)
        self.show_all()

    def show_leading_zeros(self, spin_button):
        adjustement = spin_button.get_adjustment()
        spin_button.set_text('{:02d}'.format(int(adjustement.get_value())))
        return True

    def quit_window(self, window):
        self.destroy()

    def button_set_alarm_cliked(self, button):
        task_description = self.task_field.get_text()
        date = self.cal.get_date()
        hours = self.hours_field.get_text()
        minutes = self.minutes_field.get_text()
        self.alarm_time = datetime.datetime(date.year, date.month + 1, date.day, int(hours), int(minutes))

        # if time not valid, forget the time with a notification
        if self.alarm_time < datetime.datetime.now():
            self.sendmessage("Erinnerung ist in der Vergangenheit, bitte ??ndern.")
            self.alarm_time = None
        print(task_description, self.alarm_time)

        # create task
        if self.alarm_time != None:
            share.tasklist.create_task(description=task_description, alarm=self.alarm_time)
            # save the tasks here to avoid shutdown saving
            share.tasklist.save_tasks()
            self.destroy()

    def sendmessage(self, message):
        subprocess.Popen(['notify-send', "Erinnerung", message])
