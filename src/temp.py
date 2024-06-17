import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False




# 电网总投入数据（亿元）
total_investment = 30000

# 国家电网投入数据（亿元）
state_grid_investment = 22300

# 南方电网投入数据（亿元）
southern_grid_investment = 6700

# 计算投资占比
state_grid_percentage = (state_grid_investment / total_investment) * 100
southern_grid_percentage = (southern_grid_investment / total_investment) * 100

# 饼图标签
labels = ['国家电网', '南方电网']

# 饼图数据
sizes = [state_grid_percentage, southern_grid_percentage]

# 饼图颜色
colors = ['#1f497d', '#add8e6']

# 绘制饼图
plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)

# 添加标题
plt.title('电网总投入占比')

# 显示图形
plt.show()

