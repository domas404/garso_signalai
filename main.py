import numpy as np
import os
import matplotlib
import math
import copy
from matplotlib import pyplot as plt
from matplotlib import patches as mpatches
from tkinter import Tk
from tkinter.filedialog import askopenfilename
from scipy.io import wavfile
from datetime import timedelta
import winsound

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

    def transpose_data(self):
        if(self.channel_count > 1):
            new_data = np.array(self.data)
            new_data = np.transpose(new_data)
            self.data = new_data.tolist()

    def apply_fade(self, data_with_fade):
        self.data_with_fade = np.array(data_with_fade, dtype=int)

    def clone(self):
        return copy.deepcopy(self)

root = Tk()
root.withdraw()

def read_data():
    file_path = askopenfilename()
    samplerate, data = wavfile.read(file_path)
    file = FileData(file_path, samplerate, data)
    # winsound.PlaySound(file_path, winsound.SND_FILENAME)
    # my_sound.play()
    root.update()
    return file

def convert_time_to_readable_string(timeInSeconds):
    timeString = str(timedelta(seconds=timeInSeconds))[2:]
    if (len(timeString) > 6):
        timeString = timeString[:9]
    else:
        timeString += ".000"
    return timeString

def marker_input(duration):
    print(f"Audio length: {convert_time_to_readable_string(duration)}")
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

def create_legend_patch(label):
    return mpatches.Patch(color='none', label=label)

def create_marker(playback_time):
    marker_timestamp = marker_input(playback_time)
    markerPosition = create_legend_patch(label=f"Marker at:\n{convert_time_to_readable_string(marker_timestamp)}")
    if(playback_time > 60):
        marker_timestamp = marker_timestamp/60
    return markerPosition, marker_timestamp

def plot_file_property_legend(channel_count, samplerate, bit_depth):
    channels_label = create_legend_patch(f'{channel_count} channel{"s" if channel_count > 1 else ""}')
    samplerate_label = create_legend_patch(f"{samplerate/1000} kHz")
    bit_depth_label = create_legend_patch(f"{bit_depth}-bit")
    handles = [channels_label, samplerate_label, bit_depth_label]
    leg = plt.legend(handles=handles, handlelength=0, borderpad=0.8, bbox_to_anchor=(1.01, 1), loc='upper left', borderaxespad=0.)
    plt.gca().add_artist(leg)

def plot_time_legend(duration, marker, marker_time='', time_frame=0):
    time_legend = []
    if(time_frame > 0):
        time_frame_legend = create_legend_patch(f"Frame:\n{time_frame} ms")
        time_legend.append(time_frame_legend)
    if(marker):
        time_legend.append(marker_time)
    audio_time = create_legend_patch(f"File length:\n{convert_time_to_readable_string(duration)}")
    time_legend.append(audio_time)
    plt.legend(handles=time_legend, handlelength=0, borderpad=0.8, bbox_to_anchor=(1.01, 0), loc='lower left', borderaxespad=0.)

def plot_mono(file, data, time, marker=False, segments=[], line_wt=0.5, y_label='', time_frame=0):
    x = time
    if(file.duration >= 60):
        x = x/60
    y = data

    figure = plt.figure()
    figure.set_figwidth(11)
    figure.set_figheight(5)

    plt.title(file.file_name)
    plt.grid(color='#ddd')
    plt.plot(x, y, linewidth=line_wt, color='#4986cc')

    plot_file_property_legend(file.channel_count, file.samplerate, file.bit_depth)

    if(marker):
        marker_time, marker_timestamp = create_marker(file.duration)
        plt.axvline(x=marker_timestamp, color='#ff3838')
        plot_time_legend(file.duration, marker, marker_time)
    elif(time_frame > 0):
        plot_time_legend(file.duration, marker, time_frame=time_frame)
    else:
        plot_time_legend(file.duration, marker)

    if(len(segments) > 0):
        for i in range(0, len(segments)):
            plt.axvline(x=time[segments[i]] if file.duration < 60 else time[segments[i]]/60, color='#ff3838', lw=line_wt)
    
    plt.xlabel(("Time, min" if file.duration > 60 else "Time, s"), fontsize=13)
    plt.ylabel(y_label, fontsize=13)
    plt.tight_layout()
    plt.show()

def plot_stereo(file, data, time, marker = False, segments = [], line_wt = 0.5, y_label = '', time_frame=0):
    x = time
    if(file.duration >= 60):
        x = x/60
    y = data

    figure, axis = plt.subplots(nrows=file.channel_count, ncols=1, sharey=True)
    figure.set_figwidth(12)
    figure.set_figheight(8)
    figure.suptitle(os.path.basename(file.file_name))

    plt.subplot(file.channel_count, 1, 1)
    plot_file_property_legend(file.channel_count, file.samplerate, file.bit_depth)

    plt.subplot(file.channel_count, 1, file.channel_count)
    if(marker):
        marker_time, marker_timestamp = create_marker(file.duration)
        plot_time_legend(file.duration, marker, marker_time)
    elif(time_frame > 0):
        plot_time_legend(file.duration, marker, time_frame=time_frame)
    else:
        plot_time_legend(file.duration, marker)

    colors = ['#4986CC', '#3F4756', '#A3ACBD', '#C66481', '#8D3150']

    for i in range(0, file.channel_count):
        plt.subplot(file.channel_count, 1, i+1)
        plt.grid(color='#ddd')
        plt.plot(x, y[i], linewidth=line_wt, color=colors[i%len(colors)])
        if(marker):
            plt.axvline(x=marker_timestamp, color='#ff3838')

    if(len(segments) > 0):
        for i in range(0, len(segments)):
            plt.subplot(file.channel_count, 1, i+1)
            for j in range(0, len(segments[i])):
                plt.axvline(x=time[segments[i][j]] if file.duration < 60 else time[segments[i][j]]/60, color='#ff3838', lw=line_wt)
    
    figure.supxlabel(("Time, min" if file.duration > 60 else "Time, s"), fontsize=13)
    figure.supylabel(y_label, fontsize=13)
    plt.tight_layout()
    plt.show()

def get_frame_size(time_frame, samplerate):
    return int(samplerate/1000*time_frame)

def normalize_data(data):
    min_val = min(data)
    max_val = max(data)
    new_data = []
    for i in range(0, len(data)):
        new_data.append((data[i] - min_val) / (max_val - min_val))
    return new_data

def split_data_into_frames(data, samplerate, time_frame):
    frame_size = get_frame_size(time_frame, samplerate)
    frame_overlap = 0.5
    frame_change_rate = int(frame_size*frame_overlap)
    data_frames = []

    for i in range(0, (len(data)//frame_change_rate-1)*frame_change_rate, frame_change_rate):
        single_frame = []
        for j in range(i, i+frame_size):
            single_frame.append(data[j])
        data_frames.append(single_frame)

    single_frame = []
    for i in range(len(data)-frame_size, len(data)):
        single_frame.append(data[i])
    data_frames.append(single_frame)

    return data_frames

def calculate_energy(data):
    energy = []
    for i in range(0, len(data)):
        frame_energy = 0
        for j in range(0, len(data[i])):
            frame_energy += data[i][j]**2
        energy.append(frame_energy)
    return energy

def calculate_zero_crossing_rate(data):
    ZCR = []
    for i in range(0, len(data)):
        frame_ZCR = 0
        for j in range(1, len(data[i])):
            frame_ZCR += abs(1 if data[i][j] >= 0 else -1 - 1 if data[i][j-1] >= 0 else -1)
        frame_ZCR = frame_ZCR/(2*len(data[i]))
        ZCR.append(frame_ZCR)
    return ZCR

def find_segments(data, step):
    segments = []
    multiplier = 1
    for i in range(0, len(data)):
        if(multiplier*data[i] >= multiplier*step):
            segments.append(i)
            multiplier *= (-1)
    return segments

def handle_mono_signal(file, plot_type):

    if(plot_type == "timePlot"):
        plot_mono(file, file.data, np.arange(0, file.duration, 1/file.samplerate), marker=False)
    
    else:
        time_frame = int(input("Enter frame size in ms.\n> "))
        normalized_data = normalize_data(file.data)
        normalized_data_frames = split_data_into_frames(normalized_data, file.samplerate, time_frame)
        data_frames = split_data_into_frames(file.data, file.samplerate, time_frame)
        time = np.arange(0, file.duration*100, file.duration*100/len(data_frames))
        time = time*0.01

        if(plot_type == "energyPlot"):
            energy = calculate_energy(normalized_data_frames)
            plot_mono(file, normalize_data(energy), time, line_wt=1, y_label='Energy', time_frame=time_frame)

        elif(plot_type == "segmentPlot"):
            energy = calculate_energy(normalized_data_frames)
            step = float(input("Enter step size.\n> "))
            segments = find_segments(normalize_data(energy), step)
            plot_mono(file, normalize_data(energy), time, segments=segments, line_wt=1, y_label='Energy', time_frame=time_frame)
        
        elif(plot_type == "zeroCrossingRatePlot"):
            ZCR = calculate_zero_crossing_rate(data_frames)
            plot_mono(file, normalize_data(ZCR), time, line_wt=1, y_label='Zero-Crossing Rate', time_frame=time_frame)

def handle_stereo_signal(file, plot_type):
    
    if(plot_type == "timePlot"):
        plot_stereo(file, file.data, np.arange(0, file.duration, 1/file.samplerate), marker=False, y_label='Values')
    
    else:
        time_frame = int(input("Enter frame size in ms.\n> "))
        normalized_data_frames, data_frames = [], []

        for i in range(0, file.channel_count):
            normalized_data_frames.append(split_data_into_frames(normalize_data(file.data[i]), file.samplerate, time_frame))
            data_frames.append(split_data_into_frames(file.data[i], file.samplerate, time_frame))
        
        time = np.arange(0, file.duration*100, file.duration*100/len(data_frames[0]))
        time = time*0.01

        if(plot_type == "energyPlot"):
            energy = []
            for i in range(0, file.channel_count):
                energy.append(normalize_data(calculate_energy(normalized_data_frames[i])))
            
            plot_stereo(file, energy, time, line_wt=1, y_label='Energy', time_frame=time_frame)

        elif(plot_type == "segmentPlot"):
            energy, segments = [], []
            for i in range(0, file.channel_count):
                energy.append(normalize_data(calculate_energy(normalized_data_frames[i])))
            step = float(input("Enter step size.\n> "))
            for i in range(0, file.channel_count):
                segments.append(find_segments(energy[i], step))
            plot_stereo(file, energy, time, segments=segments, line_wt=1, y_label='Energy', time_frame=time_frame)
        
        elif(plot_type == "zeroCrossingRatePlot"):
            ZCR = []
            for i in range(0, file.channel_count):
                ZCR.append(calculate_zero_crossing_rate(data_frames[i]))
            plot_stereo(file, ZCR, time, line_wt=1, y_label='Zero-Crossing Rate', time_frame=time_frame)

def linear_fade(data, fade_value_count):
    
    fade_in_data, fade_out_data = [], []
    fade_factor = 1/fade_value_count

    for i in range(0, fade_value_count):
        fading_factor = fade_factor * (i+1)
        fade_in_data.append(round(data[i] * fading_factor))
    
    for i in range(len(data)-fade_value_count, len(data)):
        fading_factor = 1 - fade_factor * (i - (len(data) - fade_value_count) + 1)
        fade_out_data.append(round(data[i] * fading_factor))

    return(fade_in_data, fade_out_data)

def log_fade(data, fade_value_count):

    fade_in_data, fade_out_data = [], []
    fade_factor = (math.e**2)/fade_value_count

    for i in range(0, fade_value_count):
        fading_factor = 1 - math.exp(-fade_factor*(i + 1))
        fade_in_data.append(round(data[i] * fading_factor))
    
    for i in range(len(data)-fade_value_count, len(data)):
        fading_factor = 1 - math.exp(-fade_factor * (fade_value_count - (i - (len(data) - fade_value_count) + 1)))
        fade_out_data.append(round(data[i] * fading_factor))

    return(fade_in_data, fade_out_data)

def handle_fade(file):

    print(f"Audio length: {convert_time_to_readable_string(file.duration)}")
    fade_time = int(input("Enter fade time in ms:\n> "))
    fade_type = input("Choose fade type:\n[1] Linear\n[2] Logarithmic\n> ")
    fade_value_count = round(file.samplerate*(fade_time/1000))

    handle_mono_signal(file, "timePlot")

    fade = linear_fade if fade_type == "1" else log_fade
    fade_in_data, fade_out_data = fade(file.data, fade_value_count)

    new_file_data = fade_in_data + list(file.data[fade_value_count:len(file.data)-fade_value_count]) + fade_out_data
    new_file = file.clone()
    new_file.data = new_file_data

    handle_mono_signal(new_file, "timePlot")
    wavfile.write(f'{file.file_name}', file.samplerate, np.int16(new_file_data))
    del new_file

def file_menu_dialog():
    file = read_data()
    input_ok = False
    handle_signal = handle_mono_signal if file.channel_count == 1 else handle_stereo_signal
    if(file.channel_count > 1):
        file.transpose_data()

    while(not input_ok):
        print(f"FILE '{file.file_name}' MENU\n",
              "[1] Energy plot\n",
              "[2] ZCR plot\n",
              "[3] Time plot\n",
              "[4] Segment plot\n",
              "[5] Fade in/fade out\n",
              "[6] Menu")
        plot_menu_input = input("> ")

        if(plot_menu_input == "1"):
            handle_signal(file, "energyPlot")

        elif(plot_menu_input == "2"):
            handle_signal(file, "zeroCrossingRatePlot")

        elif(plot_menu_input == "3"):
            handle_signal(file, "timePlot")

        elif(plot_menu_input == "4"):
            handle_signal(file, "segmentPlot")

        elif(plot_menu_input == "5"):
            handle_fade(file)

        elif(plot_menu_input == "6"):
            del file
            menu_dialog()
            input_ok = True

def menu_dialog():
    input_ok = False
    print("MENU\n", "[1] Open file\n", "[2] Quit")

    while(not input_ok):
        menu_input = input("> ")

        if(menu_input == '2'):
            print("Exiting...")
            exit()

        elif(menu_input == '1'):
            input_ok = True
            print("Processing...")
            file_menu_dialog()

menu_dialog()