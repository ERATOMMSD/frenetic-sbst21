from keras.models import Sequential
from keras.layers import Dense
import numpy as np

import json

# TODO: data_frame = pa.read_json(json_file)
def get_model(json_file):
    with open(json_file) as f:
        data = json.load(f)

    model = Sequential()
    for i in range(len(data)):
        w = np.array(data[i]).T
        b = np.zeros(w.shape[1])
        model.add(Dense(w.shape[1], input_shape=(w.shape[0], )))
        model.layers[i].set_weights([w, b])

    return model

if __name__ == "__main__":
    model = get_model("./80-30-110.trained.json")
    # we should be getting 0.0184515, 0.025336, 0.0462188, 0.0249238, 0.0182028, 0.0342065, 0.0110042, 0.0392059, 0.0136922, 0.0108584, 0.0331147, 0.033087, 0.0503947, 0.0487113, 0.0526979, 0.0282759, 0.0370352, 0.0362923, 0.0429182
    print(model.predict(np.array([[1.99506, 1.35371, 0.450784, 1.40095, 1.66572, 1.55706, 1.48581, 1.37367, 1.25288, 1.98962, 1.49743, 1.0522, 0.197334, 1.18767, 0.792962, 1.37871, 1.57626, 1.45412, 1.55921]])))
