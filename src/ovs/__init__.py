# Copyright 2015 Intel Corporation.
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

"""
A package for controlling Open vSwitch

This package is intended to stay gneneric enough to support using any data
path of OVS (linux kernel, DPDK userspace, etc.) by different parameterization
and external setup of vswitchd-external process, kernel modules etc.

"""

from src.ovs.daemon import *
from src.ovs.ofctl import *
