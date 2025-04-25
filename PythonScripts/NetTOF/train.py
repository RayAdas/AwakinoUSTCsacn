import CNN
from utility import FileIO, EchoDataset
import torch
    
if __name__ == "__main__":
    fio = FileIO()

    # 加载数据集
    echo_dataset = EchoDataset()
    echo_dataset.load_file(fio.join_datapath('echo_dataset.pt'))
    
    trained_model = None
    # 开始训练
    match fio.algorithm:
        case 'CNN':
            trained_model:CNN.CNNModel = CNN.train_model(echo_dataset)
        case 'LSTM':
            pass
        case _:
            raise ValueError("Unsupported algorithm!")

    try:
        model_path = fio.join_datapath(fio.algorithm + '_model.pth')
        torch.save(trained_model.state_dict(), model_path)
        print(f"Model saved to {model_path}")
    except Exception as e:
        print(f"Error saving model: {e}")
        raise

