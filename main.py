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
        self.file_name = os.path.basename(file_path)
        self.samplerate = samplerate
        self.data = np.array(data, dtype=int)
        self.bit_depth = data.dtype.itemsize * 8
        self.duration = len(data)/samplerate
        self.channel_count = 1 if(len(data.shape) < 2) else data.shape[1]

    def transposeData(self):
        if(self.channel_count > 1):
            new_data = np.array(self.data)
            new_data = np.transpose(new_data)
            self.data = new_data.tolist()

def readData():
    file_path = filedialog.askopenfilename()
    samplerate, data = wavfile.read(file_path)
    file = FileData(file_path, samplerate, data)
    return file

def convertTimeToReadableString(timeInSeconds):
    timeString = str(timedelta(minutes=timeInSeconds//60, seconds=timeInSeconds))[2:]
    if (len(timeString) > 6):
        timeString = timeString[:9]
    else:
        timeString += ".000"
    return timeString

def markerInput(duration):
    print(f"audio length: {convertTimeToReadableString(duration)}")
    print("Enter marker time:")
    mins = 0
    input_ok = False
    while(not input_ok):
        try:
            if(duration > 60):
                mins = float(input("Minutes: "))
            secs = float(input("Seconds: "))
            if secs >= 60 or secs < 0:
                raise ValueError("Incorrect time value")
            elif mins*60+secs > duration:
                raise ValueError("Time value out of bounds")
            else:
                input_ok = True
        except ValueError as ve:
            print(f"Error: {ve}. Try again.")
    return ((mins*60)+secs)

def createLegendPatch(label):
    return mpatches.Patch(color='none', label=label)

def createMarker(playback_time):
    markerTimestamp = markerInput(playback_time)
    if(playback_time > 60):
        markerTimestamp = markerTimestamp/60
    markerPosition = createLegendPatch(label=f"Marker at:\n{convertTimeToReadableString(markerTimestamp)}")
    plt.axvline(x=markerTimestamp, color='#ff3838')
    return markerPosition

def plotFilePropLegend(channel_count, samplerate, bit_depth):
    channels_label = createLegendPatch(f'{channel_count} channel{"s" if channel_count > 1 else ""}')
    samplerate_label = createLegendPatch(f"{samplerate/1000} kHz")
    bit_depth_label = createLegendPatch(f"{bit_depth}-bit")
    handles = [channels_label, samplerate_label, bit_depth_label]
    leg = plt.legend(handles=handles, handlelength=0, borderpad=0.8, bbox_to_anchor=(1.01, 1), loc='upper left', borderaxespad=0.)
    plt.gca().add_artist(leg)

def plotTimeLegend(duration, marker):
    timeLegend = []
    if(marker):
        markerTime = createMarker(duration)
        timeLegend.append(markerTime)
    audioTime = createLegendPatch(f"File length:\n{convertTimeToReadableString(duration)}")
    timeLegend.append(audioTime)
    plt.legend(handles=timeLegend, handlelength=0, borderpad=0.8, bbox_to_anchor=(1.01, 0), loc='lower left', borderaxespad=0.)

def plotMono(file_info, data, time, marker = False, line_wt = 0.5, y_label = ''):
    x = time
    if(file_info.duration > 60):
        x = x/60
    y = data

    figure = plt.figure()
    figure.set_figwidth(12)
    figure.set_figheight(6)

    plt.title(file_info.file_name)
    plt.grid(color='#ddd')
    plt.plot(x, y, linewidth=line_wt, color='#4986cc')

    plotFilePropLegend(1, file_info.samplerate, file_info.bit_depth)
    plotTimeLegend(file_info.duration, marker)
    
    plt.xlabel(("Time, min" if file_info.duration > 60 else "Time, s"))
    plt.ylabel(y_label)
    plt.tight_layout()

    plt.show()




# def plotStereo(file_info, data, time, marker = False, line_wt = 0.5, y_label = ''):
#     x = time

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

def splitDataIntoFrames(data, samplerate, timeFrame):
    frameSize = getFrameSize(timeFrame, samplerate) # values in one timeFrame
    frameOverlap = 0.5
    frameChangeRate = int(frameSize*frameOverlap)
    dataFrames = []

    for i in range(0, (len(data)//frameChangeRate-1)*frameChangeRate, frameChangeRate):
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

def calculateEnergy(data):
    energy = []
    for i in range(0, len(data)):
        frameEnergy = 0
        for j in range(0, len(data[i])):
            frameEnergy += data[i][j]**2
        energy.append(frameEnergy)
    return energy

def calculateZeroCrossingRate(data):
    ZCR = []
    for i in range(0, len(data)):
        frameNKS = 0
        for j in range(1, len(data[i])):
            frameNKS += abs(1 if data[i][j] >= 0 else -1 - 1 if data[i][j-1] > 0 else -1)
        frameNKS = frameNKS/(2*len(data[i]))
        ZCR.append(frameNKS)
    return ZCR

def handleMonoSignal(file, plotType):

    if(plotType == "timePlot"):
        plotMono(file, file.data, np.arange(0, file.duration, 1/file.samplerate), marker=True)
    else:
        timeFrame = int(input("Frame size in ms: "))
        normalized_data = normalizeData(file.data)
        normalized_data_frames = splitDataIntoFrames(normalized_data, file.samplerate, timeFrame)
        data_frames = splitDataIntoFrames(file.data, file.samplerate, timeFrame)
        time = np.arange(0, file.duration, file.duration/len(data_frames))

        if(plotType == "energyPlot"):
            energy = calculateEnergy(normalized_data_frames)
            plotMono(file, energy, time, line_wt=1, y_label='Energy')
        
        elif(plotType == "zeroCrossingRatePlot"):
            ZCR = calculateZeroCrossingRate(data_frames)
            plotMono(file, ZCR, time, line_wt=1, y_label='Zero-Crossing Rate')

def handleStereoSignal(file, plotType):
    file.transposeData()

def fileMenuDialog():
    file = readData()
    input_ok = False
    handleSignal = handleMonoSignal if file.channel_count == 1 else handleStereoSignal

    while(not input_ok):
        print(f"FILE '{file.file_name}' MENU\n", "[1] Energy plot\n", "[2] ZCR plot\n", "[3] Time plot\n", "[4] Menu")
        plotMenuInput = input("> ")
        if(plotMenuInput == "1"):
            handleSignal(file, "energyPlot")
            # calculateEnergy(file, splitDataIntoFrames(normalizeData(file.data), file.samplerate))
        elif(plotMenuInput == "2"):
            handleSignal(file, "zeroCrossingRatePlot")
            # calculateZeroCrossingRate(file, splitDataIntoFrames(file.data, file.samplerate))
        elif(plotMenuInput == "3"):
            handleSignal(file, "timePlot")
            # plotMono(file, file.data, np.arange(0, file.duration, 1/file.samplerate), marker=True)
        elif(plotMenuInput == "4"):
            menuDialog()
            input_ok = True

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

menuDialog()

# if(len(data.shape) < 2):
#     plotMono(data, np.arange(0, duration, 1/samplerate))
# else:
#     plotStereo()
