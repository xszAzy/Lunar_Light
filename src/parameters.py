from paraestimate import Paras
from pinformation import PInformation

class PhoneParameterEstimator:
    """手机参数估算器"""
    
    def __init__(self, specs):
        """
        specs: 手机规格字典
        {
            'name': 'iPhone 14 Pro',
            'screen': {'type': 'OLED', 'size': 6.1, 'max_brightness': 2000},
            'chip': {'name': 'A16_Bionic', 'process_nm': 4, 'max_freq': 3.46},
            'network': {'type': '5G_SA', 'max_bandwidth': 1000},
            'cooling': 'passive_advanced',
            'os': 'iOS',
            'battery': {'capacity': 3200, 'chemistry': 'Lipo'}
        }
        """
        self.specs = specs
        self.PIn=PInformation(specs)
    
    def estimate_all_parameters(self):
        """估算所有参数"""
        params = {}
        PIn=self.PIn
        # 1. 基准功率
        params['baseline'] = {
            'P_s': PIn.get_s(),
            'P_c': {
                'B':PIn.get_c('light'),
                'V':PIn.get_c('idle'),
                'G':PIn.get_c('heavy'),
                'M':PIn.get_c('medium')
                },
            'P_n': PIn.get_n(),
            'P_g': PIn.get_g(),  # GPS相对固定
            'P_b': PIn.get_b()
        }
        
        # 2. 负载系数
        params['coefficients'] = {
            'B': self.estimate_coefficients('B'),
            'V': self.estimate_coefficients('V'),
            'G': self.estimate_coefficients('G'),
            'M': self.estimate_coefficients('M')
        }
        
        # 3. 耦合系数
        params['coupling'] = {
            'B': self.estimate_coupling('B'),
            'V': self.estimate_coupling('V'),
            'G': self.estimate_coupling('G'),
            'M': self.estimate_coupling('M')
        }
        
        return params
    
    def estimate_coefficients(self, scene):
        screen_type = self.specs['screen']['type']
        chip_name = self.specs['chip']['name']
        os = self.specs.get('os', 'Android')
        
        # 能效等级判断
        chip_efficiency = 'high' if any(x in chip_name for x in ['A16', '8Gen2', '9200']) else 'medium'
        
        return {
            's': Paras.estimate_a_sj(scene, screen_type),
            'c': Paras.estimate_a_cj(scene, chip_efficiency, os),
            'n': self.estimate_a_nj(scene),
            'g': self.estimate_a_gj(scene),
            'b': self.estimate_a_bj(scene, os)
        }
    
    def estimate_a_nj(self, scene):
        # 网络负载系数
        base = {'B': 0.1, 'V': 0.3, 'G': 0.05, 'M': 0.2}[scene]
        
        # 根据网络类型调整
        network = self.specs['network']['type']
        if '5G' in network:
            return min(1.0,base * 1.5)  # 5G功耗更高
        else:
            return base
    
    def estimate_a_gj(self, scene):
        # GPS负载系数
        return {'B': 0.05, 'V': 0.0, 'G': 0.1, 'M': 0.1}[scene]
    
    def estimate_a_bj(self, scene, os):
        # 后台负载系数
        base = {'B': 1.0, 'V': 1.0, 'G': 0.8, 'M': 1.0}[scene]
        
        # 系统影响
        os_factor = {'iOS': 0.9, 'Stock_Android': 1.0, 'MIUI': 1.1, 'ColorOS': 1.05}
        return base * os_factor.get(os, 1.0)
    
    def estimate_coupling(self, scene):
        cooling = self.specs.get('cooling', 'passive_basic')
        return Paras.estimate_thermal_coupling(scene, cooling)
