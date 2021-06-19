#!/usr/bin/env python 
""" Created by Kai on 2021/06/19 """

# import python module
import sys
# import third party module
import numpy as np
import pandas as pd


""" Data information """
spec_filename = './Example/spectrum.txt'
pattern_filename = './Example/pattern.txt'
EQE = 30/100

""" Constants """
V_filename = './EyeResponse.txt' # (Don't modified)
num_per_Amp = 6.241e18
K = 683.002 # lm/W
h = 6.62607e-34 # m^2 * kg / s
c = 3e8 # m/s

""" helpful functions """
def readfile(filename):
    data = []
    try:
        with open(filename) as file:
            lines = file.readlines()
            for ii, line in enumerate(lines):
                tokens = line.split()
                if len(tokens)==0:
                    continue
                data.append( [ float(token) for token in tokens ] )
    except:
        print('Fail to read {}'.format(filename))
        print('Please check the file.')
        sys.exit()
    return data
def integration(x, y):
    x, y = np.array(x), np.array(y)
    return np.einsum( 'i,i->', x[1:] - x[0:-1], ( y[1:] + y[0:-1] ) / 2 )

""" read spectrum """
print('Now reading emission spectrum from {}'.format(spec_filename) )
spec = pd.DataFrame( readfile(spec_filename), columns=['wavelength', 'intensity']) 
# print(spec)

spec_int = integration(spec['wavelength'], spec['intensity'])
print('    spectrum integration factor : {}'.format(spec_int))

idx = np.argmax( spec['intensity'] )
lambda_peak = spec.iloc[idx,0]
print('    peak wavelength : {} nm with peak {}'.format(lambda_peak, spec.iloc[idx,1]) )

photon_energy_list = h * c / ( spec['wavelength']*1e-9 )
photon_energy_avg = integration(spec['wavelength'], photon_energy_list*spec['intensity'] ) / spec_int
print('    average photon energy: {0:<.2e} J/{1:<.2f} eV'.format(photon_energy_avg, photon_energy_avg/1.602e-19 ) )

print('-'*60 + '\n')

""" read emission pattern """
print('Now reading emission pattern from {}'.format(pattern_filename) )
pattern = pd.DataFrame( readfile(pattern_filename), columns=['angle', 'intensity']) 
pattern['intensity'] /= pattern.iloc[0,1] 
# print(pattern)

pattern_int = 2*np.pi*integration(pattern['angle']/180*np.pi, pattern['intensity'] * np.sin(pattern['angle']/180*np.pi) )
print('    pattern integration factor : {}'.format(pattern_int))

print('-'*60 + '\n')

""" read luminuous funciton """
print('Now reading eye response (V) from {}'.format(spec_filename) )
V = pd.DataFrame( readfile(V_filename), columns=['wavelength', 'V']) 
# print(V)

print('-'*60 + '\n')

""" calculate V interpolation """
V_interp = np.interp( spec['wavelength'], V['wavelength'], V['V'])
# print(V_interp.shape)


""" calclate cd/A """
spec_factor = K * integration(spec['wavelength'], spec['intensity']*V_interp )/spec_int # [lm/W/sr] = [cd/W]
pattern_factor = pattern.iloc[0,1] / pattern_int # [no unit]
photon_energy = photon_energy_avg # h*c/(lambda_peak*1e-9) # [m^2 * kg / s] * [m/s] / [m] = [m^2 * kg / s^2] = [J]
cd_A = num_per_Amp * EQE * photon_energy * pattern_factor * spec_factor # [J] * [cd/W] = [cd * s]

print( 'spectrum factor          : {}'.format( spec_factor ) )
print( 'pattern factor           : {}'.format( pattern_factor ) )
print( 'average photon energy    : {0:<.2e} J ({1:<.2f} eV)'.format( photon_energy, photon_energy/1.602e-19 ) )
print( 'EQE                      : {} (%)'.format( EQE*100 ) )
print( 'Number of electron per A : {}'.format( num_per_Amp ) )
print( '-------------------------------------------------')
print( 'current efficiency       : {} (cd/A)'.format( cd_A ) )
print( '' )






