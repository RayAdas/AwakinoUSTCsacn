from utility import MyFilter, FileIO, Circle
from torch.utils.data import Dataset
import torch
from imblearn.over_sampling import SMOTE  # Import SMOTE

# 建立数据集
class EchoDataset(Dataset):
    def __init__(self):
        self.data = []
        self.tgt = []

    def loadwave(self, wavedata, circle):
        for i in range(wavedata.shape[0]):
            for j in range(wavedata.shape[1]):
                self.data.append(torch.tensor(wavedata[i, j], dtype=torch.float32))
                if (i, j) in circle:
                    self.tgt.append(torch.tensor(1, dtype=torch.float32))
                else:
                    self.tgt.append(torch.tensor(0, dtype=torch.float32))

        # Balance the dataset using SMOTE
        smote = SMOTE()
        data_flat = [d.numpy() for d in self.data]  # Convert tensors to numpy arrays
        tgt_flat = [t.item() for t in self.tgt]    # Convert tensors to scalar values
        data_resampled, tgt_resampled = smote.fit_resample(data_flat, tgt_flat)
        
        # Convert back to tensors
        self.data = [torch.tensor(d, dtype=torch.float32) for d in data_resampled]
        self.tgt = [torch.tensor(t, dtype=torch.float32) for t in tgt_resampled]

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        return self.data[idx], self.tgt[idx]
    
if __name__ == '__main__':
    fio = FileIO()
    waveform_src = fio.get_waveform_data()
    points = [(46, 34), (25, 32), (33, 27), (30, 44)]
    circle = Circle()
    circle.fit(points)

    # Initialize dataset and dataloader
    dataset = EchoDataset()
    dataset.loadwave(waveform_src, circle)

    data_dict = {'data': dataset.data, 'tgt': dataset.tgt}
    torch.save(data_dict, fio.join_datapath('echo_dataset.pt'))