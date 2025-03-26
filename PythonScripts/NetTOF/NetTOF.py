import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, classification_report
import seaborn as sns
import pandas as pd
from utility import MyFilter, FileIO

class EchoDataset(Dataset):
    def __init__(self):
        self.data = []
        self.tgt = []

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        return self.data[idx], self.tgt[idx]

# 定义LSTM网络结构
class LSTMModel(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers):
        super(LSTMModel, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, 1)
        
    def forward(self, x):
        # 获取当前设备信息
        device = x.device
        
        # 初始化隐藏状态（自动匹配设备）
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(device)
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(device)
        
        out, _ = self.lstm(x, (h0, c0))  # 此时所有张量都在相同设备
        out = self.fc(out[:, -1, :])
        return torch.sigmoid(out)

# 超参数设置
config = {
    'batch_size': 32,
    'num_workers': 4,
    'hidden_size': 64,
    'num_layers': 2,
    'learning_rate': 0.001,
    'num_epochs': 5,
    'seq_length': 1000  # 根据实际波形长度调整
}

# 数据加载
def prepare_dataloader(file_path):
    # 加载原始数据
    # 加载数据
    dataset_dict = torch.load(file_path)
    # 重新构造数据集
    dataset = EchoDataset()
    dataset.data = dataset_dict['data']
    dataset.tgt = dataset_dict['tgt']

    # 创建DataLoader
    dataloader = DataLoader(
        dataset,
        batch_size=config['batch_size'],
        shuffle=True,
        num_workers=config['num_workers'],
        drop_last=True
    )
    return dataloader

# 训练函数
def train_model(model, train_loader):
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = model.to(device)
    
    criterion = nn.BCELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=config['learning_rate'])
    
    losses = []
    accuracies = []
    
    for epoch in range(config['num_epochs']):
        model.train()
        running_loss = 0.0
        correct = 0
        total = 0
        
        for inputs, labels in train_loader:
            inputs = inputs.unsqueeze(-1).to(device)  # [batch, seq_len] -> [batch, seq_len, 1]
            labels = labels.to(device)
            
            # 前向传播
            outputs = model(inputs)
            loss = criterion(outputs.squeeze(), labels)
            
            # 反向传播和优化
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
            # 统计信息
            running_loss += loss.item()
            predicted = (outputs > 0.5).float()
            total += labels.size(0)
            correct += (predicted.squeeze() == labels).sum().item()
        
        epoch_loss = running_loss / len(train_loader)
        epoch_acc = 100 * correct / total
        losses.append(epoch_loss)
        accuracies.append(epoch_acc)
        
        print(f'Epoch [{epoch+1}/{config["num_epochs"]}], '
              f'Loss: {epoch_loss:.4f}, '
              f'Accuracy: {epoch_acc:.2f}%')
    
    # 绘制训练曲线
    plt.figure(figsize=(12, 5))
    plt.subplot(1, 2, 1)
    plt.plot(losses)
    plt.title('Training Loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    
    plt.subplot(1, 2, 2)
    plt.plot(accuracies)
    plt.title('Training Accuracy')
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy (%)')
    plt.show()
    
    return model
def test_model(model, test_loader, model_path='echo_lstm_model.pth'):
    # 确定设备并统一管理
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    
    # 加载模型并转移到目标设备
    model.load_state_dict(torch.load(model_path, map_location=device))
    model = model.to(device)
    model.eval()
    
    # 存储预测结果
    all_preds = []
    all_labels = []
    all_probs = []
    
    with torch.no_grad():
        for inputs, labels in test_loader:
            # 统一设备转移
            inputs = inputs.unsqueeze(-1).to(device)
            labels = labels.to(device)
            
            outputs = model(inputs)
            
            # 收集结果时转回CPU
            probs = outputs.cpu().numpy().flatten()
            preds = (outputs > 0.5).float().cpu().numpy().flatten()
            
            all_preds.extend(preds)
            all_labels.extend(labels.cpu().numpy().flatten())  # 确保标签也在CPU
            all_probs.extend(probs)
    
    return np.array(all_preds), np.array(all_labels), np.array(all_probs)

def visualize_results(labels, preds, probs, sample_data=None):
    plt.figure(figsize=(15, 10))
    
    # 混淆矩阵
    plt.subplot(2, 2, 1)
    cm = confusion_matrix(labels, preds)
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=['Negative', 'Positive'],
                yticklabels=['Negative', 'Positive'])
    plt.title('Confusion Matrix')
    plt.xlabel('Predicted')
    plt.ylabel('Actual')
    
    # 概率分布直方图
    plt.subplot(2, 2, 2)
    plt.hist(probs[labels==0], bins=30, alpha=0.5, label='Negative')
    plt.hist(probs[labels==1], bins=30, alpha=0.5, label='Positive')
    plt.title('Prediction Probability Distribution')
    plt.xlabel('Probability')
    plt.ylabel('Count')
    plt.legend()
    
    # 随机样本可视化
    if sample_data is not None:
        plt.subplot(2, 2, 3)
        sample_idx = np.random.randint(0, len(sample_data))
        waveform = sample_data[sample_idx][0].numpy()
        label = sample_data[sample_idx][1].item()
        pred = preds[sample_idx]
        
        plt.plot(waveform)
        plt.title(f'Waveform Example\nTrue: {label}, Pred: {pred}')
        plt.xlabel('Time Steps')
        plt.ylabel('Amplitude')
    
    # 分类报告
    plt.subplot(2, 2, 4)
    report = classification_report(labels, preds, target_names=['Negative', 'Positive'], output_dict=True)
    sns.heatmap(pd.DataFrame(report).iloc[:-1, :].T, annot=True, cmap='YlGnBu')
    plt.title('Classification Report')
    plt.tight_layout()
    plt.show()

# 使用示例
if __name__ == "__main__":
    # 初始化模型
    model = LSTMModel(
        input_size=1,
        hidden_size=config['hidden_size'],
        num_layers=config['num_layers']
    )
    fio = FileIO()

    # 加载数据（替换为实际文件路径）
    train_loader = prepare_dataloader(fio.join_datapath('echo_dataset.pt'))
    
    # 开始训练
    trained_model = train_model(model, train_loader)
    
    # 保存模型
    torch.save(trained_model.state_dict(), 'echo_lstm_model.pth')
    # 初始化模型
    model = LSTMModel(
        input_size=1,
        hidden_size=config['hidden_size'],
        num_layers=config['num_layers']
    )
    
    # 加载测试数据
    test_loader = prepare_dataloader(fio.join_datapath('echo_dataset.pt'))
    
    # 进行预测
    preds, labels, probs = test_model(model, test_loader)
    
    # 获取原始样本数据用于可视化
    sample_data = test_loader.dataset
    
    # 可视化结果
    visualize_results(labels, preds, probs, sample_data)
    
    # 输出详细评估指标
    print("Detailed Performance Metrics:")
    print(classification_report(labels, preds, target_names=['Negative', 'Positive']))
