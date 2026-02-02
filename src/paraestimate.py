class Paras:
    def estimate_a_sj(scene, screen_type, auto_brightness=True):
        """
        估算屏幕负载系数
        基于：平均亮度 ÷ 最大亮度
        """
        # 不同场景的典型亮度比例（研究数据）
        brightness_ratios = {
            'OLED': {
                'B': 0.3 if auto_brightness else 0.4,  # 浏览：暗色模式+低亮度
                'V': 0.5,  # 视频：中等亮度
                'G': 0.8,  # 游戏：高亮度激发
                'M': 0.4   # 综合：平均
            },
            'LCD': {
                'B': 0.4,  # LCD背光变化小
                'V': 0.6,
                'G': 0.9,
                'M': 0.5
            }
        }
        
        # 内容影响（OLED特有）
        if screen_type == 'OLED':
            content_factor = {
                'B': 0.8,  # 浏览：多暗色、文字
                'V': 1.0,  # 视频：全屏彩色
                'G': 1.05,  # 游戏：鲜艳色彩
                'M': 0.9
            }
            return brightness_ratios['OLED'][scene] * content_factor[scene]
        else:
            return brightness_ratios['LCD'][scene]

    def estimate_a_cj(scene, chip_efficiency, os_optimization='iOS'):
        """
        估算CPU负载系数
        基于：CPU利用率 × 频率/电压调节
        """
        # 基础利用率（研究数据）
        base_utilization = {
            'B': 0.25,  # 浏览：轻量任务，短爆发
            'V': 0.15,  # 视频：硬解码效率高
            'G': 0.65,  # 游戏：高负载，可能降频
            'M': 0.35   # 综合：混合负载
        }
        
        # 能效调整（先进制程效率更高）
        efficiency_factor = {
            'high': 1.2,    # A16、8Gen2等
            'medium': 1.0,  # 中端芯片
            'low': 0.8      # 老旧芯片
        }
        
        # 系统优化
        os_factor = {
            'iOS': 0.9,      # 严格调度
            'Stock_Android': 1.0,
            'MIUI': 1.1,     # 较多后台
            'ColorOS': 1.05
        }
        
        base = base_utilization[scene]
        eff = efficiency_factor.get(chip_efficiency, 1.0)
        os = os_factor.get(os_optimization, 1.0)
        
        # 最终系数：利用率 × 能效影响 × 系统影响
        return base * eff * os

    def estimate_thermal_coupling(scene, cooling_design):
        """
        估算热耦合系数
        基于：ΔT ∝ P_total × R_thermal
              ΔP_leakage ∝ exp(ΔT/T0)
        """
        # 散热设计等级
        cooling_factor = {
            'passive_basic': 1.0,      # 基本被动散热
            'passive_advanced': 0.7,   # 增强被动散热
            'vapor_chamber': 0.4,      # 均热板
            'active_cooling': 0.2      # 主动散热（游戏手机）
        }
        
        # 场景热负载
        base_coupling_percent = {
            'B': 0.02,  # 浏览：低热负载
            'V': 0.05,  # 视频：中等
            'G': 0.15,  # 游戏：高热负载
            'M': 0.08   # 综合：中等
        }
        
        cooling = cooling_factor.get(cooling_design, 1.0)
        base = base_coupling_percent[scene]
        
        return base*cooling
