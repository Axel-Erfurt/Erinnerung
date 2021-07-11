#!/usr/bin/env python3

################################################
# Original by Luis Louro ©2017
# https://github.com/lapisdecor/bzoing
# Modifications June 2021 by Axel Schneider https://github.com/Axel-Erfurt
################################################

from tasks import Bzoinq, Monitor

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import share

gi.require_version('AppIndicator3', '0.1')
from gi.repository import AppIndicator3 as appindicator

import os
import setalarmwindow
import seetasks

filepath = os.path.join(os.path.dirname(__file__), 'sinoamarelo.svg')
APPINDICATOR_ID = 'bzoing'


class ReminderMenu(Gtk.Menu):
    def __init__(self):
        Gtk.Menu.__init__(self)

        new_icon = Gtk.Image.new_from_icon_name("list-add", 2)
        item_new_task = Gtk.ImageMenuItem(label='Neue Erinnerung', image=new_icon)
        item_new_task.connect('activate', self.new_task)
        self.append(item_new_task)

        item_see_icon = Gtk.Image.new_from_icon_name("calendar", 2)
        item_see_tasks = Gtk.ImageMenuItem(label='Erinnerungen anzeigen', image=item_see_icon)
        item_see_tasks.connect('activate', self.see_tasks)
        self.append(item_see_tasks)

        item_see_past_icon = Gtk.Image.new_from_icon_name("calendar", 2)
        item_see_past_tasks = Gtk.ImageMenuItem(label="vergangene Erinnerungen anzeigen", image=item_see_past_icon)
        item_see_past_tasks.connect('activate', self.see_past_tasks)
        self.append(item_see_past_tasks)

        item_separator = Gtk.SeparatorMenuItem()
        self.append(item_separator)

        exit_icon = Gtk.Image.new_from_icon_name("application-exit", 2)
        item_quit = Gtk.ImageMenuItem(label='Beenden', image=exit_icon)
        item_quit.connect('activate', self.quit)
        self.append(item_quit)

        self.show_all()

    def new_task(self, widget):
        """
        Creates new task window
        """
        alarm_window = setalarmwindow.SetAlarmWindow()


    def see_tasks(self, widget):
        """
        Shows a window with all the tasks and alarms
        """
        see_tasks_window = seetasks.SeeTasks()

    def see_past_tasks(self, widget):
        """
        Shows a window with all the done tasks
        """
        see_past_window = seetasks.SeePastTasks()


    def quit(self, widget):
        Gtk.main_quit()


class Gui:
    def __init__(self):
        self.indicator = appindicator.Indicator.new(APPINDICATOR_ID,
                                           filepath,
                                           appindicator.IndicatorCategory.APPLICATION_STATUS)
        self.indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
        self.my_menu = ReminderMenu()
        self.indicator.set_menu(self.my_menu)

def start():

    # start the tasklist (Bzoinq)
    share.tasklist = Bzoinq()

    # start the Monitor
    my_monitor = Monitor(share.tasklist)
    my_monitor.start()

    # start the gui and pass tasklist to the gui so we can create tasks
    # from the gui
    gui = Gui()
    Gtk.main()

    # save tasks
    share.tasklist.save_tasks()

    # stop the monitor
    my_monitor.stop()

    # goodbye message
    print("Auf Wiedersehen!")


if __name__ == "__main__":
    start()
