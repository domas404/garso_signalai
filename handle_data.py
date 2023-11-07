import numpy as np
from scipy.io import wavfile
from plot_data import plot_mono, plot_stereo
from audio_effects import get_fade_data
from audio_analysis import get_energy, get_zcr, get_normalized_data_frames, get_data_frames, find_segments, normalize_data

def plot_energy(file, normalized_data_frames, plot):
    """Plot energy graph."""
    energy = get_energy(normalized_data_frames)
    if file.channel_count == 1:
        energy = energy[0]
    plot(
        file,
        energy,
        line_wt=1,
        y_label='Energy')

def plot_segments(file, normalized_data_frames, plot):
    """Plot energy graph and divide graph into segments by step value."""
    energy = get_energy(normalized_data_frames)
    segments = []
    step = float(input("Enter step size.\n> "))
    for channel in energy:
        segments.append(find_segments(channel, step))
    if file.channel_count == 1:
        energy = energy[0]
        segments = segments[0]
    plot(
        file,
        energy,
        segments=segments,
        line_wt=1,
        y_label='Energy')

def plot_zcr(file, data_frames, plot):
    """Plot Zero-Crossing rate graph."""
    zcr = get_zcr(data_frames)
    print("zcr:", zcr)
    normalized_zcr = []
    for channel in zcr:
        normalized_zcr.append(normalize_data(channel))
    print("normalized_zcr:", normalized_zcr)
    if file.channel_count == 1:
        normalized_zcr = normalized_zcr[0]
    plot(
        file,
        normalized_zcr,
        line_wt=1,
        y_label='Zero-Crossing Rate')

def plot_graph(file, get_frames, plot_type, plot):
    file.set_time_frame()
    if file.channel_count == 1:
        data_frames = get_frames([file.data], file.samplerate, file.time_frame)
    else:
        data_frames = get_frames(file.data, file.samplerate, file.time_frame)
    plot_type(file, data_frames, plot)

def handle_signal(file, plot_type, plot):

    if plot_type == "timePlot":
        plot_mono(file, file.data, marker=False)
    
    elif plot_type == "zeroCrossingRatePlot":
        plot_graph(file, get_data_frames, plot_zcr, plot)

    elif plot_type == "energyPlot":
        plot_graph(file, get_normalized_data_frames, plot_energy, plot)

    elif plot_type == "segmentPlot":
        plot_graph(file, get_normalized_data_frames, plot_segments, plot)

def handle_fade(file):

    fade_value_count, fade = get_fade_data(file)
    new_file = file.clone()

    if file.channel_count == 1:
        handle_signal(file, "timePlot", plot_mono)
        fade_in_data, fade_out_data = fade(file.data, fade_value_count)
        new_file_data = (fade_in_data
                        + list(file.data[fade_value_count:len(file.data)-fade_value_count])
                        + fade_out_data)
        new_file.data = new_file_data
        handle_signal(new_file, "timePlot", plot_mono)
    else:
        handle_signal(file, "timePlot", plot_stereo)
        for i in range(0, file.channel_count):
            fade_in_data, fade_out_data = fade(file.data[i], fade_value_count)
            new_file_data = (fade_in_data
                            + list(file.data[i][fade_value_count:len(file.data[i])-fade_value_count])
                            + fade_out_data)
            new_file.data[i] = new_file_data
        handle_signal(new_file, "timePlot", plot_stereo)

    wavfile.write(f'fade_applied/{file.file_name}', file.samplerate, np.int16(new_file_data))
    del new_file
