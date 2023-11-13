import math
from plot_data import plot_tools

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
        fading_factor = (1 - math.exp(-fade_factor * (fade_value_count - (i - (len(data) - fade_value_count) + 1))))
        fade_out_data.append(round(data[i] * fading_factor))

    return(fade_in_data, fade_out_data)

def get_fade_data(file):
    print(f"Audio length: {plot_tools.convert_time_to_readable_string(file.duration)}")
    fade_time = int(input("Enter fade time in ms:\n> "))
    fade_type = input("Choose fade type:\n[1] Linear\n[2] Logarithmic\n> ")
    fade_value_count = round(file.samplerate*(fade_time/1000))
    fade = linear_fade if fade_type == "1" else log_fade
    return fade_value_count, fade
