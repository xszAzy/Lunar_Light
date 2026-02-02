import math
import numpy as np

class Aging:
    def __init__(self,battery_type='Lipo'):
        self.battery_type=battery_type
        self.AGING_PARAMS={'Lipo': {  # 锂聚合物电池（手机常用）
                'cycle_life': 500,  # 循环寿命（80%容量保持）
                'calendar_life': 5,  # 日历寿命（年，25°C下）
                'T_ref': 298.15,     # 参考温度(K)
                'Q10_temp': 2.0,     # 温度系数（每升高10°C老化加倍）
                'stress_SOC_high': 0.9,   # 高SOC应力阈值
                'stress_SOC_low': 0.2,    # 低SOC应力阈值
                'stress_temp_high': 318.15, # 高温应力阈值(45°C)
                'stress_temp_low': 273.15   # 低温应力阈值(0°C)
            },
                           'LiFePO4': {  # 磷酸铁锂
                'cycle_life': 2000,
                'calendar_life': 10,
                'T_ref': 298.15,
                'Q10_temp': 1.8,
                'stress_SOC_high': 0.95,
                'stress_SOC_low': 0.1,
                'stress_temp_high': 323.15,
                'stress_temp_low': 263.15
            }
        }
        
        self.params = self.AGING_PARAMS.get(battery_type, self.AGING_PARAMS['Lipo'])
        
    def capacity_degradation(self, age_days, cycles_completed, avg_SOC, avg_temp, DOD_avg):
        """
        综合计算电池容量衰减
        参数:
            age_days: 使用天数
            cycles_completed: 完成的循环次数
            avg_SOC: 平均SOC（0-1）
            avg_temp: 平均温度(K)
            DOD_avg: 平均放电深度（0-1）
        返回:
            容量保持率（0-1）
        """
        # 1. 日历衰减（时间相关）
        calendar_loss = self.calendar_aging(age_days, avg_SOC, avg_temp)
        
        # 2. 循环衰减（充放电相关）
        cycle_loss = self.cycle_aging(cycles_completed, DOD_avg, avg_temp)
        
        # 3. 总容量保持率（相乘模型）
        total_retention = (1 - calendar_loss) * (1 - cycle_loss)
        
        # 防止负值
        return max(0.0, min(1.0, total_retention))
    
    def calendar_aging(self, age_days, avg_SOC, avg_temp):
        """
        日历老化（时间依赖）
        公式：Q_loss = A * t^n * exp(-Ea/RT) * f(SOC)
        """
        # 基准老化率（每年衰减百分比，25°C，50% SOC）
        base_rate_per_year = 0.05  # 5%/年
        
        # 转换为天数
        base_rate_per_day = 1 - (1 - base_rate_per_year) ** (1/365)
        
        # 时间指数（通常0.5-0.75）
        time_exponent = 0.7
        
        # 温度加速因子（阿伦尼乌斯方程）
        Ea = 50000  # 活化能(J/mol)
        R = 8.314   # 气体常数
        
        T_ref = self.params['T_ref']
        temp_acceleration = math.exp(
            Ea/R * (1/T_ref - 1/avg_temp)
        ) if avg_temp > 0 else 1.0
        
        # SOC应力因子（高SOC加速老化）
        soc_stress = 1.0
        soc_deviation = abs(avg_SOC - 0.5)
        if avg_SOC > self.params['stress_SOC_high']:
            soc_stress = 1.5
        elif avg_SOC < self.params['stress_SOC_low']:
            soc_stress = 1.3
        else:
            soc_stress = 1.0 + 2.0 * soc_deviation
        
        # 计算总损失
        loss = 1 - (1 - base_rate_per_day * temp_acceleration * soc_stress) ** (age_days ** time_exponent)
        
        return min(0.5, loss)  # 最大损失50%
    
    def cycle_aging(self, cycles_completed, DOD_avg, avg_temp):
        """
        循环老化
        公式：Q_loss_cycle = B * N^m * g(DOD) * h(T)
        """
        # 基准循环寿命（100% DOD时容量降至80%的循环数）
        cycles_80percent = self.params['cycle_life']
        
        # 等效循环次数（考虑DOD影响）
        effective_cycles = cycles_completed * (DOD_avg ** 0.5)
        
        # 老化指数
        cycle_exponent = 0.8
        
        # DOD应力因子（深度放电加速老化）
        DOD_stress = 1.0
        if DOD_avg > 0.8:
            DOD_stress = 2.0
        elif DOD_avg > 0.5:
            DOD_stress = 1.5
        else:
            DOD_stress = 0.7 + DOD_avg * 0.6
        
        # 温度加速
        temp_factor = 1.0
        if avg_temp > self.params['stress_temp_high']:
            temp_factor = 2.0
        elif avg_temp < self.params['stress_temp_low']:
            temp_factor = 1.5
        
        # 计算循环损失
        loss_rate = (effective_cycles / cycles_80percent) ** cycle_exponent
        loss = loss_rate * DOD_stress * temp_factor * 0.2  # 20%为基准损失
        
        return min(0.3, loss)  # 最大损失30%
    
    def stress_score(self, usage_pattern):
        """
        计算电池压力评分（0-100，越高越伤电池）
        """
        score = 0
        
        # 高温使用
        if usage_pattern.get('avg_temp', 298) > 313:  # >40°C
            score += 30
        elif usage_pattern['avg_temp'] > 303:  # >30°C
            score += 15
        
        # 深度放电
        if usage_pattern.get('avg_dod', 0.5) > 0.8:
            score += 25
        elif usage_pattern['avg_dod'] > 0.6:
            score += 15
        
        # 高SOC存放
        if usage_pattern.get('storage_soc', 0.5) > 0.9:
            score += 20
        
        # 快充频繁
        if usage_pattern.get('fast_charge_ratio', 0) > 0.7:
            score += 15
        
        # 低温充电
        if usage_pattern.get('low_temp_charge', False):
            score += 10
        
        return min(100, score)
    
    def estimate_remaining_life(self, current_retention, usage_pattern):
        """
        估算剩余寿命
        """
        stress = self.stress_score(usage_pattern)
        
        # 简化模型：根据当前容量和压力估算剩余天数
        if current_retention > 0.8:
            remaining = 365 * 2  # 还有2年
        elif current_retention > 0.7:
            remaining = 365 * 1  # 还有1年
        elif current_retention > 0.6:
            remaining = 180      # 还有半年
        else:
            remaining = 90       # 还有3个月
        
        # 压力修正
        remaining = remaining * (1 - stress/200)
        
        return max(30, remaining)  # 最少30天

