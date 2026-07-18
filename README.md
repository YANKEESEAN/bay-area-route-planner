# bay-area-route-planner

An intelligent tourism route planning system for the Guangdong–Hong Kong–Macao Greater Bay Area (GBA).

The project integrates multiple path optimization algorithms, including Greedy Algorithm, Ant Colony Optimization (ACO), Genetic Algorithm (GA), and Dynamic Programming (DP), to generate efficient multi-destination travel routes for self-driving tourism.

---

## Features

- Multi-attraction route planning
- Greedy Algorithm
- Ant Colony Optimization (ACO)
- Genetic Algorithm (GA)
- Dynamic Programming (DP)
- Interactive map visualization based on AMap API
- Route distance and travel time calculation
- Local route storage
- Route sharing support
- Greater Bay Area tourism attraction database

The system is designed to solve the route optimization problem for multi-destination tourism scenarios in the Greater Bay Area.

---

## Technology Stack

### Frontend

- HTML5
- Tailwind CSS
- JavaScript
- AMap API

### Backend

- Python
- Flask

### Data Processing

- Pandas
- NumPy

The project uses Flask as the backend service and AMap API for route visualization.

---

## Project Structure

```text
bay-area-route-planner/
│
├── templates/
│   └── index.html          # Frontend page
│
├── app.py                  # Flask application
├── compare.py              # Algorithm comparison module
├── drive_matrix.py         # Distance & time matrix processing
├── locations.py            # Attraction information
│
└── README.md
```

---

## Algorithms

### Greedy Algorithm

Fast nearest-neighbor route generation.

### Ant Colony Optimization (ACO)

Uses pheromone-based search to approximate the global optimal route.

### Dynamic Programming (DP)

Provides exact solutions for small-scale route planning problems.

### Genetic Algorithm (GA)

Applies evolutionary optimization to improve route quality.

The system allows users to choose different algorithms according to route scale and optimization requirements. 

---

## Installation

### Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/bay-area-route-planner.git
cd bay-area-route-planner
```

### Install Dependencies

```bash
pip install flask pandas numpy
```

---

## Run

```bash
python app.py
```

Open your browser:

```text
http://127.0.0.1:5000
```

---

## Highlights

* Multi-algorithm optimization framework
* Interactive map visualization
* Route persistence with LocalStorage
* Social sharing support
* Cross-city tourism planning

The project forms a complete workflow from attraction selection to route planning, storage, and sharing. 

---

## Future Work

* Real-time traffic integration
* Personalized route recommendation
* Simulated Annealing optimization
* Particle Swarm Optimization (PSO)
* Multi-language support

---

## License

MIT License


---

# 粤港澳大湾区智游路径优化系统

基于多启发式算法的旅游路径规划引擎。

本项目面向粤港澳大湾区旅游场景，通过整合贪婪算法（Greedy）、蚁群算法（ACO）、遗传算法（GA）以及动态规划（DP）等多种优化算法，实现多景点旅游路线的智能规划与可视化展示。

---

## 项目简介

粤港澳大湾区拥有丰富的旅游资源和复杂的跨城市交通网络。

针对传统旅游规划中存在的路线绕行、耗时过长以及决策效率低等问题，本系统通过路径优化算法自动生成高效旅游路线，帮助用户快速完成行程规划。

---

## 功能特点

- 大湾区景点选择与筛选
- 多算法路径规划
  - 贪婪算法（Greedy）
  - 蚁群算法（ACO）
  - 遗传算法（GA）
  - 动态规划（DP）
- 高德地图路径可视化
- 总距离与总时间统计
- 路径本地存储
- 路径分享功能
- 景点详情展示

---

## 技术栈

### 前端

- HTML5
- Tailwind CSS
- JavaScript
- 高德地图 API

### 后端

- Python Flask

### 数据处理

- Pandas
- NumPy

系统采用 Flask 构建后端服务，并结合高德地图实现路线可视化。

---

## 项目结构

```text
bay-area-route-planner/
│
├── templates/
│   └── index.html          # 前端页面
│
├── app.py                  # Flask主程序
├── compare.py              # 算法性能对比模块
├── drive_matrix.py         # 距离/时间矩阵处理
├── locations.py            # 景点数据管理
│
└── README.md
```

---

## 核心算法

### 贪婪算法（Greedy）

采用最近邻策略快速生成路径。

### 蚁群算法（ACO）

利用信息素机制搜索近似全局最优路径。

### 动态规划（DP）

适用于小规模景点集合，可获得精确最优解。

### 遗传算法（GA）

通过遗传进化机制优化路径结果。

算法设计基于旅行商问题（TSP）变体实现。 

---

## 安装依赖

```bash
pip install flask pandas numpy
```

---

## 运行项目

```bash
python app.py
```

浏览器访问：

```text
http://127.0.0.1:5000
```

---

## 项目亮点

* 四种路径优化算法协同工作
* 高德地图可视化展示
* 路径本地持久化存储
* 支持社交分享
* 跨城市旅游规划

项目形成了“景点选择 → 路径规划 → 保存 → 分享”的完整用户闭环。 

---

## 未来展望

* 引入实时交通数据
* 个性化路径推荐
* 增加模拟退火算法
* 增加粒子群优化算法
* 多语言支持

---

## 开源协议

MIT License
