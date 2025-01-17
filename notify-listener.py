#!/usr/bin/python3
#
# Copyright (C) 2012 Paul W. Frields <stickster@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import os, sys
try:
    import gi
    gi.require_version('Notify', '0.7')
    from gi.repository import Notify, GLib
except:
    print >> sys.stderr, 'Could not locate pygobject'
    sys.exit(-1)
import dbus
import dbus.mainloop.glib
from subprocess import call

player = None
# It would be more kosher to do this with GStreamer, but in
# the interest of time:
for path in os.environ['PATH'].split(os.pathsep):
    if os.path.isfile(os.path.join(path, 'canberra-gtk-play')):
        player = os.path.join(path, 'canberra-gtk-play')
        break

class IrssiListener:
    def __init__(self):
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        self.bus = dbus.SessionBus()
        self.bus.add_signal_receiver(self.notify,
                                     signal_name='IrssiNotify',
                                     dbus_interface='org.irssi.Irssi',
                                     path='/org/irssi/Irssi')
        Notify.init('irssi')

    def notify(self, subject, message):
        n = Notify.Notification.new(subject,
                                    message,
                                    'dialog-information')
        # Concatenate messages for certain distros
        n.set_hint_string('x-canonical-append', 'true')
        n.show()

        proxy = None
        presence = None
        proxy = self.bus.get_object('org.gnome.SessionManager',
                                    '/org/gnome/SessionManager/Presence')
        if proxy:
            iface = dbus.Interface(proxy,
                                   'org.freedesktop.DBus.Properties')
            presence = iface.Get('org.gnome.SessionManager.Presence', 'status')

        if (not presence or presence == 0) and player is not None:
            retcode = call([player, '-i', 'message-new-instant'])
            if retcode < 0:
                print("ERROR: Player returned code %d" % (retcode))

    def __del__(self):
        Notify.uninit()

if __name__ == '__main__':
    l = IrssiListener()
    loop = GLib.MainLoop()
    loop.run()
