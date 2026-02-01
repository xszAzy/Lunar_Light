import numpy as np
from scipy.optimize import least_squares

def solve_power_from_runtime(runtime_B, runtime_V, runtime_G, runtime_M, 
                             battery_capacity=3700, voltage_avg=3.8):
    """
    从续航时间反推基准功率
    runtime_X: 各场景续航时间（小时）
    """
    # 电池总能量（Wh）
    E_total = battery_capacity * voltage_avg / 1000
    
    # 各场景平均功率
    P_B_est = E_total / runtime_B
    P_V_est = E_total / runtime_V
    P_G_est = E_total / runtime_G
    P_M_est = E_total / runtime_M
    
    print(f"估算的各场景功率：")
    print(f"  P_B ≈ {P_B_est:.2f} W")
    print(f"  P_V ≈ {P_V_est:.2f} W")
    print(f"  P_G ≈ {P_G_est:.2f} W")
    print(f"  P_M ≈ {P_M_est:.2f} W")
    
    # 定义残差函数（非线性最小二乘）
    def residuals(params):
        P_s, P_c, P_n, P_g, P_b = params
        
        # 计算各场景功率
        P_B_calc = 0.7*P_s + 0.5*P_c + 0.3*P_n + 0.2*P_g + P_b + 0.0075*P_c*P_n
        P_V_calc = 1.0*P_s + 0.4*P_c + 1.0*P_n + 1.1*P_b + 0.012*P_s*P_c
        P_G_calc = 1.2*P_s + 1.0*P_c + 0.4*P_n + 0.5*P_g + 0.9*P_b + 0.048*P_s*P_c
        P_M_calc = 0.9*P_s + 0.7*P_c + 0.6*P_n + 0.3*P_g + P_b + 0.0126*P_c*P_n + 0.0126*P_s*P_c
        
        return [
            P_B_calc - P_B_est,
            P_V_calc - P_V_est,
            P_G_calc - P_G_est,
            P_M_calc - P_M_est,
            # 可添加约束：所有功率 > 0
            P_s - 0.1,  # 约束：P_s >= 0.1
            P_c - 0.5,  # 约束：P_c >= 0.5
        ]
    
    # 初始猜测
    initial_guess = [0.5, 2.0, 1.0, 0.3, 0.2]
    
    # 求解
    result = least_squares(residuals, initial_guess, bounds=(0, 10))
    
    if result.success:
        P_s, P_c, P_n, P_g, P_b = result.x
        print(f"\n求解的基准功率：")
        print(f"  P_s(屏幕) = {P_s:.3f} W")
        print(f"  P_c(CPU)  = {P_c:.3f} W")
        print(f"  P_n(网络) = {P_n:.3f} W")
        print(f"  P_g(GPS)  = {P_g:.3f} W")
        print(f"  P_b(后台) = {P_b:.3f} W")
        
        # 验证
        print(f"\n验证（计算值 vs 估算值）：")
        P_B_calc = 0.7*P_s + 0.5*P_c + 0.3*P_n + 0.2*P_g + P_b + 0.0075*P_c*P_n
        P_V_calc = 1.0*P_s + 0.4*P_c + 1.0*P_n + 1.1*P_b + 0.012*P_s*P_c
        P_G_calc = 1.2*P_s + 1.0*P_c + 0.4*P_n + 0.5*P_g + 0.9*P_b + 0.048*P_s*P_c
        P_M_calc = 0.9*P_s + 0.7*P_c + 0.6*P_n + 0.3*P_g + P_b + 0.0126*P_c*P_n + 0.0126*P_s*P_c
        
        print(f"  P_B: {P_B_calc:.3f} W (估算: {P_B_est:.3f} W)")
        print(f"  P_V: {P_V_calc:.3f} W (估算: {P_V_est:.3f} W)")
        print(f"  P_G: {P_G_calc:.3f} W (估算: {P_G_est:.3f} W)")
        print(f"  P_M: {P_M_calc:.3f} W (估算: {P_M_est:.3f} W)")
        
        return result.x
    else:
        print("求解失败！")
        return None

# 示例：假设某手机实测续航
# iPhone 14 Pro 实测数据（假设）
solve_power_from_runtime(
    runtime_B=12.0,  # 浏览12小时
    runtime_V=8.5,   # 视频8.5小时
    runtime_G=5.0,   # 游戏5小时
    runtime_M=9.0,   # 综合9小时
    battery_capacity=3200,
    voltage_avg=3.85
)
