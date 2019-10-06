# pseudo-lspci
A pseudo implementation of lspci's -s option in Python.

## Configuration & Usage

Use a python3 virtual environment.

```
cd <path_to_cloned_repo>
pip install -r requirements.txt
python pci <slot_number>
```

Help:

```
$ python pci -h
usage: pci [-h] slot

positional arguments:
  slot        The PCI slot to check. Should be in the format:
              domain:bus:device.func

optional arguments:
  -h, --help  show this help message and exit
```
