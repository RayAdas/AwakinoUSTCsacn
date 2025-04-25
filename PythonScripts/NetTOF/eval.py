import review_visual
from sklearn.metrics import classification_report
import torch
import CNN
from utility import FileIO, EchoDataset

if __name__ == "__main__":
    fio = FileIO()
    model = CNN.CNNModel()
    model_path = fio.join_datapath(fio.algorithm + '_model.pth')
    model.load_state_dict(torch.load(model_path))
    model.eval()  # Set the model to evaluation mode

    # 加载数据集
    echo_dataset = EchoDataset()
    echo_dataset.load_file(fio.join_datapath('echo_dataset.pt'))
    # 进行预测
    preds, labels, probs = CNN.test_model(model, echo_dataset)
    
    # 获取原始样本数据用于可视化
    # sample_data = echo_dataset.dataset
    
    # 可视化结果
    review_visual.visualize_results(labels, preds, probs)
    
    # 输出详细评估指标
    print("Detailed Performance Metrics:")
    print(classification_report(labels, preds, target_names=['Negative', 'Positive']))