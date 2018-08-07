import matplotlib.pyplot as plt
import hashlib
import os
import numpy as np

# File checking Globals
FILE_NAME = 'IR_data.txt'
THRESHOLD_NAME = 'IR_thresholds.txt'
prev_hash = ""
curr_hash = ""

#Plotting globals
exit_bool = False

def handle_close(evt):
    global exit_bool
    print('Exiting Plot')
    exit_bool = True


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

def getThresholdData():
    f = open(THRESHOLD_NAME, 'r')

    contents = f.read().rstrip()
    contents = contents.split("\n")

    try:
        high = int(contents[0])
        low = int(contents[1])
    except ValueError:
        print('Invalid literal for int:\n', high, '\n', low)
    f.close()
        
    return high, low

def setupPlot():
    n_groups = 1
    fig, axis = plt.subplots()
    #index = np.arange(n_groups)

    plt.show(block=False)

    #set up axes and titles
    #axis.set_xticks(index)
    axis.set_xlabel('Threshold Calibration')
    axis.set_xlim(0,2)
    axis.set_ylim(0, 400)#will need to change
    axis.set_ylabel('Raw Sensor Value')
    axis.set_title('IR Sensor Threshold Debug')

    #plot thresholds
    high, low = getThresholdData()
    plt.plot([high, high, high], 'g--')
    plt.plot([low, low, low], 'r--')
    axis.annotate('^ Rover-Wall v - Threshold', xy=(1.3, high), xytext=(1.5, high+1),
                  arrowprops=dict(facecolor='black', shrink=0.05))
    axis.annotate('^ Wall-Error v - Threshold', xy=(1.3, low), xytext=(1.5, low-1),
                  arrowprops=dict(facecolor='black', shrink=0.05))

    #set up bar for IR data
    ir_data = plt.bar(1, 1, 1, align = 'center' )
    ir_data[0].set_facecolor('b')

    fig.canvas.draw()
    

    fig.canvas.mpl_connect('close_event', handle_close)
    
    
    return fig, ir_data

def updatePlot(fig, ir_data):
    f = open(FILE_NAME, 'r')

    contents = f.read().rstrip()
    contents = contents.split("\n")
    try:
        raw = int(contents[0])
    except ValueError:
        print('Invalid literal for int:\n', ir_data)
    f.close()

    ir_data[0].set_height(raw)
    fig.canvas.draw()
    plt.pause(0.01)
        


if __name__ == '__main__':
    fig, bar = setupPlot()
    # print(type(fig), type(line1), type(line2))
    while True:
        # check for exit flag to stop infinite loop
        if exit_bool:
            print('Plot Exitted')
            break
        if did_file_update() and os.stat(FILE_NAME).st_size > 0:
            updatePlot(fig, bar)

