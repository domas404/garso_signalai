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

file_path = filedialog.askopenfilename()

samplerate, data = wavfile.read(file_path)
bit_depth = data.dtype.itemsize * 8
data = np.array(data, dtype=int)

duration = len(data)/samplerate
time = np.arange(0, duration, 1/samplerate)

playback_time = time[len(time)-1]

total_length_to_display = str(timedelta(seconds=playback_time))[2:]
if(len(total_length_to_display) > 6):
    total_length_to_display = total_length_to_display[:9]

def addMarker():
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

def plotLegend(channel_count):
    channels_label = mpatches.Patch(color='none', linestyle=':', label=f'{channel_count} channel{"s" if channel_count > 1 else ""}')
    samplerate_label = mpatches.Patch(color='none', linestyle=':', label=f"{samplerate/1000} kHz")
    bit_depth_label = mpatches.Patch(color='none', label=f"{bit_depth}-bit")
    return [channels_label, samplerate_label, bit_depth_label]

def plotMono():
    x = np.array(time)
    y = data

    figure = plt.figure()
    figure.set_figwidth(13)
    figure.set_figheight(8)

    mins, secs = addMarker()
    markerTimestamp = (mins*60)+secs
    time_label = "Time, s"
    
    if(playback_time > 60):
        x = x/60
        markerTimestamp = markerTimestamp/60
        time_label = "Time, min"

    marker_time_to_display = str(timedelta(minutes=mins, seconds=secs))[2:]
    if(len(marker_time_to_display) > 6):
        marker_time_to_display = marker_time_to_display[:9]
    else:
        marker_time_to_display += ".000"

    markerPosition = mpatches.Patch(color='none', linestyle=':', label=f"Marker at:\n{marker_time_to_display}")
    audiotime = mpatches.Patch(color='none', linestyle=':', label=f"File length:\n{total_length_to_display}")
    
    plt.title(os.path.basename(file_path))
    plt.grid(color='#ddd')
    plt.plot(x, y, linewidth=0.5, color='#4986cc')
    plt.axvline(x=markerTimestamp, color='#ff3838')
    leg = plt.legend(handles=plotLegend(1), handlelength=0, borderpad=0.8, bbox_to_anchor=(1.01, 1), loc='upper left', borderaxespad=0.)
    plt.gca().add_artist(leg)
    plt.legend(handles=[markerPosition, audiotime], handlelength=0, borderpad=0.8, bbox_to_anchor=(1.01, 0), loc='lower left', borderaxespad=0.)
    plt.xlabel(time_label)
    plt.tight_layout()

def plotStereo():
    x = np.array(time)

    channelCount = data.shape[1]
    figure, axis = plt.subplots(channelCount, 1)
    figure.set_figwidth(13)
    figure.set_figheight(8)

    stereo_array = [ []*1 for i in range(channelCount) ]

    for i in range(0, channelCount):
        for j in range(0, len(data)):
            stereo_array[i].append(data[j][i])

    figure.suptitle(os.path.basename(file_path))

    mins, secs = addMarker()
    markerTimestamp = (mins*60)+secs
    time_label = "Time, s"

    if(playback_time > 60):
        x = x/60
        markerTimestamp = markerTimestamp/60
        time_label = "Time, min"

    colors = ['#4986cc', '#75aceb']
    
    for i in range(0, channelCount):
        axis[i].grid(color='#ddd')
        axis[i].plot(x, stereo_array[i], color=colors[i%2], linewidth=0.5)
        axis[i].axvline(x=markerTimestamp, color='#ff3838')

    marker_time_to_display = str(timedelta(minutes=mins, seconds=secs))[2:]
    if(len(marker_time_to_display) > 6):
        marker_time_to_display = marker_time_to_display[:9]
    else:
        marker_time_to_display += ".000"

    markerPosition = mpatches.Patch(color='none', linestyle=':', label=f"Marker at:\n{marker_time_to_display}")
    audiotime = mpatches.Patch(color='none', linestyle=':', label=f"File length:\n{total_length_to_display}")
    
    leg = axis[0].legend(handles=plotLegend(channelCount), handlelength=0, borderpad=0.8, bbox_to_anchor=(1.01, 1), loc='upper left', borderaxespad=0.)
    axis[0].add_artist(leg)
    plt.legend(handles=[markerPosition, audiotime], handlelength=0, borderpad=0.8, bbox_to_anchor=(1.01, 0), loc='lower left', borderaxespad=0.)
    axis[channelCount-1].set_xlabel(time_label)

    figure.tight_layout()

if(len(data.shape) < 2):
    plotMono()
else:
    plotStereo()

plt.show()