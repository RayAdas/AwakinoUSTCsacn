from NetTOF import CNN
from utility import FileIO, EchoDataset
import torch
import numpy as np

if __name__ == "__main__":
    fio = FileIO()
    model = CNN.CNNModel()
    model_path = fio.join_datapath(fio.algorithm + '_model.pth')
    model.load_state_dict(torch.load(model_path))
    model.eval()  # Set the model to evaluation mode

    # 加载数据集
    echo_dataset = EchoDataset()
    wavedata = fio.get_waveform_data()
    echo_dataset.data = []
    for i in range(wavedata.shape[0]):
        for j in range(wavedata.shape[1]):
            echo_dataset.data.append(torch.tensor(wavedata[i, j], dtype=torch.float32))

    preds, probs = CNN.inference(model, echo_dataset)
    preds = np.array(preds).reshape(wavedata.shape[0], wavedata.shape[1])
    probs = np.array(probs).reshape(wavedata.shape[0], wavedata.shape[1])

    import matplotlib.pyplot as plt

    x_coords, y_coords = np.meshgrid(np.arange(wavedata.shape[1]), np.arange(wavedata.shape[0]))
    plt.figure(figsize=(8, 6))
    scatter = plt.scatter(x_coords.flatten(), y_coords.flatten(), c=probs.flatten(), cmap='viridis', marker='s')
    plt.xlabel('Waveform X')
    plt.ylabel('Waveform Y')
    plt.title('Prediction Map')
    plt.colorbar(scatter, label='Predicted Value')
    plt.show()