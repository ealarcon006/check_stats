from __future__ import print_function

# Generic imports
from datetime import timedelta, datetime
import argparse
import atexit
import getpass
import ssl
import sys



from argparse import ArgumentParser
from yamlconfig import YamlConfig

# VMWare specific imports
from pyVmomi import vim, vmodl
from pyVim import connect

#from pyVim.connect import SmartConnect, Disconnect

class vmware_checklisk():
    ip_list = []
    result = {}

    def __init__(self):

        file_name="config.yml"
        try:
            self.config = YamlConfig(file_name)
            #self.config = YamlConfig(config_file)
            #if 'default' not in self.config.keys():
            #    print("Error, you must have a esx section in config file")
            #    exit(1)
            #elif 'vcenter' not in self.config.keys():
            #    print("Error, you must have a vcenter section in config file")
            #    exit(1)
        except:
            raise SystemExit("Error, cannot read configuration file")

        self._setargs()
        self._vmware_get_stat()
        self._print_reult()

    def _setargs(self):
        """
        fill IP array.
        """
        esx = self.config['default']['esx']
        #vc = self.config['default']['vc']
        if esx:
            print ("Cargando IP ESXI")
            for ip in esx:
                self.ip_list.append(ip)
                print (self.ip_list)
        else:
            print("Error al cargar IP ESXI")

        #if vc:
        #    print ("Cargando IP vCenter Server")
        #    for ip_vc in vc:
        #        self.ip_list.append(ip_vc)
        #else:
        #    print ("Error al cargar IP de vCenter Server")

        #self.config[section]['vmware_user'], self.config[section]['vmware_password'], sslContext = context


    def _vmware_connect(self, target, section):
        """
        Connect to Vcenter and get connection
        """

        context = None
        if self.config[section]['ignore_ssl'] and hasattr(ssl, "_create_unverified_context"):
            context = ssl._create_unverified_context()

        try:
            si = connect.Connect(target, 443,self.config[section]['vmware_user'],self.config[section]['vmware_password'],sslContext=context)
            #si = SmartConnect(host=target, user=self.config[section]['vmware_user'], pwd=self.config[section]['vmware_password'], port=443, sslContext=context)
            return si

        except vmodl.MethodFault as error:
            print("Caught vmodl fault: " + error.msg)
            return None

    def _vmware_disconnect(self):
        """
        Disconnect from Vcenter
        """
        connect.Disconnect(self.si)

    def _vmware_get_obj(self, content, vimtype, name=None):
        """
         Get the vsphere object associated with a given text name
        """
        obj = None
        container = content.viewManager.CreateContainerView(
            content.rootFolder, vimtype, True)
        if name:
            for c in container.view:
                if c.name == name:
                    obj = c
                    return [obj]
        else:
            return container.view

    def _vmware_get_stat(self):
        section = 'default'
        count = 1

        for target in self.ip_list:

            self.si = self._vmware_connect(target,section)
            if not self.si:
                print("Error, cannot connect to vmware")
                return
            content = self.si.RetrieveContent()

            for vm in self._vmware_get_obj(content, [vim.VirtualMachine]):
                summary = vm.summary
                vm_hardware = vm.config.hardware

                power_state = 1 if summary.runtime.powerState == 'poweredOn' else 0

                if power_state:
                    vm_memory_granted = summary.config.memorySizeMB
                    vm_cpu_quantity = summary.config.numCpu
                    vm_disk_asigned = float(0)
                    for each_vm_hardware in vm_hardware.device:
                        if (each_vm_hardware.key >= 2000) and (each_vm_hardware.key < 3000):
                            vm_disk_asigned = (vm_disk_asigned + (float(each_vm_hardware.capacityInKB) / 1024 / 1024))

                    try:
                        self.result[str(count)+"_name_"] = vm.name
                        self.result[str(count)+"_memmory_"] = vm_memory_granted
                        self.result[str(count)+"_cpu_"] = vm_cpu_quantity
                        self.result[str(count)+"_disk_"] = vm_disk_asigned
                        count +=1

                    except:
                        print("Error, cannot get vm metrics for {0}".format(vm.name))
                        pass
            self._vmware_disconnect()

        self.index = count

    def _print_reult(self):
        _table = '<table border="0" align="center">'
        _tr = '<tr>'
        _td = '<td>'
        _fin_table = '</table>'
        _fin_tr = '</tr>'
        _fin_td = '</td>'
        _inicio_file='<!DOCTYPE html><html><head><meta charset="utf-8"><title>Checkl-List</title></head><body>'
        _fin_file='</body> </html>'
        _newline ='\n'
        count = 1
        #print (self.result)
        file = open("check_list.html", "w")
        file.write(_inicio_file)
        file.write(_newline)
        file.write(_table)
        file.write(_newline)
        file.write(_tr + _td +"Nombre VM" + _fin_td +_td +"Memoria"+_fin_td + _td + "CPU" +_fin_td + _td + "Disco" +_fin_td)
        file.write(_newline)
        while count < self.index:
            name=self.result[str(count) + "_name_"]
            memory=self.result[str(count) + "_memmory_"]
            cpu=self.result[str(count) + "_cpu_"]
            disk=round(self.result[str(count) + "_disk_"],2)
            file.write(_tr + _td + name +_fin_td + _td + str(memory) + _fin_td + _td + str(cpu) + _fin_td + _td + str(disk) + _fin_td +_fin_tr)
            file.write(_newline)
            count +=1

        file.write(_fin_table)
        file.write(_newline)
        file.write(_fin_file)

        file.close()
        #print(self.result)
        print ("FIN")



if __name__ == '__main__':
    print("Starting connect to servers")

    vmware_checklisk()