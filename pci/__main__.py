import os
import re
import logging
import argparse

from libpci import LibPCI

LOGGER = logging.getLogger()
SYS_PCI_DIR = "/sys/bus/pci/devices"
VENDOR = "vendor"
DEVICE = "device"
SUBSYSTEM_DEVICE = "subsystem_device"
SUBSYSTEM_VENDOR = "subsystem_vendor"


def configure_logging():
    logging.getLogger("libpci").setLevel(logging.CRITICAL)
    LOGGER.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    LOGGER.addHandler(ch)


class SlotLookup:
    def __init__(
        self,
        pcidir,
        vendor_file,
        device_file,
        subsystem_vendor_file,
        subsystem_device_file,
    ):
        self._libpci_api = LibPCI()
        self._pcidir = pcidir
        self._vendor_file = vendor_file
        self._device_file = device_file
        self._subsystem_vendor_file = subsystem_vendor_file
        self._subsystem_device_file = subsystem_device_file

    def check_slot(self, slot):
        if not self._valid_slot(slot):
            raise Exception(
                "The slot ID format is not valid. "
                "Expected format: domain:bus:device.func"
            )
        if slot not in os.listdir(self._pcidir):
            raise Exception("The slot was not found in %s" % (self._pcidir,))
        self._report_slot_info(slot)

    def _report_slot_info(self, slot):
        slot_dir = os.path.join(self._pcidir, slot)
        self._print_slot_info(slot_dir)

    def _print_slot_info(self, slot_dir):
        vendor_id = self._open_and_read(
            os.path.join(slot_dir, self._vendor_file)
        )
        device_id = self._open_and_read(
            os.path.join(slot_dir, self._device_file)
        )
        subsystem_vendor_id = self._open_and_read(
            os.path.join(slot_dir, self._subsystem_vendor_file)
        )
        subsystem_device_id = self._open_and_read(
            os.path.join(slot_dir, self._subsystem_device_file)
        )

        if vendor_id:
            LOGGER.info(
                "Vendor Name: %s",
                self._libpci_api.lookup_vendor_name(vendor_id),
            )

        if vendor_id and device_id:
            LOGGER.info(
                "Device Name: %s",
                self._libpci_api.lookup_device_name(vendor_id, device_id),
            )

        if subsystem_vendor_id:
            LOGGER.info(
                "Subsystem Vendor Name: %s",
                self._libpci_api.lookup_vendor_name(subsystem_vendor_id),
            )

        if (
            vendor_id
            and device_id
            and subsystem_vendor_id
            and subsystem_device_id
        ):
            LOGGER.info(
                "Subsystem Device Name: %s",
                self._libpci_api.lookup_subsystem_device_name(
                    vendor_id,
                    device_id,
                    subsystem_vendor_id,
                    subsystem_device_id,
                ),
            )

    @staticmethod
    def _open_and_read(file_name, convert_hex=True):
        contents = None
        if not os.path.isfile(file_name):
            return contents
        try:
            f = open(file_name)
            contents = f.read()
        finally:
            f.close()
        if contents and convert_hex:
            contents = int(contents.rstrip(), 16)
        return contents

    @staticmethod
    def _valid_slot(slot):
        return re.match(r"[0-9a-f]{4}:[0-9a-f]{2}:\d+\.\d+$", slot)


if __name__ == "__main__":
    configure_logging()
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "slot",
        help="The PCI slot to check. "
        "Should be in the format: domain:bus:device.func",
    )
    args = parser.parse_args()
    slot_lookup = SlotLookup(
        SYS_PCI_DIR, VENDOR, DEVICE, SUBSYSTEM_VENDOR, SUBSYSTEM_DEVICE
    )
    slot_lookup.check_slot(args.slot)
