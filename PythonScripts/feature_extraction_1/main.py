from EchoModel import echo_function
import numpy as np
import matplotlib.pyplot as plt
# 从echo_function生成测试波形

def decompose(s: np.ndarray, t: np.ndarray) -> list:
    """
    在给定的时间轴 t 上，对信号 s 进行 n_iter_outer 次分解。

    每一轮分解步骤：
    - 遍历所有 tau ∈ t；
    - 对每个 tau，通过“梯度下降”在 beta ∈ [-1, 1] 上最小化误差
      E(beta) = sum((s - echo_function(t, tau, beta))^2)；
    - 选取误差最小的 (tau*, beta*)，并将对应波形从 s 中减去；
    - 记录该 (tau*, beta*, error)。

    返回：长度为 5 的列表，每个元素为字典：
      {"tau": float, "beta": float, "error": float}

    说明：echo_function 对 beta 线性，因此可以解析求解；但此处按题意使用
    梯度下降实现。为了稳定与快速收敛，使用解析梯度与自适应学习率，并对
    beta 进行区间投影（[-1, 1]）。
    """

    # 防御性拷贝，避免修改原始输入
    residual = np.asarray(s, dtype=float).copy()
    t = np.asarray(t, dtype=float)

    n_iter_outer = 2  # 外层遍历次数
    results = []

    # 小常数，避免除零
    eps = 1e-12

    for _ in range(n_iter_outer):
        best = {"tau": None, "beta": 0.0, "error": np.inf}

        # 遍历全部 tau 网格
        for tau in t:
            # 预先计算基波形 g(t; tau, beta=1)
            g = echo_function(t, tau=tau, beta=1.0)
            # 目标：min_beta sum((residual - beta*g)^2)

            # 解析梯度：dE/dbeta = -2 * (residual - beta*g)·g
            g2 = float(np.dot(g, g)) + eps        # ||g||^2
            sg = float(np.dot(residual, g))       # s·g

            # 使用梯度下降：beta <- beta - lr * dE/dbeta
            # 选 lr = 1/(2*g2)，理论上一步即可到达解析最优（未考虑截断）
            lr = 1.0 / (2.0 * g2)

            beta = 0.0  # 初始化（可设为 0）
            # 进行若干步以符合“梯度下降”的描述，同时处理 [-1,1] 投影
            for _inner in range(100):
                grad = -2.0 * (sg - beta * g2)  # dE/dbeta
                beta = beta - lr * grad
                # 投影到 [-1, 1]
                if beta > 1.0:
                    beta = 1.0
                elif beta < -1.0:
                    beta = -1.0

            # 计算该 (tau, beta) 的误差
            pred = beta * g
            err = float(np.sum((residual - pred) ** 2))

            if err < best["error"]:
                best["tau"] = float(tau)
                best["beta"] = float(beta)
                best["error"] = err

        # 应用最佳分量，从残差中剔除
        if best["tau"] is not None:
            g_best = echo_function(t, tau=best["tau"], beta=1.0)
            residual = residual - best["beta"] * g_best
            results.append(best)
        else:
            # 若没有找到有效分量，提前结束
            break

    return results

if __name__ == "__main__":
    t = np.linspace(0, 10e-6, 1000)
    s1 = echo_function(t, tau=4e-6, beta=-0.5)
    s2 = echo_function(t, tau=7e-6, beta=1.0)
    y = s1 + s2

    components = decompose(y, t)
    print("Extracted components (tau, beta, error):")
    for c in components:
        print(c)

    # 可视化结果
    plt.figure()
    plt.plot(t, y, label="Original Signal", color="black")
    residual = y.copy()
    for i, comp in enumerate(components):
        g = echo_function(t, tau=comp["tau"], beta=comp["beta"])
        plt.plot(t, g, label=f"Component {i+1} (tau={comp['tau']:.2e}, beta={comp['beta']:.2f})", linestyle="--")
        residual -= g
    plt.plot(t, residual, label="Residual", linestyle="--", color="gray")
    plt.legend()
    plt.xlabel("Time (s)")
    plt.ylabel("Amplitude")
    plt.title("Signal Decomposition")
    plt.show()