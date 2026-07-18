from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
import random
from typing import List, Dict
import os
import itertools

app = Flask(__name__)


class PathPlanner:
    def __init__(self):
        # 加载真实数据
        self.attraction_names = [
            "上下九步行街", "上川岛飞沙滩", "世界之窗", "世纪莲体育中心", "东澳岛",
            "东莞可园", "东莞市沉香文化博物馆", "东部华侨城", "中山孙中山故居",
            "中山孙中山故里旅游区", "中山市博物馆", "中山树木园", "中山纪念堂",
            "五桂山逍遥谷", "余荫山房", "佛山市西樵山景区", "佛山市长鹿旅游休博园",
            "佛山文创古镇", "佛山祖庙", "佛灵湖生态旅游区", "光孝寺", "兰桂坊",
            "华南国家植物园", "华阳湖国家湿地公园", "南海神庙", "南越王博物院（王墓展区）",
            "台山水步镇草坪里", "同沙生态公园", "嗇色园黄大仙祠", "圭峰山国家森林公园",
            "城央绿廊", "外伶仃岛", "大佛古寺", "大夫山森林公园", "大梅沙海滨公园",
            "大澳", "天星码头", "太平山顶", "孙文西路步行街", "宝墨园", "客家婆景区",
            "川山群岛海丝遗址", "平沙岛", "广东中山翠亨国家湿地公园", "广东新会小鸟天堂国家湿地公园",
            "广东省博物馆", "广州圣心大教堂", "广州塔", "广州大学城", "广州市白云山风景区",
            "广州市长隆旅游度假区", "影汇之星8字形摩天轮", "惠州体育馆", "惠州市惠州西湖旅游景区",
            "惠州市罗浮山景区", "新濠影汇水上乐园", "旗溪生态村", "昂坪360", "星光大道",
            "景山公园", "杨梅坑", "桂山岛", "惠州植物园", "永庆坊", "江根村", "江门市东湖公园",
            "江门市开平碉楼文化旅游区", "江门船厂", "沙湾古镇", "沙面", "河口百年火车站",
            "海心沙亚运公园", "深圳市华侨城旅游度假区", "深圳市观澜湖休闲旅游区",
            "深圳平安金融中心云际观光层", "深圳欢乐谷", "深圳湾公园", "清晖园", "港珠澳大桥",
            "澳门大三巴牌坊", "澳门威尼斯人度假区", "澳门巴黎人度假区", "澳门旅游塔",
            "澳门海事博物馆", "澳门渔人码头", "火炉山森林公园", "烟桥村", "牙香街文化旅游区",
            "珠江夜游码头", "珠海太空中心", "珠海情侣路", "珠海规划馆", "珠海长隆海洋王国",
            "粤晖园", "维多利亚港", "肇庆市体育中心", "肇庆市星湖旅游景区", "花城广场",
            "莲花山旅游区", "西涌沙滩", "赤坎华侨古镇", "越秀公园", "路环村及黑沙海滩",
            "较场尾", "那琴半岛地质海洋公园", "郑观应故居", "金沙滩", "金紫荆广场",
            "金钟湖公园", "锦绣中华民俗村", "长廊生态园", "陈家祠", "雍陌村",
            "香山商业文化博物馆", "香港太空馆", "香港摩天轮", "香港故宫文化博物馆",
            "香港海洋公园", "香港迪士尼乐园", "黄埔古港"
        ]
        self.n = len(self.attraction_names)
        self._load_real_data()

    def _load_real_data(self):
        """从Excel文件加载真实的距离和时间矩阵"""
        try:
            # 读取Excel文件
            file = "大湾区景点矩阵格式.xlsx"

            # 根据列范围读取数据
            dis = pd.read_excel(file, usecols="B:DQ", header=None, skiprows=1)
            name = pd.read_excel(file, usecols="A", header=None, skiprows=1)
            times = pd.read_excel(file, usecols="DS:IH", header=None, skiprows=1)

            # 转换为numpy数组并确保是n x n的矩阵
            self.distance_matrix = dis.values[:self.n, :self.n]
            self.time_matrix = times.values[:self.n, :self.n]

            print(f"成功加载数据！距离矩阵形状: {self.distance_matrix.shape}")
            print(f"时间矩阵形状: {self.time_matrix.shape}")

            # 将对角线设置为0，避免自循环
            np.fill_diagonal(self.distance_matrix, 0)
            np.fill_diagonal(self.time_matrix, 0)

            # 打印一些样本数据用于验证
            print("距离矩阵样本（前5x5）:")
            print(self.distance_matrix[:5, :5])
            print("时间矩阵样本（前5x5）:")
            print(self.time_matrix[:5, :5])

        except Exception as e:
            print(f"加载真实数据失败: {e}")
            print("使用模拟数据作为备用...")
            self._initialize_backup_matrices()

    def _initialize_backup_matrices(self):
        """备用模拟数据"""
        np.random.seed(42)
        self.distance_matrix = np.random.randint(1000, 30000, (self.n, self.n))
        self.distance_matrix = (self.distance_matrix + self.distance_matrix.T) // 2
        np.fill_diagonal(self.distance_matrix, 0)

        self.time_matrix = (self.distance_matrix * np.random.uniform(0.08, 0.15)).astype(int)
        np.fill_diagonal(self.time_matrix, 0)
        self.time_matrix = (self.time_matrix + self.time_matrix.T) // 2

    def get_indices(self, selected_attractions: List[str]) -> List[int]:
        """获取选中景点在矩阵中的索引"""
        indices = []
        for attraction in selected_attractions:
            if attraction in self.attraction_names:
                indices.append(self.attraction_names.index(attraction))
            else:
                print(f"警告: 景点 '{attraction}' 不在预定义列表中")
        return indices

    def greedy_algorithm(self, selected_indices: List[int]) -> Dict:
        """贪婪算法实现"""
        if len(selected_indices) < 2:
            return None

        # 复制选中的索引，避免修改原列表
        unvisited = set(selected_indices.copy())
        path = [unvisited.pop()]  # 随机起点
        total_distance = 0
        total_time = 0

        while unvisited:
            current = path[-1]
            min_distance = float('inf')
            next_place = -1

            # 找到最近的未访问景点
            for candidate in unvisited:
                distance = self.distance_matrix[current, candidate]
                if distance < min_distance and distance > 0:  # 确保距离有效
                    min_distance = distance
                    next_place = candidate

            if next_place == -1:
                # 如果没有找到有效路径，随机选择一个
                next_place = unvisited.pop()
                min_distance = self.distance_matrix[current, next_place]
                if min_distance <= 0:  # 如果距离无效，设为平均距离
                    min_distance = 10000

            path.append(next_place)
            total_distance += min_distance
            total_time += self.time_matrix[current, next_place]
            unvisited.remove(next_place)

        return {
            'path': path,
            'path_names': [self.attraction_names[i] for i in path],
            'total_distance': int(total_distance),
            'total_time': int(total_time),
            'places_visited': len(path)
        }

    class ACOAlgorithm:
        def __init__(self, distance_matrix, time_matrix, n_ants=15, n_iterations=50):
            self.distances = distance_matrix
            self.times = time_matrix
            self.n = len(distance_matrix)
            self.n_ants = n_ants
            self.n_iterations = n_iterations
            self.alpha = 1.0
            self.beta = 2.0
            self.rho = 0.5
            self.q = 100

            # 初始化信息素矩阵
            self.pheromone = np.ones((self.n, self.n)) / self.n
            # 启发式信息使用距离的倒数
            self.eta = 1 / (self.distances + 1e-10)
            np.fill_diagonal(self.eta, 0)

        def run(self, selected_indices):
            if len(selected_indices) < 2:
                return None, float('inf'), float('inf')

            best_path = None
            best_distance = float('inf')
            best_time = float('inf')

            for iteration in range(self.n_iterations):
                all_paths = self._generate_paths(selected_indices)
                self._update_pheromone(all_paths)

                for path, distance, time in all_paths:
                    if distance < best_distance:
                        best_path = path
                        best_distance = distance
                        best_time = time

            return best_path, best_distance, best_time

        def _generate_paths(self, selected_indices):
            all_paths = []
            available_indices = selected_indices.copy()

            for ant in range(self.n_ants):
                path = self._construct_path(available_indices)
                if len(path) > 1:
                    distance = self._calculate_path_distance(path)
                    time = self._calculate_path_time(path)
                    all_paths.append((path, distance, time))

            return all_paths

        def _construct_path(self, selected_indices):
            if not selected_indices:
                return []

            path = [random.choice(selected_indices)]
            unvisited = set(selected_indices) - {path[0]}

            while unvisited:
                current = path[-1]
                next_point = self._select_next_point(current, unvisited)
                if next_point is None:
                    break
                path.append(next_point)
                unvisited.remove(next_point)

            return path

        def _select_next_point(self, current, unvisited):
            if not unvisited:
                return None

            probabilities = []
            valid_points = []  # 存储有效点

            for next_point in unvisited:
                # 检查距离是否有效
                if self.distances[current, next_point] > 0:  # 只保留有效距离的点
                    pheromone = self.pheromone[current, next_point] ** self.alpha
                    heuristic = self.eta[current, next_point] ** self.beta
                    probabilities.append(pheromone * heuristic)
                    valid_points.append(next_point)

            # 如果没有有效点，随机选择一个
            if not valid_points:
                return random.choice(list(unvisited))

            # 归一化概率
            total = sum(probabilities)
            probabilities = [p / total for p in probabilities]

            # 从有效点中选择
            return valid_points[np.random.choice(len(valid_points), p=probabilities)]


        def _calculate_path_distance(self, path):
            total = 0
            for i in range(len(path) - 1):
                total += self.distances[path[i], path[i + 1]]
            return total

        def _calculate_path_time(self, path):
            total = 0
            for i in range(len(path) - 1):
                total += self.times[path[i], path[i + 1]]
            return total

        def _update_pheromone(self, all_paths):
            # 信息素蒸发
            self.pheromone *= (1 - self.rho)

            # 信息素增加
            for path, distance, time in all_paths:
                if distance > 0:
                    pheromone_to_add = self.q / distance
                    for i in range(len(path) - 1):
                        self.pheromone[path[i], path[i + 1]] += pheromone_to_add

    def aco_algorithm(self, selected_indices: List[int]) -> Dict:
        """ACO算法实现"""
        if len(selected_indices) < 2:
            return None

        aco = self.ACOAlgorithm(self.distance_matrix, self.time_matrix)
        best_path, best_distance, best_time = aco.run(selected_indices)

        if best_path is None or len(best_path) < 2:
            return None

        return {
            'path': best_path,
            'path_names': [self.attraction_names[i] for i in best_path],
            'total_distance': int(best_distance),
            'total_time': int(best_time),
            'places_visited': len(best_path)
        }

    def dynamic_programming(self, selected_indices: List[int]) -> Dict:
        """动态规划算法实现（适用于景点数量较少的情况，通常少于20个）"""
        n = len(selected_indices)
        if n < 2:
            return None
        if n > 20:  # 限制景点数量，避免计算量过大
            return None

        # 创建索引到原始索引的映射
        index_map = {i: selected_indices[i] for i in range(n)}

        # 初始化距离矩阵
        dist = np.zeros((n, n))
        time = np.zeros((n, n))
        for i in range(n):
            for j in range(n):
                if i != j:
                    dist[i][j] = self.distance_matrix[index_map[i]][index_map[j]]
                    time[i][j] = self.time_matrix[index_map[i]][index_map[j]]

        # DP状态定义: dp[mask][u] = (最小距离, 前一个节点)
        size = 1 << n
        INF = float('inf')
        dp = [[(INF, -1) for _ in range(n)] for _ in range(size)]

        # 初始化起点
        for i in range(n):
            dp[1 << i][i] = (0, -1)

        # 填充DP表
        for mask in range(size):
            for u in range(n):
                if not (mask & (1 << u)):
                    continue
                current_dist, _ = dp[mask][u]
                if current_dist == INF:
                    continue

                # 尝试访问所有未访问的节点
                for v in range(n):
                    if mask & (1 << v):
                        continue
                    new_mask = mask | (1 << v)
                    new_dist = current_dist + dist[u][v]
                    if new_dist < dp[new_mask][v][0]:
                        dp[new_mask][v] = (new_dist, u)

        # 找到最优路径
        full_mask = (1 << n) - 1
        min_total_dist = INF
        end_node = -1
        for u in range(n):
            if dp[full_mask][u][0] < min_total_dist:
                min_total_dist = dp[full_mask][u][0]
                end_node = u

        # 回溯构建路径
        path = []
        current_mask = full_mask
        current_node = end_node
        while current_node != -1:
            path.append(current_node)
            _, prev_node = dp[current_mask][current_node]
            current_mask &= ~(1 << current_node)
            current_node = prev_node

        path.reverse()
        # 转换回原始索引
        original_path = [index_map[i] for i in path]

        # 计算总时间
        total_time = 0
        for i in range(len(original_path) - 1):
            total_time += self.time_matrix[original_path[i]][original_path[i + 1]]

        return {
            'path': original_path,
            'path_names': [self.attraction_names[i] for i in original_path],
            'total_distance': int(min_total_dist),
            'total_time': int(total_time),
            'places_visited': len(original_path)
        }

    class GeneticAlgorithm:
        def __init__(self, distance_matrix, time_matrix, pop_size=50, generations=100, mutation_rate=0.02):
            self.distances = distance_matrix
            self.times = time_matrix
            self.pop_size = pop_size
            self.generations = generations
            self.mutation_rate = mutation_rate

        def _create_individual(self, indices):
            """创建一个个体（随机排列）"""
            return random.sample(indices, len(indices))

        def _calculate_fitness(self, individual):
            """计算适应度（路径总距离的倒数）"""
            total_distance = 0
            total_time = 0
            for i in range(len(individual) - 1):
                total_distance += self.distances[individual[i]][individual[i + 1]]
                total_time += self.times[individual[i]][individual[i + 1]]
            return 1 / (total_distance + 1e-10), total_distance, total_time

        def _select_parents(self, population, fitnesses):
            """选择父母（轮盘赌选择）"""
            total_fitness = sum(fitnesses)
            probabilities = [f / total_fitness for f in fitnesses]
            parent1 = random.choices(population, probabilities)[0]
            parent2 = random.choices(population, probabilities)[0]
            return parent1, parent2

        def _crossover(self, parent1, parent2):
            """交叉操作（部分映射交叉）"""
            size = len(parent1)
            a, b = random.sample(range(size), 2)
            if a > b:
                a, b = b, a

            child = [None] * size
            # 复制父母1的中间部分
            child[a:b + 1] = parent1[a:b + 1]

            # 填充剩余部分
            ptr = b + 1
            for gene in parent2[b + 1:] + parent2[:b + 1]:
                if ptr >= size:
                    ptr = 0
                if gene not in child:
                    child[ptr] = gene
                    ptr += 1
            return child

        def _mutate(self, individual):
            """变异操作（交换两个基因）"""
            if random.random() < self.mutation_rate:
                i, j = random.sample(range(len(individual)), 2)
                individual[i], individual[j] = individual[j], individual[i]
            return individual

        def run(self, selected_indices):
            if len(selected_indices) < 2:
                return None, float('inf'), float('inf')

            # 初始化种群
            population = [self._create_individual(selected_indices) for _ in range(self.pop_size)]

            best_fitness = 0
            best_path = None
            best_distance = float('inf')
            best_time = float('inf')

            for _ in range(self.generations):
                # 计算适应度
                fitnesses = []
                distances = []
                times = []
                for individual in population:
                    f, d, t = self._calculate_fitness(individual)
                    fitnesses.append(f)
                    distances.append(d)
                    times.append(t)

                # 记录最佳个体
                current_best_idx = np.argmax(fitnesses)
                if fitnesses[current_best_idx] > best_fitness:
                    best_fitness = fitnesses[current_best_idx]
                    best_path = population[current_best_idx]
                    best_distance = distances[current_best_idx]
                    best_time = times[current_best_idx]

                # 创建下一代
                new_population = []
                for _ in range(self.pop_size):
                    parent1, parent2 = self._select_parents(population, fitnesses)
                    child = self._crossover(parent1, parent2)
                    child = self._mutate(child)
                    new_population.append(child)

                population = new_population

            return best_path, best_distance, best_time

    def genetic_algorithm(self, selected_indices: List[int]) -> Dict:
        """遗传算法实现"""
        if len(selected_indices) < 2:
            return None

        ga = self.GeneticAlgorithm(self.distance_matrix, self.time_matrix)
        best_path, best_distance, best_time = ga.run(selected_indices)

        if best_path is None or len(best_path) < 2:
            return None

        return {
            'path': best_path,
            'path_names': [self.attraction_names[i] for i in best_path],
            'total_distance': int(best_distance),
            'total_time': int(best_time),
            'places_visited': len(best_path)
        }


# 初始化路径规划器
planner = PathPlanner()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/calculate-path', methods=['POST'])
def calculate_path():
    try:
        data = request.get_json()
        selected_attractions = data.get('attractions', [])
        algorithm = data.get('algorithm', 'greedy')

        print(f"收到请求 - 景点: {selected_attractions}, 算法: {algorithm}")

        if len(selected_attractions) < 2:
            return jsonify({
                'success': False,
                'error': '请至少选择2个景点'
            })

        # 获取选中景点的索引
        selected_indices = planner.get_indices(selected_attractions)

        print(f"对应的索引: {selected_indices}")

        if len(selected_indices) != len(selected_attractions):
            return jsonify({
                'success': False,
                'error': '部分景点名称不匹配'
            })

        # 根据算法选择路径规划方法
        if algorithm == 'greedy':
            result = planner.greedy_algorithm(selected_indices)
        elif algorithm == 'aco':
            result = planner.aco_algorithm(selected_indices)
        elif algorithm == 'dp':
            if len(selected_indices) > 20:
                return jsonify({
                    'success': False,
                    'error': '动态规划算法适用于20个以内的景点'
                })
            result = planner.dynamic_programming(selected_indices)
        elif algorithm == 'genetic':
            result = planner.genetic_algorithm(selected_indices)
        else:
            return jsonify({
                'success': False,
                'error': '未知算法'
            })

        if result:
            print(f"规划结果 - 路径: {result['path_names']}")
            print(f"总距离: {result['total_distance']}公里, 总时间: {result['total_time']}分钟")

            return jsonify({
                'success': True,
                **result
            })
        else:
            return jsonify({
                'success': False,
                'error': '路径规划失败，请尝试选择其他景点'
            })

    except Exception as e:
        print(f"服务器错误: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'服务器错误: {str(e)}'
        })


@app.route('/attractions', methods=['GET'])
def get_attractions():
    """获取所有景点列表的API"""
    return jsonify({
        'success': True,
        'attractions': planner.attraction_names
    })


if __name__ == '__main__':
    # 检查数据文件是否存在
    if not os.path.exists('大湾区景点矩阵格式.xlsx'):
        print("警告: 大湾区景点矩阵格式.xlsx 文件不存在，将使用模拟数据")

    app.run(debug=True, host='0.0.0.0', port=5000)