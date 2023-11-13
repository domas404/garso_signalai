import os
from datetime import timedelta
import matplotlib
from matplotlib import pyplot as plt
from matplotlib import patches as mpatches
import numpy as np

font = {'size': 13}
matplotlib.rc('font', **font)

class PlotTools:

    def get_time(self, file, frame_length):
        time = np.arange(0, file.duration*100, file.duration*100/frame_length)
        time = time*0.01
        return time

    def convert_time_to_readable_string(self, time_in_seconds):
        time_string = str(timedelta(seconds=time_in_seconds))[2:]
        if len(time_string) > 6:
            time_string = time_string[:9]
        else:
            time_string += ".000"
        return time_string

    def timestamp_input(self, duration, stamp):
        print(f"Audio length: {self.convert_time_to_readable_string(duration)}")
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

    def create_legend_patch(self, label):
        return mpatches.Patch(color='none', label=label)

    def create_marker(self, playback_time):
        marker_timestamp = self.timestamp_input(playback_time, "marker")
        marker_position = self.create_legend_patch(
            label=f"Marker at:\n{self.convert_time_to_readable_string(marker_timestamp)}")
        if playback_time > 60:
            marker_timestamp = marker_timestamp/60
        return marker_position, marker_timestamp

    def plot_file_property_legend(self, channel_count, samplerate, bit_depth):
        channels_label = self.create_legend_patch(
            f'{channel_count} channel{"s" if channel_count > 1 else ""}')
        samplerate_label = self.create_legend_patch(f"{samplerate/1000} kHz")
        bit_depth_label = self.create_legend_patch(f"{bit_depth}-bit")
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

    def plot_time_legend(self, duration, marker, marker_time='', frame_size_in_ms=0):
        time_legend = []
        if frame_size_in_ms > 0:
            frame_size_legend = self.create_legend_patch(f"Frame:\n{frame_size_in_ms} ms")
            time_legend.append(frame_size_legend)
        if marker:
            time_legend.append(marker_time)
        audio_time = self.create_legend_patch(
            f"File length:\n{self.convert_time_to_readable_string(duration)}")
        time_legend.append(audio_time)
        plt.legend(
            handles=time_legend,
            handlelength=0,
            borderpad=0.8,
            bbox_to_anchor=(1.01, 0),
            loc='lower left',
            borderaxespad=0.)
    
    def create_single_plot(self):
        figure = plt.figure()
        figure.set_figwidth(11)
        figure.set_figheight(5)
        return figure
    
    def create_subplots(self, file):
        figure, _ = plt.subplots(nrows=file.channel_count, ncols=1, sharey=True)
        figure.set_figwidth(12)
        figure.set_figheight(8)
        figure.suptitle(os.path.basename(file.file_name))
        return figure
    
    def get_values(self, file, data):
        length = len(data) if file.channel_count == 1 else len(data[0])
        x = self.get_time(file, length)
        if file.duration >= 60:
            x = x/60
        return x, data
    
    def plot_simple_graph(self, x, y, title):
        plt.title(title)
        plt.grid(color='#ddd')
        plt.plot(x, y, linewidth=0.5, color='#4986cc')
    
    def add_segments(self, x, segments, duration):
        if segments is not None:
            for segment in segments:
                plt.axvline(
                    x=x[segment] if duration < 60 else x[segment]/60,
                    color='#ff3838',
                    lw=0.5)

    def add_labels(self, xlabel, ylabel, duration, y_label):
        xlabel(("Time, min" if duration > 60 else "Time, s"), fontsize=13)
        ylabel(y_label, fontsize=13)
    
    def show_plot(self):
        plt.tight_layout()
        plt.show()
    
    def add_figure_legend(self, file):
        plt.subplot(file.channel_count, 1, 1)
        self.plot_file_property_legend(file.channel_count, file.samplerate, file.bit_depth)
    
    def add_time_legend(self, file, marker=False):
        if file.channel_count > 1:
            plt.subplot(file.channel_count, 1, file.channel_count)
        if file.frame_size_in_ms > 0:
            self.plot_time_legend(file.duration, marker, frame_size_in_ms=file.frame_size_in_ms)
        else:
            self.plot_time_legend(file.duration, marker)
    
    def plot_simple_stereo_plot(self, x, y, file, line_wt=0.5):
        colors = ['#4986CC', '#3F4756', '#A3ACBD', '#C66481', '#8D3150']

        for i, channel in enumerate(y):
            plt.subplot(file.channel_count, 1, i+1)
            plt.grid(color='#ddd')
            plt.plot(x, channel, linewidth=line_wt, color=colors[i%len(colors)])
    
    def add_stereo_segments(self, x, segments, file, line_wt=0.5):
        if segments is not None:
            for i, channel in enumerate(segments):
                plt.subplot(file.channel_count, 1, i+1)
                for segment in channel:
                    plt.axvline(
                        x=x[segment] if file.duration < 60 else x[segment]/60,
                        color='#ff3838',
                        lw=line_wt)

class Plot:
    def __init__(self, plot_tools):
        self.plot_tools = plot_tools
    
    def plot_mono_signal(self, file, data, marker=False, segments=None, line_wt=0.5, y_label=''):
        x, y = plot_tools.get_values(file, data)
        self.plot_tools.create_single_plot()
        self.plot_tools.plot_simple_graph(x, y, file.file_name)
        self.plot_tools.plot_file_property_legend(file.channel_count, file.samplerate, file.bit_depth)
        self.plot_tools.add_time_legend(file)
        self.plot_tools.add_segments(x, segments, file.duration)
        self.plot_tools.add_labels(plt.xlabel, plt.ylabel, file.duration, y_label)
        self.plot_tools.show_plot()

    def plot_stereo_signal(self, file, data, marker=False, segments=None, line_wt=0.5, y_label=''):
        x, y = plot_tools.get_values(file, data)
        figure = self.plot_tools.create_subplots(file)
        self.plot_tools.add_figure_legend(file)
        self.plot_tools.add_time_legend(file)
        self.plot_tools.plot_simple_stereo_plot(x, y, file)
        self.plot_tools.add_stereo_segments(x, segments, file)
        self.plot_tools.add_labels(figure.supxlabel, figure.supylabel, file.duration, y_label)
        self.plot_tools.show_plot()
       

plot_tools = PlotTools()
new_plot = Plot(plot_tools)
