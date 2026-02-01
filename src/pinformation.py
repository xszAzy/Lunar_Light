class PInformation:
    def __init__(self,specs):
        self.spec=specs
        # 不同SoC的功耗特性（典型使用场景）
        self.SOC_POWER_PROFILES = {
            # Apple A系列芯片（iOS）
            'A17 Pro': {
                'base': 0.05,      # 基础待机
                'idle': 0.2,       # 轻度待机
                'light': 0.8,      # 轻度使用（社交、网页）
                'medium': 1.8,     # 中等负载（拍照、视频）
                'heavy': 3.5,      # 重度使用（游戏）
                'peak': 5.2,       # 峰值性能
                'year': 2023,
                'process': '3nm'
            },
            'A16': {
                'base': 0.06,
                'idle': 0.25,
                'light': 1.0,
                'medium': 2.0,
                'heavy': 3.2,
                'peak': 5.5,
                'year': 2022,
                'process': '4nm'
            },
            'A15': {
                'base': 0.07,
                'idle': 0.3,
                'light': 1.2,
                'medium': 2.2,
                'heavy': 4.2,
                'peak': 5.8,
                'year': 2021,
                'process': '5nm'
            },
            
            # 高通骁龙系列（Android）
            'Snapdragon 8 Gen 3': {
                'base': 0.08,
                'idle': 0.3,
                'light': 1.1,
                'medium': 2.3,
                'heavy': 4.5,
                'peak': 7.0,
                'year': 2023,
                'process': '4nm'
            },
            'Snapdragon 8 Gen 2': {
                'base': 0.1,
                'idle': 0.35,
                'light': 1.3,
                'medium': 2.6,
                'heavy': 5.0,
                'peak': 8.0,
                'year': 2022,
                'process': '4nm'
            },
            'Snapdragon 888': {
                'base': 0.15,
                'idle': 0.5,
                'light': 1.8,
                'medium': 3.5,
                'heavy': 6.5,
                'peak': 9.5,
                'year': 2020,
                'process': '5nm'
            },
            'Snapdragon 870': {
                'base': 0.12,
                'idle': 0.4,
                'light': 1.5,
                'medium': 2.8,
                'heavy': 5.2,
                'peak': 7.5,
                'year': 2021,
                'process': '7nm'
            },
            
            # 联发科天玑系列
            'Dimensity 9200+': {
                'base': 0.09,
                'idle': 0.32,
                'light': 1.2,
                'medium': 2.5,
                'heavy': 4.8,
                'peak': 7.5,
                'year': 2023,
                'process': '4nm'
            },
            'Dimensity 8100': {
                'base': 0.1,
                'idle': 0.35,
                'light': 1.1,
                'medium': 2.2,
                'heavy': 4.0,
                'peak': 6.0,
                'year': 2022,
                'process': '5nm'
            },
            
            # 旧款芯片（对比用）
            'Snapdragon 835': {
                'base': 0.2,
                'idle': 0.6,
                'light': 1.5,
                'medium': 2.5,
                'heavy': 4.0,
                'peak': 5.0,
                'year': 2017,
                'process': '10nm'
            },
            'Apple A11': {
                'base': 0.15,
                'idle': 0.5,
                'light': 1.8,
                'medium': 3.0,
                'heavy': 4.5,
                'peak': 6.0,
                'year': 2017,
                'process': '10nm'
            }
        }

        self.NETWORK_POWER = {
            'WiFi_6': 0.8,      # W @高速传输
            'WiFi_5': 1.0,
            '5G_SA': 1.5,
            '5G_NSA': 1.8,
            '4G_LTE': 1.2,
            '4G': 1.0,
            '3G': 0.8
        }
        self.OS_FACTOR = {'iOS': 0.8, 'Stock_Android': 1.0, 'MIUI': 1.2, 'ColorOS': 1.1}
    def get_c(self,mode='idle'):
        spec=self.spec
        name=spec['chip'].get('name','A16')
        return self.SOC_POWER_PROFILES[name][mode]
    
    def get_s(self):
        spec=self.spec
        screen_type=spec['screen'].get('type','OLED')
        size_inch=spec['screen'].get('size',6.1)
        max_brightness_nits=spec['screen'].get('max_brightness',1000)
        if screen_type == 'OLED':
            # OLED: 功耗与像素发光强度相关
            # 经验公式: P ≈ 亮度 × 面积 × 效率系数
            area_cm2 = (size_inch * 2.54)**2 * 0.9  # 近似面积
            efficiency = 3.0e-6  # W/(nits·cm²)，典型值
            return max_brightness_nits * area_cm2 * efficiency  # W
        
        elif screen_type == 'LCD':
            # LCD: 背光功耗主导
            # P ≈ 亮度 × 面积 × 背光效率
            area_cm2 = (size_inch * 2.54)**2
            efficiency = 4.0e-6  # W/(nits·cm²)
            return max_brightness_nits * area_cm2 * efficiency  # W
        
        else:
            # 默认值
            return 0.5  # W    
    def get_n(self):
        spec=self.spec
        network_type=spec['network'].get('type','5G_SA')
        bandwidth_mbps=spec['network'].get('max_bandwidth',1000)
        if network_type in self.NETWORK_POWER:
            base = self.NETWORK_POWER[network_type]
            # 带宽调整（简化）
            bandwidth_factor = bandwidth_mbps / 1000
            return base * (0.5 + 0.5 * bandwidth_factor)
        else:
            return 1.0  # 默认
    def get_g(self):
        return 0.3
    def get_b(self):
        os = self.spec.get('os', 'Android')
        return 0.2 * self.OS_FACTOR.get(os, 1.0)
    
