import sys
import time
import argparse
import torch

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 简单测试 PyTorch 是否能在 GPU (CUDA) 上运行

def time_matmul(a, b, device):
    if device.type == 'cuda':
        torch.cuda.synchronize(device)
    t0 = time.perf_counter()
    c = a @ b
    if device.type == 'cuda':
        torch.cuda.synchronize(device)
    t1 = time.perf_counter()
    return c, t1 - t0


def main():
    parser = argparse.ArgumentParser(description="测试 torch 是否能使用 CUDA (GPU)")
    parser.add_argument("--size", type=int, default=1024, help="矩阵大小 n (生成 n x n 矩阵)")
    parser.add_argument("--dtype", choices=["float32", "float64"], default="float32")
    parser.add_argument("--repeat", type=int, default=3, help="重复次数取最快时间")
    args = parser.parse_args()

    print("torch 版本:", torch.__version__)

    if not torch.cuda.is_available():
        print("CUDA 不可用: torch.cuda.is_available() == False")
        print("如果你预期有 GPU，请检查驱动、CUDA 和 PyTorch 的安装。")
        sys.exit(1)

    device = torch.device("cuda:0")
    print("CUDA 可用，设备数量:", torch.cuda.device_count())
    try:
        print("当前设备(0) 名称:", torch.cuda.get_device_name(0))
    except Exception:
        pass

    dtype = torch.float32 if args.dtype == "float32" else torch.float64
    n = args.size
    print(f"测试矩阵大小: {n}x{n}, dtype={dtype}")

    # 在 CPU 上生成随机矩阵并测时
    a_cpu = torch.rand((n, n), dtype=dtype)
    b_cpu = torch.rand((n, n), dtype=dtype)

    cpu_times = []
    with torch.no_grad():
        for _ in range(args.repeat):
            _, t = time_matmul(a_cpu, b_cpu, torch.device("cpu"))
            cpu_times.append(t)
    cpu_t = min(cpu_times)
    print(f"CPU 最佳时间: {cpu_t:.4f} s")

    # 同样的矩阵复制到 GPU 上测时
    a_gpu = a_cpu.to(device)
    b_gpu = b_cpu.to(device)

    # 预热一次
    with torch.no_grad():
        _ = a_gpu @ b_gpu
        torch.cuda.synchronize(device)

    gpu_times = []
    with torch.no_grad():
        for _ in range(args.repeat):
            _, t = time_matmul(a_gpu, b_gpu, device)
            gpu_times.append(t)
    gpu_t = min(gpu_times)
    print(f"GPU 最佳时间: {gpu_t:.4f} s")

    # 验证结果一致性（小误差容忍）
    with torch.no_grad():
        c_gpu = (a_gpu @ b_gpu).cpu()
    if torch.allclose(c_gpu, (a_cpu @ b_cpu), atol=1e-5, rtol=1e-4):
        print("结果校验: OK (GPU 与 CPU 结果一致)")
    else:
        print("结果校验: 不一致！可能存在数值差异或错误。")

    speedup = cpu_t / gpu_t if gpu_t > 0 else float("inf")
    print(f"加速比 CPU/GPU: {speedup:.2f}x")

    print("测试完成。")

if __name__ == "__main__":
    main()