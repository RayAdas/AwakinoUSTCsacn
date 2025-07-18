from copy import deepcopy
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

def train_model(train_dataset, val_dataset):    
    train_loader = DataLoader(train_dataset, batch_size=config['batch_size'], shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=config['batch_size'], shuffle=True)

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
    min_val_loss = float('inf')
    best_weights = None

    for epoch in range(num_epochs):
        model.train()
        train_loss = 0.0
        for inputs, targets in train_loader:
            # Move data to the device
            inputs = inputs.to(device)
            targets = targets.to(device)

            inputs = inputs.unsqueeze(1)  # Add channel dimension
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, targets.unsqueeze(1))
            loss.backward()
            optimizer.step()
            train_loss += loss.item() * inputs.size(0)
        train_loss /= len(train_dataset)

        model.eval()
        val_loss = 0.0
        with torch.no_grad():
            for inputs, targets in val_loader:
                inputs = inputs.to(device).unsqueeze(1)
                targets = targets.to(device)
                outputs = model(inputs)
                val_loss += criterion(outputs, targets.unsqueeze(1)).item() * inputs.size(0)
        val_loss /= len(val_dataset)

        print(f'Epoch {epoch+1}/{num_epochs}, Train Loss: {train_loss}, Val Loss: {val_loss}',end='')

        if val_loss < min_val_loss:
            min_val_loss = val_loss
            best_weights = deepcopy(model.state_dict())
            print(' (best)')
        else:
            print('')

    model.load_state_dict(best_weights)
    return model

def test_model(model, test_dataset):
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    model.to(torch.device(device))
    
    test_loader = DataLoader(test_dataset, batch_size=config['batch_size'], shuffle=False)

    model.eval()
    preds = []
    labels = []
    probs = []

    with torch.no_grad():
        for inputs, targets in test_loader:
            inputs = inputs.unsqueeze(1)  # Add channel dimension
            outputs = model(inputs)
            probs.extend(outputs.cpu().numpy().flatten())
            labels.extend(targets.cpu().numpy().flatten())
            preds.extend((outputs > 0.5).int().cpu().numpy().flatten())

    return preds, labels, probs

def inference(model, test_dataset):
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    model.to(torch.device(device))
    
    test_loader = DataLoader(test_dataset, batch_size=config['batch_size'], shuffle=False)

    model.eval()
    preds = []
    probs = []

    with torch.no_grad():
        for inputs in test_loader:
            inputs = inputs.unsqueeze(1)  # Add channel dimension
            outputs = model(inputs)
            probs.extend(outputs.cpu().numpy().flatten())
            preds.extend((outputs > 0.5).int().cpu().numpy().flatten())

    return preds, probs