## CFLP 问题

现有客人 $n$ 位，工厂 $m$ 座，每个客人都有自己的服务需求，每个工厂都能提供一定数量的服务，每个客人到每座工厂都需要一定的费用，工厂刚开始是关闭的，开工厂也要付出一定的费用。现在要求： **求能满足所有客户的需求的最小代价分配方案**。

以上问题可以用数学公式表达：

$$y_i=\begin{cases}1&\text{if facility }i\text{ is opened}\\0&\text{otherwise}\end{cases}$$

$$x_{ij}=\begin{cases}1&\text{if facility }i\text{ serves customer }j\\0&\text{otherwise}\end{cases}$$

$$v^*=\min\sum^m_{i=1}\sum^n_{j=1}c_{ij}x_{ij}+\sum^m_{i=1}f_iy_i$$

$$\text{s.t.}\ \sum_n^{j=1}a_jx_{ij}\le b_iy_i \ \forall i,$$

$$\sum_{i=1}^mx_{ij}=1\ \forall j,$$

$$x_{ij}-y_i\le0\ \forall i,j,$$

$$x_{ij}\in\{0,1\}\ \forall i, j,$$

$$y_i\in\{0,1\}\ \forall i,$$

其中，$a_j$ 为第 $j$ 位顾客的需求，$b_i$ 为第 $i$ 座工厂的容量，$f_i$ 为开第 $i$ 座工厂的费用，$c_{ij}$ 为将第 $j$ 位顾客分配到 $i$

 座工厂的费用。在实际编程中，我直接将 $x_{ij}$ 简化为 $${x_j}$$。