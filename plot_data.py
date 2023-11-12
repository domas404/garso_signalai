import os
from datetime import timedelta
import matplotlib
from matplotlib import pyplot as plt
from matplotlib import patches as mpatches
import numpy as np

font = {'size': 13}
matplotlib.rc('font', **font)

def get_time(file, frame_length):
    time = np.arange(0, file.duration*100, file.duration*100/frame_length)
    time = time*0.01
    return time

def convert_time_to_readable_string(time_in_seconds):
    time_string = str(timedelta(seconds=time_in_seconds))[2:]
    if len(time_string) > 6:
        time_string = time_string[:9]
    else:
        time_string += ".000"
    return time_string

def timestamp_input(duration, stamp):
    print(f"Audio length: {convert_time_to_readable_string(duration)}")
    print(f"Enter {stamp} time.")
    mins = 0
    input_ok = False
    while not input_ok:
        try:
            if duration > 60:
                mins = float(input("Minutes:\n> "))
            secs = float(input("Seconds:\n> "))
            if secs >= 60 or secs < 0:
                raise ValueError("Incorrect time value")
            if mins*60+secs > duration:
                raise ValueError("Time value out of bounds")
            input_ok = True
        except ValueError as ve:
            print(f"Error: {ve}. Try again.")
    return (mins*60) + secs

def create_legend_patch(label):
    return mpatches.Patch(color='none', label=label)

def create_marker(playback_time):
    marker_timestamp = timestamp_input(playback_time, "marker")
    marker_position = create_legend_patch(
        label=f"Marker at:\n{convert_time_to_readable_string(marker_timestamp)}")
    if playback_time > 60:
        marker_timestamp = marker_timestamp/60
    return marker_position, marker_timestamp

def plot_file_property_legend(channel_count, samplerate, bit_depth):
    channels_label = create_legend_patch(
        f'{channel_count} channel{"s" if channel_count > 1 else ""}')
    samplerate_label = create_legend_patch(f"{samplerate/1000} kHz")
    bit_depth_label = create_legend_patch(f"{bit_depth}-bit")
    handles = [channels_label, samplerate_label, bit_depth_label]
    leg = plt.legend(
        handles=handles,
        handlelength=0,
        borderpad=0.8,
        bbox_to_anchor=(1.01, 1),
        loc='upper left',
        borderaxespad=0.
    )
    plt.gca().add_artist(leg)

def plot_time_legend(duration, marker, marker_time='', frame_size_in_ms=0):
    time_legend = []
    if frame_size_in_ms > 0:
        frame_size_legend = create_legend_patch(f"Frame:\n{frame_size_in_ms} ms")
        time_legend.append(frame_size_legend)
    if marker:
        time_legend.append(marker_time)
    audio_time = create_legend_patch(
        f"File length:\n{convert_time_to_readable_string(duration)}")
    time_legend.append(audio_time)
    plt.legend(
        handles=time_legend,
        handlelength=0,
        borderpad=0.8,
        bbox_to_anchor=(1.01, 0),
        loc='lower left',
        borderaxespad=0.)

def plot_mono(file, data, marker=False, segments=None, line_wt=0.5, y_label=''):
    x = get_time(file, len(data))
    if file.duration >= 60:
        x = x/60
    y = data

    figure = plt.figure()
    figure.set_figwidth(11)
    figure.set_figheight(5)

    plt.title(file.file_name)
    plt.grid(color='#ddd')
    plt.plot(x, y, linewidth=line_wt, color='#4986cc')

    plot_file_property_legend(file.channel_count, file.samplerate, file.bit_depth)

    if marker:
        marker_time, marker_timestamp = create_marker(file.duration)
        plt.axvline(x=marker_timestamp, color='#ff3838')
        plot_time_legend(file.duration, marker, marker_time)
    elif file.frame_size_in_ms > 0:
        plot_time_legend(file.duration, marker, frame_size_in_ms=file.frame_size_in_ms)
    else:
        plot_time_legend(file.duration, marker)

    if segments is not None:
        for segment in segments:
            plt.axvline(
                x=x[segment] if file.duration < 60 else x[segment]/60,
                color='#ff3838',
                lw=line_wt
            )
    plt.xlabel(("Time, min" if file.duration > 60 else "Time, s"), fontsize=13)
    plt.ylabel(y_label, fontsize=13)
    plt.tight_layout()
    plt.show()

def plot_stereo(file, data, marker = False, segments = None, line_wt = 0.5, y_label = ''):
    x = get_time(file, len(data[0]))
    if file.duration >= 60:
        x = x/60
    y = data

    figure, _ = plt.subplots(nrows=file.channel_count, ncols=1, sharey=True)
    figure.set_figwidth(12)
    figure.set_figheight(8)
    figure.suptitle(os.path.basename(file.file_name))

    plt.subplot(file.channel_count, 1, 1)
    plot_file_property_legend(file.channel_count, file.samplerate, file.bit_depth)

    plt.subplot(file.channel_count, 1, file.channel_count)
    if marker:
        marker_time, marker_timestamp = create_marker(file.duration)
        plot_time_legend(file.duration, marker, marker_time)
    elif file.frame_size_in_ms > 0:
        plot_time_legend(file.duration, marker, frame_size_in_ms=file.frame_size_in_ms)
    else:
        plot_time_legend(file.duration, marker)

    colors = ['#4986CC', '#3F4756', '#A3ACBD', '#C66481', '#8D3150']

    for i in range(0, file.channel_count):
        plt.subplot(file.channel_count, 1, i+1)
        plt.grid(color='#ddd')
        plt.plot(x, y[i], linewidth=line_wt, color=colors[i%len(colors)])
        if marker:
            plt.axvline(x=marker_timestamp, color='#ff3838')

    if segments is not None:
        for i, channel in enumerate(segments):
            plt.subplot(file.channel_count, 1, i+1)
            for segment in channel:
                plt.axvline(
                    x=x[segment] if file.duration < 60 else x[segment]/60,
                    color='#ff3838',
                    lw=line_wt
                )
    figure.supxlabel(("Time, min" if file.duration > 60 else "Time, s"), fontsize=13)
    figure.supylabel(y_label, fontsize=13)
    plt.tight_layout()
    plt.show()
