# Parameter Optimization System

## 系统概述

这套系统用于系统化地测试和优化交易策略参数：

1. **optimization_db.py** - SQLite数据库，存储所有测试结果
2. **optimize_parameters.py** - 自动化参数测试运行器
3. **analyze_results.py** - 结果分析和可视化工具

## 快速开始

### 1. 运行快速测试套件（推荐）

测试5个精心挑选的参数组合：

```powershell
python optimize_parameters.py quick
```

### 2. 运行完整网格搜索

测试所有参数组合（可能需要数小时）：

```powershell
python optimize_parameters.py grid
```

### 3. 分析结果

查看所有测试结果的完整分析：

```powershell
python analyze_results.py
```

查看满足比赛要求的结果（>30%收益，<50%回撤，≥10笔交易）：

```powershell
python analyze_results.py requirements
```

比较特定参数的影响：

```powershell
python analyze_results.py compare max_position_size
python analyze_results.py compare take_profit_pct
python analyze_results.py compare min_time_between_trades
```

## 数据库结构

### 存储的参数
- 策略参数：max_position_size, stop_loss_pct, take_profit_pct
- RSI参数：rsi_oversold, rsi_overbought, rsi_period
- MACD参数：macd_fast, macd_slow, macd_signal
- BB参数：bb_period, bb_std_dev
- 风险管理：max_drawdown_limit, min_time_between_trades

### 存储的结果
- BTC表现：回报率、回撤、交易数、胜率
- ETH表现：回报率、回撤、交易数、胜率
- 综合表现：总回报、平均回撤、总交易数
- 评分：综合评分（考虑收益、风险和交易频率）

## 评分系统

总分 = 收益分 (60%) + 回撤分 (30%) + 交易频率分 (10%)

- **收益分**：30%收益 = 60分（满分）
- **回撤分**：0%回撤 = 30分，10%回撤 = 0分
- **交易频率分**：50-200笔交易 = 10分（最优）

## 使用示例

### 自定义参数测试

```python
from optimize_parameters import ParameterOptimizer

optimizer = ParameterOptimizer()

# 测试单个参数组合
params = {
    'max_position_size': 0.90,
    'stop_loss_pct': 8.0,
    'take_profit_pct': 40.0,
    'rsi_oversold': 35,
    'rsi_overbought': 75,
    'min_time_between_trades': 2880
}
optimizer.test_parameter_set(params, "Manual test")

# 显示前10个结果
optimizer.show_top_results(10)
optimizer.close()
```

### 自定义网格搜索

```python
from optimize_parameters import ParameterOptimizer

optimizer = ParameterOptimizer()

# 定义要测试的参数范围
param_grid = {
    'max_position_size': [0.85, 0.90, 0.95],
    'take_profit_pct': [35.0, 40.0, 45.0],
    'min_time_between_trades': [2160, 2880, 3600]
}

optimizer.grid_search(param_grid)
optimizer.close()
```

### 随机搜索

```python
from optimize_parameters import ParameterOptimizer

optimizer = ParameterOptimizer()

# 定义参数范围（最小值，最大值）
param_ranges = {
    'max_position_size': (0.7, 0.95),
    'stop_loss_pct': (5.0, 12.0),
    'take_profit_pct': (25.0, 60.0),
    'min_time_between_trades': (720, 4320)
}

# 随机测试50个组合
optimizer.random_search(param_ranges, n_iterations=50)
optimizer.close()
```

## 输出文件

- **optimization_results.db** - SQLite数据库，包含所有测试结果
- **optimization_results.csv** - CSV导出，便于Excel分析
- **best_config.json** - 最佳参数配置（由analyze_results.py生成）

## 工作流程

1. **运行测试**：`python optimize_parameters.py quick`
2. **分析结果**：`python analyze_results.py`
3. **选择最佳配置**：查看best_config.json
4. **更新策略**：将最佳参数复制到config.json
5. **验证**：`python backtest_historical.py`
6. **继续优化**：运行更多测试或调整参数范围

## 注意事项

1. **重复测试检测**：系统会自动跳过已测试的参数组合
2. **时间估算**：每次回测约需10-30秒，规划好测试时间
3. **数据库备份**：定期备份optimization_results.db
4. **参数相关性**：某些参数组合可能不合理（如极高止损+极低目标）

## 高级用法

### 导出数据到Excel进行分析

```python
from optimization_db import OptimizationDB

db = OptimizationDB()
db.export_to_csv("my_results.csv")
db.close()
```

然后在Excel中：
- 创建数据透视表分析参数影响
- 绘制散点图（收益 vs 回撤）
- 识别最优参数区间

### 查询特定条件的结果

```python
from optimization_db import OptimizationDB

db = OptimizationDB()

# 获取收益>20%且回撤<5%的所有结果
cursor = db.conn.cursor()
cursor.execute("""
    SELECT * FROM backtest_results
    WHERE combined_return > 20 AND avg_drawdown < 5
    ORDER BY score DESC
""")

results = cursor.fetchall()
print(f"Found {len(results)} matching results")

db.close()
```

## 故障排除

**问题：回测失败**
- 确保backtest_historical.py可以正常运行
- 检查config.json格式正确

**问题：数据库锁定**
- 关闭所有使用数据库的程序
- 删除optimization_results.db-journal文件

**问题：结果解析失败**
- 检查backtest_historical.py的输出格式
- 查看optimize_parameters.py中的正则表达式

## 目标

找到满足以下条件的参数组合：
- ✅ 综合收益率 > 30%
- ✅ 平均最大回撤 < 50%（目标 < 20%）
- ✅ 总交易数 ≥ 10（目标 50-200）
- ✅ 胜率 > 50%

祝你找到最优参数组合！🚀
