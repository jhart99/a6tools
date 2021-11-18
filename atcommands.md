Command | function
---------------------|----------
DMOCONNECT | Required before issuing other commands
DMODISCONNECT | Ends the current session
DMORLIC              | Returns the Device Serial Number
DMOVERQ              | Returns Ver 1.0.0
DMOREVDATA | No response
BINARY | No response
DMOGETSTARTUP | No response
DMOGETSOFTVERSION | Returns the firmware version
DMOGETSQSTATUS | No response
DMOGETCURRCH | Replies with the current channel parameters +DMOGETCURRCH:0,DIG,438802000,438802000,0,0,1,2,0,0,0 or +DMOGETCURRCH:15,ANA,405000000,405000000,1,1
DMOGETCHFREQ | Replies with the channel parameters for the given channel number AT+DMOGETCHFREQ=<channel>
DMOGETLNAOFFS | Returns the LNA offset
DMOGETRSSIPARAM | Returns the RSSI offset
DMOGETCHIPID | A unique ID for the A6 processor
DMOGETGRPADDR | Returns the DMR contact for the current channel
DMOGETWLKTLKID | Returns the DMR radio ID of the radio
DMORDRSSI | Returns the current receive signal strength in dBm
DMOTESTMODE |
DMOSETGROUP | Sets all of the frequency settings for the given channel
DMOSETCTCDCS | Sets the CTCSS or DCS mode for the current channel AT+DMOSETCTCDCS=<mode>,<ctcDcsType>,<ctcDcsNum>,<ctcDcsInvert>
DMOSETCTCDCSGAIN | Sets the audio gain for the CTCSS or DCS tone AT+DMOSETCTCDCSGAIN=<ctcDcsType>,<gain>
DMOSETTAILFREQ | Sets the tail frequency(550-2000 in tenths of Hz) for the current channel AT+DMOSETTAILFREQ=<tailFreq>
DMOAUTOPOWCONTR | Sets the automatic power control mode for the current channel AT+DMOAUTOPOWCONTR=<mode>
DMOSETMIC | Sets the microphone gain for the current channel AT+DMOSETMIC=<gain>
DMOSETVOLUME | Sets the volume for the current channel AT+DMOSETVOLUME=<volume>
DMOSETVOLUMELEVEL | Sets the volume level for the current channel AT+DMOSETVOLUMELEVEL=<level>
DMOSETVOX | Sets the VOX level for the current channel AT+DMOSETVOX=<level>
DMOSENDDATA | ¯\\_(ツ)_/¯
DMOSETAPC |
DMOSETSN |
DMORESETSN |
DMOSETRSSIPARAM |
DMOSETLNAOFFS |
DMOSAVEPARAM |
DMOERASEPARAM |
DMOSETSMARTLO |
DMOGETRXBER | Returns the received bit error rate
DMOCHSWITCH | Changes the current channel AT+DMOCHSWITCH=<channel>
DMOSETCHFREQ | Changes the channel parameters for the given channel number AT+DMOSETCHFREQ=<txfreq>,<rxfreq> where the frequencies are like this 438.8001.  Must have this number of digits to work
DMOSETCHPOWER |
DMOSETPOWER | Sets the power level for the current channel AT+DMOSETPOWER=<level> where level is 0-2
DMOSETPWRSAVELV | Sets the FM power save level for the current channel if no audio, the radio will stop transmitting AT+DMOSETPWRSAVELV=<level>
DMOSETWLKTLKID | Set the DMR Radio ID
DMOSETGRPADDR | Set the DMR group address
DMOSETFREQBANDNUM | Set the number of frequency bands AT+DMOSETFREQBANDNUM=<number> where number is less than 16
DMOGETFREQBANDNUM | Get the current number of frequency bands
DMOSETFREQBANDVAL | Set the values of the frequency bands 
DMOGETFREQBANDVAL | Get the values of the frequency bands
DMOAMPCTRLTEST | Sets an amplifier gain and tests the amplifier AT+DMOAMPCTRLTEST=<gain> gain is 0-128
DMODIGPWRSAVECTRL |
DMOSETLCHEADERCNT | Sets the number of LC headers sent AT+DMOSETLCHEADERCNT=<count>
DMOGRPCALLREQ |
DMOINDCALLREQ |
DMOALLCALLREQ |
DMOALERTCSBKREQ | Sends an alert call request to the radio AT+DMOALERTCSBKREQ=<dmrid>
DMOCHECKCSBKREQ | Sends a check call request to the radio AT+DMOCHECKCSBKREQ=<dmrid>
DMOALARMCSBKREQ | Sends an alarm call request to the radio AT+DMOALARMCSBKREQ=<dmrid>
DMORESPCSBKREQ | Sends a response call request to the radio AT+DMORESPCSBKREQ=<dmrid>
SETIMAGEREJEMODE |
SETIMAGEREJE |
SETEQUALIZER |
SETCOMPANDER |
SETSCRAMBLER |
SETTONELIST |
SETDTMF |
RESTOREFACTORYSETTING | Restores the original settings.  The password for this is 778123456
BERTEST |
SETCOLORCODE | Set the color code for the current channel AT+SETCOLORCODE=<colorCode>
GETGPADCVALUE | Get the current value of the GPADC channel(0-1) AT+GETGPADCVALUE=<channel>
SETGPADCCHAN | Set the GPADC channel enable AT+SETGPADCCHAN=<channel>,<enable> channel=0,1 enable=0,1
GETGPIOVALUE | Get the current value of the GPIO channel(0-32) AT+GETGPIOVALUE=<channel>
SETGPIOVALUE | Set the GPIO channel value AT+SETGPIOVALUE=<channel>,<value> channel=0-32 value=0,1
SETGPIODIR | Set the direction of the GPIO channel(0-32) AT+SETGPIODIR=<channel>,<direction> channel=0-32 direction=0,1
GETPOWERAMPGAIN | Get the power amplifier gain values AT+GETPOWERAMPGAIN=<band> returns <band>,<digLow>,<digMed>,<digHigh>,<anaLow>,<anaMed>,<anaHigh>
SETPOWERAMPGAIN | Sets the power amplifier gain
GETPOWERAPCGAIN | Get the automatic power control gain values AT+GETPOWERAPCGAIN=<band> returns <band>,<digLow>,<digMed>,<digHigh>,<anaLow>,<anaMed>,<anaHigh>
SETPOWERAPCGAIN | Sets the automatic power control gain
SETPOWERAPCSW | Sets the automatic power control switch ?
GETEFLTRXADJ | Returns the RX filter adjustment for a band AT+GETEFLTRXADJ=<band> where the value is <band>,<dac>,<gain>
SETEFLTRXADJ | Sets the RX filter adjustment for a band AT+SETEFLTRXADJ=<band>,<dac>,<gain>
DMOGETVAFC | Returns the current Automatic Frequency Correction value
DMOSETVAFC | Sets the Automatic Frequency Correction value
DMOPTT | Sets the PTT state for the current channel AT+DMOPTT=<state> where state is 0 for off and 1 for on
GETFREQERR | Get the TCXO frequency error in 10s of Hz
DMOFREQERR | Set the TCXO frequency error in 10s of Hz
GETBANDBYFREQ | Returns the band number for the given frequency AT+GETBANDBYFREQ=<freq>
DMOGETFREQBANDVAL | Returns the cut offs for the different frequency bands
DMOGETFREQBANDNUM | Returns the number of frequency bands in use/defined AT+DMOGETFREQBANDNUM
DMOSETFREQBANDNUM | Can be used to change the number of defined frequency bands AT+DMOSETFREQBANDNUM=2
DMRSIGNATURE | Unknown command.  The signature looks something like this: AT+DMRSIGNATURE/aa,aa,aa,... with a total of 30 bytes worth of numbers Returns something that says AUTHSETKEYS
WRITECFS | Does something similar to the DMRSIGNATURE command
GETINCALLID | Returns the incoming call ID, <calltype>,<from>,<to> where call type is 0,1,2 corresponding to individual, group and all calls and from and to are DMR IDs
SETALERTTONE |
SETBATTDETRANGADC |
SETBATTADJ |
SETPROFILERAMPSSHIFT |
SETPROFILERAMPSDWPOS |
GETPROFILERAMPS |
SETRAMPINGTABLE |
GETAPC_FINEVALUE |
SETAPC_FINEVALUE |
DMR_ADJTXSYMDEV |
DMR_GETTXSYMDEV |
SETSTANDARD | Sets the testing standard for the radio AT+SETSTANDARD=<standard> where standard is 0-4.  Completely resets the radio's program!
SETSQLEVEL |
SETSQADJUST |
SETSQMODE |
SETTXIQGAIN |
GETSQLEVEL |
SETMODULE |
SETCHANNELKNOBMODE |
FGU_AFC_ADJ |
FGU_AFC_GET |
FGU_VCON_BIAS |
FGU_VCON_BIAS_GET |
_FGU_TUNE_GET |
FGU_TUNE_GET |

