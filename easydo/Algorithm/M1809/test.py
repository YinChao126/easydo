import matplotlib.pyplot as plt
import numpy as np

# 从[-1,1]中等距去50个数作为x的取值
x = [0, 1, 2, 3]
y = [5, 6, 8, 9]
# 第一个是横坐标的值，第二个是纵坐标的值
plt.plot(x, y, 'g--')
# 必要方法，用于将设置好的figure对象显示出来
plt.show()