import datetime
import pickle
from functools import total_ordering
#from playme import Playme
import time
import threading
import subprocess
from xdg.BaseDirectory import save_data_path
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import datetime
import locale
loc = locale.getlocale()
locale.setlocale(locale.LC_ALL, loc)

share_dir = save_data_path("bzoing")

class Playme():
    def __init__(self):
        #self.wf = wave.open(filepath, 'rb')
        self.wf = '/usr/bin/canberra-gtk-play'

    def play(self):
        subprocess.call([self.wf,'--id','bell'])

@total_ordering
class Task():
    """Defines tasks, their representation and ordering."""
    def __init__(self, id, description, alarm, sound, function, notify):
        self.id = id
        self.description = description
        self.alarm = alarm
        self.function = function
        self.sound = sound
        self.notify = notify

    def __repr__(self):
        return '{}: {} {} {}'.format(self.__class__.__name__,
                                     self.id,
                                     self.description,
                                     self.alarm)

    def __lt__(self, other):
        if hasattr(other, 'alarm'):
            return self.alarm.__lt__(other.alarm)

    def __eq__(self, other):
        if hasattr(other, 'alarm'):
            return self.alarm.__eq__(other.alarm)


class Bzoinq():
    """Creates a running Bzoinq."""
    def __init__(self):
        self.task_id = 0
        self.task_list = []
        self.due_task_list = []
        self.temp_task_list = []
        # load the saved tasks
        try:
            with open(share_dir + "/" + 'outfile.p', 'rb') as fp:
                self.temp_task_list = pickle.load(fp)
            print("Erinnerungen aus Datei geladen")

        except IOError:
            print("Datei konnte nicht geladen werden")

        # move due tasks to due_task_list and not due tasks to task_list
        for task in self.temp_task_list:
            if datetime.datetime.now() > task.alarm:
                self.due_task_list.append(task)
            else:
                self.task_list.append(task)
        assert len(self.temp_task_list) == len(self.due_task_list) + len(self.task_list)
        self.temp_task_list = []

        # make task_id equal to the greatest of all task_id's
        bigger = 0
        for task in self.task_list:
            if task.id > bigger:
                bigger = task.id
        self.task_id = bigger
        print("neue Task id = {}".format(self.task_id))

    def __repr__(self):
        return '{}'.format(self.task_list)

    def create_task(self, description="Beispielerinnerung",
                    alarm=datetime.datetime.now(),
                    sound=True,
                    function=None,
                    notify=True):
        """Creates a new task"""
        assert type(alarm) is datetime.datetime
        self.task_id += 1
        # create the task
        new_task = Task(self.task_id, description, alarm, sound, function, notify)
        # add task to task list
        self.task_list.append(new_task)
        # sort the task list
        self.task_list = sorted(self.task_list)
        print("neue Erinnerung erstellt")

    def remove_task(self, id_to_remove):
        """Removes task with given id"""
        for task in self.task_list[:]:
            if task.id == id_to_remove:
                try:
                    self.task_list.remove(task)
                except:
                    print("Erinnerung konnte nicht entfernt werden")

    def remove_all_tasks(self):
        """Clears all the tasks"""
        self.task_list = []
        self.task_id = 0
        print("Alle Erinnerungen wurden bereinigt")

    def get_task_list(self):
        """Returns the list of tasks"""
        return self.task_list

    def save_tasks(self):
        """Saves current tasks to file"""
        with open(share_dir + "/" + 'outfile.p', 'wb') as fp:
            pickle.dump(self.task_list, fp)
        print("Erinnerungen wurden gespeichert")

    def change_alarm(self, id_to_change, new_time):
        """
        Changes the alarm time of a task.
        new_time must be a datetime object
        """
        assert type(new_time) is datetime.datetime
        # time on a task can only be changed if the task still exists
        for task in self.task_list()[:]:
            if task.id == id_to_change:
                task.alarm = new_time
        print("Erinnerung mit id {} geändert".format(id_to_change))

    def get_due_tasks(self):
        return self.due_task_list

    def clear_due_tasks(self):
        self.due_task_list = []


class Monitorthread(threading.Thread):
    def __init__(self, name=None, target=None):
        super().__init__(name=name, target=target)

    # def run(self):
    #     pass


class Monitor():
    """Defines a monitor that keeps checking a task list for changes"""
    def __init__(self, bzoinq_obj):
        self.stopit = False
        self.bzoinq_obj = bzoinq_obj

    def stop(self):
        """stops the monitor thread"""
        self.stopit = True

    def start(self):
        """Starts the monitor thread"""
        t = Monitorthread(target=self.keep_checking)
        t.start()
        print("Monitor Thread gestartet")

    def keep_checking(self):
        """Keeps checking time and sorts the task_list"""
        while True:
            time.sleep(1)
            if self.stopit:
                break
            # get current task list
            task_list = self.bzoinq_obj.get_task_list()
            if len(task_list) > 0:
                # make sure task_list is sorted
                task_list = sorted(task_list)
                # check the time
                current_time = datetime.datetime.now()
                if current_time >= task_list[0].alarm:
                    # get task id
                    current_id = task_list[0].id
                    current_desc = task_list[0].description
                    print("Alarm ausführen: {}".format(task_list[0].alarm))
                    # if there is a function, execute it
                    if task_list[0].function is not None:
                        task_list[0].function()
                    # play the sound if sound is True
                    if task_list[0].sound:
                        # play sound
                        my_sound = Playme()
                        my_sound.play()
                    if task_list[0].notify:
                        subprocess.Popen(['notify-send', "-t", "0", "-i", "clock", "Erinnerung", current_desc])
                        #self.open_message_window(current_desc)

                    # put due task in due_task_list
                    self.bzoinq_obj.due_task_list.append(task_list[0])
                    # remove current alarm from the original task_list
                    self.bzoinq_obj.remove_task(current_id)
                    print("erledigt {}".format(current_desc))

    def open_message_window(self, message, *args):
        self.dialog = Gtk.MessageDialog(
            flags=0,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text=message)
        self.dialog.run()
        print("INFO dialog closed")

        self.dialog.destroy()


# help function
def to_datetime(sometime):
    """converts Y-M-D 00:00:00 (string) time input to datetime"""
    try:
        my_datetime = datetime.datetime.strptime(sometime, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        print("Incorrect time. Please use Y-M-D 00:00:00 format.")
        raise ValueError
    return my_datetime
