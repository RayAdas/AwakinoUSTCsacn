import numpy as np
import torch
from torch.utils.data import Dataset
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
import torch.nn.functional as F

class CNNModel(nn.Module):
    def __init__(self):
        super(CNNModel, self).__init__()
        self.conv1 = nn.Conv1d(1, 16, kernel_size=3, padding=1)
        self.pool = nn.MaxPool1d(2, 2)
        self.conv2 = nn.Conv1d(16, 32, kernel_size=3, padding=1)
        self.fc1 = nn.Linear(32 * (config['seq_length'] // 2 // 2), 128)
        self.fc2 = nn.Linear(128, 1)

    def forward(self, x):
        device = next(self.parameters()).device
        x = x.to(device)
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = x.view(-1, 32 * (config['seq_length'] // 2 // 2))
        x = F.relu(self.fc1(x))
        x = self.fc2(x)
        return x

# 超参数设置
config = {
    'batch_size': 32,
    'num_workers': 4,
    'hidden_size': 64,
    'num_layers': 2,
    'learning_rate': 0.001,
    'num_epochs': 5,
    'seq_length': 1000
}

def train_model(train_dataset):    
    dataloader = DataLoader(train_dataset, batch_size=32, shuffle=True)

    # Initialize model, loss function, and optimizer
    model = CNNModel()
    model.train()
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"Using {device} device")
    model.to(torch.device(device))

    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    # Training loop
    num_epochs = 20
    min_loss = float('inf')
    best_model_wts = None

    for epoch in range(num_epochs):
        for inputs, targets in dataloader:
            # Move data to the device
            inputs = inputs.to(device)
            targets = targets.to(device)

            inputs = inputs.unsqueeze(1)  # Add channel dimension
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, targets.unsqueeze(1))
            loss.backward()
            optimizer.step()

        print(f'Epoch {epoch+1}/{num_epochs}, Loss: {loss.item()}',end='')

        if loss.item() < min_loss:
            min_loss = loss.item()
            best_model_wts = model
            print(f' (best)')
        else:
            print('')
        
    return best_model_wts

def test_model(model, test_dataset):
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    model.to(torch.device(device))
    
    dataloader = DataLoader(test_dataset, batch_size=config['batch_size'], shuffle=False)

    model.eval()
    preds = []
    labels = []
    probs = []

    with torch.no_grad():
        for inputs, targets in dataloader:
            inputs = inputs.unsqueeze(1)  # Add channel dimension
            outputs = model(inputs)
            probs.append(outputs.cpu().numpy())
            labels.append(targets.cpu().numpy())
            preds.extend((outputs > 0.5).int().cpu().numpy().flatten())

    # preds = np.concatenate(preds)
    labels = np.concatenate(labels)
    probs = np.concatenate(probs)

    return preds, labels, probs