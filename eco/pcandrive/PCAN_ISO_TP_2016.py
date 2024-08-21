#  PCAN-ISO-TP_2016.py
#
#  ~~~~~~~~~~~~
#
#  PCAN-ISO-TP API 2016 (ISO 15765-2:2016)
#
#  ~~~~~~~~~~~~
#
#  ------------------------------------------------------------------
#	Last changed by:	$Author: Romain $
#  Last changed date:	$Date: 2022-05-19 09:33:18 +0200 (jeu., 19 mai 2022) $
#
#  Language: Python 2.7, 3.8
#  ------------------------------------------------------------------
#
#  Copyright (C) 2015  PEAK-System Technik GmbH, Darmstadt
#  more Info at http:#www.peak-system.com
#

# Module Imports
#
from ctypes import *
from string import *
import platform
import sys

from .PCANBasic import *

# Represents currently defined and supported PCANTP handle (a.k.a. channels)
cantp_handle = c_uint32

PCANTP_HANDLE_NONEBUS = cantp_handle(PCAN_NONEBUS.value) # Undefined/default value for a PCAN bus

PCANTP_HANDLE_ISABUS1 = cantp_handle(PCAN_ISABUS1.value) #PCAN-ISA interface, channel 1
PCANTP_HANDLE_ISABUS2 = cantp_handle(PCAN_ISABUS2.value) #PCAN-ISA interface, channel 2
PCANTP_HANDLE_ISABUS3 = cantp_handle(PCAN_ISABUS3.value) #PCAN-ISA interface, channel 3
PCANTP_HANDLE_ISABUS4 = cantp_handle(PCAN_ISABUS4.value) #PCAN-ISA interface, channel 4
PCANTP_HANDLE_ISABUS5 = cantp_handle(PCAN_ISABUS5.value) #PCAN-ISA interface, channel 5
PCANTP_HANDLE_ISABUS6 = cantp_handle(PCAN_ISABUS6.value) #PCAN-ISA interface, channel 6
PCANTP_HANDLE_ISABUS7 = cantp_handle(PCAN_ISABUS7.value) #PCAN-ISA interface, channel 7
PCANTP_HANDLE_ISABUS8 = cantp_handle(PCAN_ISABUS8.value) #PCAN-ISA interface, channel 8

PCANTP_HANDLE_DNGBUS1 = cantp_handle(PCAN_DNGBUS1.value) #PCAN-Dongle/LPT interface, channel 1

PCANTP_HANDLE_PCIBUS1 = cantp_handle(PCAN_PCIBUS1.value) #PCAN-PCI interface, channel 1
PCANTP_HANDLE_PCIBUS2 = cantp_handle(PCAN_PCIBUS2.value) #PCAN-PCI interface, channel 2
PCANTP_HANDLE_PCIBUS3 = cantp_handle(PCAN_PCIBUS3.value) #PCAN-PCI interface, channel 3
PCANTP_HANDLE_PCIBUS4 = cantp_handle(PCAN_PCIBUS4.value) #PCAN-PCI interface, channel 4
PCANTP_HANDLE_PCIBUS5 = cantp_handle(PCAN_PCIBUS5.value) #PCAN-PCI interface, channel 5
PCANTP_HANDLE_PCIBUS6 = cantp_handle(PCAN_PCIBUS6.value) #PCAN-PCI interface, channel 6
PCANTP_HANDLE_PCIBUS7 = cantp_handle(PCAN_PCIBUS7.value) #PCAN-PCI interface, channel 7
PCANTP_HANDLE_PCIBUS8 = cantp_handle(PCAN_PCIBUS8.value) #PCAN-PCI interface, channel 8
PCANTP_HANDLE_PCIBUS9 = cantp_handle(PCAN_PCIBUS9.value) #PCAN-PCI interface, channel 9
PCANTP_HANDLE_PCIBUS10 = cantp_handle(PCAN_PCIBUS10.value) #PCAN-PCI interface, channel 10
PCANTP_HANDLE_PCIBUS11 = cantp_handle(PCAN_PCIBUS11.value) #PCAN-PCI interface, channel 11
PCANTP_HANDLE_PCIBUS12 = cantp_handle(PCAN_PCIBUS12.value) #PCAN-PCI interface, channel 12
PCANTP_HANDLE_PCIBUS13 = cantp_handle(PCAN_PCIBUS13.value) #PCAN-PCI interface, channel 13
PCANTP_HANDLE_PCIBUS14 = cantp_handle(PCAN_PCIBUS14.value) #PCAN-PCI interface, channel 14
PCANTP_HANDLE_PCIBUS15 = cantp_handle(PCAN_PCIBUS15.value) #PCAN-PCI interface, channel 15
PCANTP_HANDLE_PCIBUS16 = cantp_handle(PCAN_PCIBUS16.value) #PCAN-PCI interface, channel 16

PCANTP_HANDLE_USBBUS1 = cantp_handle(PCAN_USBBUS1.value) #PCAN-USB interface, channel 1
PCANTP_HANDLE_USBBUS2 = cantp_handle(PCAN_USBBUS2.value) #PCAN-USB interface, channel 2
PCANTP_HANDLE_USBBUS3 = cantp_handle(PCAN_USBBUS3.value) #PCAN-USB interface, channel 3
PCANTP_HANDLE_USBBUS4 = cantp_handle(PCAN_USBBUS4.value) #PCAN-USB interface, channel 4
PCANTP_HANDLE_USBBUS5 = cantp_handle(PCAN_USBBUS5.value) #PCAN-USB interface, channel 5
PCANTP_HANDLE_USBBUS6 = cantp_handle(PCAN_USBBUS6.value) #PCAN-USB interface, channel 6
PCANTP_HANDLE_USBBUS7 = cantp_handle(PCAN_USBBUS7.value) #PCAN-USB interface, channel 7
PCANTP_HANDLE_USBBUS8 = cantp_handle(PCAN_USBBUS8.value) #PCAN-USB interface, channel 8
PCANTP_HANDLE_USBBUS9 = cantp_handle(PCAN_USBBUS9.value) #PCAN-USB interface, channel 9
PCANTP_HANDLE_USBBUS10 = cantp_handle(PCAN_USBBUS10.value) #PCAN-USB interface, channel 10
PCANTP_HANDLE_USBBUS11 = cantp_handle(PCAN_USBBUS11.value) #PCAN-USB interface, channel 11
PCANTP_HANDLE_USBBUS12 = cantp_handle(PCAN_USBBUS12.value) #PCAN-USB interface, channel 12
PCANTP_HANDLE_USBBUS13 = cantp_handle(PCAN_USBBUS13.value) #PCAN-USB interface, channel 13
PCANTP_HANDLE_USBBUS14 = cantp_handle(PCAN_USBBUS14.value) #PCAN-USB interface, channel 14
PCANTP_HANDLE_USBBUS15 = cantp_handle(PCAN_USBBUS15.value) #PCAN-USB interface, channel 15
PCANTP_HANDLE_USBBUS16 = cantp_handle(PCAN_USBBUS16.value) #PCAN-USB interface, channel 16

PCANTP_HANDLE_PCCBUS1 = cantp_handle(PCAN_PCCBUS1.value) #PCAN-PC Card interface, channel 1
PCANTP_HANDLE_PCCBUS2 = cantp_handle(PCAN_PCCBUS2.value) #PCAN-PC Card interface, channel 2

PCANTP_HANDLE_LANBUS1 = cantp_handle(PCAN_LANBUS1.value) #PCAN-LAN interface, channel 1
PCANTP_HANDLE_LANBUS2 = cantp_handle(PCAN_LANBUS2.value) #PCAN-LAN interface, channel 2
PCANTP_HANDLE_LANBUS3 = cantp_handle(PCAN_LANBUS3.value) #PCAN-LAN interface, channel 3
PCANTP_HANDLE_LANBUS4 = cantp_handle(PCAN_LANBUS4.value) #PCAN-LAN interface, channel 4
PCANTP_HANDLE_LANBUS5 = cantp_handle(PCAN_LANBUS5.value) #PCAN-LAN interface, channel 5
PCANTP_HANDLE_LANBUS6 = cantp_handle(PCAN_LANBUS6.value) #PCAN-LAN interface, channel 6
PCANTP_HANDLE_LANBUS7 = cantp_handle(PCAN_LANBUS7.value) #PCAN-LAN interface, channel 7
PCANTP_HANDLE_LANBUS8 = cantp_handle(PCAN_LANBUS8.value) #PCAN-LAN interface, channel 8
PCANTP_HANDLE_LANBUS9 = cantp_handle(PCAN_LANBUS9.value) #PCAN-LAN interface, channel 9
PCANTP_HANDLE_LANBUS10 = cantp_handle(PCAN_LANBUS10.value) #PCAN-LAN interface, channel 10
PCANTP_HANDLE_LANBUS11 = cantp_handle(PCAN_LANBUS11.value) #PCAN-LAN interface, channel 11
PCANTP_HANDLE_LANBUS12 = cantp_handle(PCAN_LANBUS12.value) #PCAN-LAN interface, channel 12
PCANTP_HANDLE_LANBUS13 = cantp_handle(PCAN_LANBUS13.value) #PCAN-LAN interface, channel 13
PCANTP_HANDLE_LANBUS14 = cantp_handle(PCAN_LANBUS14.value) #PCAN-LAN interface, channel 14
PCANTP_HANDLE_LANBUS15 = cantp_handle(PCAN_LANBUS15.value) #PCAN-LAN interface, channel 15
PCANTP_HANDLE_LANBUS16 = cantp_handle(PCAN_LANBUS16.value) #PCAN-LAN interface, channel 16

# Represents the baudrate register for the PCANTP channel
cantp_baudrate = c_uint32
PCANTP_BAUDRATE_1M = cantp_baudrate(PCAN_BAUD_1M.value) #Channel Baudrate 1 MBit/s
PCANTP_BAUDRATE_800K = cantp_baudrate(PCAN_BAUD_800K.value) #Channel Baudrate 800 kBit/s
PCANTP_BAUDRATE_500K = cantp_baudrate(PCAN_BAUD_500K.value) #Channel Baudrate 500 kBit/s
PCANTP_BAUDRATE_250K = cantp_baudrate(PCAN_BAUD_250K.value) #Channel Baudrate 250 kBit/s
PCANTP_BAUDRATE_125K = cantp_baudrate(PCAN_BAUD_125K.value) #Channel Baudrate 125 kBit/s
PCANTP_BAUDRATE_100K = cantp_baudrate(PCAN_BAUD_100K.value) #Channel Baudrate 100 kBit/s
PCANTP_BAUDRATE_95K = cantp_baudrate(PCAN_BAUD_95K.value) #Channel Baudrate 95,238 kBit/s
PCANTP_BAUDRATE_83K = cantp_baudrate(PCAN_BAUD_83K.value) #Channel Baudrate 83,333 kBit/s
PCANTP_BAUDRATE_50K = cantp_baudrate(PCAN_BAUD_50K.value) #Channel Baudrate 50 kBit/s
PCANTP_BAUDRATE_47K = cantp_baudrate(PCAN_BAUD_47K.value) #Channel Baudrate 47,619 kBit/s
PCANTP_BAUDRATE_33K = cantp_baudrate(PCAN_BAUD_33K.value) #Channel Baudrate 33,333 kBit/s
PCANTP_BAUDRATE_20K = cantp_baudrate(PCAN_BAUD_20K.value) #Channel Baudrate 20 kBit/s
PCANTP_BAUDRATE_10K = cantp_baudrate(PCAN_BAUD_10K.value) #Channel Baudrate 10 kBit/s
PCANTP_BAUDRATE_5K = cantp_baudrate(PCAN_BAUD_5K.value) #Channel Baudrate 5 kBit/s

# Type of PCAN (non plug-n-play) hardware
cantp_hwtype = c_uint32
PCANTP_HWTYPE_ISA = cantp_hwtype(PCAN_TYPE_ISA.value) #PCAN-ISA 82C200
PCANTP_HWTYPE_ISA_SJA = cantp_hwtype(PCAN_TYPE_ISA_SJA.value) #PCAN-ISA SJA1000
PCANTP_HWTYPE_ISA_PHYTEC = cantp_hwtype(PCAN_TYPE_ISA_PHYTEC.value) #PHYTEC ISA
PCANTP_HWTYPE_DNG = cantp_hwtype(PCAN_TYPE_DNG.value) #PCAN-Dongle 82C200
PCANTP_HWTYPE_DNG_EPP = cantp_hwtype(PCAN_TYPE_DNG_EPP.value) #PCAN-Dongle EPP 82C200
PCANTP_HWTYPE_DNG_SJA = cantp_hwtype(PCAN_TYPE_DNG_SJA.value) #PCAN-Dongle SJA1000
PCANTP_HWTYPE_DNG_SJA_EPP = cantp_hwtype(PCAN_TYPE_DNG_SJA_EPP.value) #PCAN-Dongle EPP SJA1000

# PCAN devices
cantp_device = c_uint32
PCANTP_DEVICE_NONE = cantp_device(PCAN_NONE.value) #Undefined, unknown or not selected PCAN device value
PCANTP_DEVICE_PEAKCAN = cantp_device(PCAN_PEAKCAN.value) #PCAN Non-Plug&Play devices. NOT USED WITHIN PCAN-Basic API
PCANTP_DEVICE_ISA = cantp_device(PCAN_ISA.value) #PCAN-ISA, PCAN-PC/104, and PCAN-PC/104-Plus
PCANTP_DEVICE_DNG = cantp_device(PCAN_DNG.value) #PCAN-Dongle
PCANTP_DEVICE_PCI = cantp_device(PCAN_PCI.value) #PCAN-PCI, PCAN-cPCI, PCAN-miniPCI, and PCAN-PCI Express
PCANTP_DEVICE_USB = cantp_device(PCAN_USB.value) #PCAN-USB and PCAN-USB Pro
PCANTP_DEVICE_PCC = cantp_device(PCAN_PCC.value) #PCAN-PC Card
PCANTP_DEVICE_VIRTUAL = cantp_device(PCAN_VIRTUAL.value) #PCAN Virtual hardware. NOT USED WITHIN PCAN-Basic API
PCANTP_DEVICE_LAN = cantp_device(PCAN_LAN.value) #PCAN Gateway devices

# Represents the configuration for a CAN bit rate
# Note:
#    * Each parameter and its value must be separated with a '='.
#    * Each pair of parameter/value must be separated using ','.
#
# Example:
#    f_clock=80000000,nom_brp=10,nom_tseg1=5,nom_tseg2=2,nom_sjw=1,data_brp=4,data_tseg1=7,data_tseg2=2,data_sjw=1
#
PCANTP_BITRATE_CLOCK		=PCAN_BR_CLOCK
PCANTP_BITRATE_CLOCK_MHZ	=PCAN_BR_CLOCK_MHZ
PCANTP_BITRATE_NOM_BRP		=PCAN_BR_NOM_BRP
PCANTP_BITRATE_NOM_TSEG1	=PCAN_BR_NOM_TSEG1
PCANTP_BITRATE_NOM_TSEG2	=PCAN_BR_NOM_TSEG2
PCANTP_BITRATE_NOM_SJW		=PCAN_BR_NOM_SJW
PCANTP_BITRATE_NOM_SAMPLE	=PCAN_BR_NOM_SAMPLE
PCANTP_BITRATE_DATA_BRP		=PCAN_BR_DATA_BRP
PCANTP_BITRATE_DATA_TSEG1	=PCAN_BR_DATA_TSEG1
PCANTP_BITRATE_DATA_TSEG2	=PCAN_BR_DATA_TSEG2
PCANTP_BITRATE_DATA_SJW		=PCAN_BR_DATA_SJW
PCANTP_BITRATE_DATA_SAMPLE	=PCAN_BR_DATA_SAMPLE

#//////////////////////////////////////////////////////////
# Enums definition for ISO-TP API
#//////////////////////////////////////////////////////////

# Represents each group of errors a status can hold
cantp_statustype = c_uint32
PCANTP_STATUSTYPE_OK= cantp_statustype(0X00) # no error
PCANTP_STATUSTYPE_ERR= cantp_statustype(0X01) # general error
PCANTP_STATUSTYPE_BUS= cantp_statustype(0X02) # bus status
PCANTP_STATUSTYPE_NET= cantp_statustype(0X04) # network status
PCANTP_STATUSTYPE_INFO= cantp_statustype(0X08) # extra information
PCANTP_STATUSTYPE_PCAN= cantp_statustype(0X10) # encapsulated PCAN-Basic status

# Represents the network result of the communication of an ISO-TP message (used in cantp_status).
cantp_netstatus = c_uint32
# ISO-TP network errors:
PCANTP_NETSTATUS_OK = cantp_netstatus(0X00) # No network error
PCANTP_NETSTATUS_TIMEOUT_A = cantp_netstatus(0X01) # timeout occured between 2 frames transmission (sender and receiver side)
PCANTP_NETSTATUS_TIMEOUT_Bs = cantp_netstatus(0X02) # sender side timeout while waiting for flow control frame
PCANTP_NETSTATUS_TIMEOUT_Cr = cantp_netstatus(0X03) # receiver side timeout while waiting for consecutive frame
PCANTP_NETSTATUS_WRONG_SN = cantp_netstatus(0X04) # unexpected sequence number
PCANTP_NETSTATUS_INVALID_FS = cantp_netstatus(0X05) # invalid or unknown FlowStatus
PCANTP_NETSTATUS_UNEXP_PDU = cantp_netstatus(0X06) # unexpected protocol data unit
PCANTP_NETSTATUS_WFT_OVRN = cantp_netstatus(0X07) # reception of flow control WAIT frame that exceeds the maximum counter defined by PCANTP_PARAMETER_WFT_MAX
PCANTP_NETSTATUS_BUFFER_OVFLW = cantp_netstatus(0X08) # buffer on the receiver side cannot store the data length (server side only)
PCANTP_NETSTATUS_ERROR = cantp_netstatus(0X09) # general error
PCANTP_NETSTATUS_IGNORED = cantp_netstatus(0X0A) # message was invalid and ignored
PCANTP_NETSTATUS_TIMEOUT_As = cantp_netstatus(0X0B) # sender side timeout while transmitting
PCANTP_NETSTATUS_TIMEOUT_Ar = cantp_netstatus(0X0C) # receiver side timeout while transmitting
# NON ISO-TP related network results:
PCANTP_NETSTATUS_XMT_FULL = cantp_netstatus(0X0D) # transmit queue is full (failed too many times)
PCANTP_NETSTATUS_BUS_ERROR = cantp_netstatus(0X0E) # CAN bus error
PCANTP_NETSTATUS_NO_MEMORY = cantp_netstatus(0X0F) # memory allocation error

# Represents the status of a CAN bus (used in cantp_status).
cantp_busstatus = c_uint32
PCANTP_BUSSTATUS_OK = cantp_busstatus(0X00) # Bus is in active state
PCANTP_BUSSTATUS_LIGHT = cantp_busstatus(0X01) # Bus error: an error counter reached the 'light' limit
PCANTP_BUSSTATUS_HEAVY = cantp_busstatus(0X02) # Bus error: an error counter reached the 'heavy' limit
PCANTP_BUSSTATUS_WARNING = PCANTP_BUSSTATUS_HEAVY # Bus error: an error counter reached the 'warning/heavy' limit
PCANTP_BUSSTATUS_PASSIVE = cantp_busstatus(0X04) # Bus error: the CAN controller is error passive
PCANTP_BUSSTATUS_OFF = cantp_busstatus(0X08) # Bus error: the CAN controller is in bus-off state
PCANTP_BUSSTATUS_ANY = cantp_busstatus(PCANTP_BUSSTATUS_LIGHT.value | PCANTP_BUSSTATUS_HEAVY.value | PCANTP_BUSSTATUS_WARNING.value | PCANTP_BUSSTATUS_PASSIVE.value | PCANTP_BUSSTATUS_OFF.value) # Mask for all bus errors

# Represents an general error (used in cantp_status).
cantp_errstatus = c_uint32
PCANTP_ERRSTATUS_OK = cantp_errstatus(0X00) # No error
PCANTP_ERRSTATUS_NOT_INITIALIZED = cantp_errstatus(0X01) # Not Initialized
PCANTP_ERRSTATUS_ALREADY_INITIALIZED = cantp_errstatus(0X02) # Already Initialized
PCANTP_ERRSTATUS_NO_MEMORY = cantp_errstatus(0X03) # Could not obtain memory
PCANTP_ERRSTATUS_OVERFLOW = cantp_errstatus(0X04) # Input buffer overflow
PCANTP_ERRSTATUS_NO_MESSAGE = cantp_errstatus(0X07) # No Message available
PCANTP_ERRSTATUS_PARAM_INVALID_TYPE = cantp_errstatus(0X08) # Parameter has an invalid or unexpected type
PCANTP_ERRSTATUS_PARAM_INVALID_VALUE = cantp_errstatus(0X09) # Parameter has an invalid value
PCANTP_ERRSTATUS_MAPPING_NOT_INITIALIZED = cantp_errstatus(0X0D) # PCANTP mapping not initialized
PCANTP_ERRSTATUS_MAPPING_INVALID = cantp_errstatus(0X0E) # PCANTP mapping parameters are invalid
PCANTP_ERRSTATUS_MAPPING_ALREADY_INITIALIZED = cantp_errstatus(0X0F) # PCANTP mapping already defined
PCANTP_ERRSTATUS_PARAM_BUFFER_TOO_SMALL = cantp_errstatus(0X10)
PCANTP_ERRSTATUS_QUEUE_TX_FULL = cantp_errstatus(0X11) # Tx queue is full
PCANTP_ERRSTATUS_LOCK_TIMEOUT = cantp_errstatus(0X12) # Failed to get an access to the internal lock
PCANTP_ERRSTATUS_INVALID_HANDLE = cantp_errstatus(0X13) # Invalid cantp_handle
PCANTP_ERRSTATUS_UNKNOWN = cantp_errstatus(0XFF) # unknown/generic error

# Represents additional status information (used in cantp_status).
cantp_infostatus = c_uint32
PCANTP_INFOSTATUS_OK = cantp_infostatus(0X00) # no extra information
PCANTP_INFOSTATUS_CAUTION_INPUT_MODIFIED = cantp_infostatus(0X01) # input was modified by the API
PCANTP_INFOSTATUS_CAUTION_DLC_MODIFIED = cantp_infostatus(0X02) # DLC value was modified by the API
PCANTP_INFOSTATUS_CAUTION_DATA_LENGTH_MODIFIED = cantp_infostatus(0X04) # Data Length value was modified by the API
PCANTP_INFOSTATUS_CAUTION_FD_FLAG_MODIFIED = cantp_infostatus(0X08) # FD related flags value were modified by the API
PCANTP_INFOSTATUS_CAUTION_RX_QUEUE_FULL = cantp_infostatus(0X10) # Message receive queue is full (oldest messages may be lost)
PCANTP_INFOSTATUS_CAUTION_BUFFER_IN_USE = cantp_infostatus(0X20) # Buffer is used by another thread or API

# Represents the PCAN error and status codes
cantp_pcanstatus = c_uint32

# Defines constants used by the next enum: cantp_status
PCANTP_STATUS_OFFSET_BUS	=8
PCANTP_STATUS_OFFSET_NET	=(PCANTP_STATUS_OFFSET_BUS + 5)
PCANTP_STATUS_OFFSET_INFO	=(PCANTP_STATUS_OFFSET_NET + 5)

# Represents the PCANTP error and status codes.
#
# Bits information:
#   32|  28|  24|  20|  16|  12|   8|   4|   0|
#     |    |    |    |    |    |    |    |    |
#      0000 0000 0000 0000 0000 0000 0000 0000
#     |    |    |    |    |         [0000 0000] => PCAN-ISO-TP API errors
#     |    |    |    |    |  [0 0000]           => CAN Bus status
#     |    |    |    | [00 000]                 => Networking message status
#     |    |    [0000 00]                       => API extra information
#     |[000 0000]                               => Reserved
#     [0]                                       => PCANBasic error flag (overrides the meaning of all bits)
cantp_status = c_uint32
PCANTP_STATUS_OK = cantp_status(PCANTP_ERRSTATUS_OK.value) 
PCANTP_STATUS_NOT_INITIALIZED = cantp_status(PCANTP_ERRSTATUS_NOT_INITIALIZED.value)
PCANTP_STATUS_ALREADY_INITIALIZED = cantp_status(PCANTP_ERRSTATUS_ALREADY_INITIALIZED.value)
PCANTP_STATUS_NO_MEMORY = cantp_status(PCANTP_ERRSTATUS_NO_MEMORY.value)
PCANTP_STATUS_OVERFLOW = cantp_status(PCANTP_ERRSTATUS_OVERFLOW.value)
PCANTP_STATUS_NO_MESSAGE = cantp_status(PCANTP_ERRSTATUS_NO_MESSAGE.value)
PCANTP_STATUS_PARAM_INVALID_TYPE = cantp_status(PCANTP_ERRSTATUS_PARAM_INVALID_TYPE.value)
PCANTP_STATUS_PARAM_INVALID_VALUE = cantp_status(PCANTP_ERRSTATUS_PARAM_INVALID_VALUE.value)
PCANTP_STATUS_MAPPING_NOT_INITIALIZED = cantp_status(PCANTP_ERRSTATUS_MAPPING_NOT_INITIALIZED.value)
PCANTP_STATUS_MAPPING_INVALID = cantp_status(PCANTP_ERRSTATUS_MAPPING_INVALID.value)
PCANTP_STATUS_MAPPING_ALREADY_INITIALIZED = cantp_status(PCANTP_ERRSTATUS_MAPPING_ALREADY_INITIALIZED.value)
PCANTP_STATUS_PARAM_BUFFER_TOO_SMALL = cantp_status(PCANTP_ERRSTATUS_PARAM_BUFFER_TOO_SMALL.value)
PCANTP_STATUS_QUEUE_TX_FULL = cantp_status(PCANTP_ERRSTATUS_QUEUE_TX_FULL.value)
PCANTP_STATUS_LOCK_TIMEOUT = cantp_status(PCANTP_ERRSTATUS_LOCK_TIMEOUT.value)
PCANTP_STATUS_HANDLE_INVALID = cantp_status(PCANTP_ERRSTATUS_INVALID_HANDLE.value)
PCANTP_STATUS_UNKNOWN = cantp_status(PCANTP_ERRSTATUS_UNKNOWN.value)
# Bus status flags (bits [8..11])
PCANTP_STATUS_FLAG_BUS_LIGHT = cantp_status(PCANTP_BUSSTATUS_LIGHT.value << PCANTP_STATUS_OFFSET_BUS) # PCANTP Channel is in BUS-LIGHT error state
PCANTP_STATUS_FLAG_BUS_HEAVY = cantp_status(PCANTP_BUSSTATUS_HEAVY.value << PCANTP_STATUS_OFFSET_BUS) # PCANTP Channel is in BUS-HEAVY error state
PCANTP_STATUS_FLAG_BUS_WARNING = PCANTP_STATUS_FLAG_BUS_HEAVY # PCANTP Channel is in BUS-HEAVY error state
PCANTP_STATUS_FLAG_BUS_PASSIVE = cantp_status(PCANTP_BUSSTATUS_PASSIVE.value << PCANTP_STATUS_OFFSET_BUS) # PCANTP Channel is error passive state
PCANTP_STATUS_FLAG_BUS_OFF = cantp_status(PCANTP_BUSSTATUS_OFF.value << PCANTP_STATUS_OFFSET_BUS) # PCANTP Channel is in BUS-OFF error state
PCANTP_STATUS_FLAG_BUS_ANY = cantp_status(PCANTP_BUSSTATUS_ANY.value << PCANTP_STATUS_OFFSET_BUS)
# Network status (bits [13..17])
PCANTP_STATUS_FLAG_NETWORK_RESULT = cantp_status(1 << PCANTP_STATUS_OFFSET_NET) # This flag states if one of the following network errors occured with the fetched message
PCANTP_STATUS_NETWORK_TIMEOUT_A = cantp_status(PCANTP_STATUS_FLAG_NETWORK_RESULT.value | (PCANTP_NETSTATUS_TIMEOUT_A.value << (PCANTP_STATUS_OFFSET_NET + 1))) # timeout occured between 2 frames transmission (sender and receiver side)
PCANTP_STATUS_NETWORK_TIMEOUT_Bs = cantp_status(PCANTP_STATUS_FLAG_NETWORK_RESULT.value | (PCANTP_NETSTATUS_TIMEOUT_Bs.value << (PCANTP_STATUS_OFFSET_NET + 1))) # sender side timeout while waiting for flow control frame
PCANTP_STATUS_NETWORK_TIMEOUT_Cr = cantp_status(PCANTP_STATUS_FLAG_NETWORK_RESULT.value | (PCANTP_NETSTATUS_TIMEOUT_Cr.value << (PCANTP_STATUS_OFFSET_NET + 1))) # receiver side timeout while waiting for consecutive frame
PCANTP_STATUS_NETWORK_WRONG_SN = cantp_status(PCANTP_STATUS_FLAG_NETWORK_RESULT.value | (PCANTP_NETSTATUS_WRONG_SN.value << (PCANTP_STATUS_OFFSET_NET + 1))) # unexpected sequence number
PCANTP_STATUS_NETWORK_INVALID_FS = cantp_status(PCANTP_STATUS_FLAG_NETWORK_RESULT.value | (PCANTP_NETSTATUS_INVALID_FS.value << (PCANTP_STATUS_OFFSET_NET + 1))) # invalid or unknown FlowStatus
PCANTP_STATUS_NETWORK_UNEXP_PDU = cantp_status(PCANTP_STATUS_FLAG_NETWORK_RESULT.value | (PCANTP_NETSTATUS_UNEXP_PDU.value << (PCANTP_STATUS_OFFSET_NET + 1))) # unexpected protocol data unit
PCANTP_STATUS_NETWORK_WFT_OVRN = cantp_status(PCANTP_STATUS_FLAG_NETWORK_RESULT.value | (PCANTP_NETSTATUS_WFT_OVRN.value << (PCANTP_STATUS_OFFSET_NET + 1))) # reception of flow control WAIT frame that exceeds the maximum counter defined by PCANTP_PARAMETER_WFT_MAX
PCANTP_STATUS_NETWORK_BUFFER_OVFLW = cantp_status(PCANTP_STATUS_FLAG_NETWORK_RESULT.value | (PCANTP_NETSTATUS_BUFFER_OVFLW.value << (PCANTP_STATUS_OFFSET_NET + 1))) # buffer on the receiver side cannot store the data length (server side only)
PCANTP_STATUS_NETWORK_ERROR = cantp_status(PCANTP_STATUS_FLAG_NETWORK_RESULT.value | (PCANTP_NETSTATUS_ERROR.value << (PCANTP_STATUS_OFFSET_NET + 1))) # general error
PCANTP_STATUS_NETWORK_IGNORED = cantp_status(PCANTP_STATUS_FLAG_NETWORK_RESULT.value | (PCANTP_NETSTATUS_IGNORED.value << (PCANTP_STATUS_OFFSET_NET + 1))) # message was invalid and ignored
PCANTP_STATUS_NETWORK_TIMEOUT_Ar = cantp_status(PCANTP_STATUS_FLAG_NETWORK_RESULT.value | (PCANTP_NETSTATUS_TIMEOUT_Ar.value << (PCANTP_STATUS_OFFSET_NET + 1))) # receiver side timeout while transmitting
PCANTP_STATUS_NETWORK_TIMEOUT_As = cantp_status(PCANTP_STATUS_FLAG_NETWORK_RESULT.value | (PCANTP_NETSTATUS_TIMEOUT_As.value << (PCANTP_STATUS_OFFSET_NET + 1))) # sender side timeout while transmitting
# ISO-TP extra information flags
PCANTP_STATUS_CAUTION_INPUT_MODIFIED = cantp_status(PCANTP_INFOSTATUS_CAUTION_INPUT_MODIFIED.value << PCANTP_STATUS_OFFSET_INFO) # input was modified
PCANTP_STATUS_CAUTION_DLC_MODIFIED = cantp_status(PCANTP_INFOSTATUS_CAUTION_DLC_MODIFIED.value << PCANTP_STATUS_OFFSET_INFO) # DLC value of the input was modified
PCANTP_STATUS_CAUTION_DATA_LENGTH_MODIFIED = cantp_status(PCANTP_INFOSTATUS_CAUTION_DATA_LENGTH_MODIFIED.value << PCANTP_STATUS_OFFSET_INFO) # Data Length value of the input was modified
PCANTP_STATUS_CAUTION_FD_FLAG_MODIFIED = cantp_status(PCANTP_INFOSTATUS_CAUTION_FD_FLAG_MODIFIED.value << PCANTP_STATUS_OFFSET_INFO) # FD flags of the input was modified
PCANTP_STATUS_CAUTION_RX_QUEUE_FULL = cantp_status(PCANTP_INFOSTATUS_CAUTION_RX_QUEUE_FULL.value << PCANTP_STATUS_OFFSET_INFO) # Receive queue is full
PCANTP_STATUS_CAUTION_BUFFER_IN_USE = cantp_status(PCANTP_INFOSTATUS_CAUTION_BUFFER_IN_USE.value << PCANTP_STATUS_OFFSET_INFO) # Buffer is used by another thread or API
# Lower API status code: see also PCANTP_STATUS_xx macros
PCANTP_STATUS_FLAG_PCAN_STATUS = cantp_status(0X80000000) # PCAN error flag, remove flag to get a usable PCAN error/status code (cf. PCANBasic API)
# Masks to merge/retrieve different PCANTP status by type in a cantp_status
PCANTP_STATUS_MASK_ERROR = cantp_status(0X000000FF) # filter by PCANTP_STATUSTYPE_ERR type
PCANTP_STATUS_MASK_BUS = cantp_status(0X00001F00) # filter by PCANTP_STATUSTYPE_BUS type
PCANTP_STATUS_MASK_ISOTP_NET = cantp_status(0X0003E000) # filter by PCANTP_STATUSTYPE_NET type
PCANTP_STATUS_MASK_INFO = cantp_status(0X00FC0000) # filter by PCANTP_STATUSTYPE_INFO type
PCANTP_STATUS_MASK_PCAN = cantp_status(~PCANTP_STATUS_FLAG_PCAN_STATUS.value) # filter by PCANTP_STATUSTYPE_PCAN type

# List of parameters handled by PCAN-ISO-TP (rev. 2016)
#	Note: PCAN-Basic parameters (PCAN_PARAM_xxx) are compatible via casting.
cantp_parameter = c_uint32
PCANTP_PARAMETER_API_VERSION= cantp_parameter(0X101) # PCAN-ISO-TP API version parameter
PCANTP_PARAMETER_CHANNEL_CONDITION= cantp_parameter(0X102) # 1 BYTE data describing the condition of a channel.
PCANTP_PARAMETER_DEBUG= cantp_parameter(0X103) # 1 BYTE data describing the debug mode
PCANTP_PARAMETER_RECEIVE_EVENT= cantp_parameter(0X104) # data is pointer to a HANDLE created by CreateEvent function

PCANTP_PARAMETER_FRAME_FILTERING= cantp_parameter(0X105) # 1 BYTE data stating if unsegmented (NON-ISO-TP) CAN frames can be received
PCANTP_PARAMETER_CAN_TX_DL= cantp_parameter(0X106) # 1 BYTE data stating the default DLC to use when transmitting messages with CAN FD
PCANTP_PARAMETER_CAN_DATA_PADDING= cantp_parameter(0X107) # 1 BYTE data stating if CAN frame DLC uses padding or not
PCANTP_PARAMETER_CAN_PADDING_VALUE= cantp_parameter(0X108) # 1 BYTE data stating the value used for CAN data padding
PCANTP_PARAMETER_ISO_REV= cantp_parameter(0X109) # 1 BYTE data stating which revision of ISO 15765-2 to use (see PCANTP_ISO_REV_*).
PCANTP_PARAMETER_J1939_PRIORITY= cantp_parameter(0X10A) # 1 BYTE data stating the default priority value for normal fixed, mixed and enhanced addressing (default=6)
PCANTP_PARAMETER_MSG_PENDING= cantp_parameter(0X10B) # 1 BYTE data stating if pending messages are displayed/hidden

PCANTP_PARAMETER_BLOCK_SIZE= cantp_parameter(0X10C) # 1 BYTE data describing the block size parameter (BS)
PCANTP_PARAMETER_BLOCK_SIZE_TX= cantp_parameter(0X10D) # 2 BYTE data describing the transmit block size parameter (BS_TX)
PCANTP_PARAMETER_SEPARATION_TIME= cantp_parameter(0X10E) # 1 BYTE data describing the seperation time parameter (STmin)
PCANTP_PARAMETER_SEPARATION_TIME_TX= cantp_parameter(0X10F) # 2 BYTE data describing the transmit seperation time parameter (STmin_TX)
PCANTP_PARAMETER_WFT_MAX= cantp_parameter(0X123) # 4 BYTE data describing the Wait Frame Transmissions parameter (maximum number of WFT FC frame a receiver can send).
PCANTP_PARAMETER_WFT_MAX_TX= cantp_parameter(0X110) # 4 BYTE data describing the transmit Wait Frame Transmissions parameter (WFT_TX as maximum number of WFT FC frame a transmitter can receive).

PCANTP_PARAMETER_TIMEOUT_AS= cantp_parameter(0X111) # 4 BYTE data describing ISO-15765-2:Timeout As.
PCANTP_PARAMETER_TIMEOUT_AR= cantp_parameter(0X112) # 4 BYTE data describing ISO-15765-2:Timeout Ar.
PCANTP_PARAMETER_TIMEOUT_BR= cantp_parameter(0X121) # 4 BYTE data describing ISO-15765-2:Timeout Br.
PCANTP_PARAMETER_TIMEOUT_BS= cantp_parameter(0X113) # 4 BYTE data describing ISO-15765-2:Timeout Bs.
PCANTP_PARAMETER_TIMEOUT_CR= cantp_parameter(0X114) # 4 BYTE data describing ISO-15765-2:Timeout Cr.
PCANTP_PARAMETER_TIMEOUT_CS= cantp_parameter(0X122) # 4 BYTE data describing ISO-15765-2:Timeout Cs.
PCANTP_PARAMETER_TIMEOUT_TOLERANCE= cantp_parameter(0X115) # 1 BYTE data describing the tolerence to apply to all timeout as a percentage ([0..100].
PCANTP_PARAMETER_ISO_TIMEOUTS= cantp_parameter(0X116) # 1 BYTE data to set predefined ISO values for timeouts (see PCANTP_ISO_TIMEOUTS_*).

PCANTP_PARAMETER_SELFRECEIVE_LATENCY= cantp_parameter(0X117) # 1 BYTE data to set optimization options to improve delay between ISO-TP consecutive frames.
PCANTP_PARAMETER_MAX_RX_QUEUE= cantp_parameter(0X118) # 2 BYTE data describing the maximum number of messages in the Rx queue.
PCANTP_PARAMETER_KEEP_HIGHER_LAYER_MESSAGES= cantp_parameter(0X119) # 1 BYTE data stating if messages handled by higher layer APIs are still available in this API (default=0).
PCANTP_PARAMETER_FILTER_CAN_ID= cantp_parameter(0X11A) # 1 BYTE data stating if the white-list CAN IDs filtering mechanism is enabled.
PCANTP_PARAMETER_SUPPORT_29B_ENHANCED= cantp_parameter(0X11B) # 1 BYTE data stating if the 29 bit Enhanced Diagnostic CAN identifier is supported (ISO-15765-3:2004, default is false with ISO revision 2016).
PCANTP_PARAMETER_SUPPORT_29B_FIXED_NORMAL= cantp_parameter(0X11C) # 1 BYTE data stating if the 29 bit Fixed Normal addressing CAN identifier is supported (default is true).
PCANTP_PARAMETER_SUPPORT_29B_MIXED= cantp_parameter(0X11D) # 1 BYTE data stating if the 29 bit Mixed addressing CAN identifier is supported (default is true).
PCANTP_PARAMETER_MSG_CHECK= cantp_parameter(0X11E) # Pointer to a cantp_msg, checks if the message is valid and can be sent (ex. if a mapping is needed) and corrects input if needed.
PCANTP_PARAMETER_RESET_HARD= cantp_parameter(0X11F) # 1 BYTE data stating to clear Rx/Tx queues and CAN controller (channel is unitialized and re-initialized but settings and mappings are kept)
PCANTP_PARAMETER_NETWORK_LAYER_DESIGN= cantp_parameter(0X120) # 1 BYTE data stating if network is full-duplex (default) or half-duplex
#PCANTP_PARAMETER_TIMEOUT_BR= cantp_parameter(0x121,		// 4 BYTE data describing ISO-15765-2:Timeout Br.
#PCANTP_PARAMETER_TIMEOUT_CS= cantp_parameter(0x122,		// 4 BYTE data describing ISO-15765-2:Timeout Cs.
#PCANTP_PARAMETER_WFT_MAX= cantp_parameter(0x123,			// 4 BYTE data describing the Wait Frame Transmissions parameter (maximum number of WFT FC frame a receiver can send).
PCANTP_PARAMETER_ALLOW_MSGTYPE_CANINFO= cantp_parameter(0X124) # 1 BYTE data stating if API allows receiption PCANTP_MSGTYPE_CANINFO from lower layer APIs
PCANTP_PARAMETER_RECEIVE_EVENT_CALLBACK= cantp_parameter(0X125) # Data is a pointer to a user-defined callback triggered when a message is received.
PCANTP_PARAMETER_RECEIVE_EVENT_CALLBACK_USER_CONTEXT= cantp_parameter(0X126) # Data is a pointer to a user-defined structure. It can be used to pass user arguments to the reception callback function.

PCANTP_PARAMETER_HARDWARE_NAME= cantp_parameter(PCAN_HARDWARE_NAME.value) # PCAN hardware name parameter
PCANTP_PARAMETER_DEVICE_ID= cantp_parameter(PCAN_DEVICE_ID.value) # PCAN-USB device identifier parameter
PCANTP_PARAMETER_DEVICE_NUMBER= cantp_parameter(PCAN_DEVICE_ID.value) # deprecated use PCANTP_PARAMETER_DEVICE_ID instead
PCANTP_PARAMETER_CONTROLLER_NUMBER= cantp_parameter(PCAN_CONTROLLER_NUMBER.value) # CAN-Controller number of a PCAN-Channel
PCANTP_PARAMETER_CHANNEL_FEATURES= cantp_parameter(PCAN_CHANNEL_FEATURES.value) # Capabilities of a PCAN device (FEATURE_***)

# Represents the type of a CANTP message (see field "cantp_msg.type").
cantp_msgtype = c_uint32
PCANTP_MSGTYPE_NONE = cantp_msgtype(0X00) # uninitialized message (data is NULL)
PCANTP_MSGTYPE_CAN = cantp_msgtype(0X01) # standard CAN frame
PCANTP_MSGTYPE_CANFD = cantp_msgtype(0X02) # CAN frame with FD support
PCANTP_MSGTYPE_ISOTP = cantp_msgtype(0X04) # ISO-TP message (ISO:15765)
PCANTP_MSGTYPE_CANINFO = cantp_msgtype(0X08) # CAN bus information

PCANTP_MSGTYPE_FRAME = cantp_msgtype(PCANTP_MSGTYPE_CAN.value | PCANTP_MSGTYPE_CANFD.value) # frame only: unsegmented messages
PCANTP_MSGTYPE_ANY = cantp_msgtype(PCANTP_MSGTYPE_FRAME.value | PCANTP_MSGTYPE_ISOTP.value | 0XFFFFFFFF) # any supported message type

# Represents the flags common to all types of cantp_msg (see field "cantp_msg.msgdata.flags").
cantp_msgflag = c_uint32
PCANTP_MSGFLAG_NONE = cantp_msgflag(0) # no flag
PCANTP_MSGFLAG_LOOPBACK = cantp_msgflag(1) # message is the confirmation of a transmitted message
PCANTP_MSGFLAG_ISOTP_FRAME = cantp_msgflag(2) # message is a frame of a segmented ISO-TP message


# Represents the flags of a CAN or CAN FD frame (must be used as flags for ex. EXTENDED|FD|BRS.) (see field "cantp_msg.can_info.can_msgtype")
cantp_can_msgtype = c_uint32
PCANTP_CAN_MSGTYPE_STANDARD = cantp_can_msgtype(PCAN_MESSAGE_STANDARD.value) # The PCAN message is a CAN Standard Frame (11-bit identifier)
PCANTP_CAN_MSGTYPE_RTR = cantp_can_msgtype(PCAN_MESSAGE_RTR.value) # The PCAN message is a CAN Remote-Transfer-Request Frame
PCANTP_CAN_MSGTYPE_EXTENDED = cantp_can_msgtype(PCAN_MESSAGE_EXTENDED.value) # The PCAN message is a CAN Extended Frame (29-bit identifier)
PCANTP_CAN_MSGTYPE_FD = cantp_can_msgtype(PCAN_MESSAGE_FD.value) # The PCAN message represents a FD frame in terms of CiA Specs
PCANTP_CAN_MSGTYPE_BRS = cantp_can_msgtype(PCAN_MESSAGE_BRS.value) # The PCAN message represents a FD bit rate switch (CAN data at a higher bit rate)
PCANTP_CAN_MSGTYPE_ESI = cantp_can_msgtype(PCAN_MESSAGE_ESI.value) # The PCAN message represents a FD error state indicator(CAN FD transmitter was error active)
PCANTP_CAN_MSGTYPE_ERRFRAME = cantp_can_msgtype(PCAN_MESSAGE_ERRFRAME.value) # The PCAN message represents an error frame.
PCANTP_CAN_MSGTYPE_STATUS = cantp_can_msgtype(PCAN_MESSAGE_STATUS.value) # The PCAN message represents a PCAN status message.
PCANTP_CAN_MSGTYPE_ECHO = cantp_can_msgtype(PCAN_MESSAGE_ECHO.value) # Echo messages reception status within a PCAN-Channel
PCANTP_CAN_MSGTYPE_FLAG_INFO = cantp_can_msgtype(PCAN_MESSAGE_ERRFRAME.value | PCAN_MESSAGE_STATUS.value) # Flag stating that the message is not a CAN Frame

# Represents the type of an ISO-TP message (see field "cantp_msg.msgdata.isotp.netaddrinfo.msgtype").
cantp_isotp_msgtype = c_uint32
PCANTP_ISOTP_MSGTYPE_UNKNOWN = cantp_isotp_msgtype(0X00) # Unknown (non-ISO-TP) message
PCANTP_ISOTP_MSGTYPE_DIAGNOSTIC = cantp_isotp_msgtype(0X01) # Diagnostic message (request or confirmation)
PCANTP_ISOTP_MSGTYPE_REMOTE_DIAGNOSTIC = cantp_isotp_msgtype(0X02) # Remote Diagnostic message (request or confirmation)
PCANTP_ISOTP_MSGTYPE_FLAG_INDICATION_RX = cantp_isotp_msgtype(0X10) # Multi-Frame Message is being received
PCANTP_ISOTP_MSGTYPE_FLAG_INDICATION_TX = cantp_isotp_msgtype(0X20) # Multi-Frame Message is being transmitted
PCANTP_ISOTP_MSGTYPE_FLAG_INDICATION = cantp_isotp_msgtype((0X10 | 0X20)) # Multi-Frame Message is being communicated (Tx or Rx)
PCANTP_ISOTP_MSGTYPE_MASK_INDICATION = cantp_isotp_msgtype(0X0F) # Mask to remove Indication flags

# Represents the addressing format of an ISO-TP message (see field "cantp_msg.msgdata.isotp.netaddrinfo.format").
cantp_isotp_format = c_uint32
PCANTP_ISOTP_FORMAT_UNKNOWN = cantp_isotp_format(0XFF) # unknown adressing format
PCANTP_ISOTP_FORMAT_NONE = cantp_isotp_format(0X00) # unsegmented CAN frame
PCANTP_ISOTP_FORMAT_NORMAL = cantp_isotp_format(0X01) # normal adressing format from ISO 15765-2
PCANTP_ISOTP_FORMAT_FIXED_NORMAL = cantp_isotp_format(0X02) # fixed normal adressing format from ISO 15765-2
PCANTP_ISOTP_FORMAT_EXTENDED = cantp_isotp_format(0X03) # extended adressing format from ISO 15765-2
PCANTP_ISOTP_FORMAT_MIXED = cantp_isotp_format(0X04) # mixed adressing format from ISO 15765-2
PCANTP_ISOTP_FORMAT_ENHANCED = cantp_isotp_format(0X05) # enhanced adressing format from ISO 15765-3

# Represents the type of target of an ISO-TP message (see field "cantp_msg.msgdata.isotp.netaddrinfo.target_type").
cantp_isotp_addressing = c_uint32
PCANTP_ISOTP_ADDRESSING_UNKNOWN = cantp_isotp_addressing(0X00) # Unknown adressing format
PCANTP_ISOTP_ADDRESSING_PHYSICAL = cantp_isotp_addressing(0X01) # Physical addressing ("peer to peer")
PCANTP_ISOTP_ADDRESSING_FUNCTIONAL = cantp_isotp_addressing(0X02) # Functional addressing ("peer to any")

# Represents the options of a message (mainly supported for ISO-TP message) (see field "cantp_msg.msgdata.options").
cantp_option = c_uint32
PCANTP_OPTION_DEBUG = cantp_option(PCANTP_PARAMETER_DEBUG.value) # 1 BYTE data describing the debug mode
PCANTP_OPTION_CAN_DATA_PADDING = cantp_option(PCANTP_PARAMETER_CAN_DATA_PADDING.value) # 1 BYTE data stating if CAN frame DLC uses padding or not
PCANTP_OPTION_CAN_PADDING_VALUE = cantp_option(PCANTP_PARAMETER_CAN_PADDING_VALUE.value) # 1 BYTE data stating the value used for CAN data padding
PCANTP_OPTION_J1939_PRIORITY = cantp_option(PCANTP_PARAMETER_J1939_PRIORITY.value) # 1 BYTE data stating the default priority value for normal fixed, mixed and enhanced addressing (default=6)
PCANTP_OPTION_MSG_PENDING = cantp_option(PCANTP_PARAMETER_MSG_PENDING.value) # 1 BYTE data stating if pending messages are displayed/hidden
PCANTP_OPTION_BLOCK_SIZE = cantp_option(PCANTP_PARAMETER_BLOCK_SIZE.value) # 1 BYTE data describing the block size parameter (BS)
PCANTP_OPTION_BLOCK_SIZE_TX = cantp_option(PCANTP_PARAMETER_BLOCK_SIZE_TX.value) # 2 BYTE data describing the transmit block size parameter (BS_TX)
PCANTP_OPTION_SEPARATION_TIME = cantp_option(PCANTP_PARAMETER_SEPARATION_TIME.value) # 1 BYTE data describing the seperation time parameter (STmin)
PCANTP_OPTION_SEPARATION_TIME_TX = cantp_option(PCANTP_PARAMETER_SEPARATION_TIME_TX.value) # 2 BYTE data describing the transmit seperation time parameter (STmin_TX)
PCANTP_OPTION_WFT_MAX = cantp_option(PCANTP_PARAMETER_WFT_MAX.value) # 4 BYTE data describing the Wait Frame Transmissions parameter.
PCANTP_OPTION_WFT_MAX_TX = cantp_option(PCANTP_PARAMETER_WFT_MAX_TX.value) # 4 BYTE data describing the transmite Wait Frame Transmissions parameter (WFT_TX).
PCANTP_OPTION_TIMEOUT_AS = cantp_option(PCANTP_PARAMETER_TIMEOUT_AS.value) # 4 BYTE data describing ISO-15765-2:Timeout As.
PCANTP_OPTION_TIMEOUT_AR = cantp_option(PCANTP_PARAMETER_TIMEOUT_AR.value) # 4 BYTE data describing ISO-15765-2:Timeout Ar.
PCANTP_OPTION_TIMEOUT_BS = cantp_option(PCANTP_PARAMETER_TIMEOUT_BS.value) # 4 BYTE data describing ISO-15765-2:Timeout Bs.
PCANTP_OPTION_TIMEOUT_BR = cantp_option(PCANTP_PARAMETER_TIMEOUT_BR.value) # 4 BYTE data describing ISO-15765-2:Timeout Br.
PCANTP_OPTION_TIMEOUT_CS = cantp_option(PCANTP_PARAMETER_TIMEOUT_CS.value) # 4 BYTE data describing ISO-15765-2:Timeout Cs.
PCANTP_OPTION_TIMEOUT_CR = cantp_option(PCANTP_PARAMETER_TIMEOUT_CR.value) # 4 BYTE data describing ISO-15765-2:Timeout Cr.
PCANTP_OPTION_SELFRECEIVE_LATENCY = cantp_option(PCANTP_PARAMETER_SELFRECEIVE_LATENCY.value) # 1 BYTE data to set optimization options to improve delay between ISO-TP consecutive frames.

# Represents the status for a message whose transmission is in progress.
cantp_msgprogress_state = c_uint32
PCANTP_MSGPROGRESS_STATE_QUEUED = cantp_msgprogress_state(0) # Message is not yet handled.
PCANTP_MSGPROGRESS_STATE_PROCESSING = cantp_msgprogress_state(1) # Message is being processed (received or transmitted).
PCANTP_MSGPROGRESS_STATE_COMPLETED = cantp_msgprogress_state(2) # Message is completed.
PCANTP_MSGPROGRESS_STATE_UNKNOWN = cantp_msgprogress_state(3) # Message is unknown/not found.

# Represents the direction of a message's communication.
cantp_msgdirection = c_uint32
PCANTP_MSGDIRECTION_RX = cantp_msgdirection(0) # Message is being received.
PCANTP_MSGDIRECTION_TX = cantp_msgdirection(1) # Message is being transmitted.

# Reserved extra information
cantp_msginfo_flag =c_int
cantp_msginfo_extra =c_void_p
cantp_isotp_info =c_void_p

#//////////////////////////////////////////////////////////
# Types definition
#//////////////////////////////////////////////////////////

cantp_bitrate	=c_char_p		# Represents a PCAN-FD bit rate string
cantp_timestamp =c_ulonglong	# Timestamp


# PCANTP parameter values
PCANTP_VALUE_PARAMETER_OFF				=PCAN_PARAMETER_OFF
PCANTP_VALUE_PARAMETER_ON				=PCAN_PARAMETER_ON
PCANTP_DEBUG_NONE						=PCANTP_VALUE_PARAMETER_OFF		# No debug messages
PCANTP_DEBUG_CAN						=PCANTP_VALUE_PARAMETER_ON		# Enable debug messages
PCANTP_DEBUG_NOTICE						=0xF4		# Enable debug messages (only notices, informations, warnings, errors)
PCANTP_DEBUG_INFO						=0xF3		# Enable debug messages (only informations, warnings, errors)
PCANTP_DEBUG_WARNING					=0xF2		# Enable debug messages (only warnings, errors)
PCANTP_DEBUG_ERROR						=0xF1		# Enable debug messages (only errors)
PCANTP_CHANNEL_UNAVAILABLE				=0x00		# The Channel is illegal or not available
PCANTP_CHANNEL_AVAILABLE				=0x01		# The Channel is available
PCANTP_CHANNEL_OCCUPIED					=0x02		# The Channel is valid, and is being used
PCANTP_WFT_MAX_UNLIMITED				=0x00		# if set Flow Control frame shall not use the WT flow status value
PCANTP_WFT_MAX_DEFAULT					=0x10		# an integer describing the Wait Frame Transmissions parameter.
PCANTP_WFT_MAX_TX_DEFAULT				=PCANTP_WFT_MAX_UNLIMITED		# an integer describing the transmit Wait Frame Transmissions parameter.
PCANTP_MSG_PENDING_HIDE					=PCANTP_VALUE_PARAMETER_OFF		# hide messages with type PCANTP_MESSAGE_INDICATION from CANTP_Read function
PCANTP_MSG_PENDING_SHOW					=PCANTP_VALUE_PARAMETER_ON		# show messages with type PCANTP_MESSAGE_INDICATION from CANTP_Read function
PCANTP_CAN_DATA_PADDING_NONE			=PCANTP_VALUE_PARAMETER_OFF		# uses CAN frame data optimization
PCANTP_CAN_DATA_PADDING_ON				=PCANTP_VALUE_PARAMETER_ON		# uses CAN frame data padding (default, i.e. CAN DLC = 8)
PCANTP_CAN_DATA_PADDING_VALUE			=0x55		# default value used if CAN data padding is enabled
PCANTP_FRAME_FILTERING_ISOTP			=0x00		# disable reception of unformatted (NON-ISO-TP) CAN frames (default)
															#	only ISO 15765 messages will be received
PCANTP_FRAME_FILTERING_CAN				=0x01		# enable reception of unformatted (NON-ISO-TP) CAN frames
															#	received messages will be treated as either ISO 15765 or as an unformatted CAN frame
PCANTP_FRAME_FILTERING_VERBOSE			=0x02		# enable reception of unformatted (NON-ISO-TP) CAN frames
															#	received messages will be treated as ISO 15765, unformatted CAN frame, or both (user will able to read fragmented CAN frames)
PCANTP_J1939_PRIORITY_DEFAULT			=0x06		# default priority for ISO-TP messages (only available fot normal fixed, mixed and enhanced addressing)
PCANTP_MAX_CAN_ID_11_BIT				=0x7FF		# Highest 11 bit (standard) CAN ID
PCANTP_MAX_CAN_ID_29_BIT				=0x1FFFFFFF	# Hignest 29 bit (extended) CAN ID
PCANTP_MAX_LENGTH_CAN_STANDARD			=0x08		# maximum length of a CAN (non-FD) frame (8)
PCANTP_MAX_LENGTH_CAN_FD				=0x40		# maximum length of a CAN FD frame (64)
PCANTP_MAX_LENGTH_ISOTP2004				=0xFFF		# maximum length of an ISO-TP rev. 2004 frame (4095)
PCANTP_MAX_LENGTH_ISOTP2016				=0xFFFFFFFF	# maximum length of an ISO-TP rev. 2016 frame (4294967295)
PCANTP_MAX_LENGTH_ALLOC					=0xFFFFFF	# maximum length before using virtual allocation for ISO-TP messages
PCANTP_CAN_TX_DL_DEFAULT				=PCANTP_MAX_LENGTH_CAN_STANDARD	 # default DLC for fragmented frames when transmiting ISO-TP messages
PCANTP_ISO_REV_2004						=0x01		# ISO-15765-2:2004(E)
PCANTP_ISO_REV_2016						=0x02		# ISO-15765-2:2016(E)
PCANTP_BLOCK_SIZE_TX_IGNORE				=0xFFFF		# disables the feature "ignore received BlockSize value"
PCANTP_SEPERATION_TIME_TX_IGNORE		=0xFFFF		# disables the feature "ignore received STMin value"
PCANTP_ISO_TIMEOUTS_15765_2				=0			# sets timeouts according to ISO-15765-2
PCANTP_ISO_TIMEOUTS_15765_4				=1			# sets timeouts according to ISO-15765-4 (OBDII)
PCANTP_SELFRECEIVE_LATENCY_NONE			=0			# no optimization (use this parameter if ECU requires strict respect of Minimum Separation Time)
PCANTP_SELFRECEIVE_LATENCY_LIGHT		=1			# (DEFAULT) fragmented self-receive frame mechanism is ignored when STmin is set to 0xF3 and lower (<300microseconds)
PCANTP_SELFRECEIVE_LATENCY_OPTIMIZED	=2			# as LIGHT value plus optimize self-receive latency by predicting the time to effectively write frames on bus
PCANTP_MAX_RX_QUEUE_DEFAULT				=32767		# (DEFAULT) maxinum number of items in the receive queue
PCANTP_NETWORK_LAYER_FULL_DUPLEX		=0			# (DEFAULT) Network layer design is full-duplex
PCANTP_NETWORK_LAYER_HALF_DUPLEX		=1			# Network layer design is half-duplex (only one transmission/reception of the same NAI at a time)
# Standard ISO-15765-2 values
PCANTP_STMIN_ISO_15765_2				=10			# Default value for Separation time
PCANTP_BS_ISO_15765_2					=10			# Default value for BlockSize
PCANTP_TIMEOUT_AR_ISO_15765_2			=(1000*1000)	# Default value for Timeout Ar in microseconds
PCANTP_TIMEOUT_AS_ISO_15765_2			=(1000*1000)	# Default value for Timeout As in microseconds
PCANTP_TIMEOUT_BR_ISO_15765_2			=(1000*1000)	# Default value for Timeout Br in microseconds
PCANTP_TIMEOUT_BS_ISO_15765_2			=(1000*1000)	# Default value for Timeout Bs in microseconds
PCANTP_TIMEOUT_CR_ISO_15765_2			=(1000*1000)	# Default value for Timeout Cr in microseconds
PCANTP_TIMEOUT_CS_ISO_15765_2			=(1000*1000)	# Default value for Timeout Cs in microseconds
PCANTP_TIMEOUT_TOLERANCE				=0			# Default value for timeout tolerance [0..100] (timeout = t * (1 + tolerance/100))
# Standard ISO-15765-4 (OBDII) values
PCANTP_STMIN_ISO_15765_4				=0			# OBDII value for Separation time
PCANTP_BS_ISO_15765_4					=0			# OBDII value for BlockSize
PCANTP_TIMEOUT_AR_ISO_15765_4			=(1000*25)	# OBDII value for Timeout Ar in microseconds
PCANTP_TIMEOUT_AS_ISO_15765_4			=(1000*25)	# OBDII value for Timeout As in microseconds
PCANTP_TIMEOUT_BR_ISO_15765_4			=(1000*75)	# OBDII value for Timeout Br in microseconds
PCANTP_TIMEOUT_BS_ISO_15765_4			=(1000*75)	# OBDII value for Timeout Bs in microseconds
PCANTP_TIMEOUT_CR_ISO_15765_4			=(1000*150)	# OBDII value for Timeout Cr in microseconds
PCANTP_TIMEOUT_CS_ISO_15765_4			=(1000*150)	# OBDII value for Timeout Cs in microseconds


# Values for cfg_value
PCANTP_FLAG_MASK_PRIORITY = 0x07 # Mask for the 29bits ISOTP priority value (stored in bits [0..2])
PCANTP_FLAG_PADDING_ON = 0x08 # Padding is enabled
PCANTP_FLAG_INDICATION_ON = 0x10 # Message's indication is enabled
PCANTP_FLAG_ECHO_FRAMES_ON = 0x20 # Echo of fragmented frames is enabled

#//////////////////////////////////////////////////////////
# Constants definition
#//////////////////////////////////////////////////////////
PCANTP_MAPPING_FLOW_CTRL_NONE	= 0xFFFFFFFF # Mapping does not require a Flow Control frame.

#//////////////////////////////////////////////////////////
# miscellaneous message related definitions
#//////////////////////////////////////////////////////////


# Internal information about cantp_msg message (reserved).
class cantp_msginfo (Structure):
    """
    Internal information about cantp_msg message (reserved).
    """
    _pack_ = 8
    _fields_ = [ ("size",      c_uint),               # (read-only) size of the message object
                 ("flags",     cantp_msginfo_flag),   # (read-only) reserved
                 ("extra",     cantp_msginfo_extra) ] # (read-only) reserved

#	Represents message's options to override.
class cantp_msgoption (Structure):
    """
    Represents message's options to override.
    """
    _pack_ = 8
    _fields_ = [("name", cantp_option),   	# Name of the option. 
                ("value", c_uint) ]		# Value of the option.
                
#	Represents a list of message's options to override.
class cantp_msgoption_list (Structure):
    """
    Represents a list of message's options to override.
    """
    _pack_ = 8
    _fields_ = [ ("buffer", POINTER(cantp_msgoption)), # Pointer to an array of cantp_msgoption.
                 ("count", c_uint) ]                   # Number of options in the array	


#	Represents common CAN information.
class cantp_can_info (Structure):
    """
    Represents common CAN information.
    """
    _pack_ = 8
    _fields_ = [ ("can_id", c_uint),         # CAN identifier
                 ("can_msgtype", c_uint),    # Types and flags of the CAN/CAN-FD frame (see cantp_can_msgtype) 
                 ("dlc", c_ubyte) ]          # Data Length Code of the frame (0..15)

# Represents the network address information of an ISO-TP message.
class cantp_netaddrinfo (Structure):
    """
    Represents the network address information of an ISO-TP message.
    """
    _pack_ = 8
    _fields_ = [ ("msgtype", cantp_isotp_msgtype),          # ISO-TP message type 
                 ("format", cantp_isotp_format),            # ISO-TP format addressing 
                 ("target_type", cantp_isotp_addressing),   # ISO-TP addressing/target type 
                 ("source_addr", c_ushort),                 # source address
                 ("target_addr",  c_ushort),                # target address
                 ("extension_addr", c_ubyte) ]              # extension address

# Represents a mapping between an ISO-TP network address information and a CAN ID.
class cantp_mapping (Structure):
    """
    Represents a mapping between an ISO-TP network address information and a CAN ID.
    """
    _pack_ = 8
    _fields_ = [ ("uid", c_void_p),                     # Mapping's unique ID (read-only, set by CANTP_AddMapping_2016).
                 ("can_id", c_uint),                    # CAN ID mapped to the Network Address Information
                 ("can_id_flow_ctrl", c_uint),          # CAN ID used for the flow control frame (formerly 'can_id_resp')
                 ("can_msgtype", cantp_can_msgtype),    # CAN frame msgtype (only PCANTP_CAN_MSGTYPE_STANDARD or PCANTP_CAN_MSGTYPE_EXTENDED is mandatory)
                 ("can_tx_dlc", c_ubyte),               # Default CAN DLC value to use with segmented messages
                 ("netaddrinfo", cantp_netaddrinfo) ]   # ISO-TP Network Address Information

# Represents a message rule for filtering.
class cantp_msgrule (Structure):
    """
    
    """
    _pack_ = 8
    _fields_ = [ ("uid", c_void_p),                 # Unique ID (read-only)
                 ("type", cantp_msgtype),           # type of the message 
                 ("can_info", cantp_can_info),      # common CAN information
                 ("netaddrinfo", cantp_netaddrinfo),# ISO-TP network address information   
                 ("options", cantp_msgoption_list), # specific options to override global CAN configuration  
                 ("reserved", c_void_p) ]           # reserved

#//////////////////////////////////////////////////////////
# Message definitions
#//////////////////////////////////////////////////////////

# Represents the content of a generic message.
class cantp_msgdata (Structure):
    """
    Represents the content of a generic message.
    """
    _pack_ = 8
    _fields_ = [ ("flags", cantp_msgflag),                      # structure specific flags 
                 ("length", c_uint),                            # Length of the message
                 ("data", POINTER(c_ubyte)),                    # Data of the message
                 ("netstatus", cantp_netstatus),                # Network status 
                 ("options", POINTER(cantp_msgoption_list)) ]   # Defines specific options to override global message configuration

# Represents the content of a standard CAN frame.
class cantp_msgdata_can  (Structure):
    """
    Represents the content of a standard CAN frame.
    """
    _pack_ = 8
    _fields_ = [ ("flags", cantp_msgflag),                                  # structure specific flags 
                ("length", c_uint),                                        # Length of the message (0..8)
                ("data", POINTER(c_ubyte)),                                # Data of the message
                ("netstatus", cantp_netstatus),                            # Network status 
                ("options", POINTER(cantp_msgoption_list)),                # Defines specific options to override global CAN configuration (not used yet)
                ("data_max", c_ubyte * PCANTP_MAX_LENGTH_CAN_STANDARD) ]   # Data of the message (DATA[0]..DATA[7])

# Represents the content of a CAN FD frame.
class cantp_msgdata_canfd  (Structure):
    """
    Represents the content of a CAN FD frame.
    """
    _pack_ = 8
    _fields_ = [ ("flags", cantp_msgflag),                          # structure specific flags 
                ("length", c_uint),                                # Length of the message (0..64)
                ("data", POINTER(c_ubyte)),                        # Data of the message
                ("netstatus", cantp_netstatus),                    # Network status 
                ("options", POINTER(cantp_msgoption_list)),        # Defines specific options to override global CAN configuration (not used yet)
                ("data_max", c_ubyte*PCANTP_MAX_LENGTH_CAN_FD) ]   # Data of the message (DATA[0]..DATA[63])


# Represents the content of an ISO-TP message.
class cantp_msgdata_isotp  (Structure):
    """
    Represents the content of an ISO-TP message.
    """
    _pack_ = 8
    _fields_ = [ ("flags", cantp_msgflag),                          # structure specific flags 
                 ("length", c_uint),                            # Length of the data
                 ("data",  POINTER(c_ubyte)),                   # Data
                 ("netstatus", cantp_netstatus),                # Network status 
                 ("options",  POINTER(cantp_msgoption_list)),   # Defines specific options to override global CAN configuration
                 ("netaddrinfo", cantp_netaddrinfo),            # ISO-TP network address information
                 ("reserved", cantp_isotp_info) ]               # Reserved ISO-TP information

# Union only used in cantp_msg structure
class msgData (Union):
    """
    Union only used in cantp_msg structure
    """
    _pack_ = 8
    _fields_ = [ ("any",  POINTER(cantp_msgdata)),             # shortcut to access msgdata as Generic content
                 ("can",  POINTER(cantp_msgdata_can)),         # shortcut to access msgdata as CAN content
                 ("canfd", POINTER(cantp_msgdata_canfd)),      # shortcut to access msgdata as CAN-FD content
                 ("isotp", POINTER(cantp_msgdata_isotp)) ]     # shortcut to access msgdata as ISO-TP content
    
# A cantp_msg message is a generic CAN related message than can be either a standard CAN frame,
#  a CAN FD frame, an ISO-TP message, etc.
class cantp_msg  (Structure):
    """
    A cantp_msg message is a generic CAN related message than can be either a standard CAN frame, a CAN FD frame, an ISO-TP message, etc.
    """
    _pack_ = 8
    _fields_ = [ ("type", cantp_msgtype),       # type of the message
                 ("reserved", cantp_msginfo),   # misc. read-only information
                 ("can_info", cantp_can_info),  # common CAN information
                 ("msgdata", msgData)]         # shortcuts to access msgdata


# Holds information on the communication progress of a message.
class cantp_msgprogress  (Structure):
    """
    Holds information on the communication progress of a message.
    """
    _pack_ = 8
    _fields_ = [ ("state", cantp_msgprogress_state),    # State of the message 
                 ("percentage", c_ubyte),               # Progress of the transmission/reception in percent.
                 ("buffer", POINTER(cantp_msg)) ]       # Buffer to get a copy of the pending message.
				

#//////////////////////////////////////////////////////////
#  PCAN-ISO-TP API function declarations
#//////////////////////////////////////////////////////////

# PCAN-ISO-TP_2016 API class implementation
#
class PCAN_ISO_TP_2016:
    """
      PCAN-ISO-TP_2016 class implementation
    """      
    def __init__(self):
        # Loads the PCAN-ISO-TP_2016 API
        #     
        if platform.system() == 'Windows':
            # Loads the API on Windows
            libpath = r".\PCAN-ISO-TP.dll"
            self.__m_dllIsotp = windll.LoadLibrary(libpath)
        elif platform.system() == 'Linux':
            # Loads the API on Linux
            self.__m_dllIsotp = cdll.LoadLibrary("libpcanisotp.so")            

        if self.__m_dllIsotp == None:
            msg = f"Exception: The PCAN-ISO-TP.dll couldn't be loaded!"
            print(msg)
            raise FileNotFoundError(msg)

    # Initializes a PCANTP-Client based on a CANTP handle (without CAN-FD support)
    def Initialize_2016 (
        self,
        channel,
        baudrate,
        hw_type =0,
        io_port =0,
        interrupt =0):
        
        """
        Initializes a PCANTP-Client based on a CANTP handle (without CAN-FD support)
        
        remarks:
         Only one PCANTP-Client can be initialized per CAN-Channel
        parameters:
         channel: A PCANTP Channel Handle representing a PCANTP-Client
         baudrate: The CAN Hardware speed
         hw_type: NON PLUG-N-PLAY: The type of hardware and operation mode
         io_port: NON PLUG-N-PLAY: The I/O address for the parallel port
         interrupt: NON PLUG-N-PLAY: Interrupt number of the parallel port
        returns:
         A cantp_status code. PCANTP_STATUS_OK is returned on success
        """
        try:
            res = self.__m_dllIsotp.CANTP_Initialize_2016(channel,baudrate,hw_type,io_port,interrupt)
            return cantp_status(res)
        except:
            print ("Exception on PCAN-ISO-TP.Initialize_2016")
            raise
            
    # Initializes a PCANTP-Client based on a CANTP Channel (including CAN-FD support)      
    def InitializeFD_2016 (
        self,
        channel,
        bitrate_fd):
        
        """
        Initializes a PCANTP-Client based on a CANTP Channel (including CAN-FD support)    
        
        remarks:
         Only one PCANTP-Client can be initialized per CAN-Channel.
        parameters:
         channel: The handle of a FD capable PCAN Channel
         bitrate_fd: The speed for the communication (FD bit rate string)
        remarks:
         See PCAN_BR_* values
            * Parameter and values must be separated by '='
            * Couples of Parameter/value must be separated by ','
            * Following Parameter must be filled out: f_clock, data_brp, data_sjw, data_tseg1, data_tseg2,
                nom_brp, nom_sjw, nom_tseg1, nom_tseg2.
            * Following Parameters are optional (not used yet): data_ssp_offset, nom_samp
        example:
         f_clock_mhz=80,nom_brp=0,nom_tseg1=13,nom_tseg2=0,nom_sjw=0,data_brp=0,
            data_tseg1=13,data_tseg2=0,data_sjw=0
        returns:
         A cantp_status code
        """
        try:
            res = self.__m_dllIsotp.CANTP_InitializeFD_2016(channel, byref(bitrate_fd))
            return cantp_status(res)
        except:
            print ("Exception on PCAN-ISO-TP.InitializeFD_2016")
            raise

    # Uninitializes a PCANTP-Client initialized before
    def Uninitialize_2016 (
        self,
        channel):
        
        """
        Uninitializes a PCANTP-Client initialized before
        
        parameters:
         channel: A PCANTP Channel Handle representing a PCANTP-Client        
        returns:
         A cantp_status code. PCANTP_STATUS_OK is returned on success
        """
        try:
            res = self.__m_dllIsotp.CANTP_Uninitialize_2016(channel)
            return cantp_status(res)
        except Exception as ex:
            print ("Exception on PCAN-ISO-TP.Uninitialize_2016:",ex)
            raise

    # Resets the receive and transmit queues of a PCANTP-Client
    def Reset_2016 (
        self, channel):

        """
        Resets the receive and transmit queues of a PCANTP-Client

        parameters:
         channel: A PCANTP Channel Handle representing a PCANTP-Client        
        returns:
         A cantp_status code. PCANTP_STATUS_OK is returned on success
        """
        try:
            res = self.__m_dllIsotp.CANTP_Reset_2016(channel)
            return cantp_status(res)
        except Exception as ex:
            print ("Exception on PCAN-ISO-TP.Reset_2016:",ex)
            raise

    # Gets information about the internal BUS status of a PCANTP-Channel.
    def GetCanBusStatus_2016(
        self, channel):
       
        """
        Gets information about the internal BUS status of a PCANTP-Channel.

        parameters:
         channel: A PCANTP Channel Handle representing a PCANTP-Client        
        returns:
         A cantp_status code. PCANTP_STATUS_OK is returned on success
        """
        try:
            res = self.__m_dllIsotp.CANTP_GetCanBusStatus_2016(channel)
            return cantp_status(res)
        except Exception as ex:
            print ("Exception on PCAN-ISO-TP.GetCanBusStatus_2016:",ex)
            raise

    # Reads a PCANTP message from the receive queue of a PCANTP-Client
    def Read_2016(
        self,
        channel,
	    msg_buffer,
	    timestamp_buffer=None,
	    msg_type=PCANTP_MSGTYPE_ANY):

        """
        Reads a PCANTP message from the receive queue of a PCANTP-Client

        parameters:
        channel: A PCANTP Channel Handle representing a PCANTP-Client
         msg_buffer: A cantp_msg structure buffer to store the PUDS message
         timestamp_buffer: A cantp_timestamp structure buffer to get the reception time of the message. If this value is not desired, this parameter should be passed as None
         msg_type: A cantp_msgtype structure buffer to filter the message to read. If this value is not desired, this parameter should be passed as PCANTP_MSGTYPE_ANY
        returns: A cantp_status code. PCANTP_STATUS_OK is returned on success
        """
        try:
            res = self.__m_dllIsotp.CANTP_Read_2016(channel, byref(msg_buffer), None if timestamp_buffer == None else byref(timestamp_buffer), msg_type)
            return cantp_status(res)
        except Exception as ex:
            print ("Exception on PCAN-ISO-TP.Read_2016:",ex)
            raise

    # Gets progress information on a specific message
    def GetMsgProgress_2016(
        self,
        channel,
	    msg_buffer,
	    direction,
	    msgprogress_buffer):

        """
        Gets progress information on a specific message

        parameters:
         channel: A PCANTP Channel Handle representing a PCANTP-Client
         msg_buffer: A cantp_msg structure buffer matching the message to look for
         direction: The expected direction (incoming/outgoing) of the message
         msgprogress_buffer: A cantp_msgprogress structure buffer to store the progress information
        returns: A cantp_status code. PCANTP_STATUS_OK is returned on success
        """

        try:
            res = self.__m_dllIsotp.CANTP_GetMsgProgress_2016(channel, byref(msg_buffer), direction, byref(msgprogress_buffer))
            return cantp_status(res)
        except Exception as ex:
            print ("Exception on PCAN-ISO-TP.GetMsgProgress_2016:",ex)
            raise


    # Adds a PCANTP message to the Transmit queue
    def Write_2016(
        self,
        channel,
        msg_buffer):

        """
        Adds a PCANTP message to the Transmit queue

        parameters:
         channel: A PCANTP Channel Handle representing a PCANTP-Client
         msg_buffer: A cantp_msg buffer with the message to be sent
        returns: A cantp_status code. PCANTP_STATUS_OK is returned on success
        """
        try:
            res = self.__m_dllIsotp.CANTP_Write_2016(channel, byref(msg_buffer))
            return cantp_status(res)
        except Exception as ex:
            print ("Exception on PCAN-ISO-TP.Write_2016:",ex)
            raise


    # Retrieves a PCANTP-Client value
    def GetValue_2016 (
        self,
        channel,
        parameter,
        buffer,
        buffer_size):
        
        """
        Retrieves a PCANTP-Client value
        
        parameters:
         channel: A PCANTP Channel Handle representing a PCANTP-Client
         parameter: The cantp_parameter parameter to get
         buffer: Buffer for the parameter value
         buffer_size: Size in bytes of the buffer
        returns:
         A cantp_status code. PCANTP_STATUS_OK is returned on success

        """
        try:
            res = self.__m_dllIsotp.CANTP_GetValue_2016(channel,parameter,byref(buffer),buffer_size)
            return cantp_status(res)
        except Exception as ex:
            print ("Exception on PCAN-ISO-TP.GetValue_2016:",ex)
            raise


    # Configures or sets a PCANTP-Client value
    def SetValue_2016 (
        self,
        channel,
        parameter,
        buffer,
        buffer_size):
        
        """
        Configures or sets a PCANTP-Client value
        
        parameters:
         channel: A PCANTP Channel Handle representing a PCANTP-Client
         parameter: The cantp_parameter parameter to set
         buffer: Buffer with the value to be set
         buffer_size: Size in bytes of the buffer
        returns:
         A cantp_status code. PCANTP_STATUS_OK is returned on success
        """
        try:
            res = self.__m_dllIsotp.CANTP_SetValue_2016(channel, parameter, byref(buffer), buffer_size)
            return cantp_status(res)
        except Exception as ex:
            print ("Exception on PCAN-ISO-TP.SetValue_2016:",ex)
            raise

    # Adds a user-defined PCAN-TP mapping between CAN ID and Network Address Information
    def AddMapping_2016(
	    self,
        channel,
	    mapping):

        """
        Adds a user-defined PCAN-TP mapping between CAN ID and Network Address Information

        remarks:
         Defining a mapping enables ISO-TP communication with 11BITS CAN ID or
         with opened Addressing Formats (like PCANTP_ISOTP_FORMAT_NORMAL or PCANTP_ISOTP_FORMAT_EXTENDED).
        parameters:
         channel: A PCANTP Channel Handle representing a PCANTP-Client
         mapping: Buffer to the mapping to be added
        returns:
         A cantp_status code : PCANTP_STATUS_OK is returned on success, PCANTP_STATUS_WRONG_PARAM states invalid Network Address Information parameters.
        """

        try:
            res = self.__m_dllIsotp.CANTP_AddMapping_2016(channel, byref(mapping))
            return cantp_status(res)
        except Exception as ex:
            print ("Exception on PCAN-ISO-TP.AddMapping_2016:",ex)
            raise

    # Removes all user-defined PCAN-TP mappings corresponding to a CAN ID
    def RemoveMappings_2016(
        self,
        channel,
        can_id):

        """
        Removes all user-defined PCAN-TP mappings corresponding to a CAN ID

        parameters:
         channel: A PCANTP Channel Handle representing a PCANTP-Client
         can_id: The mapped CAN ID to search for
        returns: A cantp_status code. PCANTP_STATUS_OK is returned on success
        """

        try:
            res = self.__m_dllIsotp.CANTP_RemoveMappings_2016(channel, can_id)
            return cantp_status(res)
        except Exception as ex:
            print ("Exception on PCAN-ISO-TP.RemoveMappings_2016:",ex)
            raise

    # Removes all user-defined PCAN-TP mappings corresponding to a CAN ID
    def RemoveMapping_2016(
        self,
        channel,
        uid):

        """
        Removes a user-defined PCAN-TP mapping between a CAN ID and Network Address Information

        parameters:
         channel: A PCANTP Channel Handle representing a PCANTP-Client
         uid: The identifier of the mapping
        returns: A cantp_status code. PCANTP_STATUS_OK is returned on success
        """

        try:
            res = self.__m_dllIsotp.CANTP_RemoveMapping_2016(channel, uid)
            return cantp_status(res)
        except Exception as ex:
            print ("Exception on PCAN-ISO-TP.RemoveMapping_2016:",ex)
            raise

    # Retrieves all the mappings defined for a PCAN-TP channel

    def GetMappings_2016(
        self,
        channel,
        buffer,
        buffer_length):

        """
        Retrieves all the mappings defined for a PCAN-TP channel

        parameters:
         channel: A PCANTP Channel Handle representing a PCANTP-Client
         buffer: A buffer to store an array of cantp_mapping.
         buffer_length: [In]The number of cantp_mapping element the buffer can store. [Out]The actual number of element copied in the buffer (c_uint32). 
        returns: A cantp_status code. PCANTP_STATUS_OK is returned on success, PCANTP_STATUS_PARAM_BUFFER_TOO_SMALL if the number of mappings exceeds buffer_length.
        """

        try:
            res = self.__m_dllIsotp.CANTP_GetMappings_2016(channel, byref(buffer), byref(buffer_length))
            return cantp_status(res)
        except Exception as ex:
            print ("Exception on PCAN-ISO-TP.GetMappings_2016:",ex)
            raise

    # Adds an entry to the CAN-ID white-list filtering.

    def AddFiltering_2016(
        self,
        channel,
        can_id_from,
        can_id_to,
        ignore_can_msgtype,
        can_msgtype):

        """
        Adds an entry to the CAN-ID white-list filtering.

        parameters:
         channel: A PCANTP Channel Handle representing a PCANTP-Client
         can_id_from: The lowest CAN ID wanted to be received
         can_id_to: The highest CAN ID wanted to be received
         ignore_can_msgtype: States if filter should check the CAN message type.
         can_msgtype: If ignore_can_msgtype is false, the value states which types of CAN frame should be allowed.
        returns: A cantp_status code : PCANTP_STATUS_OK is returned on success, and PCANTP_STATUS_ALREADY_INITIALIZED otherwise.
        """

        try:
            res = self.__m_dllIsotp.CANTP_AddFiltering_2016(channel, can_id_from, can_id_to, ignore_can_msgtype, can_msgtype)
            return cantp_status(res)
        except Exception as ex:
            print ("Exception on PCAN-ISO-TP.AddFiltering_2016:",ex)
            raise

    # Removes an entry from the CAN-ID white-list filtering.

    def RemoveFiltering_2016(
        self,
        channel,
        can_id_from,
        can_id_to,
        ignore_can_msgtype,
        can_msgtype):

        """
        Removes an entry from the CAN-ID white-list filtering.

        parameters:
         channel: A PCANTP Channel Handle representing a PCANTP-Client
         can_id_from: The lowest CAN ID wanted to be removed
         can_id_to: The highest CAN ID wanted to be removed
         ignore_can_msgtype: States if filter should check the CAN message type.
         can_msgtype: If ignore_can_msgtype is false, the value states which types of CAN frame should be allowed.
        returns: A cantp_status code : PCANTP_STATUS_OK is returned on success, and PCANTP_STATUS_ALREADY_INITIALIZED otherwise.
        """

        try:
            res = self.__m_dllIsotp.CANTP_RemoveFiltering_2016(channel, can_id_from, can_id_to, ignore_can_msgtype, can_msgtype)
            return cantp_status(res)
        except Exception as ex:
            print ("Exception on PCAN-ISO-TP.RemoveFiltering_2016:",ex)
            raise

    # Adds an entry to the message's rules.
    def AddMsgRule_2016(
        self,
        channel,
        msgrule):

        """
        Adds an entry to the message's rules.

        parameters:
         channel: A PCANTP Channel Handle representing a PCANTP-Client
         msgrule: The rule (cantp_msgrule) to insert.
        returns: A cantp_status code : PCANTP_STATUS_OK is returned on success
        """
        try:
            res = self.__m_dllIsotp.CANTP_AddMsgRule_2016(channel, byref(msgrule))
            return cantp_status(res)
        except Exception as ex:
            print ("Exception on PCAN-ISO-TP.AddMsgRule_2016:",ex)
            raise

    # Removes an entry from the message's rules.
    def RemoveMsgRule_2016(
        self,
        channel,
        uid):

        """
        Removes an entry from the message's rules.

        parameters:
         channel: A PCANTP Channel Handle representing a PCANTP-Client
         uid: The unique ID of the rule to remove.
        returns: A cantp_status code : PCANTP_STATUS_OK is returned on success
        """
        try:
            res = self.__m_dllIsotp.CANTP_RemoveMsgRule_2016(channel, uid)
            return cantp_status(res)
        except Exception as ex:
            print ("Exception on PCAN-ISO-TP.RemoveMsgRule_2016:",ex)
            raise

    # Returns a descriptive text of a given cantp_status error

    def GetErrorText_2016(
        self,
        error,
	    language,
	    buffer,
	    buffer_size):

        """
        Returns a descriptive text of a given cantp_status error

        remarks:The current languages available for translation are: Neutral (0x00), German (0x07), English (0x09), Spanish (0x0A), Italian (0x10) and French (0x0C)
        parameters:
         error: A cantp_status error code
         language: Indicates a 'Primary language ID'
         buffer: Buffer for a null terminated char array
         buffer_size: Buffer size
        returns: A cantp_status error code
        """

        try:
            res = self.__m_dllIsotp.CANTP_GetErrorText_2016(error, language, byref(buffer), buffer_size)
            return cantp_status(res)
        except Exception as ex:
            print ("Exception on PCAN-ISO-TP.GetErrorText_2016:",ex)
            raise


    # Allocates a PCAN-TP message based on the given type
    def MsgDataAlloc_2016(
        self,
        msg_buffer,
        type):

        """
        Allocates a PCAN-TP message based on the given type

        parameters:
         msg_buffer: A cantp_msg structure buffer (it will be freed if required)
         type: Type of the message to allocate
        returns: A cantp_status code. PCANTP_STATUS_OK is returned on success
        """

        try:
            res = self.__m_dllIsotp.CANTP_MsgDataAlloc_2016(byref(msg_buffer), type)
            return cantp_status(res)
        except Exception as ex:
            print ("Exception on PCAN-ISO-TP.MsgDataAlloc_2016:",ex)
            raise

    # Initializes an allocated PCAN-TP message
    def MsgDataInit_2016(
        self,
        msg_buffer,
        can_id,
        can_msgtype,
        data_length,
        data,
        netaddrinfo=None):   

        """
        Initializes an allocated PCAN-TP message

        parameters:
         msg_buffer: An allocated cantp_msg structure buffer
         can_id: CAN identifier (ISO-TP message may ignore this parameter and use PCANTP_MAPPING_FLOW_CTRL_NONE (-1)
         can_msgtype: Combination of CAN message types (like "extended CAN ID", "FD", "RTR", etc. flags)
         data_length: Length of the data
         data: A buffer to initialize the message's data with. If None, message's data is initialized with zeros.
         netaddrinfo: Network address information of the ISO-TP message (only valid with an ISO-TP message) (cantp_netaddrinfo)
        returns: A cantp_status code. PCANTP_STATUS_OK is returned on success
        """

        try:
            res = self.__m_dllIsotp.CANTP_MsgDataInit_2016(byref(msg_buffer), can_id, can_msgtype, data_length, 
                                                           None if data == None else byref(data), 
                                                           None if netaddrinfo == None else byref(netaddrinfo))
            return cantp_status(res)
        except Exception as ex:
            print ("Exception on PCAN-ISO-TP.MsgDataInit_2016:",ex)
            raise

    # Initializes a number of options for the PCAN-TP message that will override the channel's parameter(s)

    def MsgDataInitOptions_2016(
        self,
        msg_buffer,
        nb_options):

        """
        Initializes a number of options for the PCAN-TP message that will override the channel's parameter(s)

        parameters:
         msg_buffer: An allocated cantp_msg structure buffer.
         nb_options: Number of options to initialize.
       returns: A cantp_status code. PCANTP_STATUS_OK is returned on success
        """

        try:
            res = self.__m_dllIsotp.CANTP_MsgDataInitOptions_2016(byref(msg_buffer), nb_options)
            return cantp_status(res)
        except Exception as ex:
            print ("Exception on PCAN-ISO-TP.MsgDataInitOptions_2016:",ex)
            raise

    # Deallocates a PCAN-TP message
    def MsgDataFree_2016(
        self,
        msg_buffer):

        """
        Deallocates a PCAN-TP message

        parameters:
         msg_buffer: An allocated cantp_msg structure buffer.
        returns: A cantp_status code. PCANTP_STATUS_OK is returned on success
        """

        try:
            res = self.__m_dllIsotp.CANTP_MsgDataFree_2016(byref(msg_buffer))
            return cantp_status(res)
        except Exception as ex:
            print ("Exception on PCAN-ISO-TP.MsgDataFree_2016:",ex)
            raise


    # Checks if two PCAN-TP messages are equal.
    def MsgEqual_2016(
        self,
        msg_buffer1,
        msg_buffer2,
        ignoreSelfReceiveFlag):

        """
        Checks if two PCAN-TP messages are equal.
        If one message is the indication of an incoming/outgoing ISO-TP message, the actual data-content will not be compared.
        In that case the function checks if the messages' network address information matches.

        parameters:
         msg_buffer1: A cantp_msg structure buffer.
         msg_buffer2: Another cantp_msg structure buffer to compare with first parameter.
         ignoreSelfReceiveFlag: States if comparison should ignore loopback flag (i.e if true the function will return true when comparing a request and its loopback confirmation).
        returns: A boolean stating if the cantp_msgs are equal.
        """
        try:
            res = c_byte(self.__m_dllIsotp.CANTP_MsgEqual_2016(byref(msg_buffer1), byref(msg_buffer2), ignoreSelfReceiveFlag))
            booleanRes = False if res.value == 0 else True
            return booleanRes
        except Exception as ex:
            print ("Exception on PCAN-ISO-TP.MsgEqual_2016:",ex)
            raise

    # Copies a PCAN-TP message to another buffer.
    def MsgCopy_2016(
        self,
        msg_buffer_dst,
        msg_buffer_src):

        """
        Copies a PCAN-TP message to another buffer.

        parameters:
         msg_buffer_dst: A cantp_msg structure buffer to store the copied message.
         msg_buffer_src: The cantp_msg structure buffer used as the source.
        returns: A cantp_status code. PCANTP_STATUS_OK is returned on success
        """
        try:
            res = self.__m_dllIsotp.CANTP_MsgCopy_2016(byref(msg_buffer_dst), byref(msg_buffer_src))
            return cantp_status(res)
        except Exception as ex:
            print ("Exception on PCAN-ISO-TP.MsgCopy_2016:",ex)
            raise

    # Converts a CAN DLC to its corresponding length.
    def MsgDlcToLength_2016(
        self,
        dlc):

        """
        Converts a CAN DLC to its corresponding length.

        parameters:
         dlc: The Data Length Code (DLC) to convert.
        returns: The corresponding length of the dlc parameter.
        """
        try:
            res = self.__m_dllIsotp.CANTP_MsgDlcToLength_2016(dlc)
            return res
        except Exception as ex:
            print ("Exception on PCAN-ISO-TP.MsgDlcToLength_2016:",ex)
            raise

    # Converts a data length to a corresponding CAN DLC.
    def MsgLengthToDlc_2016(
        self,
        length):

        """
        Converts a data length to a corresponding CAN DLC.

        remarks: the returned DLC can hold more data that the requested length.
        parameters:
         length: The length to convert.
        returns: The smallest DLC that can hold the requested length (0x00-0x0F).
        """
        try:
            res = c_ubyte(self.__m_dllIsotp.CANTP_MsgLengthToDlc_2016(length))
            return res.value
        except Exception as ex:
            print ("Exception on PCAN-ISO-TP.MsgDlcToLength_2016:",ex)
            raise

    # Lists the subtypes contained in the PCAN-TP status.

    def StatusListTypes_2016(
        self,
        status):

        """
        Lists the subtypes contained in the PCAN-TP status.

        parameters:
         status: The status to analyze.
        returns: An aggregation of cantp_statustype values.
        """

        try:
            res = cantp_statustype(self.__m_dllIsotp.CANTP_StatusListTypes_2016(status))
            return res
        except Exception as ex:
            print ("Exception on PCAN-ISO-TP.StatusListTypes_2016:",ex)
            raise


    # Retrieves the value of a cantp_status subtype (like cantp_errstatus, cantp_busstatus, etc.).
    def StatusGet_2016(
        self,
        status,
        type):

        """
        Retrieves the value of a cantp_status subtype (like cantp_errstatus, cantp_busstatus, etc.).

        parameters:
         status: The status to analyze.
         type: The type of status to filter.

        returns: The value of the enumeration matching the requested type.
        """
        try:
            res = self.__m_dllIsotp.CANTP_StatusGet_2016(status, type)
            return res
        except Exception as ex:
            print ("Exception on PCAN-ISO-TP.StatusGet_2016:",ex)
            raise




    # Checks if a status matches an expected result (default is PCANTP_STATUS_OK).
    def StatusIsOk_2016 (
        self,
        status,
        status_expected = PCANTP_STATUS_OK,
        strict = 0):

        """
        Checks if a status matches an expected result (default is PCANTP_STATUS_OK).

        parameters:
         status: The status to analyze
         status_expected: The expected status (default is PCANTP_STATUS_OK).
         strict: Enable strict mode (default is false). Strict mode ensures that bus or extra information are the same.
        returns: 
         true if the status matches expected parameter.
        """
        try:
            res = c_byte(self.__m_dllIsotp.CANTP_StatusIsOk_2016(status, status_expected, strict))
            booleanRes = False if res.value == 0 else True
            return booleanRes
        except Exception as ex:
            print ("Exception on PCAN-ISO-TP.StatusIsOk_2016:",ex)
            raise
