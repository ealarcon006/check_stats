from __future__ import print_function

# Generic imports
import argparse
import pytz
import ssl
import sys
import time

# VMWare specific imports
from pyVmomi import vim, vmodl
from pyVim import connect







for vm in self._vmware_get_obj(content, [vim.VirtualMachine]):
    summary = vm.summary
    vm_hardware = vm.config.hardware

    power_state = 1 if summary.runtime.powerState == 'poweredOn' else 0

    if power_state:
        disk_asigned = float(0)
        for each_vm_hardware in vm_hardware.device:
            if (each_vm_hardware.key >= 2000) and (each_vm_hardware.key < 3000):
                disk_asigned = (disk_asigned + (float(each_vm_hardware.capacityInKB) / 1024 / 1024))

        try:
            self.metrics["vmware_vm_total_disk_asigned"].add_metric([vm.name], round(disk_asigned, 2))
        except:
            print("Error, cannot get vm metrics {0} for {1}".format("vmware_vm_total_disk_asigned", vm.name))
            pass


    for vm in self._vmware_get_obj(content, [vim.VirtualMachine]):
        summary = vm.summary
        power_state = 1 if summary.runtime.powerState == 'poweredOn' else 0
        #vm_metrics['vmware_vm_power_state'].add_metric([vm.name], power_state)

        # Get metrics for poweredOn vms only
        if power_state:
            #Agregado Por Mi
            vmware_vm_memory_granted = summary.config.memorySizeMB
            vmware_vm_cpu_quantity = summary.config.numCpu