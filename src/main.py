from dependencies import Dependencies
import math

#Dependencies.get_installation_status()

np=Dependencies.get_numpy()
plt=Dependencies.get_plt()
sympy=Dependencies.get_sympy()
scipy=Dependencies.get_scipy()

def calculate_I(t):
    return 50*1#1 as Coulomic Efficiency
def calculate_SOC(t:float,t0:float=0.0,C=1000):
    x=sympy.symbols('x')
    total_I=sympy.integrate(calculate_I(x),(x,t0,t))
    delta=-(1/C)*total_I
    return calculate_SOC(t=t0)+delta if t0!=0 else 100+delta

print(calculate_SOC(t=21.0,t0=0.0))
