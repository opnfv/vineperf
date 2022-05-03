[TestParameters]
name = Rapid_ETSINFV_TST009
number_of_tests = 1
total_number_of_test_machines = 1 
lat_percentile = 99

[TestM1]
name = Generator
prox_launch_exit = false
config_file = configs/prox.cfg
dest_vm = 1
mcore = [14]
gencores = [15]
latcores = [16]

[test1]
test=TST009test
warmupflowsize=128
warmupimix=[64]
warmupspeed=1
warmuptime=2
imixs=[[64],[128],[256],[512],[1024],[1280],[1512]]
flows=[1]
drop_rate_threshold = 0
MAXr = 3
MAXz = 5000
MAXFramesPerSecondAllIngress = 12000000
StepSize = 10000
