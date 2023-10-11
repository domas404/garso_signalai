import numpy as np
import os
import matplotlib
from matplotlib import pyplot as plt
from matplotlib import patches as mpatches
from tkinter import Tk
from tkinter.filedialog import askopenfilename
from scipy.io import wavfile
from datetime import timedelta

font = {'size': 13}
matplotlib.rc('font', **font)

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

root = Tk()
root.withdraw()

def readData():
    file_path = askopenfilename()
    samplerate, data = wavfile.read(file_path)
    file = FileData(file_path, samplerate, data)
    root.update()
    return file

def convertTimeToReadableString(timeInSeconds):
    timeString = str(timedelta(seconds=timeInSeconds))[2:]
    if (len(timeString) > 6):
        timeString = timeString[:9]
    else:
        timeString += ".000"
    return timeString

def markerInput(duration):
    print(f"Audio length: {convertTimeToReadableString(duration)}")
    print("Enter marker time.")
    mins = 0
    input_ok = False
    while(not input_ok):
        try:
            if(duration > 60):
                mins = float(input("Minutes:\n> "))
            secs = float(input("Seconds:\n> "))
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
    markerPosition = createLegendPatch(label=f"Marker at:\n{convertTimeToReadableString(markerTimestamp)}")
    if(playback_time > 60):
        markerTimestamp = markerTimestamp/60
    return markerPosition, markerTimestamp

def plotFilePropLegend(channel_count, samplerate, bit_depth):
    channels_label = createLegendPatch(f'{channel_count} channel{"s" if channel_count > 1 else ""}')
    samplerate_label = createLegendPatch(f"{samplerate/1000} kHz")
    bit_depth_label = createLegendPatch(f"{bit_depth}-bit")
    handles = [channels_label, samplerate_label, bit_depth_label]
    leg = plt.legend(handles=handles, handlelength=0, borderpad=0.8, bbox_to_anchor=(1.01, 1), loc='upper left', borderaxespad=0.)
    plt.gca().add_artist(leg)

def plotTimeLegend(duration, marker, markerTime=''):
    timeLegend = []
    if(marker):
        timeLegend.append(markerTime)
    audioTime = createLegendPatch(f"File length:\n{convertTimeToReadableString(duration)}")
    timeLegend.append(audioTime)
    plt.legend(handles=timeLegend, handlelength=0, borderpad=0.8, bbox_to_anchor=(1.01, 0), loc='lower left', borderaxespad=0.)

def plotMono(file, data, time, marker = False, segments = [], line_wt = 0.5, y_label = ''):
    x = time
    if(file.duration >= 60):
        x = x/60
    y = data

    figure = plt.figure()
    figure.set_figwidth(11)
    figure.set_figheight(4)

    plt.title(file.file_name)
    plt.grid(color='#ddd')
    plt.plot(x, y, linewidth=line_wt, color='#4986cc')
    # plt.locator_params(axis='y', nbins=1)

    plotFilePropLegend(1, file.samplerate, file.bit_depth)

    if(marker):
        markerTime, markerTimestamp = createMarker(file.duration)
        plt.axvline(x=markerTimestamp, color='#ff3838')
        plotTimeLegend(file.duration, marker, markerTime)
    else:
        plotTimeLegend(file.duration, marker)

    if(len(segments) > 0):
        for i in range(0, len(segments)):
            plt.axvline(x=time[segments[i]] if file.duration < 60 else time[segments[i]]/60, color='#ff3838', lw=line_wt)
    
    plt.xlabel(("Time, min" if file.duration > 60 else "Time, s"), fontsize=13)
    plt.ylabel(y_label, fontsize=13)
    plt.tight_layout()
    plt.show()

def plotStereo(file, data, time, marker = False, segments = [], line_wt = 0.5, y_label = ''):
    x = time
    if(file.duration >= 60):
        x = x/60
    y = data

    figure, axis = plt.subplots(nrows=file.channel_count, ncols=1, sharey=True)
    figure.set_figwidth(12)
    figure.set_figheight(8)
    figure.suptitle(os.path.basename(file.file_name))

    plt.subplot(file.channel_count, 1, 1)
    plotFilePropLegend(1, file.samplerate, file.bit_depth)

    plt.subplot(file.channel_count, 1, file.channel_count)
    if(marker):
        markerTime, markerTimestamp = createMarker(file.duration)
        plotTimeLegend(file.duration, marker, markerTime)
    else:
        plotTimeLegend(file.duration, marker)

    if(len(segments) > 0):
        for i in range(0, len(segments)):
            plt.subplot(file.channel_count, 1, i+1)
            for j in range(0, len(segments[i])):
                plt.axvline(x=time[segments[i][j]] if file.duration < 60 else time[segments[i][j]]/60, color='#ff3838', lw=line_wt)

    colors = ['#4986CC', '#3F4756', '#A3ACBD', '#C66481', '#8D3150']

    for i in range(0, file.channel_count):
        plt.subplot(file.channel_count, 1, i+1)
        plt.grid(color='#ddd')
        plt.plot(x, y[i], linewidth=line_wt, color=colors[i%len(colors)])
        if(marker):
            plt.axvline(x=markerTimestamp, color='#ff3838')

    figure.supxlabel(("Time, min" if file.duration > 60 else "Time, s"), fontsize=13)
    figure.supylabel(y_label, fontsize=13)
    plt.tight_layout()
    plt.show()

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
            frameNKS += abs(1 if data[i][j] >= 0 else -1 - 1 if data[i][j-1] >= 0 else -1)
        frameNKS = frameNKS/(2*len(data[i]))
        ZCR.append(frameNKS)
    return ZCR

def findSegments(data, step):
    segments = []
    multiplier = 1
    for i in range(0, len(data)):
        if(multiplier*data[i] >= multiplier*step):
            segments.append(i)
            multiplier *= (-1)
    return segments

def handleMonoSignal(file, plotType):

    if(plotType == "timePlot"):
        plotMono(file, file.data, np.arange(0, file.duration, 1/file.samplerate), marker=True)
    
    else:
        timeFrame = int(input("Enter frame size in ms.\n> "))
        normalized_data = normalizeData(file.data)
        normalized_data_frames = splitDataIntoFrames(normalized_data, file.samplerate, timeFrame)
        data_frames = splitDataIntoFrames(file.data, file.samplerate, timeFrame)
        time = np.arange(0, file.duration, file.duration/len(data_frames))

        if(plotType == "energyPlot"):
            energy = calculateEnergy(normalized_data_frames)
            plotMono(file, normalizeData(energy), time, line_wt=1, y_label='Energy')

        elif(plotType == "segmentPlot"):
            energy = calculateEnergy(normalized_data_frames)
            step = float(input("Enter step size.\n> "))
            segments = findSegments(normalizeData(energy), step)
            plotMono(file, normalizeData(energy), time, segments=segments, line_wt=1, y_label='Energy')
        
        elif(plotType == "zeroCrossingRatePlot"):
            ZCR = calculateZeroCrossingRate(data_frames)
            plotMono(file, normalizeData(ZCR), time, line_wt=1, y_label='Zero-Crossing Rate')

def handleStereoSignal(file, plotType):
    
    if(plotType == "timePlot"):
        plotStereo(file, file.data, np.arange(0, file.duration, 1/file.samplerate), marker=True, y_label='Values')
    
    else:
        timeFrame = int(input("Enter frame size in ms.\n> "))
        normalized_data_frames, data_frames = [], []

        for i in range(0, file.channel_count):
            normalized_data_frames.append(splitDataIntoFrames(normalizeData(file.data[i]), file.samplerate, timeFrame))
            data_frames.append(splitDataIntoFrames(file.data[i], file.samplerate, timeFrame))
        
        time = np.arange(0, file.duration, file.duration/len(data_frames[0]))

        if(plotType == "energyPlot"):
            energy = []
            for i in range(0, file.channel_count):
                energy.append(normalizeData(calculateEnergy(normalized_data_frames[i])))
            
            plotStereo(file, energy, time, line_wt=1, y_label='Energy')

        elif(plotType == "segmentPlot"):
            energy, segments = [], []
            for i in range(0, file.channel_count):
                energy.append(normalizeData(calculateEnergy(normalized_data_frames[i])))
            step = float(input("Enter step size.\n> "))
            for i in range(0, file.channel_count):
                segments.append(findSegments(energy[i], step))
            plotStereo(file, energy, time, segments=segments, line_wt=1, y_label='Energy')
        
        elif(plotType == "zeroCrossingRatePlot"):
            ZCR = []
            for i in range(0, file.channel_count):
                ZCR.append(calculateZeroCrossingRate(data_frames[i]))
            plotStereo(file, ZCR, time, line_wt=1, y_label='Zero-Crossing Rate')

def fileMenuDialog():
    file = readData()
    input_ok = False
    handleSignal = handleMonoSignal if file.channel_count == 1 else handleStereoSignal
    if(file.channel_count > 1):
        file.transposeData()

    while(not input_ok):
        print(f"FILE '{file.file_name}' MENU\n", "[1] Energy plot\n", "[2] ZCR plot\n", "[3] Time plot\n", "[4] Segment plot\n", "[5] Menu")
        plotMenuInput = input("> ")

        if(plotMenuInput == "1"):
            handleSignal(file, "energyPlot")

        elif(plotMenuInput == "2"):
            handleSignal(file, "zeroCrossingRatePlot")

        elif(plotMenuInput == "3"):
            handleSignal(file, "timePlot")

        elif(plotMenuInput == "4"):
            handleSignal(file, "segmentPlot")

        elif(plotMenuInput == "5"):
            del file
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
            print("Processing...")
            fileMenuDialog()

menuDialog()