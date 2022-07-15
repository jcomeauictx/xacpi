#!/usr/bin/python3 -OO
'''
tray icon battery indicator

adapted from //ubuntuforums.org/showthread.php?t=1153951,
//code.activestate.com/recipes/475155-dynamic-system-tray-icon-wxpython/,
//stackoverflow.com/a/35622776/493161
any original code Copyright (c) 2013, 2022 jc.unternet.net
licensing GPL3 or later
'''
import subprocess, re, logging  # pylint: disable=multiple-imports
import wx
import wx.adv
logging.basicConfig(level=logging.DEBUG if __debug__ else logging.INFO)
# python2-3 compatibility
if bytes([255]) == '[255]':  # python2
    # pylint: disable=redefined-builtin
    bytes = lambda values: ''.join(map(chr, values))
# pylint complains about wx attributes for no reason
# pylint: disable=no-member
APP = wx.App()  # must put this near beginning
ACPI_PATTERN = b'^Battery 0:\\s+(\\w+), (\\d+)%'
ACPI_FAIL = '(acpi failure)'
UPDATE_TIME = 5  # seconds
MILLISECONDS = 1000  # multiplier for seconds
UPDATER = wx.NewEventType()  # returns unique (to this app) ID
WIDTH = HEIGHT = 32
BORDER_WIDTH = BORDER_HEIGHT = 1  # black border -- width and height the same
PADDING_WIDTH = int(WIDTH / 5)
BATTERY_WIDTH = WIDTH - (PADDING_WIDTH * 2) - (BORDER_WIDTH * 2)
TRANSPARENT = wx.Colour('white').Get(includeAlpha=False)
GREEN = wx.Colour('green').Get(includeAlpha=False)
YELLOW = wx.Colour('yellow').Get(includeAlpha=False)
RED = wx.Colour('red').Get(includeAlpha=False)
BLACK = wx.Colour('black').Get(includeAlpha=False)
COLORS = {
    # colors from acpi call results
    'Full': 'green',
    'Charging': 'green',
    'Discharging': 'yellow',
    ACPI_FAIL: 'red',
    # actual wx colors as RGB tuples
    'red': RED,
    'yellow': YELLOW,
    'green': GREEN,
    'border': BLACK,
    'padding': TRANSPARENT,
}
WARNING_LEVEL = 3  # show red when this many lines

class Icon(wx.adv.TaskBarIcon):
    '''
    battery monitor icon
    '''
    # pylint: disable=too-few-public-methods
    def __init__(self, frame):
        '''
        initialize the TaskBarIcon
        '''
        wx.adv.TaskBarIcon.__init__(self)
        self.frame = frame
        self.update()
        self.timer = wx.Timer(self, UPDATER)
        self.Bind(wx.EVT_TIMER, self.update, self.timer)
        self.timer.Start(UPDATE_TIME * MILLISECONDS)
        logging.debug('initialization complete')

    def update(self, event=None):
        '''
        update battery charge level
        '''
        logging.log(logging.NOTSET, 'event: %s', event)  # for pylint
        status, charge = acpi()
        color, charge = icon_data(status, charge)
        pixels = build_image(color, charge)
        image = wx.Image(WIDTH, HEIGHT, pixels)
        bitmap = image.ConvertToBitmap()
        bitmap.SetMask(wx.Mask(bitmap, TRANSPARENT))
        icon_image = wx.Icon()
        icon_image.CopyFromBitmap(bitmap)
        self.SetIcon(
            icon=icon_image,
            tooltip="Battery 0 State: %s, %s" % (status, charge)
        )

class IconApp(wx.Frame):
    '''
    1-pixel frame just to satisfy wx
    '''
    # pylint: disable=too-few-public-methods
    def __init__(self):
        '''
        initialize "application", really just a container for the icon
        '''
        wx.Frame.__init__(self, None, wx.ID_ANY, "", size=(1,1))
        self.app = Icon(self)
        self.Bind(wx.EVT_CLOSE, self.on_close)

    def on_close(self, event):
        '''
        cleanup when app signaled to stop
        '''
        logging.debug('cleaning up after %s', event)
        self.app.RemoveIcon()
        self.app.Destroy()
        self.Destroy()

def build_image(color, charge):
    '''
    create RGB representation of battery charge level

    just a bunch of joined RGB bytes, WIDTH * HEIGHT * 3 bytes long
    '''
    border = pixel(COLORS['border'])
    padding = pixel(COLORS['padding'])
    battery_height = HEIGHT - (2 * BORDER_HEIGHT)
    charge_height = int((float(charge) / 100) * battery_height)
    if color == 'yellow' and charge_height <= WARNING_LEVEL:
        color = 'red'
    charge = pixel(COLORS[color])
    left = (padding * PADDING_WIDTH) + border
    right = border + (padding * PADDING_WIDTH)
    # top line of icon, just border and padding
    pixels = left + (border * BATTERY_WIDTH) + right
    # now color in the battery
    for i in range(battery_height):
        rowcolor = charge
        if (battery_height - 1 - i) > charge_height:
            rowcolor = padding
        pixels += left + (rowcolor * BATTERY_WIDTH) + right
    # bottom line of icon
    pixels += left + (border * BATTERY_WIDTH) + right
    logging.debug('pixels: %r, length: %d', pixels, len(pixels))
    return pixels

def pixel(color):
    '''
    turn RGB color tuple into bytestring
    '''
    return bytes(color)

def acpi():
    '''
    call the `acpi` program and return charging status and level
    '''
    output = subprocess.check_output(['acpi']).rstrip()
    logging.debug('acpi: %s', output)
    status = re.compile(ACPI_PATTERN).match(output)
    logging.debug('status: %s', repr(status.groups()) if status else status)
    return status.groups() if status else (ACPI_FAIL, '5')

def icon_data(word, number):
    '''
    convert charging status to color, and make sure number is an integer

    yellow is default; gets turned to red at image creation time if very low
    '''
    color, charge = COLORS.get(word, 'yellow'), int(number)
    return color, charge

if __name__ == '__main__':
    IconApp()
    APP.MainLoop()
