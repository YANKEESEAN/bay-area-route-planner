import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random
import time

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

def load_distance_matrix(matrix_path=None, n=120):
    """
    加载距离矩阵：优先读取项目文档中的"大湾区景点矩阵格式.xlsx"，失败则生成模拟矩阵
    单位：米→千米
    """
    try:
        # 数据文件路径，若存在则读取
        df = pd.read_excel(matrix_path or "大湾区景点矩阵格式.xlsx", header=None, engine='openpyxl')
        # 适配目标景点数量n，不足则补充模拟数据
        if df.shape[0] < n:
            supplement = np.random.uniform(5, 200, (n - df.shape[0], n - df.shape[0]))
            np.fill_diagonal(supplement, 0)  # 自身到自身距离为0
            supplement = (supplement + supplement.T) / 2  # 矩阵对称
            distance_matrix = np.pad(df.values, ((0, n - df.shape[0]), (0, n - df.shape[0])),
                                     mode='constant', constant_values=0)
            distance_matrix[df.shape[0]:, df.shape[0]:] = supplement
        else:
            distance_matrix = df.values[:n, :n]
        distance_matrix = distance_matrix / 1000  # 米转换为千米
    except:
        # 生成模拟矩阵（贴合项目"100+景点"规模，距离范围5-200km）
        np.random.seed(42)  # 固定随机种子，确保结果可复现
        distance_matrix = np.random.uniform(5, 200, (n, n))
        np.fill_diagonal(distance_matrix, 0)
        distance_matrix = (distance_matrix + distance_matrix.T) / 2
    return distance_matrix

def greedy_algorithm(distance_matrix):
    """
    贪婪算法：每步选择局部最优（最短距离），构建全局路径
    核心逻辑：随机起点→每次选当前到未访问景点的最短路径
    """
    n = distance_matrix.shape[0]
    if n <= 1:
        return 0.0
    visited = [False] * n
    start = random.randint(0, n - 1)  # 随机起点（项目文档定义）
    path = [start]
    visited[start] = True
    total_distance = 0.0

    while len(path) < n:
        current = path[-1]
        min_dist = float('inf')
        next_point = -1
        # 遍历未访问景点，选择最短距离
        for i in range(n):
            if not visited[i] and distance_matrix[current][i] < min_dist:
                min_dist = distance_matrix[current][i]
                next_point = i
        if next_point == -1:
            break  # 异常处理
        path.append(next_point)
        visited[next_point] = True
        total_distance += min_dist
    return total_distance

def aco_algorithm(distance_matrix, ant_num=15, iter_num=50, alpha=1.0, beta=2.0, rho=0.5, Q=100):
    """
    蚁群优化算法（ACO）：模拟蚂蚁觅食，信息素正反馈+蒸发机制
    参数：蚂蚁数量15、迭代次数50、α=1.0、β=2.0、ρ=0.5、Q=100
    """
    n = distance_matrix.shape[0]
    if n <= 1:
        return 0.0
    # 初始化信息素矩阵与启发信息
    pheromone = np.ones((n, n))  # 初始信息素浓度为1
    heuristic = 1 / (distance_matrix + 1e-6)  # 启发信息=距离倒数（避免除0）
    min_total_distance = float('inf')

    for _ in range(iter_num):
        ant_paths = []
        ant_distances = []
        # 每只蚂蚁构建路径
        for _ in range(ant_num):
            visited = [False] * n
            start = random.randint(0, n - 1)
            path = [start]
            visited[start] = True
            current_distance = 0.0

            while len(path) < n:
                current = path[-1]
                # 计算选择概率（信息素+启发信息）
                prob = (pheromone[current] ** alpha) * (heuristic[current] ** beta)
                prob[visited] = 0  # 未访问景点概率置0
                prob = prob / prob.sum()  # 归一化
                # 按概率选择下一个景点
                next_point = np.random.choice(range(n), p=prob)
                # 更新路径与距离
                path.append(next_point)
                visited[next_point] = True
                current_distance += distance_matrix[current][next_point]

            ant_paths.append(path)
            ant_distances.append(current_distance)
            # 更新全局最短距离
            if current_distance < min_total_distance:
                min_total_distance = current_distance

        # 信息素更新（蒸发+新增）
        pheromone *= (1 - rho)  # 信息素蒸发（避免局部最优）
        for i in range(ant_num):
            path = ant_paths[i]
            distance = ant_distances[i]
            delta_pheromone = Q / distance  # 信息素增量（距离越短增量越大）
            for j in range(n - 1):
                u = path[j]
                v = path[j + 1]
                pheromone[u][v] += delta_pheromone
                pheromone[v][u] += delta_pheromone  # 对称更新（往返距离一致）
    return min_total_distance


def dynamic_programming_algorithm(distance_matrix):
    """
    动态规划算法：支持20个景点，优化内存占用计算
    """
    n = distance_matrix.shape[0]
    if n <= 1:
        return 0.0

    # 根据内存计算调整最大支持景点数量为20
    max_support_n = 20  # 20个景点仅需160MB内存
    if n > max_support_n:
        print(f"动态规划算法：景点数量{n}超出支持上限{max_support_n}，返回'超出范围'")
        return np.nan  # 用NaN标识超出范围

    # 内存占用预判（避免意外报错）
    mask_size = 1 << n  # 2^n个状态
    estimated_memory_mb = (mask_size * n * 8) / (1024 * 1024)  # 估算内存（MB）
    if estimated_memory_mb > 512:  # 限制最大内存占用为512MB
        print(f"动态规划算法：预估内存{estimated_memory_mb:.1f}MB超出限制，返回'超出范围'")
        return np.nan

    try:
        # 初始化DP表（使用更节省内存的方式）
        dp = np.full((mask_size, n), float('inf'), dtype=np.float32)  # 改用float32，内存减少一半
        dp[1 << 0][0] = 0.0  # 起点设为0号景点

        # 填充DP表（优化循环逻辑，减少计算量）
        for mask in range(mask_size):
            # 只处理包含当前点的有效状态
            for u in range(n):
                if not (mask & (1 << u)):
                    continue
                current_dist = dp[mask][u]
                if current_dist == float('inf'):
                    continue
                # 只遍历未访问的景点
                for v in range(n):
                    if mask & (1 << v):
                        continue
                    new_mask = mask | (1 << v)
                    new_dist = current_dist + distance_matrix[u][v]
                    if new_dist < dp[new_mask][v]:
                        dp[new_mask][v] = new_dist

        # 计算全局最短距离
        full_mask = (1 << n) - 1
        min_total_distance = min(dp[full_mask][v] + distance_matrix[v][0] for v in range(n))
        return min_total_distance

    except MemoryError:
        print(f"动态规划算法：处理{n}个景点时内存不足，返回'超出范围'")
        return np.nan
    except Exception as e:
        print(f"动态规划算法：处理{n}个景点时出错：{str(e)}")
        return np.nan


def genetic_algorithm(distance_matrix, pop_size=50, iter_num=100, mutation_rate=0.02):
    """
    遗传算法：模拟生物进化，适配中大规模景点
    核心逻辑：初始化种群→计算适应度→选择→交叉→变异→迭代优化
    """
    n = distance_matrix.shape[0]
    if n <= 1:
        return 0.0

    # 1. 初始化种群（每个个体为景点排列，代表一条路径）
    def init_population():
        population = []
        for _ in range(pop_size):
            individual = list(range(n))
            random.shuffle(individual)  # 随机打乱生成个体
            population.append(individual)
        return population

    # 2. 计算适应度（路径总距离越短，适应度越高）
    def calculate_fitness(individual):
        total_distance = 0.0
        for i in range(n - 1):
            u = individual[i]
            v = individual[i + 1]
            total_distance += distance_matrix[u][v]
        total_distance += distance_matrix[individual[-1]][individual[0]]  # 返回起点，形成闭环
        return 1 / total_distance  # 适应度=1/距离（距离越短，适应度越高）

    # 3. 选择（轮盘赌选择，适应度高的个体被选中概率高）
    def selection(population, fitnesses):
        total_fitness = sum(fitnesses)
        probabilities = [f / total_fitness for f in fitnesses]
        selected = random.choices(population, probabilities, k=pop_size)
        return selected

    # 4. 交叉（部分映射交叉，避免重复景点，符合TSP路径合法性）
    def crossover(parent1, parent2):
        if random.random() < 0.8:  # 交叉概率80%（平衡多样性与稳定性）
            start = random.randint(0, n - 2)
            end = random.randint(start + 1, n - 1)
            child = [-1] * n
            child[start:end + 1] = parent1[start:end + 1]  # 复制交叉区间
            # 填充剩余位置（从parent2复制未出现的元素）
            parent2_idx = 0
            for i in range(n):
                if child[i] == -1:
                    while parent2[parent2_idx] in child:
                        parent2_idx += 1
                    child[i] = parent2[parent2_idx]
                    parent2_idx += 1
            return child
        else:
            return parent1  # 不交叉，直接返回父代

    # 5. 变异（交换两个位置，避免陷入局部最优）
    def mutate(individual):
        if random.random() < mutation_rate:
            i, j = random.sample(range(n), 2)
            individual[i], individual[j] = individual[j], individual[i]
        return individual

    # 执行遗传算法主流程
    population = init_population()
    min_total_distance = float('inf')

    for _ in range(iter_num):
        # 计算适应度与总距离
        fitnesses = [calculate_fitness(ind) for ind in population]
        distances = [1 / fit for fit in fitnesses]  # 从适应度反推总距离
        # 更新全局最短距离
        current_min = min(distances)
        if current_min < min_total_distance:
            min_total_distance = current_min

        # 生成新一代种群（选择→交叉→变异）
        selected = selection(population, fitnesses)
        new_population = []
        for i in range(0, pop_size, 2):
            parent1 = selected[i]
            parent2 = selected[i + 1] if (i + 1) < pop_size else selected[i]
            child1 = crossover(parent1, parent2)
            child2 = crossover(parent2, parent1)
            new_population.append(mutate(child1))
            new_population.append(mutate(child2))
        population = new_population[:pop_size]  # 确保种群规模不变

    return min_total_distance

# -------------------------- 3. 性能测试（覆盖项目120个景点） --------------------------
def test_four_algorithms_performance():
    """
    性能测试：景点数量梯度适配动态规划内存限制，覆盖项目"120景点"
    测试梯度：[5, 10, 20, 40, 60, 80, 100, 120]
    """
    spot_counts = [5, 10, 20, 40, 60, 80, 100, 120]
    # 结果列名：景点数量 + 四算法的距离与耗时
    columns = ["景点数量", "贪婪距离(km)", "贪婪耗时(ms)",
               "ACO距离(km)", "ACO耗时(ms)",
               "动态规划距离(km)", "动态规划耗时(ms)",
               "遗传距离(km)", "遗传耗时(ms)"]
    results = []
    repeat = 3  # 每个场景重复3次取平均（平衡随机误差与测试效率）

    for n in spot_counts:
        print(f"\n正在测试【{n}个景点】...")
        dist_matrix = load_distance_matrix(n=n)
        # 存储单次测试结果
        greedy_dist, greedy_time = [], []
        aco_dist, aco_time = [], []
        dp_dist, dp_time = [], []
        ga_dist, ga_time = [], []

        for _ in range(repeat):
            # 1. 测试贪婪算法（快速规划算法）
            start = time.time()
            g_dist = greedy_algorithm(dist_matrix)
            g_t = (time.time() - start) * 1000  # 秒→毫秒
            greedy_dist.append(g_dist)
            greedy_time.append(g_t)

            # 2. 测试ACO算法（最优路径算法）
            start = time.time()
            a_dist = aco_algorithm(dist_matrix)
            a_t = (time.time() - start) * 1000
            aco_dist.append(a_dist)
            aco_time.append(a_t)

            # 3. 测试动态规划算法（小规模精确算法）
            start = time.time()
            d_dist = dynamic_programming_algorithm(dist_matrix)
            d_t = (time.time() - start) * 1000
            dp_dist.append(d_dist)
            dp_time.append(d_t)

            # 4. 测试遗传算法（中大规模优化算法）
            start = time.time()
            ga_d = genetic_algorithm(dist_matrix)
            ga_t = (time.time() - start) * 1000
            ga_dist.append(ga_d)
            ga_time.append(ga_t)

        # 计算平均值（处理动态规划的NaN值）
        avg_greedy = [np.mean(greedy_dist), np.mean(greedy_time)]
        avg_aco = [np.mean(aco_dist), np.mean(aco_time)]
        # 动态规划：过滤NaN值后计算平均（仅保留有效数据）
        valid_dp_dist = [d for d in dp_dist if not np.isnan(d)]
        valid_dp_time = [t for t, d in zip(dp_time, dp_dist) if not np.isnan(d)]
        avg_dp = [np.mean(valid_dp_dist) if valid_dp_dist else np.nan,
                  np.mean(valid_dp_time) if valid_dp_time else np.nan]
        avg_ga = [np.mean(ga_dist), np.mean(ga_time)]

        # 保存当前景点数量的结果
        results.append([n] + avg_greedy + avg_aco + avg_dp + avg_ga)
        # 打印中间结果（便于实时查看）
        print(f"【{n}个景点】结果（平均值）：")
        print(f"  贪婪算法：{avg_greedy[0]:.1f}km / {avg_greedy[1]:.1f}ms")
        print(f"  ACO算法：{avg_aco[0]:.1f}km / {avg_aco[1]:.1f}ms")
        print(f"  动态规划：{'超出范围' if np.isnan(avg_dp[0]) else f'{avg_dp[0]:.1f}km'} / {'超出范围' if np.isnan(avg_dp[1]) else f'{avg_dp[1]:.1f}ms'}")
        print(f"  遗传算法：{avg_ga[0]:.1f}km / {avg_ga[1]:.1f}ms")

    # 转换为DataFrame，便于后续处理
    results_df = pd.DataFrame(results, columns=columns)
    return results_df

# -------------------------- 4. 性能可视化 --------------------------
def plot_four_algorithms_performance(results_df):

    # 1. 指定图表保存路径
    save_path = "E:\\桌面\\粤港澳大湾区智游系统四算法性能对比图.png"
    spot_counts = results_df["景点数量"].values

    # 2. 关闭matplotlib交互模式（关键：确保非GUI环境也能生成图片）
    plt.switch_backend('Agg')  # 非交互后端，支持无窗口生成图片
    plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']  # 再次确保中文字体
    plt.rcParams['axes.unicode_minus'] = False

    try:
        # 3. 创建图表（固定尺寸，避免内容截断）
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 16), dpi=300)  # 增大尺寸，确保显示完整
        algo_config = {
            "贪婪算法": {"color": "#FF6B6B", "marker": "o", "col_dist": "贪婪距离(km)", "col_time": "贪婪耗时(ms)"},
            "ACO算法": {"color": "#4ECDC4", "marker": "s", "col_dist": "ACO距离(km)", "col_time": "ACO耗时(ms)"},
            "动态规划算法": {"color": "#45B7D1", "marker": "^", "col_dist": "动态规划距离(km)", "col_time": "动态规划耗时(ms)"},
            "遗传算法": {"color": "#96CEB4", "marker": "D", "col_dist": "遗传距离(km)", "col_time": "遗传耗时(ms)"}
        }

        # ---------------- 子图1：总距离对比 ----------------
        for algo, config in algo_config.items():
            valid_data = ~np.isnan(results_df[config["col_dist"]])
            if valid_data.any():
                ax1.plot(spot_counts[valid_data], results_df[config["col_dist"]][valid_data],
                         marker=config["marker"], linewidth=3, label=algo, color=config["color"], markersize=8)
                # 数值标签（放大字体，避免重叠）
                for i, (n, dist) in enumerate(zip(spot_counts, results_df[config["col_dist"]])):
                    if not np.isnan(dist):
                        ax1.text(n, dist + 20, f"{dist:.0f}", ha="center", va="bottom",
                                 fontsize=10, color=config["color"], fontweight="bold")

        ax1.set_xlabel("景点数量", fontsize=14, fontweight="bold")
        ax1.set_ylabel("总距离（km）", fontsize=14, fontweight="bold")
        ax1.set_title("粤港澳大湾区智游系统四算法路径总距离对比（优化效果）",
                      fontsize=18, fontweight="bold", pad=30)
        ax1.legend(loc="upper left", fontsize=12)
        ax1.grid(True, alpha=0.3, linestyle="--", linewidth=1.5)
        ax1.set_xticks(spot_counts)  # 显示所有景点数量刻度

        # ---------------- 子图2：耗时对比 ----------------
        for algo, config in algo_config.items():
            valid_data = ~np.isnan(results_df[config["col_time"]])
            if valid_data.any():
                ax2.plot(spot_counts[valid_data], results_df[config["col_time"]][valid_data],
                         marker=config["marker"], linewidth=3, label=algo, color=config["color"], markersize=8)
                # 数值标签（区分贪婪算法位置，避免重叠）
                for i, (n, t) in enumerate(zip(spot_counts, results_df[config["col_time"]])):
                    if not np.isnan(t):
                        if algo == "贪婪算法":
                            ax2.text(n, t + 50, f"{t:.1f}", ha="center", va="bottom",
                                     fontsize=10, color=config["color"], fontweight="bold")
                        else:
                            ax2.text(n, t - 100, f"{t:.1f}", ha="center", va="top",
                                     fontsize=10, color=config["color"], fontweight="bold")

        ax2.set_xlabel("景点数量", fontsize=14, fontweight="bold")
        ax2.set_ylabel("计算耗时（ms）", fontsize=14, fontweight="bold")
        ax2.set_title("粤港澳大湾区智游系统四算法计算耗时对比（效率）",
                      fontsize=18, fontweight="bold", pad=30)
        ax2.legend(loc="upper left", fontsize=12)
        ax2.grid(True, alpha=0.3, linestyle="--", linewidth=1.5)
        ax2.set_xticks(spot_counts)  # 显示所有景点数量刻度

        # 4. 调整布局并保存
        plt.tight_layout(pad=5.0)  # 增大边距，避免标题/标签被截断
        fig.savefig(save_path, bbox_inches="tight", dpi=300) 
        plt.close(fig)  # 关闭图表，释放内存

        print(f"\n✅ 图表已成功保存到桌面：{save_path}")
        print(f"   路径：E:\\桌面\\粤港澳大湾区智游系统四算法性能对比图.png")

    except Exception as e:
        # 5. 捕获并显示绘图错误
        print(f"\n❌ 绘图失败，错误原因：{str(e)}")
        print("   请检查：1. matplotlib是否安装完整；2. 桌面路径是否存在；3. 内存是否充足")


def plot_satisfaction_trend(results_df):
    """
    绘制算法的满意路径趋势图
    满意路径定义为：算法结果与理论最优解的接近程度（值越小满意度越高）
    """
    # 指定保存路径为桌面
    save_path = "E:\\桌面\\算法满意路径趋势图.png"
    spot_counts = results_df["景点数量"].values

    # 关闭交互模式，确保图片可以保存
    plt.switch_backend('Agg')
    plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False

    try:
        # 创建图表
        fig, ax = plt.subplots(figsize=(12, 8), dpi=300)

        # 算法配置
        algo_config = {
            "贪婪算法": {"color": "#FF6B6B", "marker": "o", "col_dist": "贪婪距离(km)"},
            "ACO算法": {"color": "#4ECDC4", "marker": "s", "col_dist": "ACO距离(km)"},
            "遗传算法": {"color": "#96CEB4", "marker": "D", "col_dist": "遗传距离(km)"}
        }

        # 以动态规划结果作为基准（理论最优解），计算其他算法的相对偏差
        # 对于动态规划不支持的场景，使用ACO结果作为参考基准
        base_distances = []
        for i, n in enumerate(spot_counts):
            dp_dist = results_df["动态规划距离(km)"][i]
            if not np.isnan(dp_dist):
                base_distances.append(dp_dist)
            else:
                # 动态规划不支持时，用ACO结果作为基准
                base_distances.append(results_df["ACO距离(km)"][i])

        # 绘制各算法的满意度趋势（相对偏差）
        for algo, config in algo_config.items():
            # 计算相对偏差 = (算法结果 - 基准结果) / 基准结果 × 100%
            # 偏差越小，满意度越高
            valid_data = ~np.isnan(results_df[config["col_dist"]])
            if valid_data.any():
                relative_deviation = [
                    (results_df[config["col_dist"]][i] - base_distances[i]) / base_distances[i] * 100
                    for i in range(len(spot_counts)) if valid_data[i]
                ]
                ax.plot(spot_counts[valid_data], relative_deviation,
                        marker=config["marker"], linewidth=3, label=algo,
                        color=config["color"], markersize=8)

                # 添加数值标签
                for i, (n, dev) in enumerate(zip(spot_counts, relative_deviation)):
                    if valid_data[i]:
                        ax.text(spot_counts[valid_data][i], dev + 0.5,
                                f"{dev:.1f}%", ha="center", va="bottom",
                                fontsize=10, color=config["color"])

        # 图表配置
        ax.set_xlabel("景点数量", fontsize=14, fontweight="bold")
        ax.set_ylabel("相对偏差（%）", fontsize=14, fontweight="bold")
        ax.set_title("算法满意路径趋势图（相对偏差越小，满意度越高）",
                     fontsize=16, fontweight="bold", pad=20)
        ax.legend(loc="upper left", fontsize=12)
        ax.grid(True, alpha=0.3, linestyle="--")
        ax.axhline(y=0, color='gray', linestyle='--', alpha=0.5)  # 零偏差参考线
        ax.set_xticks(spot_counts)

        # 保存图表
        plt.tight_layout()
        fig.savefig(save_path, bbox_inches="tight")
        plt.close(fig)

        print(f"\n✅ 满意路径趋势图已保存到桌面：{save_path}")

    except Exception as e:
        print(f"\n❌ 满意路径趋势图绘制失败：{str(e)}")


# -------------------------- 5. 主函数 --------------------------
if __name__ == "__main__":
    # 1. 执行性能测试
    performance_results = test_four_algorithms_performance()
    # 调用绘图函数
    plot_four_algorithms_performance(performance_results)
    # 满意路径趋势图的调用
    plot_satisfaction_trend(performance_results)
    # 2. 打印完整结果表格
    print("\n" + "="*100)
    print("粤港澳大湾区智游系统四算法性能对比完整结果（平均值）")
    print("="*100)
    # 格式化显示：动态规划超出范围时显示"-"
    display_df = performance_results.copy()
    for col in ["动态规划距离(km)", "动态规划耗时(ms)"]:
        display_df[col] = display_df[col].apply(lambda x: "-" if np.isnan(x) else f"{x:.1f}")
    # 其他列保留1位小数
    for col in display_df.columns:
        if col not in ["景点数量", "动态规划距离(km)", "动态规划耗时(ms)"]:
            display_df[col] = display_df[col].apply(lambda x: f"{x:.1f}")
    print(display_df.to_string(index=False))
    # 3. 保存结果到Excel
    performance_results.to_excel("粤港澳大湾区智游系统四算法性能测试结果.xlsx", index=False)
    print(f"\n性能测试结果已保存：粤港澳大湾区智游系统四算法性能测试结果.xlsx")