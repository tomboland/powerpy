#!/usr/bin/python
# x86_energy_perf_policy --cpu all --epb 15 --hwp-epp 100 --hwp-min 8 --hwp-max 39 -t 1 --hwp-desired 0
# /sys/devices/system/cpu/intel_pstate/hwp_dynamic_boost
# sudo cpupower idle-set -D 1
import sys
from dataclasses import dataclass
import sh

def hex_digits(adecimal: int) -> str:
    return hex(adecimal).lstrip('0x')

@dataclass
class CPUMultiplier:
    a: int
    b: int
    c: int
    d: int

def cpu_multiplier_to_hex_string(m: CPUMultiplier) -> str:
    return '0x' + ''.join([hex(x).lstrip('0x') for x in (m.a, m.b, m.c, m.d)])

@dataclass
class PowerProfile:
    frequency_governor: str
    energy_performance_governor: str
    turbo_enabled: bool
    energy_efficiency_enabled: bool
    max_performance_pct: int
    cpu_multiplier: CPUMultiplier
    energy_performance_bias: int
    energy_performance_preference: int
    hwp_min_freq_x100: int
    hwp_max_freq_x100: int
    hwp_desired_freq_x100: int
    icon: str

super_turbo = PowerProfile(
    frequency_governor='performance',
    energy_performance_governor='performance',
    turbo_enabled=True,
    energy_efficiency_enabled=False,
    max_performance_pct=100,
    cpu_multiplier=CPUMultiplier(39, 39, 39, 39),
    icon='\uf2c7'
)
turbo = PowerProfile(
    frequency_governor='performance',
    energy_performance_governor='balance-performance',
    turbo_enabled=True,
    energy_efficiency_enabled=True,
    max_performance_pct=100,
    cpu_multiplier=CPUMultiplier(36, 37, 38, 39),
    icon='\uf2c8'
)
normal = PowerProfile(
    frequency_governor='powersave',
    energy_performance_governor='normal',
    turbo_enabled=True,
    energy_efficiency_enabled=True,
    max_performance_pct=100,
    cpu_multiplier=CPUMultiplier(35, 36, 37, 39),
    icon='\uf2c9'
)
quiet = PowerProfile(
    frequency_governor='powersave',
    energy_performance_governor='balance-power',
    turbo_enabled=True,
    energy_efficiency_enabled=True,
    max_performance_pct=100,
    cpu_multiplier=CPUMultiplier(34, 35, 36, 38),
    icon='\uf2ca'
)
super_quiet = PowerProfile(
    frequency_governor='powersave',
    energy_performance_governor='power',
    turbo_enabled=False,
    energy_efficiency_enabled=True,
    max_performance_pct=100,
    cpu_multiplier=CPUMultiplier(33, 34, 35, 37),
    icon='\uf2cb'
)

def profile_from_cl_param (param: str) -> PowerProfile:
    if param == 'superturbo': return super_turbo
    if param == 'turbo': return turbo
    if param == 'normal': return normal
    if param == 'quiet': return quiet
    if param == 'superquiet': return super_quiet
    raise Exception(f'Unrecognised param: {param}')

if __name__ == "__main__":
    try: 
        param = sys.argv[1]
    except:
        print('\uf059')
        sys.exit(0)

    profile = profile_from_cl_param(param)

    sys.stderr.write(f'Setting cpu frequency governor: {profile.frequency_governor}\n')
    sh.cpupower('frequency-set', '-g', profile.frequency_governor, _out=sys.stderr)

    sys.stderr.write(f'\n{"Enabling" if profile.turbo_enabled else "Disabling"} turbo\n')
    sh.x86_energy_perf_policy('--cpu', 'all', '--turbo-enable', '1' if profile.turbo_enabled else '0', _out=sys.stderr)

    sys.stderr.write(f'\nSetting "{profile.energy_performance_governor}" CPU energy profile\n')
    sh.x86_energy_perf_policy('--cpu', 'all', '--all', profile.energy_performance_governor, _out=sys.stderr)

    sys.stderr.write(f'\n{"Enabling" if profile.energy_efficiency_enabled else "Disabling"} energy_efficiency mode\n')
    with open('/sys/devices/system/cpu/intel_pstate/energy_efficiency', 'w') as f:
        f.write('1' if profile.energy_efficiency_enabled else '0')

    sys.stderr.write(f'Setting maximum p-state to {profile.max_performance_pct}%\n')
    with open('/sys/devices/system/cpu/intel_pstate/max_perf_pct', 'w') as f:
        f.write(str(profile.max_performance_pct))

    m = profile.cpu_multiplier # for brevity
    sys.stderr.write(f'Setting CPU multiplier to {m.d}/{m.c}/{m.b}/{m.a} - hex {cpu_multiplier_to_hex_string(m)}\n')
    sh.wrmsr('-a', '0x1AD', cpu_multiplier_to_hex_string(profile.cpu_multiplier))

    print(profile.icon)
