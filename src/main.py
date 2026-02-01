from dependencies import Dependencies
from parameters import PhoneParameterEstimator
import math
import json

#Dependencies.get_installation_status()

np=Dependencies.get_numpy()
plt=Dependencies.get_plt()
sympy=Dependencies.get_sympy()
scipy=Dependencies.get_scipy()
from scipy.integrate import quad

specs={
    'name': 'iPhone 14 Pro',
    'screen': {'type': 'OLED', 'size': 6.1, 'max_brightness': 2000},
    'chip': {'name': 'A16'},
    'network': {'type': '5G_SA', 'max_bandwidth': 1000},
    'cooling': 'passive_advanced',
    'os': 'iOS',
    'battery': {'capacity': 3200, 'chemistry': 'Lipo'}
}
total_Capacity=specs['battery']['capacity']
params=PhoneParameterEstimator(specs).estimate_all_parameters()

def voltage(SOC):
    SOC_pct = SOC / 100.0
    
    if SOC_pct <= 0:
        return 3.0
    
    if SOC_pct >= 0.95:
        x = SOC_pct - 0.95
        return 4.05 + 0.15 * (1 - 5*x)
    elif SOC_pct >= 0.2:
        return 3.70 + 0.35 * (SOC_pct - 0.2) / 0.75
    elif SOC_pct >= 0.1:
        return 3.50 + 0.20 * (SOC_pct - 0.1) / 0.1
    else:
        return 3.00 + 0.50 * (SOC_pct / 0.1)
    
def power_scene(scene,params):
    p_total=0
    P_s=params['baseline']['P_s']
    P_c=params['baseline']['P_c'][scene]
    P_n=params['baseline']['P_n']
    for e in ['s','n','g','b']:
        p_single='P_'+e
        power=params['coefficients'][scene][e]*params['baseline'][p_single]
        p_total+=power
    p_total+=params['coefficients'][scene]['c']*P_c
    p_total*=(1+params['coupling'][scene])
    return p_total
    
def C_eff(SOC,T,C_0=total_Capacity):
    def f_T(T):
        T_0=298.15
        T_c=278.15
        delta_T=4
        alpha_T=0.001
        r=(1-alpha_T*(T-T_0)**2)/(1+math.exp(-(T-T_c)/(delta_T))) if T<T_0 else 1
        return r
    def f_SOC(SOC):
        SOC_val = SOC
        if SOC_val <= 0:
            return 0.8
        def V(s):
            s_pct = s / 100.0
            if s_pct >= 0.95:
                x = s_pct - 0.95
                return 4.05 + 0.15 * (1 - 5*x)
            elif s_pct >= 0.2:
                return 3.70 + 0.35 * (s_pct - 0.2) / 0.75
            elif s_pct >= 0.1:
                return 3.50 + 0.20 * (s_pct - 0.1) / 0.1
            else:
                return 3.00 + 0.50 * (s_pct / 0.1)
        integral, error = quad(V, 0, SOC_val)
        
        V_nom = 3.7
        if SOC_val > 0:
            f = integral / (V_nom * SOC_val)
        else:
            f = 1.0
    
        return max(0.7, min(1.0, f))
    return C_0*f_T(T)*f_SOC(SOC)*1.0

def SOC(t:float,dt:float=600,SOC_0:float=100,T:float=298.15,scene='B',params=params):
    n_steps=int(t/dt)+1
    soc_values=[SOC_0]
    def I(SOC,scene='B'):
        P_total=power_scene(scene,params)
        V=voltage(SOC)
        return 1000*P_total/V

    for i in range(1,n_steps):
        t_curr=dt*i
        SOC_curr=soc_values[i-1]
        C_eff_mAh=C_eff(SOC_curr,T,C_0=3200)

        I_mA=I(SOC_curr,scene)

        dSOC=-100*(I_mA*dt/3600)/C_eff_mAh

        soc_new=SOC_curr+dSOC
        soc_values.append(max(0,min(100,soc_new)))
    return soc_values

print(json.dumps(params,indent=2))
# 测试不同场景
scenes = ['B', 'V', 'G','M']
scene_names = ['浏览', '视频', '游戏','Moderate']

for scene, name in zip(scenes, scene_names):
    soc_vals = SOC(t=15*3600, dt=300, SOC_0=100,T=298.15, scene=scene)
    
    # 找到放空时间
    empty_time = None
    for i, soc in enumerate(soc_vals):
        if soc <= 1:  # 小于1%认为放空
            empty_time = i * 300 / 3600  # 小时
            break

    print(f"{name}场景：")
    print(f"  总续航：{empty_time:.1f}小时")
    
