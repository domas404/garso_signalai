def normalize_data(data):
    min_val = min(data)
    max_val = max(data)
    new_data = []
    for el in data:
        new_data.append((el - min_val) / (max_val - min_val))
    return new_data

def calculate_energy(data):
    energy = []
    for i in range(0, len(data)):
        frame_energy = 0
        for j in range(0, len(data[i])):
            frame_energy += data[i][j]**2
        energy.append(frame_energy)
    return energy

def calculate_zero_crossing_rate(data):
    zcr = []
    for i in range(0, len(data)):
        frame_zcr = 0
        for j in range(1, len(data[i])):
            frame_zcr += abs(1 if data[i][j] >= 0 else -1 - 1 if data[i][j-1] >= 0 else -1)
        frame_zcr = frame_zcr/(2*len(data[i]))
        zcr.append(frame_zcr)
    return zcr

def get_energy(normalized_data_frames):
    energy = []
    for frame in normalized_data_frames:
        energy.append(normalize_data(calculate_energy(frame)))
    return energy

def get_zcr(data_frames):
    zcr = []
    for frame in data_frames:
        zcr.append(calculate_zero_crossing_rate(frame))
    return zcr

def get_frame_size(time_frame, samplerate):
    return int(samplerate/1000*time_frame)

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

def get_normalized_data_frames(data, samplerate, time_frame):
    normalized_data_frames = []
    for channel in data:
        normalized_data_frames.append(
            split_data_into_frames(
                normalize_data(channel),
                samplerate,
                time_frame
            ))
    return normalized_data_frames

def get_data_frames(data, samplerate, time_frame):
    data_frames = []
    for channel in data:
        data_frames.append(split_data_into_frames(channel, samplerate, time_frame))
    return data_frames

def find_segments(data, step):
    segments = []
    multiplier = 1
    for i in range(0, len(data)):
        if multiplier*data[i] >= multiplier*step:
            segments.append(i)
            multiplier *= (-1)
    return segments
