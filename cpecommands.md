Command | Description
--------|------------
0000 | SendBaseInfo
0001 | Unknown
0002 | Unknown Writes to NVRAM!
0003 | SetEmbInfo
0004 | GetEmbInfoAll
000f | SetBaseSetting
0010 | SendBaseSettingsBasicSet
0011 | SetChanInfo
0012 | GetChanInfo
0013 | SetChanName
0014 | GetChanName
0015 | SetTalkieName
0016 | Unknown
0017 | SetIndividualCallCnt
0018 | SetIndividualCallInfo
0019 | SendIndividualCallCnt
001a | SendIndividualCallInfo
001b | SendCmdResponse ?
001c | SetGroupCallInfo
001d | Unknown
001e | GetGroupCallInfo
001e | SendCmdResponse ?
0020 | Unknown
0021 | SetShortcutMsgInfo ?
0022 | SetShortcutCnt
0023 | SetShortcutMsgInfo ?
0024 | GetShortcutMsgInfo
0025 | SetKeyFunc
0026 | GetKeyFunc
0027 | SetScanlist
0028 | GetScanlistCnt
002a | GetScanlist
002b | Checks the programming password
0100 | Unknown
0101 | Unknown
0102 | Unknown
0104 | Unknown
0a00 | Populates the CPS area in RAM and also pauses transmissions for 5 seconds.  Returns @CpsByHostPort_ConcatenateHdr CPS_Hdr[StartAddr:0x82004810 len:772] 0x88105948
0a01 | ? Clear CPS area ?
0a02 | ? Writes CPS from RAM to flash and reboots ?
0a03 | Unknown called during CPS read operation
0a04 | Unknown but same as 0a07 called during CPS read finalizer
0a05 | Stops transmissions for 5 seconds.  Might pause BCPU?
0a06 | ? Cancels powersaving mode ? Called during the initialization sequence
0a07 | Unknown but same as 0a04
0a08 | PROT_SendDataFrame Seems to echo the sent packet back. Called during the initialization sequence.  Might be a check that the CPS in the radio is running.
