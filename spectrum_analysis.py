import numpy as np
from plot_data import plot_tools
from handle_data import handle_signal
from plot_data import new_plot
from matplotlib import pyplot as plt

def choose_interval(duration):
    start_time = plot_tools.timestamp_input(duration, "start")
    end_time = plot_tools.timestamp_input(duration, "end")
    if start_time > 60:
        start_time = start_time/60
        end_time = end_time/60
    return start_time, end_time

def get_file_interval(file, start, end):

    start_index = int(start*file.samplerate)
    end_index = int(end*file.samplerate)

    file_interval = file.clone()
    new_data = file.data[start_index:end_index]
    file_interval.set_data(new_data)

    return file_interval

def apply_window_function(interval):
    interval = interval * np.hanning(len(interval))
    return interval

def apply_dft(interval):
    interval = np.fft.fft(interval)
    interval = np.abs(interval)
    N = len(interval)
    if N % 2 == 0:
        interval = interval[0:int((len(interval)/2)+1)]
    else:
        interval = interval[0:int((len(interval)+1)/2)]
    return interval, N

def scale_interval(interval, N):
    if N % 2 == 0:
        length = len(interval)-1
    else:
        length = len(interval)
    for i in range(1, length):
        interval[i] = 2*interval[i]
    return interval

def get_frequencies(interval, samplerate):
    step = 1/len(interval)
    frequencies = []
    for i in range(0, len(interval)):
        frequencies.append((samplerate/2)*step*(i+1))
    return frequencies

def analyze_spectrum(original_file):
    start, end = choose_interval(original_file.duration)
    file = get_file_interval(original_file, start, end)
    plot = new_plot.plot_mono_signal
    # handle_signal(file, "timePlot", plot)
    file.set_data(apply_window_function(file.data))
    # handle_signal(file, "timePlot", plot)
    interval, N = apply_dft(file.data)
    interval = scale_interval(interval, N)
    frequencies = get_frequencies(interval, file.samplerate)
    # print(interval, frequencies)
    plt.plot(frequencies, interval)
    plt.show()
    # print(interval)
