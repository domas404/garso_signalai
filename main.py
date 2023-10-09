import numpy as np
import os
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import tkinter as tk
from tkinter import filedialog
from scipy.io import wavfile
from datetime import timedelta

root = tk.Tk()
root.withdraw()

class FileData:
    def __init__(self, file_path, samplerate, data):
        self.file_path = file_path
        self.samplerate = samplerate
        self.data = data
        self.bit_depth = data.dtype.itemsize * 8
        self.duration = len(data)/samplerate

def readData():
    file_path = filedialog.askopenfilename()
    samplerate, data = wavfile.read(file_path)
    return file_path, samplerate, data

def menuDialog():
    input_ok = False
    print("MENU\n", "[1] Open file\n", "[2] Quit")
    while(not input_ok):
        menuInput = input("> ")
        if(menuInput == '2'):
            print("Exiting...")
            exit()
        elif(menuInput == '1'):
            input_ok = True
            fileMenuDialog()
            print("Processing...")
    
def markerInput(playback_time, total_length_to_display):
    print(f"audio length: {total_length_to_display}")
    print("Enter marker time:")
    mins = 0
    input_ok = False
    while(not input_ok):
        try:
            if(playback_time > 60):
                mins = float(input("Minutes: "))
            secs = float(input("Seconds: "))
            if secs >= 60 or secs < 0:
                raise ValueError("Incorrect time value")
            elif mins*60+secs > playback_time:
                raise ValueError("Time value out of bounds")
            else:
                input_ok = True
        except ValueError as ve:
            print(f"Error: {ve}. Try again.")
    return (mins, secs)

def createMarker(playback_time, total_length_to_display):
    mins, secs = markerInput(playback_time, total_length_to_display)
    markerTimestamp = (mins*60)+secs
    if(playback_time > 60):
        markerTimestamp = markerTimestamp/60
    marker_time_to_display = str(timedelta(minutes=mins, seconds=secs))[2:]
    if(len(marker_time_to_display) > 6):
        marker_time_to_display = marker_time_to_display[:9]
    else:
        marker_time_to_display += ".000"
    markerPosition = mpatches.Patch(color='none', linestyle=':', label=f"Marker at:\n{marker_time_to_display}")
    plt.axvline(x=markerTimestamp, color='#ff3838')
    return markerPosition

def plotLegend(channel_count, samplerate, bit_depth):
    channels_label = mpatches.Patch(color='none', linestyle=':', label=f'{channel_count} channel{"s" if channel_count > 1 else ""}')
    samplerate_label = mpatches.Patch(color='none', linestyle=':', label=f"{samplerate/1000} kHz")
    bit_depth_label = mpatches.Patch(color='none', label=f"{bit_depth}-bit")
    return [channels_label, samplerate_label, bit_depth_label]

def plotMono(data, time, samplerate, bit_depth, marker = False, line_wt = 0.5, y_label = '', file_path=''):
    x = time
    y = data

    figure = plt.figure()
    figure.set_figwidth(12)
    figure.set_figheight(6)

    timeLabels = []
    playback_time = time[len(time)-1]

    if(playback_time > 60):
        x = x/60
        time_label = "Time, min"

    plt.title(os.path.basename(file_path))
    plt.grid(color='#ddd')
    plt.plot(x, y, linewidth=line_wt, color='#4986cc')

    leg = plt.legend(handles=plotLegend(1, samplerate, bit_depth), handlelength=0, borderpad=0.8, bbox_to_anchor=(1.01, 1), loc='upper left', borderaxespad=0.)
    plt.gca().add_artist(leg)
    total_length_to_display = str(timedelta(seconds=playback_time))[2:]
    if (len(total_length_to_display) > 6):
        total_length_to_display = total_length_to_display[:9]
    if(marker):
        markerPosition = createMarker(playback_time, total_length_to_display)
        timeLabels.append(markerPosition)
    audiotime = mpatches.Patch(color='none', linestyle=':', label=f"File length:\n{total_length_to_display}")
    timeLabels.append(audiotime)
    time_label = "Time, s"
    plt.legend(handles=timeLabels, handlelength=0, borderpad=0.8, bbox_to_anchor=(1.01, 0), loc='lower left', borderaxespad=0.)

    plt.xlabel(time_label)
    plt.ylabel(y_label)
    plt.tight_layout()

    plt.show()

# def plotStereo():
#     x = np.array(time)

#     channelCount = data.shape[1]
#     figure, axis = plt.subplots(channelCount, 1)
#     figure.set_figwidth(13)
#     figure.set_figheight(8)

#     stereo_array = [ []*1 for i in range(channelCount) ]

#     for i in range(0, channelCount):
#         for j in range(0, len(data)):
#             stereo_array[i].append(data[j][i])

#     figure.suptitle(os.path.basename(file_path))

#     mins, secs = addMarker()
#     markerTimestamp = (mins*60)+secs
#     time_label = "Time, s"

#     if(playback_time > 60):
#         x = x/60
#         markerTimestamp = markerTimestamp/60
#         time_label = "Time, min"

#     colors = ['#4986cc', '#75aceb']
    
#     for i in range(0, channelCount):
#         axis[i].grid(color='#ddd')
#         axis[i].plot(x, stereo_array[i], color=colors[i%2], linewidth=0.5)
#         axis[i].axvline(x=markerTimestamp, color='#ff3838')

#     marker_time_to_display = str(timedelta(minutes=mins, seconds=secs))[2:]
#     if(len(marker_time_to_display) > 6):
#         marker_time_to_display = marker_time_to_display[:9]
#     else:
#         marker_time_to_display += ".000"

#     markerPosition = mpatches.Patch(color='none', linestyle=':', label=f"Marker at:\n{marker_time_to_display}")
#     audiotime = mpatches.Patch(color='none', linestyle=':', label=f"File length:\n{total_length_to_display}")
    
#     leg = axis[0].legend(handles=plotLegend(channelCount), handlelength=0, borderpad=0.8, bbox_to_anchor=(1.01, 1), loc='upper left', borderaxespad=0.)
#     axis[0].add_artist(leg)
#     plt.legend(handles=[markerPosition, audiotime], handlelength=0, borderpad=0.8, bbox_to_anchor=(1.01, 0), loc='lower left', borderaxespad=0.)
#     axis[channelCount-1].set_xlabel(time_label)

#     figure.tight_layout()

#     plt.show()

def getFrameSize(timeFrame, samplerate):
    return int(samplerate/1000*timeFrame)

def normalizeData(data):
    min_val = min(data)
    max_val = max(data)
    new_data = []
    for i in range(0, len(data)):
        new_data.append((data[i] - min_val) / (max_val - min_val))
    return new_data

def splitDataIntoFrames(data, samplerate):
    timeFrame = 20 # milliseconds
    frameSize = getFrameSize(timeFrame, samplerate) # values in one timeFrame
    frameRate = int(frameSize/2) # frames overlap between each other by 50% of values
    dataFrames = []

    for i in range(0, len(data)-frameSize, frameRate):
        singleFrame = []
        for j in range(i, i+frameSize):
            singleFrame.append(data[j])
        dataFrames.append(singleFrame)

    # last frame from remaining values
    singleFrame = []
    for i in range(len(data)-frameSize, len(data)):
        singleFrame.append(data[i])
    dataFrames.append(singleFrame)

    return dataFrames

def calculateEnergy(data, samplerate, duration, file_path, bit_depth):
    energy = []
    for i in range(0, len(data)):
        frameEnergy = 0
        for j in range(0, len(data[i])):
            frameEnergy += data[i][j]**2
        energy.append(frameEnergy)
    plotMono(energy, np.arange(0, duration, duration/len(energy)), samplerate, bit_depth, line_wt=1, y_label='Energy', file_path=file_path)

def calculateZeroCrossingRate(data, samplerate, duration, file_path, bit_depth):
    ZCR = []
    for i in range(0, len(data)):
        frameNKS = 0
        for j in range(1, len(data[i])):
            frameNKS += abs(1 if data[i][j] >= 0 else -1 - 1 if data[i][j-1] > 0 else -1)
        frameNKS = frameNKS/(2*len(data[i]))
        ZCR.append(frameNKS)
    plotMono(ZCR, np.arange(0, duration, duration/len(ZCR)), samplerate, bit_depth, line_wt=1, y_label='Zero-Crossing Rate', file_path=file_path)

def fileMenuDialog():
    file_path, samplerate, data = readData()
    data = np.array(data, dtype=int)
    duration = len(data)/samplerate
    bit_depth = data.dtype.itemsize * 8

    input_ok = False
    while(not input_ok):
        print("\nfilename.wav\n", "[1] Energy plot\n", "[2] ZCR plot\n", "[3] Time plot\n", "[4] Menu")
        plotMenuInput = input("> ")
        if(plotMenuInput == "1"):
            calculateEnergy(splitDataIntoFrames(normalizeData(data), samplerate), samplerate, duration, file_path, bit_depth)
        elif(plotMenuInput == "2"):
            calculateZeroCrossingRate(splitDataIntoFrames(data, samplerate), samplerate, duration, file_path, bit_depth)
        elif(plotMenuInput == "3"):
            plotMono(data, np.arange(0, duration, 1/samplerate), samplerate, bit_depth, file_path=file_path, marker=True)
        elif(plotMenuInput == "4"):
            menuDialog()
            input_ok = True

menuDialog()

# if(len(data.shape) < 2):
#     plotMono(data, np.arange(0, duration, 1/samplerate))
# else:
#     plotStereo()
