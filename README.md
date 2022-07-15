# xacpi
battery monitor for minimalist GNU/Linux Xwindow managers such as fluxbox

## prerequisites (assumes Debian Bullseye, adapt to your distribution)
`sudo apt install acpi`

Python3: `sudo apt install python3-wxgtk4.0`

Python2: `pip2 install --user --upgrade wxpython`

## quickstart
From command line: `./xacpi.py`

You should see the icon appear in the taskbar (systray)

## installation
In ~/.fluxbox/startup, put (for example)
`/usr/src/jcomeauictx/xacpi/xacpi.py &>/tmp/xacpi.log &`

It may also work on python2. It does at the creation of this repository.
