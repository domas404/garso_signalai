import os
import sys
import copy
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import numpy as np
from scipy.io import wavfile
from handle_data import handle_signal, handle_fade
from plot_data import plot_mono, plot_stereo
from spectrum_analysis import analyze_spectrum

class FileData:
    def __init__(self, file_path, samplerate, data):
        self.file_name = os.path.basename(file_path)
        self.samplerate = samplerate
        self.data = np.array(data, dtype=int)
        self.bit_depth = data.dtype.itemsize * 8
        self.duration = len(data)/samplerate
        self.channel_count = 1 if len(data.shape) < 2 else data.shape[1]
        self.data_with_fade = None
        self.frame_size_in_ms = 0

    def set_data(self, data):
        self.data = data
        self.duration = len(data)/self.samplerate

    def transpose_data(self):
        if self.channel_count > 1:
            new_data = np.array(self.data)
            new_data = np.transpose(new_data)
            self.data = new_data.tolist()

    def apply_fade(self, data_with_fade):
        self.data_with_fade = np.array(data_with_fade, dtype=int)

    def clone(self):
        return copy.deepcopy(self)

    def set_frame_size(self):
        self.frame_size_in_ms = int(input("Enter frame size in ms.\n> "))

root = Tk()
root.withdraw()

def read_data():
    file_path = askopenfilename()
    samplerate, data = wavfile.read(file_path)
    file = FileData(file_path, samplerate, data)
    root.update()
    return file

def prepare_data():
    file = read_data()
    if file.channel_count > 1:
        plot = plot_stereo
        file.transpose_data()
    else:
        plot = plot_mono
    return file, plot

def file_menu_dialog():
    file, plot = prepare_data()
    plot_types = ["energyPlot", "zeroCrossingRatePlot", "timePlot", "segmentPlot"]
    input_ok = False
    while not input_ok:
        print(f"FILE '{file.file_name}' MENU\n",
              "[1] Energy plot\n",
              "[2] ZCR plot\n",
              "[3] Time plot\n",
              "[4] Segment plot\n",
              "[5] Fade effect\n",
              "[6] Spectrum analysis\n",
              "[7] Menu")
        plot_menu_input = int(float(input("> ")))

        if plot_menu_input > 0 and plot_menu_input < 5:
            handle_signal(file, plot_types[plot_menu_input-1], plot)

        elif plot_menu_input == 5:
            handle_fade(file)

        elif plot_menu_input == 6:
            analyze_spectrum(file)

        elif plot_menu_input == 7:
            del file
            menu_dialog()
            input_ok = True

def menu_dialog():
    input_ok = False
    print("MENU\n", "[1] Open file\n", "[2] Quit")

    while not input_ok:
        menu_input = input("> ")

        if menu_input == '2':
            print("Exiting...")
            sys.exit()

        elif menu_input == '1':
            input_ok = True
            print("Processing...")
            file_menu_dialog()

menu_dialog()
