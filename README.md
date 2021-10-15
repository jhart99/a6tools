## A6tools

A Python library and tools AUCTUS A6 based radios.

### Radios
Tested and working with:
* COTRE CO01D
* COTRE CO04D
* COTRE CO06D
* GOCOM GD900

Probably also works with:
* GOCOM GD100
* GOCOM GD700
* GOCOM GD800
* CONNECOM radios as well

### Usage

#### atcommander

atcommander sends AT commands to the radio which can be used to change many of the parameters.

Usage:
```
$ python3 atcommander.py AT+DMOCONNECT
OnCmd_DMOCONNECT
ATE_SendCmdAck: cmd:DMOCONNECT isOk:0x1
tx_length:17
ATE_SendDataFrame:
+DMOCONNECT:0

ATE pipe. used[HOST]
```
You must start with AT+DMOCONNECT prior to any other commands
