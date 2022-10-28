Just my personal utility for power management, using utilities such as:

```
# x86_energy_perf_policy --cpu all --epb 15 --hwp-epp 100 --hwp-min 8 --hwp-max 39 -t 1 --hwp-desired 0
# /sys/devices/system/cpu/intel_pstate/hwp_dynamic_boost
# sudo cpupower idle-set -D 1
```
Profiles are configured through a dataclass like so:
```
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
...
# actual instance
super_quiet = PowerProfile(
    frequency_governor='powersave',
    energy_performance_governor='power',
    turbo_enabled=False,
    energy_efficiency_enabled=True,
    max_performance_pct=100,
    cpu_multiplier=CPUMultiplier(33, 34, 35, 37),
    icon='\uf2cb'
)
```
I have an i3status-rs menu item which implements a menu to select the powerplan like so:
```
sudo /home/tom/bin/powerpy.py $(echo -e 'superquiet\nquiet\nnormal\nturbo\nsuperturbo' | rofi -dmenu)
```
