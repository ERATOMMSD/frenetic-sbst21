from keras.models import Sequential
from keras.layers import Dense
import numpy as np

import json

# TODO: data_frame = pa.read_json(json_file)
def get_model(weights_json_file, biases_json_file):
    with open(weights_json_file) as f:
        weights_data = json.load(f)
    with open(biases_json_file) as f:
        biases_data = json.load(f)

    model = Sequential()
    for i in range(len(weights_data)):
        w = np.array(weights_data[i]).T
        b = np.array(biases_data[i])
        model.add(Dense(w.shape[1], input_shape=(w.shape[0], )))
        model.layers[i].set_weights([w, b])

    return model

def oob_distances_to_kappas(model, oob_distances):
    """
    model: trained nn model (use get_model on Mathematica-trained weights and biases json files)
    oob_distances: numpy array
    """
    return model.predict(np.array([oob_distances]))[0]

if __name__ == "__main__":
    model = get_model("./80-30-110.trained-on-600.weights.json", "./80-30-110.trained-on-600.biases.json")
    print(model.predict(np.array([[1.99506, 1.35371, 0.450784, 1.40095, 1.66572, 1.55706, 1.48581, 1.37367, 1.25288, 1.98962, 1.49743, 1.0522, 0.197334, 1.18767, 0.792962, 1.37871, 1.57626, 1.45412, 1.55921]])))
    # we should get 0.0169863, 0.0320919, 0.0519882, 0.0351862, 0.0257261, 0.0426494, 0.0202672, 0.0256207, 0.0166942, 0.0220529, 0.0413528, 0.0399505, 0.056026, 0.0530632, 0.0462601, 0.0365292, 0.0474662, 0.0335889, 0.0570663

    print(model.predict(np.array([[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1.0]])))
    # we should get 0.068571, 0.0507337, 0.0193429, 0.0160792, 0.0186856, 0.0360606, 0.0415764, 0.00727972, 0.0218964, 0.0380979, -0.00853481, 0.0428443, 0.00459742, 0.0114542, 0.0182725, 0.0264718, 0.0157071, 0.0302471, 0.0224392

    print(model.predict(np.array([[1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1.0]])))
    # we should get 0.06723875  0.08602888 -0.0073002   0.0182815  -0.01545558  0.01309468 0.0181048   0.01887268 -0.01474006  0.04656088 -0.0302649   0.03788421 0.00528702 -0.00264266  0.01873981  0.03209383 -0.00823759  0.05838466 0.05022907

    print(oob_distances_to_kappas(model,np.array([1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1.0])))
    # we should get 0.06723875  0.08602888 -0.0073002   0.0182815  -0.01545558  0.01309468 0.0181048   0.01887268 -0.01474006  0.04656088 -0.0302649   0.03788421 0.00528702 -0.00264266  0.01873981  0.03209383 -0.00823759  0.05838466 0.05022907
