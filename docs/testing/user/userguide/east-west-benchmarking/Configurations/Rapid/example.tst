# Copyright 2022 Anuket, Intel Corporation, and The Linux Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

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
