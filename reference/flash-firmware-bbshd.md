## Warning
Proceed with caution. It is a good idea to have access to the original firmware if you for any reason want to roll back.

**BBSHD**  
If you have any other BBSHD controller revision than 1.4 or 1.5, DO NOT PROCEED unless you can accept bricking your controller.  
If you have verified this firmware working on older BBSHD controller revisions, please let me know.  
If you have an older revision, run "Check MCU" and let me know the output and I may be able to tell if is could work or not.

**BBS02**  
There are compatibility issues reported, this firmware is suspected to be incompatible with older BBS02 controllers.  
If you have a newer BBS02B you are probably fine, if you have an older controller it might not be a good idéa to flash this firmware.

I am not responsible if you brick your controller, but it is unlikely if you follow this guide closely.

## Requirements

* [STC ISP Programming Software](http://www.stcmicro.com/rjxz.html)
* Programming Cable

## Download and Flash
[[/img/flash_tool.png|Flash Tool]]

1. Download and start the STC ISP Programming Tool (v6.88, do not update). 
2. Download the latest released firmware from the [release page](https://github.com/danielnilsson9/bbshd-fw/releases).
3. Extract the archive and locate the firmware .hex file intended for your controller type.
4. Connect your controller to your computer using the programming cable.
5. Select the correct COM port in the STC ISP programming tool.
6. Power of your controller. 
7. Click "Check MCU" and then power on your controller to verify.  
Log should say "Complete!" if connection was successful and the MCU type should be printed in the log.
8. Verify that the printed MCU type is one of the supported ones in tables [here](https://github.com/danielnilsson9/bbs-fw/blob/master/README.md), do not proceed if incorrect.
9. Set flashing parameters according to image below (very important!), pay special attention to highlighted areas.  
**Remember to set Input IRC Frequency to to 20MHz**  
NOTE: Selected MCU Type in image below is for BBSHD controller revision 1.5.
10. Open firmware file by clicking "Open Code File" button.
11. Power of controller.
12. Click "Download/Program" and power on your controller.
13. The flash operation should start.


If it fails, try again, it is a bit unstable.

## Linux
If you are running Linux you can try using the open source stcgal flashing software.  
https://github.com/grigorig/stcgal



