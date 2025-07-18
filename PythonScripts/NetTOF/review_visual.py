import seaborn as sns
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, classification_report

def visualize_results(labels, preds, probs, title = "Figure", sample_data=None):
    plt.figure(figsize=(15, 10), num = title)

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