# makefile to manage dpdk package
#

# Copyright 2022 Anuket
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

#
# Contributors:
#   Aihua Li, Huawei Technologies.
#   Martin Klozik, Intel Corporation.
#   Christian Trautman, Red Hat Inc.
#   Sridhar Rao, The Linux Foundation.

include ../mk/master.mk
include ../package-list.mk
include /etc/os-release

.PHONY: install force_make

ifndef VHOST_USER
    VHOST_USER = n
endif
WORK_DIR = dpdk
TAG_DONE_FLAG = $(WORK_DIR)/.$(DPDK_TAG).tag.done

all: force_make
	@echo "Finished making $(WORK_DIR) "

INSTALL_TARGET = force_make

force_make: $(TAG_DONE_FLAG)
	$(AT)cd $(WORK_DIR) && git pull $(DPDK_URL) $(DPDK_TAG)
	$(AT)cd $(WORK_DIR) && meson --prefix=$(CURDIR)/dpdk/build -Dtests=false build
	$(AT)cd $(WORK_DIR) && ninja -C build
	$(AT)cd $(WORK_DIR) && ninja -C build install
	$(AT)cd $(WORK_DIR) && cd build && meson configure -Denable_kmods=true && ninja
	@echo "Make done"

install: $(INSTALL_TARGET)
	$(AT)sudo cp -a $(WORK_DIR)/$(DPDK_TARGET)/kmod $(INSTALL_DIR)/lib/modules/$(KERNEL_VERSION)
	@echo "install done"

# hard way to clean and clobber
clean:
	$(AT)cd $(WORK_DIR) && git clean -xfd *.o
clobber:
	$(AT)rm -rf $(WORK_DIR)

# distclean is for developer who would like to keep the
# clone git repo, saving time to fetch again from url
distclean:
	$(AT)cd $(WORK_DIR) && git clean -xfd && git checkout -f

test:
	@echo "Make test in $(WORK_DIR) (stub) "

sanity:
	@echo "Make sanity in $(WORK_DIR) (stub) "

$(WORK_DIR):
	$(AT)git clone $(DPDK_URL) dpdk

$(TAG_DONE_FLAG): $(WORK_DIR)
	$(AT)cd $(WORK_DIR); git checkout $(DPDK_TAG)
	$(AT)touch $@
