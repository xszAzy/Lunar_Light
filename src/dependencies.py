class Dependencies:
    _required_libs=["pandas","numpy"]
    _installed_libs={}
    @classmethod
    def check_import(cls,lib_name):
        try:
            if lib_name=="pandas":
                import pandas as pd
                cls._installed_libs[lib_name]=True
                return pd
            elif lib_name=="numpy":
                import numpy as np
                cls._installed_libs[lib_name]=True
                return np
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
