from dependencies import Dependencies
import math

#Dependencies.get_installation_status()

np=Dependencies.get_numpy()
plt=Dependencies.get_plt()
sympy=Dependencies.get_sympy()
scipy=Dependencies.get_scipy()
from scipy.integrate import quad

total_Capacity=3700

def voltage(SOC):
    '''
    SOC_pct=SOC/100
    if SOC_pct<0.3:
        r=3.7-1.0*(0.3-SOC_pct)
    else:
        r=4.2-0.5*math.exp(-5*SOC_pct)
    return r
'''
    SOC_pct = SOC/100
    if SOC_pct <= 0:
        return 3.3
    elif SOC_pct < 0.2:
        return 3.6 - 0.5*(0.2 - SOC_pct)
    elif SOC_pct < 0.5:
        return 4.0 - 0.4*(0.5 - SOC_pct)
    elif SOC_pct < 0.8:
        return 4.15 - 0.15*(0.8 - SOC_pct)
    else:
        return 4.2 - 0.05*(1.0 - SOC_pct)
        
def power_scene(scene,P_s=0.3,P_c=1.0,P_n=0.6,P_g=0.2,P_b=0.1):
    if scene=='B':
        return 0.7*P_s+0.5*P_c+0.3*P_n+0.2*P_g+1.0*P_b+0.0075*P_c*P_n
    elif scene=='V':
        return 1.0*P_s+0.4*P_c+1.0*P_n+0.0*P_g+1.1*P_b+0.0120*P_s*P_c
    elif scene=='G':
        return 1.2*P_s+1.0*P_c+0.4*P_n+0.5*P_g+0.9*P_b+0.0480*P_s*P_c
    elif scene=='M':
        return 0.9*P_s+0.7*P_c+0.6*P_n+0.3*P_g+1.0*P_b+0.0126*P_c*P_n+0.0126*P_s*P_c
    else:
        raise ValueError("Unknown scene")
    
def I(SOC,scene='B'):
    P_total=power_scene(scene)
    V=voltage(SOC)
    return 1000*P_total/V
def f_T(T):
    T_0=298.15
    T_c=278.15
    delta_T=4
    alpha_T=0.001
    r=(1-alpha_T*(T-T_0)**2)/(1+math.exp(-(T-T_c)/(delta_T))) if T<T_0 else 1
    return r
def f_SOC(SOC):
    SOC_pct = SOC/100
    if SOC_pct <= 0:
        return 0.75
    elif SOC_pct >= 1.0:
        return 1.00
    elif SOC_pct >= 0.9:
        return 1.00
    elif SOC_pct >= 0.7:
        return 0.95 + 0.05*(SOC_pct - 0.7)/0.2
    elif SOC_pct >= 0.4:
        return 0.85 + 0.10*(SOC_pct - 0.4)/0.3
    elif SOC_pct >= 0.1:
        return 0.80 + 0.05*(SOC_pct - 0.1)/0.3
    else:
        return 0.75 + 0.05*(SOC_pct/0.1)
    
def C_eff(SOC,T,C_0=total_Capacity):
    return C_0*f_T(T)*f_SOC(SOC)*1.0

def consumption(SOC,t):
    x=sympy.symbols('x')
    r=sympy.integrate(I(SOC,t),(x,0,t))
    return r

def SOC(t:float,dt:float=600,SOC_0:float=100,T:float=298.15,scene='B'):
    n_steps=int(t/dt)+1
    soc_values=[SOC_0]

    for i in range(1,n_steps):
        t_curr=dt*i
        SOC_curr=soc_values[i-1]
        C_eff_mAh=C_eff(SOC_curr,T)

        I_mA=I(SOC_curr)

        dSOC=-100*(I_mA*dt/3600)/C_eff_mAh

        soc_new=SOC_curr+dSOC
        soc_values.append(max(0,min(100,soc_new)))
    return soc_values

if __name__ == "__main__":
    print("=== 增强非线性模型测试 ===")
    
    # 测试5小时放电
    soc_vals = SOC(t=15*3600, dt=300, SOC_0=100, scene='B')
    
    print("时间(小时)  SOC(%)  每30分钟下降")
    print("-" * 40)
    
    # 每30分钟输出（dt=300秒=5分钟，6个点=30分钟）
    for i in range(0, len(soc_vals), 6):
        if i < len(soc_vals):
            t_hour = i * 5 / 60  # 5分钟一个点
            soc = soc_vals[i]
            
            if i == 0:
                print(f"{t_hour:6.1f}      {soc:6.2f}%")
            else:
                prev_soc = soc_vals[i-6]
                drop = prev_soc - soc
                print(f"{t_hour:6.1f}      {soc:6.2f}%    {drop:6.2f}%")
