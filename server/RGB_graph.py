import matplotlib.pyplot as plt
import hashlib
import os
import numpy as np

# File checking Globals
FILE_NAME = 'RGB_data.txt'
THRESHOLD_NAME = 'RGB_thresholds.txt'
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
        high = list(map(int, contents[0].split(" ")))
        low = list(map(int, contents[1].split(" ")))
    except ValueError:
        print("Invalid literal for int:\n", high, "\n", low)
    f.close()
        
    return high, low

def setupPlot():
    n_groups = 24
    fig, axis = plt.subplots()
    index = np.arange(n_groups)

    plt.show(block=False)

    #set up axes and titles
    axis.set_xticks(index)
    axis.set_xlabel('Threshold Calibration')
    axis.set_xlim(0,24)
    axis.set_ylim(0, 1500000)#will need to change
    axis.set_ylabel('Raw Sensor Value')
    axis.set_title('RGB Sensor Threshold Debug')

    #plot thresholds
    high, low = getThresholdData()
    plt.plot(high, 'g--')
    plt.plot(low, 'r--')
    axis.annotate('|       Red       |', xy=(1, 1400000))
    axis.annotate('|       Green      |', xy=(7, 1400000))
    axis.annotate('|        Blue        |', xy=(13, 1400000))
    axis.annotate('|      Black      |', xy=(19, 1400000))

    #set up bar for RGB data
    rgb_data = plt.bar([1,3,5,7,9,11,13,15,17,19,21,23], [0,0,0,0,0,0,0,0,0,0,0,0])
    #ir_data[0].set_facecolor('b')

    fig.canvas.draw()
    

    fig.canvas.mpl_connect('close_event', handle_close)
    
    
    return fig, rgb_data

def updatePlot(fig, rgb_data):
    f = open(FILE_NAME, 'r')

    contents = f.read().rstrip()
    contents = contents.split("\n")
    r = 0
    g = 0
    b = 0
    try:
        #raw = int(contents[0])
        r = int(contents[0])
        g = int(contents[1])
        b = int(contents[2])
    except ValueError:
        print('Invalid literal for int:\n', r, g, b, '\n')
    f.close()
    
    num = 0
    for each in rgb_data:
        if num == 0:
            each.set_height(r)
            each.set_facecolor('r')
            num = 1
        elif num == 1:
            each.set_height(g)
            each.set_facecolor('g')
            num = 2
        else:
            each.set_height(b)
            each.set_facecolor('b')
            num = 0
            
    fig.canvas.draw()
    plt.pause(0.01)
        


if __name__ == '__main__':
    fig, bar = setupPlot()
    while True:
        # check for exit flag to stop infinite loop
        if exit_bool:
            print('Plot Exitted')
            break
        if did_file_update() and os.stat(FILE_NAME).st_size > 0:
            updatePlot(fig, bar)

