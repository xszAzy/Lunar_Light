class Dependencies:
    _required_libs=["pandas","numpy","matplotlib","sympy","scipy"]
    _installed_libs={}
    @classmethod
    def check_import(cls,lib_name):
        try:
            if lib_name=="pandas":
                import pandas as pd
                cls._installed_libs[lib_name]=True
                return pd
            elif lib_name=="numpy":
                import numpy
                cls._installed_libs[lib_name]=True
                return numpy
            elif lib_name=="matplotlib":
                import matplotlib.pyplot as plt
                cls._installed_libs[lib_name]=True
                return plt
            elif lib_name=="sympy":
                import sympy 
                cls._installed_libs[lib_name]=True
                return sympy
            elif lib_name=="scipy":
                import scipy
                cls._installed_libs[lib_name]=True
                return scipy
            else:
                return None
        except ImportError:
            cls._installed_libs[lib_name]=False
            raise ImportError(f"Need to install {lib_name}\n")
    @classmethod
    def get_installation_status(cls):
        for c in cls._required_libs:
            cls.check_import(c)
        print(cls._installed_libs)

    
    @classmethod
    def get_pandas(cls):
        return cls.check_import("pandas")
    @classmethod
    def get_numpy(cls):
        return cls.check_import("numpy")
    @classmethod
    def get_plt(cls):
        return cls.check_import("matplotlib")
    @classmethod
    def get_sympy(cls):
        return cls.check_import("sympy")
    @classmethod
    def get_scipy(cls):
        return cls.check_import("scipy")
