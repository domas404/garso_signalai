import numpy as np
from scipy.io import wavfile
from plot_data import plot_tools, new_plot

def choose_interval(duration):
    start_time = plot_tools.get_time_input(duration, "start")
    end_time = plot_tools.get_time_input(duration, "end")
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
    file_interval.set_frame_size(round((end-start)*1000))
    return file_interval

def apply_window_function(interval):
    window = np.hamming(len(interval))
    interval = interval * window
    return interval

def apply_dft(interval):
    complex_dft = np.fft.fft(interval)
    return complex_dft

def scale_dft(dft, n):
    if n % 2 == 0:
        length = len(dft)-1
    else:
        length = len(dft)
    for i in range(1, length):
        dft[i] = 2*dft[i]
    return dft

def get_simplified_dft(complex_dft):
    simplified_dft = np.abs(complex_dft)
    n = len(simplified_dft)
    if n % 2 == 0:
        simplified_dft = simplified_dft[0:int((len(simplified_dft)/2)+1)]
    else:
        simplified_dft = simplified_dft[0:int((len(simplified_dft)+1)/2)]
    simplified_dft = scale_dft(simplified_dft, n)
    return simplified_dft

def get_frequencies(interval, samplerate):
    step = 1/len(interval)
    frequencies = []
    for i in range(0, len(interval)):
        frequencies.append((samplerate/2)*step*(i+1))
    return frequencies

def inverse_dft(interval):
    modified_signal = np.fft.ifft(interval).real
    return modified_signal

def inverse_window_function(interval):
    window = 1 / np.hamming(len(interval))
    interval = interval * window
    return interval

def modify_spectrum(signal, complex_dft, modify):
    complex_dft = modify(complex_dft, signal.samplerate)
    return complex_dft

def export_signal(signal):
    wavfile.write(f'spectrum_modified/{signal.file_name}', signal.samplerate, np.int16(signal.data))

def show_spectrum(signal, complex_dft):
    simplified_dft = get_simplified_dft(complex_dft)
    frequencies = get_frequencies(simplified_dft, signal.samplerate)
    new_plot.plot_spectrum(signal, frequencies, simplified_dft)

def choose_modification():
    option = input("Choose how to modify:\n [1] remove frequencies\n [2] add frequencies\n [3] move frequencies right\n> ")
    options = {
        1: remove_frequencies,
        2: add_frequencies,
        3: move_frequencies
    }
    return options[int(option)]

def add_frequencies(interval, samplerate):
    frequencies = np.fft.fftfreq(len(interval), 1/samplerate)
    freq_to_add = 4000
    amplitude = 1e7/2
    index = np.argmax(frequencies >= freq_to_add)
    modified_fft = interval
    modified_fft[index] += amplitude
    return modified_fft

def remove_frequencies(interval, samplerate):
    frequencies = np.fft.fftfreq(len(interval), 1/samplerate)
    mask = (frequencies < -2000) | (frequencies > 2000)
    modified_fft = interval
    modified_fft[mask] *= 0
    return modified_fft

def move_frequencies(interval, samplerate):
    '''not implemented yet'''
    frequencies = np.fft.fftfreq(len(interval), 1/samplerate)
    mask = (frequencies < -1000) | (frequencies > 1000)
    modified_fft = interval
    modified_fft[mask] *= 0
    return modified_fft

def analyze_spectrum(full_signal):

    start, end = choose_interval(full_signal.duration)
    original_interval = get_file_interval(full_signal, start, end)
    new_plot.plot_time(original_interval, original_interval.data, start_time=start, duration=full_signal.duration)

    signal_copy = full_signal.clone()
    signal_copy.set_data(apply_window_function(signal_copy.data))

    complex_dft = apply_dft(signal_copy.data)
    show_spectrum(signal_copy, complex_dft)

    mod_option = choose_modification()
    complex_dft = modify_spectrum(signal_copy, complex_dft, mod_option)
    show_spectrum(signal_copy, complex_dft)

    signal_copy.set_data(inverse_window_function(inverse_dft(complex_dft)))

    modified_interval = get_file_interval(signal_copy, start, end)
    new_plot.plot_time(modified_interval, modified_interval.data, start_time=start, duration=full_signal.duration)

    export_signal(signal_copy)
