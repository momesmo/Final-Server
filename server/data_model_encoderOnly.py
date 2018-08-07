import matplotlib.pyplot as plt
import hashlib
import os
import sys
import numpy as np

# Plotting Globals
MAX_ENCODER_DATA = 200
exit_bool = False
xdata = []
ydata_left = []
ydata_right = []

# File checking Globals
FILE_NAME = 'a.txt'
prev_hash = ""
curr_hash = ""

def did_file_update():
    global prev_hash, curr_hash
    prev_hash = curr_hash
    hasher = hashlib.md5()
    with open(FILE_NAME, 'rb') as f:
        buf = f.read()
        hasher.update(buf)
    curr_hash = hasher.digest()
    if curr_hash != prev_hash:
        return True
    else:
        return False

def handle_close(evt):
    global exit_bool
    print('Exiting Plot')
    exit_bool = True
    plt.close(fig)
    sys.exit()

def setupPlot():
    global xdata, ydata_left, ydata_right

    plt.show()

    fig = plt.figure()
    ax = fig.add_subplot(111)
    # Setting up encoder plot
    ax.set_title('Encoder Values', fontsize=14)
    ax.set_ylabel('Encoder Ticks (ticks/second', fontsize=12)
    ax.set_xlabel('', fontsize=12)
    ax.set_xlim(0, MAX_ENCODER_DATA)
    ax.set_ylim(30, 60)

    major_ticks = np.arange(0, 101, 10)
    minor_ticks = np.arange(0, 101, 5)
    major_ticks200 = np.arange(0, 201, 20)
    minor_ticks200 = np.arange(0, 201, 5)
    ax.set_yticks(major_ticks, minor=False)
    ax.set_yticks(minor_ticks, minor=True)
    ax.set_xticks(major_ticks200, minor=False)
    ax.set_xticks(minor_ticks200, minor=True)
    ax.grid(which='major', alpha=0.8)
    ax.grid(which='minor', alpha=0.4)

    #ax.grid(c='grey', linestyle='-', linewidth='1')

    line1, = ax.plot(xdata, ydata_left, 'r-')
    line2, = ax.plot(xdata, ydata_right, 'g-')

    ax.relim()
    ax.autoscale_view(True, True, True)
    fig.canvas.draw()
    plt.show(block=False)

    fig.canvas.mpl_connect('close_event', handle_close)

    return fig, line1, line2


def update_plot(fi, l1, l2):
    global xdata, ydata_left, ydata_right
    f = open(FILE_NAME, 'r')

    contents = f.read().rstrip()
    contents = contents.split("\n")
    try:
        xdata = list(map(int, contents[0].split(" ")))
        ydata_left = list(map(int, contents[1].split(" ")))
        ydata_right = list(map(int, contents[2].split(" ")))
    except ValueError:
        print('Invalid literal for int [Line 82]:\n', xdata, '\n', ydata_left, '\n', ydata_right)

    f.close()

    l1.set_xdata(xdata)
    l1.set_ydata(ydata_left)
    l2.set_xdata(xdata)
    l2.set_ydata(ydata_right)

    fi.canvas.draw()
    plt.pause(0.01)


if __name__ == '__main__':
    fig, line1, line2 = setupPlot()
    # print(type(fig), type(line1), type(line2))
    while True:
        if exit_bool:
            print('Plot Exitted')
            break
        if did_file_update() and os.stat(FILE_NAME).st_size > 0:
            update_plot(fig, line1, line2)
        # check for exit flag to stop infinite loop
