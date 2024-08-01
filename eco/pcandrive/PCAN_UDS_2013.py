#  PCAN_UDS_2013.h
#
#  ~~~~~~~~~~~~
#
#  PCAN-UDS API 2013 (ISO 14229-1:2013)
#
#  ~~~~~~~~~~~~
#
#  ------------------------------------------------------------------
#  Last changed by:    $Author: Romain $
#  Last changed date:  $Date: 2021-10-12 12:25:45 +0200 (mar., 12 oct. 2021) $
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
from .PCAN_ISO_TP_2016 import *

##############################
# Enums definition for UDS API
##############################

# Represents PUDS error codes (used in uds_status)
uds_errstatus = c_uint32
PUDS_ERRSTATUS_SERVICE_NO_MESSAGE = uds_errstatus(1)
PUDS_ERRSTATUS_SERVICE_TIMEOUT_CONFIRMATION = uds_errstatus(2)
PUDS_ERRSTATUS_SERVICE_TIMEOUT_RESPONSE = uds_errstatus(3)
PUDS_ERRSTATUS_RESET = uds_errstatus(4)
PUDS_ERRSTATUS_ERROR_WAIT_FOR_P3_TIMING = uds_errstatus(5)
PUDS_ERRSTATUS_SERVICE_ALREADY_PENDING = uds_errstatus(6)
PUDS_ERRSTATUS_SERVICE_TX_ERROR = uds_errstatus(7)
PUDS_ERRSTATUS_SERVICE_RX_ERROR = uds_errstatus(8)
PUDS_ERRSTATUS_SERVICE_RX_OVERFLOW = uds_errstatus(9)
PUDS_ERRSTATUS_MESSAGE_BUFFER_ALREADY_USED = uds_errstatus(10)

# Defines constants used by the next enum: uds_status
PCANTP_STATUS_OFFSET_BUS = 8
PCANTP_STATUS_OFFSET_NET = (PCANTP_STATUS_OFFSET_BUS + 5)
PCANTP_STATUS_OFFSET_INFO = (PCANTP_STATUS_OFFSET_NET + 5)
PCANTP_STATUS_OFFSET_UDS = (PCANTP_STATUS_OFFSET_INFO + 6)
# Represents the PCANTP & UDS error and status codes.
#
# Bits information:
#   32|  28|  24|  20|  16|  12|   8|   4|   0|
#     |    |    |    |    |    |    |    |    |
#      0000 0000 0000 0000 0000 0000 0000 0000
#     |    |    |    |    |         [0000 0000] => PCAN-ISO-TP API errors
#     |    |    |    |    |  [0 0000]           => CAN Bus status
#     |    |    |    | [00 000]                 => Networking message status
#     |    |    [0000 00]                       => PCAN-ISO-TP API extra information
#     |  [0 0000]                               => API Status
#     | [0]                                     => UDS Status
#     |[0]                                      => Reserved
#     [0]                                       => PCANBasic error flag
uds_status = c_uint32
PUDS_STATUS_OK = uds_status(PCANTP_STATUS_OK.value)  # No error
PUDS_STATUS_NOT_INITIALIZED = uds_status(PCANTP_STATUS_NOT_INITIALIZED.value)  # Not Initialized.
PUDS_STATUS_ALREADY_INITIALIZED = uds_status(PCANTP_STATUS_ALREADY_INITIALIZED.value)  # Already Initialized.
PUDS_STATUS_NO_MEMORY = uds_status(PCANTP_STATUS_NO_MEMORY.value)  # Could not obtain memory.
PUDS_STATUS_OVERFLOW = uds_status(PCANTP_STATUS_OVERFLOW.value)  # Input buffer overflow.
PUDS_STATUS_NO_MESSAGE = uds_status(PCANTP_STATUS_NO_MESSAGE.value)  # No message available.
PUDS_STATUS_PARAM_INVALID_TYPE = uds_status(PCANTP_STATUS_PARAM_INVALID_TYPE.value)  # Wrong message parameters.
PUDS_STATUS_PARAM_INVALID_VALUE = uds_status(PCANTP_STATUS_PARAM_INVALID_VALUE.value)  # Wrong message parameters.
PUDS_STATUS_MAPPING_NOT_INITIALIZED = uds_status(
    PCANTP_STATUS_MAPPING_NOT_INITIALIZED.value)  # Mapping not initialized.
PUDS_STATUS_MAPPING_INVALID = uds_status(PCANTP_STATUS_MAPPING_INVALID.value)  # Mapping parameters are invalid.
PUDS_STATUS_MAPPING_ALREADY_INITIALIZED = uds_status(
    PCANTP_STATUS_MAPPING_ALREADY_INITIALIZED.value)  # Mapping already defined.
PUDS_STATUS_PARAM_BUFFER_TOO_SMALL = uds_status(PCANTP_STATUS_PARAM_BUFFER_TOO_SMALL.value)  # Buffer is too small.
PUDS_STATUS_QUEUE_TX_FULL = uds_status(PCANTP_STATUS_QUEUE_TX_FULL.value)  # Tx queue is full.
PUDS_STATUS_LOCK_TIMEOUT = uds_status(PCANTP_STATUS_LOCK_TIMEOUT.value)  # Failed to get an access to the internal lock.
PUDS_STATUS_HANDLE_INVALID = uds_status(PCANTP_STATUS_HANDLE_INVALID.value)  # Invalid cantp_handle.
PUDS_STATUS_UNKNOWN = uds_status(PCANTP_STATUS_UNKNOWN.value)  # Unknown/generic error.
# Bus status flags (bits [8..11])
PUDS_STATUS_FLAG_BUS_LIGHT = uds_status(PCANTP_STATUS_FLAG_BUS_LIGHT.value)  # Channel is in BUS - LIGHT error state.
PUDS_STATUS_FLAG_BUS_HEAVY = uds_status(PCANTP_STATUS_FLAG_BUS_HEAVY.value)  # Channel is in BUS - HEAVY error state.
PUDS_STATUS_FLAG_BUS_WARNING = uds_status(
    PCANTP_STATUS_FLAG_BUS_WARNING.value)  # Channel is in BUS - HEAVY error state.
PUDS_STATUS_FLAG_BUS_PASSIVE = uds_status(PCANTP_STATUS_FLAG_BUS_PASSIVE.value)  # Channel is error passive state.
PUDS_STATUS_FLAG_BUS_OFF = uds_status(PCANTP_STATUS_FLAG_BUS_OFF.value)  # Channel is in BUS - OFF error state.
PUDS_STATUS_FLAG_BUS_ANY = uds_status(PCANTP_STATUS_FLAG_BUS_ANY.value)  # Mask for all bus errors.
PUDS_STATUS_FLAG_NETWORK_RESULT = uds_status(
    PCANTP_STATUS_FLAG_NETWORK_RESULT.value)  # This flag states if one of the following network errors occurred with the fetched message.
# Network status (bits [13..17])
PUDS_STATUS_NETWORK_TIMEOUT_A = uds_status(
    PCANTP_STATUS_NETWORK_TIMEOUT_A.value)  # Timeout occurred between 2 frames transmission (sender and receiver side).
PUDS_STATUS_NETWORK_TIMEOUT_Bs = uds_status(
    PCANTP_STATUS_NETWORK_TIMEOUT_Bs.value)  # Sender side timeout while waiting for flow control frame.
PUDS_STATUS_NETWORK_TIMEOUT_Cr = uds_status(
    PCANTP_STATUS_NETWORK_TIMEOUT_Cr.value)  # Receiver side timeout while waiting for consecutive frame.
PUDS_STATUS_NETWORK_WRONG_SN = uds_status(PCANTP_STATUS_NETWORK_WRONG_SN.value)  # Unexpected sequence number.
PUDS_STATUS_NETWORK_INVALID_FS = uds_status(PCANTP_STATUS_NETWORK_INVALID_FS.value)  # Invalid or unknown FlowStatus.
PUDS_STATUS_NETWORK_UNEXP_PDU = uds_status(PCANTP_STATUS_NETWORK_UNEXP_PDU.value)  # Unexpected protocol data unit.
PUDS_STATUS_NETWORK_WFT_OVRN = uds_status(
    PCANTP_STATUS_NETWORK_WFT_OVRN.value)  # Reception of flow control WAIT frame that exceeds the maximum counter defined by PUDS_PARAMETER_WFT_MAX.
PUDS_STATUS_NETWORK_BUFFER_OVFLW = uds_status(
    PCANTP_STATUS_NETWORK_BUFFER_OVFLW.value)  # Buffer on the receiver side cannot store the data length (server side only).
PUDS_STATUS_NETWORK_ERROR = uds_status(PCANTP_STATUS_NETWORK_ERROR.value)  # General error.
PUDS_STATUS_NETWORK_IGNORED = uds_status(PCANTP_STATUS_NETWORK_IGNORED.value)  # Message was invalid and ignored.
PUDS_STATUS_NETWORK_TIMEOUT_Ar = uds_status(
    PCANTP_STATUS_NETWORK_TIMEOUT_Ar.value)  # Receiver side timeout while transmitting.
PUDS_STATUS_NETWORK_TIMEOUT_As = uds_status(
    PCANTP_STATUS_NETWORK_TIMEOUT_As.value)  # Sender side timeout while transmitting.
# Extra information flags
PUDS_STATUS_CAUTION_INPUT_MODIFIED = uds_status(
    PCANTP_STATUS_CAUTION_INPUT_MODIFIED.value)  # Input was modified by the API.
PUDS_STATUS_CAUTION_DLC_MODIFIED = uds_status(
    PCANTP_STATUS_CAUTION_DLC_MODIFIED.value)  # DLC value of the input was modified by the API.
PUDS_STATUS_CAUTION_DATA_LENGTH_MODIFIED = uds_status(
    PCANTP_STATUS_CAUTION_DATA_LENGTH_MODIFIED.value)  # Data Length value of the input was modified by the API.
PUDS_STATUS_CAUTION_FD_FLAG_MODIFIED = uds_status(
    PCANTP_STATUS_CAUTION_FD_FLAG_MODIFIED.value)  # FD flags of the input was modified by the API.
PUDS_STATUS_CAUTION_RX_QUEUE_FULL = uds_status(PCANTP_STATUS_CAUTION_RX_QUEUE_FULL.value)  # Receive queue is full.
PUDS_STATUS_CAUTION_BUFFER_IN_USE = uds_status(
    PCANTP_STATUS_CAUTION_BUFFER_IN_USE.value)  # Buffer is used by another thread or API.
# Lower API status code: see also PCANTP_STATUS_xx macros
PUDS_STATUS_FLAG_PCAN_STATUS = uds_status(
    PCANTP_STATUS_FLAG_PCAN_STATUS.value)  # PCAN error flag, remove flag to get a usable PCAN error/status code (cf. PCANBasic API).
# Masks to merge/retrieve different status by type in a uds_status
PUDS_STATUS_MASK_ERROR = uds_status(PCANTP_STATUS_MASK_ERROR.value)  # Filter general error.
PUDS_STATUS_MASK_BUS = uds_status(PCANTP_STATUS_MASK_BUS.value)  # Filter bus error.
PUDS_STATUS_MASK_ISOTP_NET = uds_status(PCANTP_STATUS_MASK_ISOTP_NET.value)  # Filter network error.
PUDS_STATUS_MASK_INFO = uds_status(PCANTP_STATUS_MASK_INFO.value)  # Filter extra information.
PUDS_STATUS_MASK_PCAN = uds_status(PCANTP_STATUS_MASK_PCAN.value)  # Filter PCAN error (encapsulated PCAN-Basic status).
# UDS service status.
PUDS_STATUS_FLAG_UDS_ERROR = uds_status(0x20 << PCANTP_STATUS_OFFSET_UDS)  # UDS error flag.
PUDS_STATUS_MASK_UDS_ERROR = uds_status(0x3f << PCANTP_STATUS_OFFSET_UDS)  # Filter UDS error.
PUDS_STATUS_SERVICE_NO_MESSAGE = uds_status(PUDS_STATUS_FLAG_UDS_ERROR.value | (
            PUDS_ERRSTATUS_SERVICE_NO_MESSAGE.value << PCANTP_STATUS_OFFSET_UDS))  # UDS No message avaiable.
PUDS_STATUS_SERVICE_TIMEOUT_CONFIRMATION = uds_status(PUDS_STATUS_FLAG_UDS_ERROR.value | (
            PUDS_ERRSTATUS_SERVICE_TIMEOUT_CONFIRMATION.value << PCANTP_STATUS_OFFSET_UDS))  # Timeout while waiting message confirmation (loopback).
PUDS_STATUS_SERVICE_TIMEOUT_RESPONSE = uds_status(PUDS_STATUS_FLAG_UDS_ERROR.value | (
            PUDS_ERRSTATUS_SERVICE_TIMEOUT_RESPONSE.value << PCANTP_STATUS_OFFSET_UDS))  # Timeout while waiting request message response.
PUDS_STATUS_RESET = uds_status(
    PUDS_STATUS_FLAG_UDS_ERROR.value | (PUDS_ERRSTATUS_RESET.value << PCANTP_STATUS_OFFSET_UDS))  # UDS reset error.
PUDS_STATUS_ERROR_WAIT_FOR_P3_TIMING = uds_status(PUDS_STATUS_FLAG_UDS_ERROR.value | (
            PUDS_ERRSTATUS_ERROR_WAIT_FOR_P3_TIMING.value << PCANTP_STATUS_OFFSET_UDS))  # UDS wait for P3 timing error.
PUDS_STATUS_SERVICE_ALREADY_PENDING = uds_status(PUDS_STATUS_FLAG_UDS_ERROR.value | (
            PUDS_ERRSTATUS_SERVICE_ALREADY_PENDING.value << PCANTP_STATUS_OFFSET_UDS))  # A message with the same service identifier is already pending in the reception queue, user must read response for his previous request before or clear the reception queues with UDS_Reset_2013.
PUDS_STATUS_SERVICE_TX_ERROR = uds_status(PUDS_STATUS_FLAG_UDS_ERROR.value | (
            PUDS_ERRSTATUS_SERVICE_TX_ERROR.value << PCANTP_STATUS_OFFSET_UDS))  # An error occurred during the transmission of the UDS request message.
PUDS_STATUS_SERVICE_RX_ERROR = uds_status(PUDS_STATUS_FLAG_UDS_ERROR.value | (
            PUDS_ERRSTATUS_SERVICE_RX_ERROR.value << PCANTP_STATUS_OFFSET_UDS))  # An error occurred during the reception of the UDS response message.
PUDS_STATUS_SERVICE_RX_OVERFLOW = uds_status(PUDS_STATUS_FLAG_UDS_ERROR.value | (
            PUDS_ERRSTATUS_SERVICE_RX_OVERFLOW.value << PCANTP_STATUS_OFFSET_UDS))  # Service received more messages than input buffer expected.
PUDS_STATUS_MESSAGE_BUFFER_ALREADY_USED = uds_status(PUDS_STATUS_FLAG_UDS_ERROR.value | (
            PUDS_ERRSTATUS_MESSAGE_BUFFER_ALREADY_USED.value << PCANTP_STATUS_OFFSET_UDS))  # Given message buffer was already used, user must release buffer with UDS_MsgFree_2013 before reusing it.

# List of parameters handled by PCAN-UDS
#  Note: PCAN-ISO-TP and PCAN-Basic parameters (PCANTP_PARAMETER_xxx, PCAN_PARAM_xxx) are compatible via casting.
uds_parameter = c_uint32
PUDS_PARAMETER_API_VERSION = uds_parameter(0x201)  # (R/ ) uint8_t[]      :   PCAN-UDS API version parameter
PUDS_PARAMETER_DEBUG = uds_parameter(
    0x203)  # (R/W) uint8_t        :   data describing the debug mode  (use PUDS_DEBUG_LVL_ values)
PUDS_PARAMETER_RECEIVE_EVENT = uds_parameter(
    0x204)  # (R/W) uintptr_t      :   data is pointer to a HANDLE created by CreateEvent function
PUDS_PARAMETER_SERVER_ADDRESS = uds_parameter(0x207)  # (R/W) uint16_t       :   ISO-TP physical address
PUDS_PARAMETER_SESSION_INFO = uds_parameter(0x209)  # (R/W) uds_sessioninfo:   ECU Session information
PUDS_PARAMETER_TIMEOUT_REQUEST = uds_parameter(
    0x20A)  # (R/W) uint32_t       :   max time in milliseconds to wait to receive the request loopback
PUDS_PARAMETER_TIMEOUT_RESPONSE = uds_parameter(
    0x20B)  # (R/W) uint32_t       :   max time in milliseconds to wait to receive the message response indication
PUDS_PARAMETER_AUTOMATIC_TESTER_PRESENT = uds_parameter(
    0x20C)  # (R/W) bool           :   Automatic tester present. Default value: true
PUDS_PARAMETER_USE_NO_RESPONSE_AUTOMATIC_TESTER_PRESENT = uds_parameter(
    0x213)  # (R/W) bool           :   Use no response flag for automatic tester present. Default value: true
PUDS_PARAMETER_AUTO_P3_TIMING_MANAGEMENT = uds_parameter(
    0x20D)  # (R/W) bool           :   Wait for P3 timing. Default value: true (ISO-14229-2_2013 8.3 Minimum time between client request messages, p.36)

PUDS_PARAMETER_LISTENED_ADDRESSES = uds_parameter(
    0x210)  # (R/ ) uint16_t[size] :   List of pysical addresses to listen to.
#                          NOTE: for the parameter PUDS_PARAMETER_LISTENED_ADDRESSES the size of the array must
#                          be specified in the "buffer_size" parameter of the "UDS_GetValue_2013" function
PUDS_PARAMETER_ADD_LISTENED_ADDRESS = uds_parameter(
    0x211)  # ( /W) uint16_t       :   Add a listening address to the list of physical addresses to listen to
PUDS_PARAMETER_REMOVE_LISTENED_ADDRESS = uds_parameter(
    0x212)  # ( /W) uint16_t       :   Remove a listening address from the list of physical addresses to listen to

PUDS_PARAMETER_CHANNEL_CONDITION = uds_parameter(
    PCANTP_PARAMETER_CHANNEL_CONDITION.value)  # (R/ ) uint8_t        :   data describing the condition of a channel.
PUDS_PARAMETER_CAN_TX_DL = uds_parameter(
    PCANTP_PARAMETER_CAN_TX_DL.value)  # (R/W) uint8_t        :   data stating the default DLC to use when transmitting messages with CAN FD
PUDS_PARAMETER_CAN_DATA_PADDING = uds_parameter(
    PCANTP_PARAMETER_CAN_DATA_PADDING.value)  # (R/W) uint8_t        :   data stating if CAN frame DLC uses padding or not
PUDS_PARAMETER_CAN_PADDING_VALUE = uds_parameter(
    PCANTP_PARAMETER_CAN_PADDING_VALUE.value)  # (R/W) uint8_t        :   data stating the value used for CAN data padding
PUDS_PARAMETER_J1939_PRIORITY = uds_parameter(
    PCANTP_PARAMETER_J1939_PRIORITY.value)  # (R/W) uint8_t        :   data stating the default priority value for normal fixed, mixed and enhanced addressing (default=6)
PUDS_PARAMETER_BLOCK_SIZE = uds_parameter(
    PCANTP_PARAMETER_BLOCK_SIZE.value)  # (R/W) uint8_t        :   data describing the block size parameter (BS)
PUDS_PARAMETER_SEPARATION_TIME = uds_parameter(
    PCANTP_PARAMETER_SEPARATION_TIME.value)  # (R/W) uint8_t        :   data describing the seperation time parameter (STmin)
PUDS_PARAMETER_WFT_MAX = uds_parameter(
    PCANTP_PARAMETER_WFT_MAX.value)  # (R/W) uint8_t[4]     :   data describing the Wait Frame Transmissions parameter.
PUDS_PARAMETER_ISO_TIMEOUTS = uds_parameter(
    PCANTP_PARAMETER_ISO_TIMEOUTS.value)  # (R/W) uint8_t        :   data to set predefined ISO values for timeouts (see PCANTP_ISO_TIMEOUTS_*).
PUDS_PARAMETER_RESET_HARD = uds_parameter(
    PCANTP_PARAMETER_RESET_HARD.value)  # ( /W) uint8_t        :   data stating to clear Rx/Tx queues and CAN controller (channel is unitialized and re-initialized but settings and mappings are kept)

PUDS_PARAMETER_HARDWARE_NAME = uds_parameter(PCAN_HARDWARE_NAME.value)  # PCAN hardware name parameter
PUDS_PARAMETER_DEVICE_ID = uds_parameter(PCAN_DEVICE_ID.value)  # PCAN-USB device identifier parameter
PUDS_PARAMETER_DEVICE_NUMBER = uds_parameter(PCAN_DEVICE_ID.value)  # deprecated use PCANTP_PARAMETER_DEVICE_ID instead
PUDS_PARAMETER_CONTROLLER_NUMBER = uds_parameter(
    PCAN_CONTROLLER_NUMBER.value)  # CAN-Controller number of a PCAN-Channel
PUDS_PARAMETER_CHANNEL_FEATURES = uds_parameter(
    PCAN_CHANNEL_FEATURES.value)  # Capabilities of a PCAN device (FEATURE_***)

# Represents type and flags for a usd_msg
uds_msgtype = c_uint32
PUDS_MSGTYPE_USDT = uds_msgtype(0)  # Unacknowledge Segmented Data Transfert (ISO-TP message)
PUDS_MSGTYPE_UUDT = uds_msgtype(
    1)  # Unacknowledge Unsegmented Data Transfert (msg_physical will use a single CAN/CAN-FD frame without ISO-TP protocol control information)
PUDS_MSGTYPE_FLAG_NO_POSITIVE_RESPONSE = uds_msgtype(2)  # ECU(s) shall not reply to the request on positive response.
PUDS_MSGTYPE_FLAG_LOOPBACK = uds_msgtype(4)  # Message is a loopback
PUDS_MSGTYPE_MASK_TYPE = uds_msgtype(0x01)  # Mask to get the type (USDT or UUDT)

# Represents ISO-TP network addressing information supported in UDS
uds_msgprotocol = c_uint32
PUDS_MSGPROTOCOL_NONE = uds_msgprotocol(0x00)  # Non ISO-TP frame (Unacknowledge Unsegmented Data Transfer)
PUDS_MSGPROTOCOL_ISO_15765_2_11B_EXTENDED = uds_msgprotocol(
    0x07)  # ISO-TP 11 bits Extended addressing (mapping required)
PUDS_MSGPROTOCOL_ISO_15765_2_11B_NORMAL = uds_msgprotocol(0x01)  # ISO-TP 11 bits Normal addressing (mapping required)
PUDS_MSGPROTOCOL_ISO_15765_2_11B_REMOTE = uds_msgprotocol(0x02)  # ISO-TP 11 bits Mixed addressing (mapping required)
PUDS_MSGPROTOCOL_ISO_15765_2_29B_EXTENDED = uds_msgprotocol(
    0x08)  # ISO-TP 29 bits Extended addressing (mapping required)
PUDS_MSGPROTOCOL_ISO_15765_2_29B_FIXED_NORMAL = uds_msgprotocol(0x03)  # ISO-TP 29 bits Fixed Normal addressing
PUDS_MSGPROTOCOL_ISO_15765_2_29B_NORMAL = uds_msgprotocol(0x06)  # ISO-TP 29 bits Normal addressing (mapping required)
PUDS_MSGPROTOCOL_ISO_15765_2_29B_REMOTE = uds_msgprotocol(0x04)  # ISO-TP 29 bits Mixed addressing
PUDS_MSGPROTOCOL_ISO_15765_3_29B_ENHANCED = uds_msgprotocol(0x05)  # ISO-TP Enhanced addressing

# Represents UDS negative response codes (see ISO 14229-1:2013 A.1 Negative response codes p.325)
uds_nrc = c_uint32
PUDS_NRC_PR = uds_nrc(0x00)  # Positive Response
PUDS_NRC_GR = uds_nrc(0x10)  # General Reject
PUDS_NRC_SNS = uds_nrc(0x11)  # Service Not Supported
PUDS_NRC_SFNS = uds_nrc(0x12)  # Sub Function Not Supported
PUDS_NRC_IMLOIF = uds_nrc(0x13)  # Incorrect Message Length Or Invalid Format
PUDS_NRC_RTL = uds_nrc(0x14)  # Response Too Long
PUDS_NRC_BRR = uds_nrc(0x21)  # Busy Repeat Request
PUDS_NRC_CNC = uds_nrc(0x22)  # Conditions Not Correct
PUDS_NRC_RSE = uds_nrc(0x24)  # Request Sequence Error
PUDS_NRC_NRFSC = uds_nrc(0x25)  # No Response From Subnet Component
PUDS_NRC_FPEORA = uds_nrc(0x26)  # Failure Prevents Execution Of Requested Action
PUDS_NRC_ROOR = uds_nrc(0x31)  # Request Out Of Range
PUDS_NRC_SAD = uds_nrc(0x33)  # Security Access Denied
PUDS_NRC_AR = uds_nrc(0x34)  # Authentication Required
PUDS_NRC_IK = uds_nrc(0x35)  # Invalid Key
PUDS_NRC_ENOA = uds_nrc(0x36)  # Exceeded Number Of Attempts
PUDS_NRC_RTDNE = uds_nrc(0x37)  # Required Time Delay Not Expired
PUDS_NRC_SDTR = uds_nrc(0x38)  # Secure Data Transmission Required
PUDS_NRC_SDTNA = uds_nrc(0x39)  # Secure Data Transmission Not Allowed
PUDS_NRC_SDTF = uds_nrc(0x3A)  # Secure Data Verification Failed
PUDS_NRC_CVFITP = uds_nrc(0x50)  # Certificate Verification Failed Invalid Time Period
PUDS_NRC_CVFISIG = uds_nrc(0x51)  # Certificate Verification Failed Invalid SIGnature
PUDS_NRC_CVFICOT = uds_nrc(0x52)  # Certificate Verification Failed Invalid Chain of Trust
PUDS_NRC_CVFIT = uds_nrc(0x53)  # Certificate Verification Failed Invalid Type
PUDS_NRC_CVFIF = uds_nrc(0x54)  # Certificate Verification Failed Invalid Format
PUDS_NRC_CVFIC = uds_nrc(0x55)  # Certificate Verification Failed Invalid Content
PUDS_NRC_CVFISCP = uds_nrc(0x56)  # Certificate Verification Failed Invalid SCoPe
PUDS_NRC_CVFICERT = uds_nrc(0x57)  # Certificate Verification Failed Invalid CERTificate(revoked)
PUDS_NRC_OVF = uds_nrc(0x58)  # Ownership Verification Failed
PUDS_NRC_CCF = uds_nrc(0x59)  # Challenge Calculation Failed
PUDS_NRC_SARF = uds_nrc(0x5A)  # Setting Access Rights Failed
PUDS_NRC_SKCDF = uds_nrc(0x5B)  # Session Key Creation / Derivation Failed
PUDS_NRC_CDUF = uds_nrc(0x5C)  # Configuration Data Usage Failed
PUDS_NRC_DAF = uds_nrc(0x5D)  # DeAuthentication Failed
PUDS_NRC_UDNA = uds_nrc(0x70)  # Upload Download Not Accepted
PUDS_NRC_TDS = uds_nrc(0x71)  # Transfer Data Suspended
PUDS_NRC_GPF = uds_nrc(0x72)  # General Programming Failure
PUDS_NRC_WBSC = uds_nrc(0x73)  # Wrong Block Sequence Counter
PUDS_NRC_RCRRP = uds_nrc(0x78)  # Request Correctly Received - Response Pending
PUDS_NRC_SFNSIAS = uds_nrc(0x7E)  # Sub Function Not Supported In Active Session
PUDS_NRC_SNSIAS = uds_nrc(0x7F)  # Service Not Supported In Active Session
PUDS_NRC_RPMTH = uds_nrc(0x81)  # RPM Too High
PUDS_NRC_RPMTL = uds_nrc(0x82)  # RPM Too Low
PUDS_NRC_EIR = uds_nrc(0x83)  # Engine Is Running
PUDS_NRC_EINR = uds_nrc(0x84)  # Engine Is Not Running
PUDS_NRC_ERTTL = uds_nrc(0x85)  # Engine Run Time Too Low
PUDS_NRC_TEMPTH = uds_nrc(0x86)  # TEMPerature Too High
PUDS_NRC_TEMPTL = uds_nrc(0x87)  # TEMPerature Too Low
PUDS_NRC_VSTH = uds_nrc(0x88)  # Vehicle Speed Too High
PUDS_NRC_VSTL = uds_nrc(0x89)  # Vehicle Speed Too Low
PUDS_NRC_TPTH = uds_nrc(0x8A)  # Throttle / Pedal Too High
PUDS_NRC_TPTL = uds_nrc(0x8B)  # Throttle / Pedal Too Low
PUDS_NRC_TRNIN = uds_nrc(0x8C)  # Transmission Range Not In Neutral
PUDS_NRC_TRNIG = uds_nrc(0x8D)  # Transmission Range Not In Gear
PUDS_NRC_BSNC = uds_nrc(0x8F)  # Brake Switch(es) Not Closed(brake pedal not pressed or not applied)
PUDS_NRC_SLNIP = uds_nrc(0x90)  # Shifter Lever Not In Park
PUDS_NRC_TCCL = uds_nrc(0x91)  # Torque Converter Clutch Locked
PUDS_NRC_VTH = uds_nrc(0x92)  # Voltage Too High
PUDS_NRC_VTL = uds_nrc(0x93)  # Voltage Too Low
PUDS_NRC_RTNA = uds_nrc(0x94)  # Resource Temporarily Not Available

# PUDS ISO_15765_4 11 bit CAN ID definitions
PUDS_ISO_15765_4_CAN_ID_FUNCTIONAL_REQUEST = 0x7DF  # CAN ID for functionally addressed request messages sent by external test equipment
PUDS_ISO_15765_4_CAN_ID_PHYSICAL_REQUEST_1 = 0x7E0  # physical request CAN ID from external test equipment to ECU #1
# PUDS_ISO_15765_4_CAN_ID_PHYSICAL_REQUEST_1      = 0x791
PUDS_ISO_15765_4_CAN_ID_PHYSICAL_RESPONSE_1 = 0x7E8  # physical response CAN ID from ECU #1 to external test equipment
# PUDS_ISO_15765_4_CAN_ID_PHYSICAL_RESPONSE_1     = 0x799
PUDS_ISO_15765_4_CAN_ID_PHYSICAL_REQUEST_2 = 0x7E1  # physical request CAN ID from external test equipment to ECU #2
PUDS_ISO_15765_4_CAN_ID_PHYSICAL_RESPONSE_2 = 0x7E9  # physical response CAN ID from ECU #2 to external test equipment
PUDS_ISO_15765_4_CAN_ID_PHYSICAL_REQUEST_3 = 0x7E2  # physical request CAN ID from external test equipment to ECU #3
PUDS_ISO_15765_4_CAN_ID_PHYSICAL_RESPONSE_3 = 0x7EA  # physical response CAN ID from ECU #3 to external test equipment
PUDS_ISO_15765_4_CAN_ID_PHYSICAL_REQUEST_4 = 0x7E3  # physical request CAN ID from external test equipment to ECU #4
PUDS_ISO_15765_4_CAN_ID_PHYSICAL_RESPONSE_4 = 0x7EB  # physical response CAN ID from ECU #4 to external test equipment
PUDS_ISO_15765_4_CAN_ID_PHYSICAL_REQUEST_5 = 0x7E4  # physical request CAN ID from external test equipment to ECU #5
PUDS_ISO_15765_4_CAN_ID_PHYSICAL_RESPONSE_5 = 0x7EC  # physical response CAN ID from ECU #5 to external test equipment
PUDS_ISO_15765_4_CAN_ID_PHYSICAL_REQUEST_6 = 0x7E5  # physical request CAN ID from external test equipment to ECU #6
PUDS_ISO_15765_4_CAN_ID_PHYSICAL_RESPONSE_6 = 0x7ED  # physical response CAN ID from ECU #6 to external test equipment
PUDS_ISO_15765_4_CAN_ID_PHYSICAL_REQUEST_7 = 0x7E6  # physical request CAN ID from external test equipment to ECU #7
PUDS_ISO_15765_4_CAN_ID_PHYSICAL_RESPONSE_7 = 0x7EE  # physical response CAN ID from ECU #7 to external test equipment
PUDS_ISO_15765_4_CAN_ID_PHYSICAL_REQUEST_8 = 0x7E7  # physical request CAN ID from external test equipment to ECU #8
PUDS_ISO_15765_4_CAN_ID_PHYSICAL_RESPONSE_8 = 0x7EF  # physical response CAN ID from ECU #8 to external test equipment

# PUDS ISO_15765_4 address definitions
PUDS_ISO_15765_4_ADDR_TEST_EQUIPMENT = 0xF1  # external test equipment
PUDS_ISO_15765_4_ADDR_OBD_FUNCTIONAL = 0x33  # OBD funtional system
PUDS_ISO_15765_4_ADDR_ECU_1 = 0x01  # ECU 1
PUDS_ISO_15765_4_ADDR_ECU_2 = 0x02  # ECU 2
PUDS_ISO_15765_4_ADDR_ECU_3 = 0x03  # ECU 3
PUDS_ISO_15765_4_ADDR_ECU_4 = 0x04  # ECU 4
PUDS_ISO_15765_4_ADDR_ECU_5 = 0x05  # ECU 5
PUDS_ISO_15765_4_ADDR_ECU_6 = 0x06  # ECU 6
PUDS_ISO_15765_4_ADDR_ECU_7 = 0x07  # ECU 7
PUDS_ISO_15765_4_ADDR_ECU_8 = 0x08  # ECU 8

# PUDS parameter values
PUDS_TIMEOUT_REQUEST = 10000  # Default maximum timeout in milliseconds for UDS transmit confirmation
PUDS_TIMEOUT_RESPONSE = 10000  # Default maximum timeout in milliseconds for UDS response reception
PUDS_SERVER_ADDR_FLAG_ENHANCED_ISO_15765_3 = 0x1000  # Flag stating that the address is defined as a ISO-15765-3 address
PUDS_SERVER_ADDR_MASK_ENHANCED_ISO_15765_3 = 0x07FF  # Mask used for the ISO-15765-3 enhanced addresses
PUDS_CHANNEL_UNAVAILABLE = 0x00  # The Channel is illegal or not available
PUDS_CHANNEL_AVAILABLE = 0x01  # The Channel is available
PUDS_CHANNEL_OCCUPIED = 0x02  # The Channel is valid, and is being used
PUDS_CAN_DATA_PADDING_NONE = 0x00  # Uses CAN frame data optimization
PUDS_CAN_DATA_PADDING_ON = 0x01  # Uses CAN frame data padding (default, i.e. CAN DLC = 8)
PUDS_CAN_DATA_PADDING_VALUE = 0x55  # Default value used if CAN data padding is enabled

PUDS_P2CAN_SERVER_MAX_DEFAULT = 50  # Default server performance requirement in ms (See ISO_14229-2_2013 7.2 table 4)
PUDS_P2CAN_ENHANCED_SERVER_MAX_DEFAULT = 5000  # Enhanced server performance requirement in ms (See ISO_14229-2_2013 7.2 table 4)
PUDS_S3_CLIENT_TIMEOUT_RECOMMENDED = 2000  # Recommended S3 client timeout in ms (See ISO_14229-2_2013 7.5 table 5)
PUDS_P3CAN_DEFAULT = PUDS_P2CAN_SERVER_MAX_DEFAULT  # Default P3 timing parameter in ms (See ISO_14229-2_2013 7.2 table 4)

PUDS_DEBUG_LVL_NONE = 0x00  # Disable debug messages (default)
PUDS_DEBUG_LVL_ERROR = 0xF1  # Enable debug messages (only errors)
PUDS_DEBUG_LVL_WARNING = 0xF2  # Enable debug messages (only warnings, errors)
PUDS_DEBUG_LVL_INFORMATION = 0xF3  # Enable debug messages (only informations, warnings, errors)
PUDS_DEBUG_LVL_NOTICE = 0xF4  # Enable debug messages (only notices, informations, warnings, errors)
PUDS_DEBUG_LVL_DEBUG = 0xF5  # Enable debug messages (only debug, notices, informations, warnings, errors)
PUDS_DEBUG_LVL_TRACE = 0xF6  # Enable all debug messages

PUDS_ONLY_PREPARE_REQUEST = PCANTP_HANDLE_NONEBUS  # Option that can be used as channel identifier in UDS_Svc* functions: only prepare uds_msg structure and do not send it

# PUDS message data flags
PUDS_FLAG_SUPPRESS_POSITIVE_RESPONSE = 0x80  # Flag to suppress positive response message


##############################
# Message definitions
##############################

# Represents a UDS Network Addressing Information
class uds_netaddrinfo(Structure):
    """
    Represents a UDS Network Addressing Information
    """
    _pack_ = 8
    _fields_ = [("protocol", uds_msgprotocol),  # communication protocol
                ("target_type", cantp_isotp_addressing),  # ISO-TP target type
                ("source_addr", c_uint16),  # source address
                ("target_addr", c_uint16),  # target address
                ("extension_addr", c_uint8)]  # extension address


# Represents the diagnostic session's information of a server
class uds_sessioninfo(Structure):
    """
    Represents the diagnostic session's information of a server
    """
    _pack_ = 8
    _fields_ = [("nai", uds_netaddrinfo),  # Network address information
                ("can_msg_type", cantp_can_msgtype),  # Types and flags of the CAN/CAN-FD frames
                ("session_type", c_uint8),  # Activated Diagnostic Session (see PUDS_SVC_PARAM_DSC_xxx values)
                ("timeout_p2can_server_max", c_uint16),
                # Default P2Can_Server_Max timing for the activated session (resolution: 1ms)
                ("timeout_enhanced_p2can_server_max", c_uint16),
                # Enhanced P2Can_Server_Max timing for the activated session (resolution: 10ms)
                ("s3_client_ms", c_uint16)]  # Time between 2 TesterPresents


# Represents the configuration of a PUDS message
class uds_msgconfig(Structure):
    """
    Represents the configuration of a PUDS message
    """
    _pack_ = 8
    _fields_ = [("type", uds_msgtype),  # structure specific flags
                ("nai", uds_netaddrinfo),  # Network Addressing Information
                ("can_id", c_uint32),  # (optional) CAN ID (for configuration use either nai or m_can_id)
                ("can_msgtype", cantp_can_msgtype),  # optional flags for the CAN layer (29 bits CAN-ID, FD, BRS)
                ("can_tx_dlc", c_uint8)]  # Default CAN DLC value to use with segmented messages


# Represents a mapping between an UDS Network Addressing Information and a CAN ID.
class uds_mapping(Structure):
    """
    Represents a mapping between an UDS Network Addressing Information and a CAN ID.
    """
    _pack_ = 8
    _fields_ = [("uid", c_void_p),  # Mapping's unique ID
                ("can_id", c_uint32),  # CAN ID mapped to the Network Address Information
                ("can_id_flow_ctrl", c_uint32),  # CAN ID used for the flow control frame (formerly 'can_id_resp')
                ("can_msgtype", cantp_can_msgtype),
                # CAN frame msgtype (only PCANTP_CAN_MSGTYPE_STANDARD or PCANTP_CAN_MSGTYPE_EXTENDED is mandatory)
                ("can_tx_dlc", c_uint8),  # Default CAN DLC value to use with segmented messages
                ("nai", uds_netaddrinfo)]  # Network Addressing Information


PUDS_MAPPING_FLOW_CTRL_NONE = 0xFFFFFFFF  # Mapping does not require a Flow Control frame.


# Provides accessors to the corresponding data in the cantp_msg
class uds_msgaccess(Structure):
    """
    Provides accessors to the corresponding data in the cantp_msg
    """
    _pack_ = 8
    _fields_ = [("service_id", POINTER(c_ubyte)),  # Pointer to the Service ID in message's data.
                ("param", POINTER(c_ubyte)),  # Pointer to the first parameter in message's data.
                ("nrc", POINTER(
                    c_ubyte))]  # Pointer to the Negative Response Code (see uds_nrc enumeration) in message's data (NULL on positive response).


# Represents the content of a UDS message.
class uds_msg(Structure):
    """
    Represents the content of a UDS message.
    """
    _pack_ = 8
    _fields_ = [("type", uds_msgtype),  # structure specific flags
                ("links", uds_msgaccess),  # quick accessors to the cantp_msg data
                ("msg", cantp_msg)]  # the PCANTP message encapsulating the UDS data


###########################################
# PCAN-UDS API: Core function declarations
###########################################

# PCAN-UDS_2013 API class implementation
#
class PCAN_UDS_2013:
    """
      PCAN-UDS_2013 class implementation
    """

    def __init__(self):
        # Loads the PCAN-UDS_2013 API
        #     
        if platform.system() == 'Windows':
            # Loads the API on Windows
            libpath = r'.\PCAN-UDS.dll'
            self.__m_dllUds = windll.LoadLibrary(libpath)
        elif platform.system() == 'Linux':
            # Loads the API on Linux
            self.__m_dllUds = cdll.LoadLibrary("libpcanuds.so")

        if self.__m_dllUds == None:
            msg = f"Exception: The PCAN-UDS.dll couldn't be loaded!"
            print(msg)
            raise FileNotFoundError(msg)

    def Initialize_2013(
            self,
            channel,
            baudrate,
            hw_type=0,
            io_port=0,
            interrupt=0):
        """
        Initializes a PUDS channel based on a PCANTP channel handle (without CAN-FD support)
        
        remarks: Only one PUDS channel can be initialized per CAN-Channel
        parameters:
         channel : A PCANTP channel handle
         baudrate : The CAN Hardware speed
         hw_type : NON PLUG-N-PLAY: The type of hardware and operation mode
         io_port : NON PLUG-N-PLAY: The I/O address for the parallel port
         interrupt : NON PLUG-N-PLAY: Interrupt number of the parallel port
        returns: A uds_status code. PUDS_STATUS_OK is returned on success
        """
        try:
            res = self.__m_dllUds.UDS_Initialize_2013(channel, baudrate, hw_type, io_port, interrupt)
            return uds_status(res)
        except:
            print("Exception")
            raise

    def InitializeFD_2013(
            self,
            channel,
            bitrate_fd):
        """
        Initializes a PUDS channel based on a PCANTP channel handle (including CAN-FD support)
        
        parameters:
         channel : The handle of a FD capable PCANTP Channel
         bitrate_fd : The speed for the communication (FD bit rate string)
        remarks: 
            Only one PUDS channel can be initialized per CAN-Channel.
            See PCAN_BR_* values
            * Parameter and values must be separated by '='
            * Couples of parameter/value must be separated by ','
            * Following parameter must be filled out: f_clock, data_brp, data_sjw, data_tseg1, data_tseg2,
            nom_brp, nom_sjw, nom_tseg1, nom_tseg2.
            * Following parameters are optional (not used yet): data_ssp_offset, nom_samp
        example: f_clock_mhz=80,nom_brp=0,nom_tseg1=13,nom_tseg2=0,nom_sjw=0,data_brp=0,data_tseg1=13,data_tseg2=0,data_sjw=0
        returns: A uds_status error code
        """
        try:
            res = self.__m_dllUds.UDS_InitializeFD_2013(channel, byref(bitrate_fd))
            return uds_status(res)
        except:
            print("Exception")
            raise

    def Uninitialize_2013(
            self,
            channel):
        """
        Uninitializes a PUDS channel
        
        parameters:
         channel : A PCANTP channel handle representing a PUDS channel
        returns: A uds_status code. PUDS_STATUS_OK is returned on success
        """
        try:
            res = self.__m_dllUds.UDS_Uninitialize_2013(channel)
            return uds_status(res)
        except:
            print("Exception")
            raise

    def Reset_2013(
            self,
            channel):
        """
        Resets the receive and transmit queues of a PUDS channel
        
        parameters:
         channel : A PCANTP channel handle representing a PUDS channel
        returns: A uds_status code. PUDS_STATUS_OK is returned on success
        """
        try:
            res = self.__m_dllUds.UDS_Reset_2013(channel)
            return uds_status(res)
        except:
            print("Exception")
            raise

    def GetCanBusStatus_2013(
            self,
            channel):
        """
        Gets information about the internal BUS status of a PUDS channel
        
         channel : A PCANTP channel handle representing a PUDS channel
        returns: A uds_status code. PUDS_STATUS_OK is returned on success
        """
        try:
            res = self.__m_dllUds.UDS_GetCanBusStatus_2013(channel)
            return uds_status(res)
        except:
            print("Exception")
            raise

    def Read_2013(
            self,
            channel,
            out_msg_buffer,
            in_msg_request=None,
            out_timestamp=None):
        """
        Reads a PUDS message from the receive queue of a PUDS channel
        
        parameters:
         channel : A PCANTP channel handle representing a PUDS channel
         out_msg_buffer : [out]A uds_msg structure buffer to store the PUDS message
         in_msg_request : (Optional) If None the first available message is fetched.
            Otherwise in_msg_request must represent a sent PUDS request.
            To look for the request confirmation, in_msg_request->type should not have the loopback flag;
            otherwise a response from the target ECU will be searched.
         out_timestamp : A cantp_timestamp structure buffer to get
            the reception time of the message. If this value is not desired, this parameter
            should be passed as None
        returns: A uds_status code. PUDS_STATUS_OK is returned on success
        """
        try:
            res = self.__m_dllUds.UDS_Read_2013(channel, byref(out_msg_buffer),
                                                None if in_msg_request == None else byref(in_msg_request),
                                                None if out_timestamp == None else byref(out_timestamp))
            return uds_status(res)
        except:
            print("Exception")
            raise

    def Write_2013(
            self,
            channel,
            msg_buffer):
        """
        Transmits a PUDS message
        
         channel : A PCANTP channel handle representing a PUDS channel
         msg_buffer : A uds_msg buffer with the message to be sent
        returns: A uds_status code. PUDS_STATUS_OK is returned on success
        """
        try:
            res = self.__m_dllUds.UDS_Write_2013(channel, byref(msg_buffer))
            return uds_status(res)
        except:
            print("Exception")
            raise

    def AddMapping_2013(
            self,
            channel,
            mapping):
        """
        Adds a user-defined UDS mapping (relation between a CAN ID and a UDS Network Address Information)
        
        remark: 
        Defining a mapping enables ISO-TP communication with opened Addressing Formats
        (like PCANTP_ISOTP_FORMAT_NORMAL or PCANTP_ISOTP_FORMAT_EXTENDED).
        
        parameters:
         channel : A PCANTP channel handle representing a PUDS channel
         mapping : Mapping (uds_mapping) to be added
        returns: A uds_status code. PUDS_STATUS_OK is returned on success
        """
        try:
            res = self.__m_dllUds.UDS_AddMapping_2013(channel, byref(mapping))
            return uds_status(res)
        except:
            print("Exception")
            raise

    def RemoveMappingByCanId_2013(
            self,
            channel,
            can_id):
        """
        Removes all user-defined PUDS mappings corresponding to a CAN ID
        
         channel : A PCANTP channel handle representing a PUDS channel
         can_id : The mapped CAN ID to search for
        returns: A uds_status code. PUDS_STATUS_OK is returned on success
        """
        try:
            res = self.__m_dllUds.UDS_RemoveMappingByCanId_2013(channel, can_id)
            return uds_status(res)
        except:
            print("Exception")
            raise

    def RemoveMapping_2013(
            self,
            channel,
            mapping):
        """
        Removes a user-defined PUDS mapping
        
        parameters:
         channel : A PCANTP channel handle representing a PUDS channel
         mapping : The mapping (uds_mapping) to remove
        returns: A uds_status code. PUDS_STATUS_OK is returned on success
        """
        try:
            res = self.__m_dllUds.UDS_RemoveMapping_2013(channel, mapping)
            return uds_status(res)
        except:
            print("Exception")
            raise

    def GetMapping_2013(
            self,
            channel,
            buffer,
            can_id,
            can_msgtype):
        """
        Retrieves a mapping matching the given CAN identifier and message type (11bits, 29 bits, FD, etc.)
        
        parameters:
         channel : A PCANTP channel handle representing a PUDS channel
         buffer : [out]Buffer (uds_mapping) to store the searched mapping
         can_id : The mapped CAN ID to look for
         can_msgtype : The CAN message type to look for (11bits, 29 bits, FD, etc.)
        returns: A uds_status code. PUDS_STATUS_OK is returned on success,
            PUDS_STATUS_MAPPING_NOT_INITIALIZED if no mapping was found.
        """
        try:
            res = self.__m_dllUds.UDS_GetMapping_2013(channel, byref(buffer), can_id, can_msgtype)
            return uds_status(res)
        except:
            print("Exception")
            raise

    def GetMappings_2013(
            self,
            channel,
            buffer,
            buffer_length,
            count):
        """
        Retrieves all the mappings defined for a PUDS channel
        
        parameters:
         channel : A PCANTP channel handle representing a PUDS channel
         buffer : [out]Buffer of mappings (uds_mapping)
         buffer_length : The number of uds_mapping elements the buffer can store.
         count : [out]The actual number of elements copied in the buffer (c_uint16).
        """
        try:
            res = self.__m_dllUds.UDS_GetMappings_2013(channel, byref(buffer), buffer_length, byref(count))
            return uds_status(res)
        except:
            print("Exception")
            raise

    def AddCanIdFilter_2013(
            self,
            channel,
            can_id):
        """
        Adds a "PASS" filter on a CAN ID
        
        remark: 
        CAN and CAN FD frames matching this CAN ID will be fetchable by the UDS API with UDS_Read_2013 function.
        By default all frames are ignored and are available in lower APIs.
        
         channel : A PCANTP channel handle representing a PUDS channel
         can_id : CAN identifier to listen to
        returns: A uds_status code. PUDS_STATUS_OK is returned on success
        """
        try:
            res = self.__m_dllUds.UDS_AddCanIdFilter_2013(channel, can_id)
            return uds_status(res)
        except:
            print("Exception")
            raise

    def RemoveCanIdFilter_2013(
            self,
            channel,
            can_id):
        """
        Remove a "PASS" filter on a CAN ID
        
        parameters:
         channel : A PCANTP channel handle representing a PUDS channel
         can_id : CAN identifier to remove
        returns: A uds_status code. PUDS_STATUS_OK is returned on success
        """
        try:
            res = self.__m_dllUds.UDS_RemoveCanIdFilter_2013(channel, can_id)
            return uds_status(res)
        except:
            print("Exception")
            raise

    def GetValue_2013(
            self,
            channel,
            parameter,
            buffer,
            buffer_size):
        """
        Retrieves a PUDS channel value
        
        remark: 
            * Parameter PUDS_PARAM_SERVER_ADDRESS uses 2 bytes data to describe
            the physical address of the equipment, but the first byte is needed only
            for ISO-15765-3 Enhanced diagnostics 29 bit CAN ID where addresses
            are 11 bits long.
            * Parameter PUDS_PARAM_SERVER_FILTER uses 2 bytes data to describe
            a functional address, but the first byte is needed only
            for ISO-15765-3 Enhanced diagnostics 29 bit CAN ID where addresses
            are 11 bits long; the Most Significant Bit is used to define filter
            status (see PUDS_SERVER_FILTER_LISTEN).
        
        parameters:
         channel : A PCANTP channel handle representing a PUDS channel
         parameter : The parameter to get
         buffer : Buffer for the parameter value
         buffer_size : Size in bytes of the buffer
        returns: A uds_status code. PUDS_STATUS_OK is returned on success
        """
        try:
            res = self.__m_dllUds.UDS_GetValue_2013(channel, parameter, byref(buffer), buffer_size)
            return uds_status(res)
        except:
            print("Exception")
            raise

    def SetValue_2013(
            self,
            channel,
            parameter,
            buffer,
            buffer_size):
        """
        Configures or sets a PUDS channel value
        
        remark: 
             * Parameter PUDS_PARAM_SERVER_ADDRESS uses 2 bytes data to describe
            the physical address of the equipment, but the first byte is needed only
            for ISO-15765-3 Enhanced diagnostics 29 bit CAN ID where addresses
            are 11 bits long.
             * Parameter PUDS_PARAM_SERVER_FILTER uses 2 bytes data to describe
            a functional address, but the first byte is needed only
            for ISO-15765-3 Enhanced diagnostics 29 bit CAN ID where addresses
            are 11 bits long; the Most Significant Bit is used to define filter
            status.
        
        parameters:
         channel : A PCANTP channel handle representing a PUDS channel
         parameter : The parameter to set
         buffer : Buffer with the value to be set
         buffer_size : Size in bytes of the buffer
        returns: A uds_status code. PUDS_STATUS_OK is returned on success
        """
        try:
            res = self.__m_dllUds.UDS_SetValue_2013(channel, parameter, byref(buffer), buffer_size)
            return uds_status(res)
        except:
            print("Exception")
            raise

    def GetErrorText_2013(
            self,
            error_code,
            language,
            buffer,
            buffer_size):
        """
        Returns a descriptive text of a given cantp_status error
        code, in any desired language
        
        remarks: The current languages available for translation are:
            Neutral (0x00), German (0x07), English (0x09), Spanish (0x0A),
            Italian (0x10) and French (0x0C)
        parameters:
         error_code : A uds_status error code
         language : Indicates a 'Primary language ID'
         buffer : Buffer for a null terminated char array
         buffer_size : Buffer size
        returns: A uds_status error code
        """
        try:
            res = self.__m_dllUds.UDS_GetErrorText_2013(error_code, language, byref(buffer), buffer_size)
            return uds_status(res)
        except:
            print("Exception")
            raise

    def GetSessionInformation_2013(
            self,
            channel,
            session_info):
        """
        Gets the session information known by the API
        
        remark: 
        session_info must be initialized a network address information associated to an ECU.
        Note that the session's information within the API may be different to the actual session of the corresponding ECU.
        
        parameters:
         channel : A PCANTP channel handle representing a PUDS channel
         session_info : [in|out] The session (uds_sessioninfo) is filled if an ECU session, matching session_info->nai, exists
        returns: A uds_status code. PUDS_STATUS_OK is returned on success
        """
        try:
            res = self.__m_dllUds.UDS_GetSessionInformation_2013(channel, byref(session_info))
            return uds_status(res)
        except:
            print("Exception")
            raise

    def StatusIsOk_2013(
            self,
            status,
            status_expected=PUDS_STATUS_OK,
            strict_mode=0):
        """
        Checks if a status matches an expected result (default is PUDS_STATUS_OK).
        
        parameters:
         status : The status to analyze.
         status_expected : The expected status (default is PUDS_STATUS_OK).
         strict_mode : Enable strict mode (default is false). Strict mode ensures that bus or extra information are the same.
        returns: Returns true if the status matches expected parameter.
        """
        try:
            res = c_byte(self.__m_dllUds.UDS_StatusIsOk_2013(status, status_expected, strict_mode))
            booleanRes = False if res.value == 0 else True
            return booleanRes
        except:
            print("Exception")
            raise

    ##################################################################
    # PCAN-UDS API: PUDS Message initialization function declarations
    ##################################################################

    def MsgAlloc_2013(
            self,
            msg_buffer,
            msg_configuration,
            msg_data_length):
        """
        Allocates a PUDS message based on the given configuration
        
        parameters:
         msg_buffer : A uds_msg structure buffer (it will be freed if required)
         msg_configuration : Configuration of the PUDS message to allocate
         msg_data_length : Length of the message's data
        returns: A uds_status code. PUDS_STATUS_OK is returned on success
        """
        try:
            res = self.__m_dllUds.UDS_MsgAlloc_2013(byref(msg_buffer), msg_configuration, msg_data_length)
            return uds_status(res)
        except:
            print("Exception")
            raise

    def MsgFree_2013(
            self,
            msg_buffer):
        """
        Deallocates a PUDS message
        
        parameters:
         msg_buffer : An allocated uds_msg structure buffer
        returns: A uds_status code. PUDS_STATUS_OK is returned on success
        """
        try:
            res = self.__m_dllUds.UDS_MsgFree_2013(byref(msg_buffer))
            return uds_status(res)
        except:
            print("Exception")
            raise

    def MsgCopy_2013(
            self,
            msg_buffer_dst,
            msg_buffer_src):
        """
        Copies a PUDS message to another buffer.
        
        parameters:
         msg_buffer_dst : A uds_msg structure buffer to store the copied message.
         msg_buffer_src : The uds_msg structure buffer to copy.
        returns: A uds_status code. PUDS_STATUS_OK is returned on success
        """
        try:
            res = self.__m_dllUds.UDS_MsgCopy_2013(byref(msg_buffer_dst), byref(msg_buffer_src))
            return uds_status(res)
        except:
            print("Exception")
            raise

    def MsgMove_2013(
            self,
            msg_buffer_dst,
            msg_buffer_src):
        """
        Moves a PUDS message to another buffer (and cleans the original message structure).
        
        parameters:
         msg_buffer_dst : A uds_msg structure buffer to store the message.
         msg_buffer_src : The uds_msg structure buffer used as the source (will be cleaned).
        returns: A uds_status code. PUDS_STATUS_OK is returned on success
        """
        try:
            res = self.__m_dllUds.UDS_MsgMove_2013(byref(msg_buffer_dst), byref(msg_buffer_src))
            return uds_status(res)
        except:
            print("Exception")
            raise

    ##############################################
    # PCAN-UDS API: Utility function declarations
    ##############################################

    def WaitForSingleMessage_2013(
            self,
            channel,
            msg_request,
            is_waiting_for_tx,
            timeout,
            timeout_enhanced,
            out_msg_response):
        """
        Waits for a message (a response or a transmit confirmation) based on a UDS request
        
        remarks: 
            Warning: The order of the parameters has changed in PCAN-UDS 2.0 API.
        
        parameters:
         channel : A PCANTP channel handle representing a PUDS channel
         msg_request : A sent uds_msg message used as a reference to find the waited message
         is_waiting_for_tx : States if the message to wait for is a transmit confirmation
         timeout : Maximum time to wait (in milliseconds) for a message indication corresponding to the message request
         timeout_enhanced : Maximum time to wait for a message indication if the server requests more time
         out_msg_response : A uds_msg structure buffer to store the PUDS response
        returns: A uds_status code. PUDS_STATUS_OK is returned on success
        """
        try:
            res = self.__m_dllUds.UDS_WaitForSingleMessage_2013(channel, byref(msg_request), is_waiting_for_tx, timeout,
                                                                timeout_enhanced, byref(out_msg_response))
            return uds_status(res)
        except:
            print("Exception")
            raise

    def WaitForFunctionalResponses_2013(
            self,
            channel,
            msg_request,
            timeout,
            timeout_enhanced,
            wait_until_timeout,
            max_msg_count,
            out_msg_responses,
            out_msg_count):
        """
        Waits for multiple responses (from a functional request for instance) based on a PUDS message request.
        
        remarks: 
            Warning: The order of the parameters has changed in PCAN-UDS 2.0 API.
        
        parameters:
         channel : A PCANTP channel handle representing a PUDS channel
         msg_request : A sent uds_msg message used as a reference to find the waited message
         timeout : Maximum time to wait (in milliseconds) for a message indication corresponding to the message request.
         timeout_enhanced : Maximum time to wait for a message indication if the server requested more time
         wait_until_timeout : if <code>FALSE</code> the function is interrupted if out_msg_count reaches max_msg_count.
         max_msg_count : Length of the buffer array (max. messages that can be received)
         out_msg_responses : Buffer must be an array of 'max_msg_count' entries (must have at least
            a size of max_msg_count * sizeof(uds_msg) bytes
         out_msg_count : Actual number of messages read (c_uint32)
        returns: A uds_status code. PUDS_STATUS_OK is returned on success,
        PUDS_ERROR_OVERFLOW indicates success but buffer was too small to hold all responses.
        """
        try:
            res = self.__m_dllUds.UDS_WaitForFunctionalResponses_2013(channel, byref(msg_request), timeout,
                                                                      timeout_enhanced, wait_until_timeout,
                                                                      max_msg_count, byref(out_msg_responses),
                                                                      byref(out_msg_count))
            return uds_status(res)
        except:
            print("Exception")
            raise

    def WaitForService_2013(
            self,
            channel,
            msg_request,
            out_msg_response,
            out_msg_request_confirmation):
        """
        Handles the communication workflow for a UDS service expecting a single response.
        
        remark: 
        1) Warning: The order of the parameters has changed in PCAN-UDS 2.0 API.
        2) The function waits for a transmit confirmation then for a message response.
        Even if the SuppressPositiveResponseMessage flag is set, the function will still wait
        for an eventual Negative Response.
        
        parameters:
         channel : A PCANTP channel handle representing a PUDS channel
         msg_request : A sent uds_msg message used as a reference to manage the UDS service
         out_msg_response : A uds_msg structure buffer to store the PUDS response
         out_msg_request_confirmation : A uds_msg structure buffer to store the PUDS request confirmation
        returns: A uds_status code. PUDS_STATUS_OK is returned on success
        """
        try:
            res = self.__m_dllUds.UDS_WaitForService_2013(channel, byref(msg_request), byref(out_msg_response),
                                                          byref(out_msg_request_confirmation))
            return uds_status(res)
        except:
            print("Exception")
            raise

    def WaitForServiceFunctional_2013(
            self,
            channel,
            msg_request,
            max_msg_count,
            wait_until_timeout,
            out_msg_responses,
            out_msg_count,
            out_msg_request_confirmation):
        """
        Handles the communication workflow for a UDS service expecting multiple responses.
        
        remark: 
        1) Warning: The order of the parameters has changed in PCAN-UDS 2.0 API.
        2) The function waits for a transmit confirmation then for N message responses.
        Even if the SuppressPositiveResponseMessage flag is set, the function will still wait
        for eventual Negative Responses.
        
        parameters:
         channel : A PCANTP channel handle representing a PUDS channel
         msg_request : sent uds_msg message
         max_msg_count : Length of the buffer array (max. messages that can be received)
         wait_until_timeout : if <code>FALSE</code> the function is interrupted if out_msg_count reaches max_msg_count.
         out_msg_responses : Buffer must be an array of 'max_msg_count' entries (must have at least
            a size of max_msg_count * sizeof(uds_msg) bytes
         out_msg_count : Actual number of messages read (c_uint32)
         out_msg_request_confirmation : A uds_msg structure buffer to store the PUDS request confirmation
        returns: A uds_status code. PUDS_STATUS_OK is returned on success,
            PUDS_ERROR_OVERFLOW indicates success but buffer was too small to hold all responses.
        """
        try:
            res = self.__m_dllUds.UDS_WaitForServiceFunctional_2013(channel, byref(msg_request), max_msg_count,
                                                                    wait_until_timeout, byref(out_msg_responses),
                                                                    byref(out_msg_count),
                                                                    byref(out_msg_request_confirmation))
            return uds_status(res)
        except:
            print("Exception")
            raise

    ##################################################
    # PCAN-UDS API: UDS Service function declarations
    ##################################################

    # PUDS Service ids defined in ISO 14229-1:2013
    #
    PUDS_SI_DiagnosticSessionControl = 0x10  # see ISO 14229-1:2013
    PUDS_SI_ECUReset = 0x11  # see ISO 14229-1:2013
    PUDS_SI_SecurityAccess = 0x27  # see ISO 14229-1:2013
    PUDS_SI_CommunicationControl = 0x28  # see ISO 14229-1:2013
    PUDS_SI_TesterPresent = 0x3E  # see ISO 14229-1:2013
    PUDS_SI_AccessTimingParameter = 0x83  # see ISO 14229-1:2013
    PUDS_SI_SecuredDataTransmission = 0x84  # see ISO 14229-1:2013
    PUDS_SI_ControlDTCSetting = 0x85  # see ISO 14229-1:2013
    PUDS_SI_ResponseOnEvent = 0x86  # see ISO 14229-1:2013
    PUDS_SI_LinkControl = 0x87  # see ISO 14229-1:2013
    PUDS_SI_ReadDataByIdentifier = 0x22  # see ISO 14229-1:2013
    PUDS_SI_ReadMemoryByAddress = 0x23  # see ISO 14229-1:2013
    PUDS_SI_ReadScalingDataByIdentifier = 0x24  # see ISO 14229-1:2013
    PUDS_SI_ReadDataByPeriodicIdentifier = 0x2A  # see ISO 14229-1:2013
    PUDS_SI_DynamicallyDefineDataIdentifier = 0x2C  # see ISO 14229-1:2013
    PUDS_SI_WriteDataByIdentifier = 0x2E  # see ISO 14229-1:2013
    PUDS_SI_WriteMemoryByAddress = 0x3D  # see ISO 14229-1:2013
    PUDS_SI_ClearDiagnosticInformation = 0x14  # see ISO 14229-1:2013
    PUDS_SI_ReadDTCInformation = 0x19  # see ISO 14229-1:2013
    PUDS_SI_InputOutputControlByIdentifier = 0x2F  # see ISO 14229-1:2013
    PUDS_SI_RoutineControl = 0x31  # see ISO 14229-1:2013
    PUDS_SI_RequestDownload = 0x34  # see ISO 14229-1:2013
    PUDS_SI_RequestUpload = 0x35  # see ISO 14229-1:2013
    PUDS_SI_TransferData = 0x36  # see ISO 14229-1:2013
    PUDS_SI_RequestTransferExit = 0x37  # see ISO 14229-1:2013
    PUDS_SI_RequestFileTransfer = 0x38  # see ISO 14229-1:2013
    PUDS_SI_Authentication = 0x29  # see ISO 14229-1:2020
    PUDS_NR_SI = 0x7F  # negative response
    PUDS_NRC_EXTENDED_TIMING = 0x78  # server wants more time
    PUDS_SI_POSITIVE_RESPONSE = 0x40  # positive response offset

    # ISO-14229-1:2013 9.2.2.2 p.39
    PUDS_SVC_PARAM_DSC_DS = 0x01  # Default Session
    PUDS_SVC_PARAM_DSC_ECUPS = 0x02  # ECU Programming Session
    PUDS_SVC_PARAM_DSC_ECUEDS = 0x03  # ECU Extended Diagnostic Session
    PUDS_SVC_PARAM_DSC_SSDS = 0x04  # Safety System Diagnostic Session

    def SvcDiagnosticSessionControl_2013(
            self,
            channel,
            request_config,
            out_msg_request,
            session_type):
        """
        The DiagnosticSessionControl service is used to enable different diagnostic sessions in the server.
        
        parameters:
         channel : A PCANTP channel handle representing a PUDS channel
         request_config : Request configuration (uds_msgconfig)
         out_msg_request : (out) request message created and sent by the function (uds_msg)
         session_type : Subfunction parameter: type of the session (see PUDS_SVC_PARAM_DSC_xxx)
        returns: A uds_status code. PUDS_STATUS_OK is returned on success
        """
        try:
            res = self.__m_dllUds.UDS_SvcDiagnosticSessionControl_2013(channel, request_config, byref(out_msg_request),
                                                                       session_type)
            return uds_status(res)
        except:
            print("Exception")
            raise

    # ISO-14229-1:2013 9.3.2.2 p.43
    PUDS_SVC_PARAM_ER_HR = 0x01  # Hard Reset
    PUDS_SVC_PARAM_ER_KOFFONR = 0x02  # Key Off on Reset
    PUDS_SVC_PARAM_ER_SR = 0x03  # Soft Reset
    PUDS_SVC_PARAM_ER_ERPSD = 0x04  # Enable Rapid Power Shutdown
    PUDS_SVC_PARAM_ER_DRPSD = 0x05  # Disable Rapid Power Shutdown

    def SvcECUReset_2013(
            self,
            channel,
            request_config,
            out_msg_request,
            reset_type):
        """
        The ECUReset service is used by the client to request a server reset.
        
        parameters:
         channel : A PCANTP channel handle representing a PUDS channel
         request_config : Request configuration (uds_msgconfig)
         out_msg_request : (out) request message created and sent by the function (uds_msg)
         reset_type : Subfunction parameter: type of Reset (see PUDS_SVC_PARAM_ER_xxx)
        returns: A uds_status code. PUDS_STATUS_OK is returned on success
        """
        try:
            res = self.__m_dllUds.UDS_SvcECUReset_2013(channel, request_config, byref(out_msg_request), reset_type)
            return uds_status(res)
        except:
            print("Exception")
            raise

    # ISO-14229-1:2013 9.4.2.2 p.49
    PUDS_SVC_PARAM_SA_RSD_1 = 0x01  # Request Seed
    PUDS_SVC_PARAM_SA_RSD_3 = 0x03  # Request Seed
    PUDS_SVC_PARAM_SA_RSD_5 = 0x05  # Request Seed
    PUDS_SVC_PARAM_SA_RSD_MIN = 0x07  # Request Seed (odd numbers)
    PUDS_SVC_PARAM_SA_RSD_MAX = 0x5F  # Request Seed (odd numbers)
    PUDS_SVC_PARAM_SA_SK_2 = 0x02  # Send Key
    PUDS_SVC_PARAM_SA_SK_4 = 0x04  # Send Key
    PUDS_SVC_PARAM_SA_SK_6 = 0x06  # Send Key
    PUDS_SVC_PARAM_SA_SK_MIN = 0x08  # Send Key (even numbers)
    PUDS_SVC_PARAM_SA_SK_MAX = 0x60  # Send Key (even numbers)

    def SvcSecurityAccess_2013(
            self,
            channel,
            request_config,
            out_msg_request,
            security_access_type,
            security_access_data,
            security_access_data_size):
        """
        SecurityAccess service provides a means to access data and/or diagnostic services which have
        restricted access for security, emissions or safety reasons.
        
        parameters:
         channel : A PCANTP channel handle representing a PUDS channel
         request_config : Request configuration (uds_msgconfig)
         out_msg_request : (out) request message created and sent by the function (uds_msg)
         security_access_type : Subfunction parameter: type of SecurityAccess (see PUDS_SVC_PARAM_SA_xxx)
         security_access_data : If Requesting Seed, buffer is the optional data bytes to transmit to a server (like identification).
            If Sending Key, data holds the value generated by the security algorithm corresponding to a specific "seed" value
            security_access_data_size : Size in bytes of the buffer
        returns: A uds_status code. PUDS_STATUS_OK is returned on success
        """
        try:
            res = self.__m_dllUds.UDS_SvcSecurityAccess_2013(channel, request_config, byref(out_msg_request),
                                                             security_access_type, \
                                                             None if security_access_data == None else byref(
                                                                 security_access_data), security_access_data_size)
            return uds_status(res)
        except:
            print("Exception")
            raise

    # ISO-14229-1:2013 9.5.2.2 p.54
    PUDS_SVC_PARAM_CC_ERXTX = 0x00  # Enable Rx and Tx
    PUDS_SVC_PARAM_CC_ERXDTX = 0x01  # Enable Rx and Disable Tx
    PUDS_SVC_PARAM_CC_DRXETX = 0x02  # Disable Rx and Enable Tx
    PUDS_SVC_PARAM_CC_DRXTX = 0x03  # Disable Rx and Tx
    PUDS_SVC_PARAM_CC_ERXDTXWEAI = 0x04  # Enable Rx And Disable Tx With Enhanced Address Information
    PUDS_SVC_PARAM_CC_ERXTXWEAI = 0x05  # Enable Rx And Tx With Enhanced Address Information
    PUDS_SVC_PARAM_CC_FLAG_APPL = 0x01  # Application (01b)
    PUDS_SVC_PARAM_CC_FLAG_NWM = 0x02  # NetworkManagement (10b)
    PUDS_SVC_PARAM_CC_FLAG_DESCTIRNCN = 0x00  # Disable/Enable specified communicationType (see Flags APPL/NMW)
    # in the receiving node and all connected networks
    PUDS_SVC_PARAM_CC_FLAG_DENWRIRO = 0xF0  # Disable/Enable network which request is received on
    PUDS_SVC_PARAM_CC_FLAG_DESNIBNN_MIN = 0x10  # Disable/Enable specific network identified by network number (minimum value)
    PUDS_SVC_PARAM_CC_FLAG_DESNIBNN_MAX = 0xE0  # Disable/Enable specific network identified by network number (maximum value)
    PUDS_SVC_PARAM_CC_FLAG_DESNIBNN_MASK = 0xF0  # Mask for DESNIBNN bits

    def SvcCommunicationControl_2013(
            self,
            channel,
            request_config,
            out_msg_request,
            control_type,
            communication_type,
            node_identification_number=0):
        """
        CommunicationControl service's purpose is to switch on/off the transmission
        and/or the reception of certain messages of (a) server(s).
        
        parameters:
         channel : A PCANTP channel handle representing a PUDS channel
         request_config : Request configuration (uds_msgconfig)
         out_msg_request : (out) request message created and sent by the function (uds_msg)
         control_type : Subfunction parameter: type of CommunicationControl (see PUDS_SVC_PARAM_CC_xxx)
         communication_type : a bit-code value to reference the kind of communication to be controlled,
            See PUDS_SVC_PARAM_CC_FLAG_xxx flags and ISO_14229-1:2013 B.1 p.333 for bit-encoding
         node_identification_number : Identify a node on a sub-network (only used with
            PUDS_SVC_PARAM_CC_ERXDTXWEAI or PUDS_SVC_PARAM_CC_ERXTXWEAI control type)
        returns: A uds_status code. PUDS_STATUS_OK is returned on success
        """
        try:
            res = self.__m_dllUds.UDS_SvcCommunicationControl_2013(channel, request_config, byref(out_msg_request),
                                                                   control_type, communication_type,
                                                                   node_identification_number)
            return uds_status(res)
        except:
            print("Exception")
            raise

    # ISO-14229-1:2013 9.6.2.2 p.59
    PUDS_SVC_PARAM_TP_ZSUBF = 0x00  # Zero SubFunction

    def SvcTesterPresent_2013(
            self,
            channel,
            request_config,
            out_msg_request,
            testerpresent_type=PUDS_SVC_PARAM_TP_ZSUBF):
        """
        TesterPresent service indicates to a server (or servers) that a client is still connected
        to the vehicle and that certain diagnostic services and/or communications
        that have been previously activated are to remain active.
        
        parameters:
         channel : A PCANTP channel handle representing a PUDS channel
         request_config : Request configuration (uds_msgconfig)
         out_msg_request : (out) request message created and sent by the function (uds_msg)
         testerpresent_type : No Subfunction parameter by default (PUDS_SVC_PARAM_TP_ZSUBF)
        returns: A uds_status code. PUDS_STATUS_OK is returned on success
        """
        try:
            res = self.__m_dllUds.UDS_SvcTesterPresent_2013(channel, request_config, byref(out_msg_request),
                                                            testerpresent_type)
            return uds_status(res)
        except:
            print("Exception")
            raise

    # ISO-14229-1:2013 9.8 p.66
    def SvcSecuredDataTransmission_2013(
            self,
            channel,
            request_config,
            out_msg_request,
            security_data_request_record,
            security_data_request_record_size):
        """
        SecuredDataTransmission(2013) service's purpose is to transmit data that is protected
        against attacks from third parties, which could endanger data security.
        
        parameters:
         channel : A PCANTP channel handle representing a PUDS channel
         request_config : Request configuration (uds_msgconfig) (PUDS_MSGTYPE_FLAG_NO_POSITIVE_RESPONSE is ignored)
         out_msg_request : (out) request message created and sent by the function (uds_msg)
         security_data_request_record : buffer containing the data bytes as processed by the Security Sub-Layer (See ISO-15764)
         security_data_request_record_size : Size in bytes of the buffer
        returns: A uds_status code. PUDS_STATUS_OK is returned on success
        """
        try:
            res = self.__m_dllUds.UDS_SvcSecuredDataTransmission_2013(channel, request_config, byref(out_msg_request),
                                                                      byref(security_data_request_record),
                                                                      security_data_request_record_size)
            return uds_status(res)
        except:
            print("Exception")
            raise

    # ISO-14229-1:2020 16.2 p.358
    PUDS_SVC_PARAM_APAR_REQUEST_MSG_FLAG = 0x1  # The messsage is a request message.
    PUDS_SVC_PARAM_APAR_PRE_ESTABLISHED_KEY_FLAG = 0x8  # A pre - established key is used.
    PUDS_SVC_PARAM_APAR_ENCRYPTED_MSG_FLAG = 0x10  # Message is encrypted.
    PUDS_SVC_PARAM_APAR_SIGNED_MSG_FLAG = 0x20  # Message is signed.
    PUDS_SVC_PARAM_APAR_REQUEST_RESPONSE_SIGNATURE_FLAG = 0x40  # Signature on the response is requested.

    def SvcSecuredDataTransmission_2020(
            self,
            channel,
            request_config,
            out_msg_request,
            administrative_parameter,
            signature_encryption_calculation,
            anti_replay_counter,
            internal_service_identifier,
            service_specific_parameters,
            service_specific_parameters_size,
            signature_mac,
            signature_size):
        """
        SecuredDataTransmission(2020) service's purpose is to transmit data that is protected
        against attacks from third parties, which could endanger data security.
        
        parameters:
         channel : A PCANTP channel handle representing a PUDS channel
         request_config : Request configuration (uds_msgconfig) (PUDS_MSGTYPE_FLAG_NO_POSITIVE_RESPONSE is ignored)
         out_msg_request : (out) request message created and sent by the function (uds_msg)
         administrative_parameter : Security features used in the message (see PUDS_SVC_PARAM_APAR* definitions)
         signature_encryption_calculation : Signature or encryption algorithm identifier
         anti_replay_counter : Anti-replay counter value
         internal_service_identifier : Internal message service request identifier
         service_specific_parameters : Buffer that contains internal message service request data bytes
         service_specific_parameters_size : Internal message service request data size (in bytes)
         signature_mac : Buffer that contains signature bytes used to verify the message
         signature_size : Size in bytes of the signature
        returns: A uds_status code. PUDS_STATUS_OK is returned on success
        """
        try:
            res = self.__m_dllUds.UDS_SvcSecuredDataTransmission_2020(channel, request_config, byref(out_msg_request),
                                                                      administrative_parameter,
                                                                      signature_encryption_calculation, \
                                                                      anti_replay_counter, internal_service_identifier,
                                                                      byref(service_specific_parameters),
                                                                      service_specific_parameters_size, \
                                                                      byref(signature_mac), signature_size)
            return uds_status(res)
        except:
            print("Exception")
            raise

    # ISO-14229-1:2013 9.9.2.2 p.72
    PUDS_SVC_PARAM_CDTCS_ON = 0x01  # The server(s) shall resume the setting of diagnostic trouble codes
    PUDS_SVC_PARAM_CDTCS_OFF = 0x02  # The server(s) shall stop the setting of diagnostic trouble codes

    def SvcControlDTCSetting_2013(
            self,
            channel,
            request_config,
            out_msg_request,
            dtc_setting_type,
            dtc_setting_control_option_record,
            dtc_setting_control_option_record_size):
        """
        ControlDTCSetting service shall be used by a client to stop or resume the setting of
        diagnostic trouble codes (DTCs) in the server(s).
        
        parameters:
         channel : A PCANTP channel handle representing a PUDS channel
         request_config : Request configuration (uds_msgconfig)
         out_msg_request : (out) request message created and sent by the function (uds_msg)
         dtc_setting_type : Subfunction parameter (see PUDS_SVC_PARAM_CDTCS_xxx)
         dtc_setting_control_option_record : This parameter record is user-optional and transmits data bytes to a server when controlling the DTC setting.
            It can contain a list of DTCs to be turned on or off.
         dtc_setting_control_option_record_size : Size in bytes of the buffer
        returns: A uds_status code. PUDS_STATUS_OK is returned on success
        """
        try:
            res = self.__m_dllUds.UDS_SvcControlDTCSetting_2013(channel, request_config, byref(out_msg_request),
                                                                dtc_setting_type, \
                                                                None if dtc_setting_control_option_record == None else byref(
                                                                    dtc_setting_control_option_record),
                                                                dtc_setting_control_option_record_size)
            return uds_status(res)
        except:
            print("Exception")
            raise

    # ISO-14229-1:2013 9.10.2.2.1 p.78
    PUDS_SVC_PARAM_ROE_STPROE = 0x00  # Stop Response On Event
    PUDS_SVC_PARAM_ROE_ONDTCS = 0x01  # On DTC Status Change
    PUDS_SVC_PARAM_ROE_OTI = 0x02  # On Timer Interrupt
    PUDS_SVC_PARAM_ROE_OCODID = 0x03  # On Change Of Data Identifier
    PUDS_SVC_PARAM_ROE_RAE = 0x04  # Report Activated Events
    PUDS_SVC_PARAM_ROE_STRTROE = 0x05  # Start Response On Event
    PUDS_SVC_PARAM_ROE_CLRROE = 0x06  # Clear Response On Event
    PUDS_SVC_PARAM_ROE_OCOV = 0x07  # On Comparison Of Values
    PUDS_SVC_PARAM_ROE_RMRDOSC = 0x08  # Report Most Recent Dtc On Status Change (ISO 14229-1:2020 10.9.2.2 p.121)
    PUDS_SVC_PARAM_ROE_RDRIODSC = 0x09  # Report Dtc Record Information On Dtc Status Change (ISO 14229-1:2020 10.9.2.2 p.121)
    PUDS_SVC_PARAM_ROE_STPROE_LEN = 0  # Expected size of event type record for ROE_STPROE
    PUDS_SVC_PARAM_ROE_ONDTCS_LEN = 1  # Expected size of event type record for ROE_ONDTCS
    PUDS_SVC_PARAM_ROE_OTI_LEN = 1  # Expected size of event type record for ROE_OTI
    PUDS_SVC_PARAM_ROE_OCODID_LEN = 2  # Expected size of event type record for ROE_OCODID
    PUDS_SVC_PARAM_ROE_RAE_LEN = 0  # Expected size of event type record for ROE_RAE
    PUDS_SVC_PARAM_ROE_STRTROE_LEN = 0  # Expected size of event type record for ROE_STRTROE
    PUDS_SVC_PARAM_ROE_CLRROE_LEN = 0  # Expected size of event type record for ROE_CLRROE
    PUDS_SVC_PARAM_ROE_OCOV_LEN = 10  # Expected size of event type record for ROE_OCOV
    PUDS_SVC_PARAM_ROE_RMRDOSC_LEN = 1  # Expected size of event type record for ROE_RMRDOSC
    PUDS_SVC_PARAM_ROE_EWT_ITTR = 0x02  # Infinite Time To Response (eventWindowTime parameter)
    PUDS_SVC_PARAM_ROE_EWT_SEWT = 0x03  # Short event window time (eventWindowTime parameter)
    PUDS_SVC_PARAM_ROE_EWT_MEWT = 0x04  # Medium event window time (eventWindowTime parameter)
    PUDS_SVC_PARAM_ROE_EWT_LEWT = 0x05  # Long event window time (eventWindowTime parameter)
    PUDS_SVC_PARAM_ROE_EWT_PWT = 0x06  # Power window time (eventWindowTime parameter)
    PUDS_SVC_PARAM_ROE_EWT_IWT = 0x07  # Ignition window time (eventWindowTime parameter)
    PUDS_SVC_PARAM_ROE_EWT_MTEWT = 0x08  # Manufacturer trigger event window time (eventWindowTime parameter)
    PUDS_SVC_PARAM_ROE_OTI_SLOW_RATE = 0x01  # Slow rate (onTimerInterrupt parameter)
    PUDS_SVC_PARAM_ROE_OTI_MEDIUM_RATE = 0x02  # Medium rate (onTimerInterrupt parameter)
    PUDS_SVC_PARAM_ROE_OTI_FAST_RATE = 0x03  # Fast rate (onTimerInterrupt parameter)
    PUDS_SVC_PARAM_ROE_STRT_SI_RDBI = PUDS_SI_ReadDataByIdentifier  # Recommended service (first byte of service to respond to record)
    PUDS_SVC_PARAM_ROE_STRT_SI_RDTCI = PUDS_SI_ReadDTCInformation  # Recommended service (first byte of service to respond to record)
    PUDS_SVC_PARAM_ROE_STRT_SI_RC = PUDS_SI_RoutineControl  # Recommended service (first byte of service to respond to record)
    PUDS_SVC_PARAM_ROE_STRT_SI_IOCBI = PUDS_SI_InputOutputControlByIdentifier  # Recommended service (first byte of service to respond to record)

    def SvcResponseOnEvent_2013(
            self,
            channel,
            request_config,
            out_msg_request,
            event_type,
            store_event,
            event_window_time,
            event_type_record=None,
            event_type_record_size=0,
            service_to_respond_to_record=None,
            service_to_respond_to_record_size=0):
        """
        The ResponseOnEvent service requests a server to
        start or stop transmission of responses on a specified event.
        
        parameters:
         channel : A PCANTP channel handle representing a PUDS channel
         request_config : Request configuration (uds_msgconfig)
         out_msg_request : (out) request message created and sent by the function (uds_msg)
         event_type : Subfunction parameter: event type (see PUDS_SVC_PARAM_ROE_xxx)
         store_event : Storage State (TRUE = Store Event, FALSE = Do Not Store Event)
         event_window_time : Specify a window for the event logic to be active in the server (see PUDS_SVC_PARAM_ROE_EWT_ITTR)
         event_type_record : Additional parameters for the specified event type
         event_type_record_size : Size in bytes of the event type record (see PUDS_SVC_PARAM_ROE_xxx_LEN)
         service_to_respond_to_record : Service parameters, with first byte as service Id (see PUDS_SVC_PARAM_ROE_STRT_SI_xxx)
         service_to_respond_to_record_size : Size in bytes of the service to respond to record
        returns: A uds_status code. PUDS_STATUS_OK is returned on success
        """
        try:
            res = self.__m_dllUds.UDS_SvcResponseOnEvent_2013(channel, request_config, byref(out_msg_request),
                                                              event_type, store_event, event_window_time, \
                                                              None if event_type_record == None else byref(
                                                                  event_type_record), event_type_record_size, \
                                                              None if service_to_respond_to_record == None else byref(
                                                                  service_to_respond_to_record),
                                                              service_to_respond_to_record_size)
            return uds_status(res)
        except:
            print("Exception")
            raise

    # ISO-14229-1:2013 9.11.2.2 p.101
    PUDS_SVC_PARAM_LC_VBTWFBR = 0x01  # Verify Baudrate Transition With Fixed Baudrate
    PUDS_SVC_PARAM_LC_VBTWSBR = 0x02  # Verify Baudrate Transition With Specific Baudrate
    PUDS_SVC_PARAM_LC_TB = 0x03  # Transition Baudrate
    PUDS_SVC_PARAM_LC_BAUDRATE_PC_9600 = 0x01  # standard PC baud rate of 9.6 KBaud
    PUDS_SVC_PARAM_LC_BAUDRATE_PC_19200 = 0x02  # standard PC baud rate of 19.2 KBaud
    PUDS_SVC_PARAM_LC_BAUDRATE_PC_38400 = 0x03  # standard PC baud rate of 38.4 KBaud
    PUDS_SVC_PARAM_LC_BAUDRATE_PC_57600 = 0x04  # standard PC baud rate of 57.6 KBaud
    PUDS_SVC_PARAM_LC_BAUDRATE_PC_115200 = 0x05  # standard PC baud rate of 115.2 KBaud
    PUDS_SVC_PARAM_LC_BAUDRATE_CAN_125K = 0x10  # standard CAN baud rate of 125 KBaud
    PUDS_SVC_PARAM_LC_BAUDRATE_CAN_250K = 0x11  # standard CAN baud rate of 250 KBaud
    PUDS_SVC_PARAM_LC_BAUDRATE_CAN_500K = 0x12  # standard CAN baud rate of 500 KBaud
    PUDS_SVC_PARAM_LC_BAUDRATE_CAN_1M = 0x13  # standard CAN baud rate of 1 MBaud
    PUDS_SVC_PARAM_LC_BAUDRATE_PROGSU = 0x20  # Programming setup

    def SvcLinkControl_2013(
            self,
            channel,
            request_config,
            out_msg_request,
            link_control_type,
            baudrate_identifier,
            link_baudrate=0):
        """
        The LinkControl service is used to control the communication link baud rate
        between the client and the server(s) for the exchange of diagnostic data.
        
        parameters:
         channel : A PCANTP channel handle representing a PUDS channel
         request_config : Request configuration (uds_msgconfig)
         out_msg_request : (out) request message created and sent by the function (uds_msg)
         link_control_type : Subfunction parameter: Link Control Type (see PUDS_SVC_PARAM_LC_xxx)
         baudrate_identifier : defined baud rate identifier (see PUDS_SVC_PARAM_LC_BAUDRATE_xxx)
         link_baudrate : used only with PUDS_SVC_PARAM_LC_VBTWSBR parameter:
            a three-byte value baud rate (baudrate High, Middle and Low bytes).
        returns: A uds_status code. PUDS_STATUS_OK is returned on success 
        """
        try:
            res = self.__m_dllUds.UDS_SvcLinkControl_2013(channel, request_config, byref(out_msg_request),
                                                          link_control_type, baudrate_identifier, link_baudrate)
            return uds_status(res)
        except:
            print("Exception")
            raise

    # ISO-14229-1:2013 C.1 p337
    PUDS_SVC_PARAM_DI_BSIDID = 0xF180  # bootSoftwareIdentificationDataIdentifier
    PUDS_SVC_PARAM_DI_ASIDID = 0xF181  # applicationSoftwareIdentificationDataIdentifier
    PUDS_SVC_PARAM_DI_ADIDID = 0xF182  # applicationDataIdentificationDataIdentifier
    PUDS_SVC_PARAM_DI_BSFPDID = 0xF183  # bootSoftwareIdentificationDataIdentifier
    PUDS_SVC_PARAM_DI_ASFPDID = 0xF184  # applicationSoftwareFingerprintDataIdentifier
    PUDS_SVC_PARAM_DI_ADFPDID = 0xF185  # applicationDataFingerprintDataIdentifier
    PUDS_SVC_PARAM_DI_ADSDID = 0xF186  # activeDiagnosticSessionDataIdentifier
    PUDS_SVC_PARAM_DI_VMSPNDID = 0xF187  # vehicleManufacturerSparePartNumberDataIdentifier
    PUDS_SVC_PARAM_DI_VMECUSNDID = 0xF188  # vehicleManufacturerECUSoftwareNumberDataIdentifier
    PUDS_SVC_PARAM_DI_VMECUSVNDID = 0xF189  # vehicleManufacturerECUSoftwareVersionNumberDataIdentifier
    PUDS_SVC_PARAM_DI_SSIDDID = 0xF18A  # systemSupplierIdentifierDataIdentifier
    PUDS_SVC_PARAM_DI_ECUMDDID = 0xF18B  # ECUManufacturingDateDataIdentifier
    PUDS_SVC_PARAM_DI_ECUSNDID = 0xF18C  # ECUSerialNumberDataIdentifier
    PUDS_SVC_PARAM_DI_SFUDID = 0xF18D  # supportedFunctionalUnitsDataIdentifier
    PUDS_SVC_PARAM_DI_VMKAPNDID = 0xF18E  # vehicleManufacturerKitAssemblyPartNumberDataIdentifier
    PUDS_SVC_PARAM_DI_VINDID = 0xF190  # VINDataIdentifier
    PUDS_SVC_PARAM_DI_VMECUHNDID = 0xF191  # vehicleManufacturerECUHardwareNumberDataIdentifier
    PUDS_SVC_PARAM_DI_SSECUHWNDID = 0xF192  # systemSupplierECUHardwareNumberDataIdentifier
    PUDS_SVC_PARAM_DI_SSECUHWVNDID = 0xF193  # systemSupplierECUHardwareVersionNumberDataIdentifier
    PUDS_SVC_PARAM_DI_SSECUSWNDID = 0xF194  # systemSupplierECUSoftwareNumberDataIdentifier
    PUDS_SVC_PARAM_DI_SSECUSWVNDID = 0xF195  # systemSupplierECUSoftwareVersionNumberDataIdentifier
    PUDS_SVC_PARAM_DI_EROTANDID = 0xF196  # exhaustRegulationOrTypeApprovalNumberDataIdentifier
    PUDS_SVC_PARAM_DI_SNOETDID = 0xF197  # systemNameOrEngineTypeDataIdentifier
    PUDS_SVC_PARAM_DI_RSCOTSNDID = 0xF198  # repairShopCodeOrTesterSerialNumberDataIdentifier
    PUDS_SVC_PARAM_DI_PDDID = 0xF199  # programmingDateDataIdentifier
    PUDS_SVC_PARAM_DI_CRSCOCESNDID = 0xF19A  # calibrationRepairShopCodeOrCalibrationEquipmentSerialNumberDataIdentifier
    PUDS_SVC_PARAM_DI_CDDID = 0xF19B  # calibrationDateDataIdentifier
    PUDS_SVC_PARAM_DI_CESWNDID = 0xF19C  # calibrationEquipmentSoftwareNumberDataIdentifier
    PUDS_SVC_PARAM_DI_EIDDID = 0xF19D  # ECUInstallationDateDataIdentifier
    PUDS_SVC_PARAM_DI_ODXFDID = 0xF19E  # ODXFileDataIdentifier
    PUDS_SVC_PARAM_DI_EDID = 0xF19F  # entityDataIdentifier

    # ISO-14229-1:2013 10.2 p.106
    def SvcReadDataByIdentifier_2013(
            self,
            channel,
            request_config,
            out_msg_request,
            data_identifier,
            data_identifier_length):
        """
        The ReadDataByIdentifier service allows the client to request data record values
        from the server identified by one or more dataIdentifiers.
        
        parameters:
         channel : A PCANTP channel handle representing a PUDS channel
         request_config : Request configuration (uds_msgconfig) (PUDS_MSGTYPE_FLAG_NO_POSITIVE_RESPONSE is ignored)
         out_msg_request : (out) request message created and sent by the function (uds_msg)
         data_identifier : buffer containing a list of two-byte Data Identifiers (see PUDS_SVC_PARAM_DI_xxx)
         data_identifier_length : Number of elements in the buffer (size in uint16_t of the buffer)
        returns: A uds_status code. PUDS_STATUS_OK is returned on success
        """
        try:
            res = self.__m_dllUds.UDS_SvcReadDataByIdentifier_2013(channel, request_config, byref(out_msg_request),
                                                                   byref(data_identifier), data_identifier_length)
            return uds_status(res)
        except:
            print("Exception")
            raise

    # ISO-14229-1:2013 10.3 p.113
    def SvcReadMemoryByAddress_2013(
            self,
            channel,
            request_config,
            out_msg_request,
            memory_address_buffer,
            memory_address_size,
            memory_size_buffer,
            memory_size_size):
        """
        The ReadMemoryByAddress service allows the client to request memory data from the server
        via a provided starting address and to specify the size of memory to be read.
        
         channel : A PCANTP channel handle representing a PUDS channel
         request_config : Request configuration (uds_msgconfig) (PUDS_MSGTYPE_FLAG_NO_POSITIVE_RESPONSE is ignored)
         out_msg_request : (out) request message created and sent by the function (uds_msg)
         memory_address_buffer : starting address buffer of server memory from which data is to be retrieved
         memory_address_size : Size in bytes of the memory_address_buffer (max.: 0xF)
         memory_size_buffer : number of bytes to be read starting at the address specified by memory_address_buffer
         memory_size_size : Size in bytes of the memory_size_buffer (max.: 0xF)
        returns: A uds_status code. PUDS_STATUS_OK is returned on success
        """
        try:
            res = self.__m_dllUds.UDS_SvcReadMemoryByAddress_2013(channel, request_config, byref(out_msg_request),
                                                                  byref(memory_address_buffer), memory_address_size, \
                                                                  byref(memory_size_buffer), memory_size_size)
            return uds_status(res)
        except:
            print("Exception")
            raise

    # ISO-14229-1:2013 10.4 p.119
    def SvcReadScalingDataByIdentifier_2013(
            self,
            channel,
            request_config,
            out_msg_request,
            data_identifier):
        """
        The ReadScalingDataByIdentifier service allows the client to request
        scaling data record information from the server identified by a dataIdentifier.
        
        parameters:
         channel : A PCANTP channel handle representing a PUDS channel
         request_config : Request configuration (uds_msgconfig) (PUDS_MSGTYPE_FLAG_NO_POSITIVE_RESPONSE is ignored)
         out_msg_request : (out) request message created and sent by the function (uds_msg)
         data_identifier : a two-byte Data Identifier (see PUDS_SVC_PARAM_DI_xxx)
        returns: A uds_status code. PUDS_STATUS_OK is returned on success
        """
        try:
            res = self.__m_dllUds.UDS_SvcReadScalingDataByIdentifier_2013(channel, request_config,
                                                                          byref(out_msg_request), data_identifier)
            return uds_status(res)
        except:
            print("Exception")
            raise

    # ISO-14229-1:2013 C.4 p.351
    PUDS_SVC_PARAM_RDBPI_SASR = 0x01  # Send At Slow Rate
    PUDS_SVC_PARAM_RDBPI_SAMR = 0x02  # Send At Medium Rate
    PUDS_SVC_PARAM_RDBPI_SAFR = 0x03  # Send At Fast Rate
    PUDS_SVC_PARAM_RDBPI_SS = 0x04  # Stop Sending

    def SvcReadDataByPeriodicIdentifier_2013(
            self,
            channel,
            request_config,
            out_msg_request,
            transmission_mode,
            periodic_data_identifier,
            periodic_data_identifier_size):
        """
        The ReadDataByPeriodicIdentifier service allows the client to request the periodic transmission
        of data record values from the server identified by one or more periodicDataIdentifiers.
        
        parameters:
         channel : A PCANTP channel handle representing a PUDS channel
         request_config : Request configuration (uds_msgconfig) (PUDS_MSGTYPE_FLAG_NO_POSITIVE_RESPONSE is ignored)
         out_msg_request : (out) request message created and sent by the function (uds_msg)
         transmission_mode : transmission rate code (see PUDS_SVC_PARAM_RDBPI_xxx)
         periodic_data_identifier : buffer containing a list of Periodic Data Identifiers
         periodic_data_identifier_size : Number of elements in the buffer (size in bytes of the buffer)
        returns: A uds_status code. PUDS_STATUS_OK is returned on success
        """
        try:
            res = self.__m_dllUds.UDS_SvcReadDataByPeriodicIdentifier_2013(channel, request_config,
                                                                           byref(out_msg_request), transmission_mode,
                                                                           byref(periodic_data_identifier),
                                                                           periodic_data_identifier_size)
            return uds_status(res)
        except:
            print("Exception")
            raise

    # ISO-14229-1:2013 10.6.2.2 p.144
    PUDS_SVC_PARAM_DDDI_DBID = 0x01  # Define By Identifier
    PUDS_SVC_PARAM_DDDI_DBMA = 0x02  # Define By Memory Address
    PUDS_SVC_PARAM_DDDI_CDDDI = 0x03  # Clear Dynamically Defined Data Identifier

    def SvcDynamicallyDefineDataIdentifierDBID_2013(
            self,
            channel,
            request_config,
            out_msg_request,
            dynamically_defined_data_identifier,
            source_data_identifier,
            memory_size,
            position_in_source_data_record,
            number_of_elements):
        """
        The DynamicallyDefineDataIdentifier service allows the client to dynamically define
        in a server a data identifier that can be read via the ReadDataByIdentifier service at a later time.
        The Define By Identifier subfunction specifies that definition of the dynamic data
        identifier shall occur via a data identifier reference.
        
        parameters:
         channel : A PCANTP channel handle representing a PUDS channel
         request_config : Request configuration (uds_msgconfig)
         out_msg_request : (out) request message created and sent by the function (uds_msg)
         dynamically_defined_data_identifier : a two-byte Data Identifier (see PUDS_SVC_PARAM_DI_xxx)
         source_data_identifier : buffer containing the sources of information to be included into the dynamic data record (c_uint16)
         memory_size : buffer containing the total numbers of bytes from the source data record address
         position_in_source_data_record : buffer containing the starting byte positions of the excerpt of the source data record
         number_of_elements : Number of elements in SourceDataIdentifier/position_in_source_data_record/memory_size triplet.
        returns: A uds_status code. PUDS_STATUS_OK is returned on success
        """
        try:
            res = self.__m_dllUds.UDS_SvcDynamicallyDefineDataIdentifierDBID_2013(channel, request_config,
                                                                                  byref(out_msg_request),
                                                                                  dynamically_defined_data_identifier, \
                                                                                  byref(source_data_identifier),
                                                                                  byref(memory_size),
                                                                                  byref(position_in_source_data_record),
                                                                                  number_of_elements)
            return uds_status(res)
        except:
            print("Exception")
            raise

    def SvcDynamicallyDefineDataIdentifierDBMA_2013(
            self,
            channel,
            request_config,
            out_msg_request,
            dynamically_defined_data_identifier,
            memory_address_size,
            memory_size_size,
            memory_address_buffer,
            memory_size_buffer,
            number_of_elements):
        """
        The DynamicallyDefineDataIdentifier service allows the client to dynamically define
        in a server a data identifier that can be read via the ReadDataByIdentifier service at a later time.
        The Define By Memory Address subfunction specifies that definition of the dynamic data
        identifier shall occur via an address reference.
        
        parameters:
         channel : A PCANTP channel handle representing a PUDS channel
         request_config : Request configuration (uds_msgconfig)
         out_msg_request : (out) request message created and sent by the function (uds_msg)
         dynamically_defined_data_identifier : a two-byte Data Identifier (see PUDS_SVC_PARAM_DI_xxx)
         memory_address_size : Size in bytes of the memory address items in the memory_address_buffer (max.: 0xF)
         memory_size_size : Size in bytes of the memory size items in the memory_size_buffer (max.: 0xF)
         memory_address_buffer : buffer containing the memory address buffer,
            must be an array of 'number_of_elements' items whose size is 'memory_address_size'
            (size is 'number_of_elements * memory_address_size' bytes)
         memory_size_buffer : buffer containing the memory size buffer,
            must be an array of 'number_of_elements' items whose size is 'memory_size_size'
            (size is 'number_of_elements * memory_size_size' bytes)
         number_of_elements : Number of elements in memory_address_buffer/memory_size_buffer couple.
        returns: A uds_status code. PUDS_STATUS_OK is returned on success
        """
        try:
            res = self.__m_dllUds.UDS_SvcDynamicallyDefineDataIdentifierDBMA_2013(channel, request_config,
                                                                                  byref(out_msg_request),
                                                                                  dynamically_defined_data_identifier, \
                                                                                  memory_address_size, memory_size_size,
                                                                                  byref(memory_address_buffer),
                                                                                  byref(memory_size_buffer),
                                                                                  number_of_elements)
            return uds_status(res)
        except:
            print("Exception")
            raise

    def SvcDynamicallyDefineDataIdentifierCDDDI_2013(
            self,
            channel,
            request_config,
            out_msg_request,
            dynamically_defined_data_identifier):
        """
        The Clear Dynamically Defined Data Identifier subfunction shall be used to clear
        the specified dynamic data identifier.
        
        parameters:
         channel : A PCANTP channel handle representing a PUDS channel
         request_config : Request configuration (uds_msgconfig)
         out_msg_request : (out) request message created and sent by the function (uds_msg)
         dynamically_defined_data_identifier : a two-byte Data Identifier (see PUDS_SVC_PARAM_DI_xxx)
        returns: A uds_status code. PUDS_STATUS_OK is returned on success
        """
        try:
            res = self.__m_dllUds.UDS_SvcDynamicallyDefineDataIdentifierCDDDI_2013(channel, request_config,
                                                                                   byref(out_msg_request),
                                                                                   dynamically_defined_data_identifier)
            return uds_status(res)
        except:
            print("Exception")
            raise

    def SvcDynamicallyDefineDataIdentifierClearAllDDDI_2013(
            self,
            channel,
            request_config,
            out_msg_request):
        """
        The Clear All Dynamically Defined Data Identifier function shall be used to clear
        all dynamic data identifier declared in the server.
        
        parameters:
         channel : A PCANTP channel handle representing a PUDS channel
         request_config : Request configuration (uds_msgconfig)
         out_msg_request : (out) request message created and sent by the function (uds_msg)
        returns: A uds_status code. PUDS_STATUS_OK is returned on success
        """
        try:
            res = self.__m_dllUds.UDS_SvcDynamicallyDefineDataIdentifierClearAllDDDI_2013(channel, request_config,
                                                                                          byref(out_msg_request))
            return uds_status(res)
        except:
            print("Exception")
            raise

    # ISO-14229-1:2013 10.7 p.162
    def SvcWriteDataByIdentifier_2013(
            self,
            channel,
            request_config,
            out_msg_request,
            data_identifier,
            data_record,
            data_record_size):
        """
        The WriteDataByIdentifier service allows the client to write information into the server at an internal location
        specified by the provided data identifier.
        
        parameters:
         channel : A PCANTP channel handle representing a PUDS channel
         request_config : Request configuration (uds_msgconfig) (PUDS_MSGTYPE_FLAG_NO_POSITIVE_RESPONSE is ignored)
         out_msg_request : (out) request message created and sent by the function (uds_msg)
         data_identifier : a two-byte Data Identifier (see PUDS_SVC_PARAM_DI_xxx)
         data_record : buffer containing the data to write
         data_record_size : Size in bytes of the buffer
        returns: A uds_status code. PUDS_STATUS_OK is returned on success
        """
        try:
            res = self.__m_dllUds.UDS_SvcWriteDataByIdentifier_2013(channel, request_config, byref(out_msg_request),
                                                                    data_identifier, byref(data_record),
                                                                    data_record_size)
            return uds_status(res)
        except:
            print("Exception")
            raise

    # ISO-14229-1:2013 10.8 p.167
    def SvcWriteMemoryByAddress_2013(
            self,
            channel,
            request_config,
            out_msg_request,
            memory_address_buffer,
            memory_address_size,
            memory_size_buffer,
            memory_size_size,
            data_record,
            data_record_size):
        """
        The WriteMemoryByAddress service allows the client to write
        information into the server at one or more contiguous memory locations.
        
        parameters:
         channel : A PCANTP channel handle representing a PUDS channel
         request_config : Request configuration (uds_msgconfig) (PUDS_MSGTYPE_FLAG_NO_POSITIVE_RESPONSE is ignored)
         out_msg_request : (out) request message created and sent by the function (uds_msg)
         memory_address_buffer : Starting address buffer of server memory to which data is to be written
         memory_address_size : Size in bytes of the memory_address_buffer (max.: 0xF)
         memory_size_buffer : number of bytes to be written starting at the address specified by memory_address_buffer
         memory_size_size : Size in bytes of the memory_size_buffer (max.: 0xF)
         data_record : buffer containing the data to write
         data_record_size : Size in bytes of the buffer
        returns: A uds_status code. PUDS_STATUS_OK is returned on success
        """
        try:
            res = self.__m_dllUds.UDS_SvcWriteMemoryByAddress_2013(channel, request_config, byref(out_msg_request),
                                                                   byref(memory_address_buffer), \
                                                                   memory_address_size, byref(memory_size_buffer),
                                                                   memory_size_size, byref(data_record),
                                                                   data_record_size)
            return uds_status(res)
        except:
            print("Exception")
            raise

    # ISO-14229-1:2013 11.2 p.175
    PUDS_SVC_PARAM_CDI_ERS = 0x000000  # Emissions-related systems group of DTCs
    PUDS_SVC_PARAM_CDI_AGDTC = 0xFFFFFF  # All Groups of DTCs

    def SvcClearDiagnosticInformation_2013(
            self,
            channel,
            request_config,
            out_msg_request,
            group_of_dtc):
        """
        The ClearDiagnosticInformation service is used by the client to clear diagnostic information
        in one server's or multiple servers' memory.
        
        parameters:
         channel : A PCANTP channel handle representing a PUDS channel
         request_config : Request configuration (uds_msgconfig) (PUDS_MSGTYPE_FLAG_NO_POSITIVE_RESPONSE is ignored)
         out_msg_request : (out) request message created and sent by the function (uds_msg)
         group_of_dtc : a three-byte value indicating the group of DTCs (e.g. powertrain, body, chassis)
            or the particular DTC to be cleared (see PUDS_SVC_PARAM_CDI_xxx)
        returns: A uds_status code. PUDS_STATUS_OK is returned on success
        """
        try:
            res = self.__m_dllUds.UDS_SvcClearDiagnosticInformation_2013(channel, request_config,
                                                                         byref(out_msg_request), group_of_dtc)
            return uds_status(res)
        except:
            print("Exception")
            raise

    def SvcClearDiagnosticInformation_2020(
            self,
            channel,
            request_config,
            out_msg_request,
            group_of_dtc,
            memory_selection):
        """
        The ClearDiagnosticInformation service is used by the client to clear diagnostic information
        in one server's or multiple servers' memory.
        
        parameters:
         channel : A PCANTP channel handle representing a PUDS channel
         request_config : Request configuration (uds_msgconfig) (PUDS_MSGTYPE_FLAG_NO_POSITIVE_RESPONSE is ignored)
         out_msg_request : (out) request message created and sent by the function (uds_msg)
         group_of_dtc : a three-byte value indicating the group of DTCs (e.g. powertrain, body, chassis)
            or the particular DTC to be cleared (see PUDS_SVC_PARAM_CDI_xxx)
         memory_selection : User defined DTC memory
        returns: A uds_status code. PUDS_STATUS_OK is returned on success
        """
        try:
            res = self.__m_dllUds.UDS_SvcClearDiagnosticInformation_2020(channel, request_config,
                                                                         byref(out_msg_request), group_of_dtc,
                                                                         memory_selection)
            return uds_status(res)
        except:
            print("Exception")
            raise

    # ISO-14229-1:2013 11.3.2.2 p.194
    PUDS_SVC_PARAM_RDTCI_RNODTCBSM = 0x01  # report Number Of DTC By Status Mask
    PUDS_SVC_PARAM_RDTCI_RDTCBSM = 0x02  # report DTC By Status Mask
    PUDS_SVC_PARAM_RDTCI_RDTCSSI = 0x03  # report DTC Snapshot Identification
    PUDS_SVC_PARAM_RDTCI_RDTCSSBDTC = 0x04  # report DTC Snapshot Record By DTC Number
    PUDS_SVC_PARAM_RDTCI_RDTCSSBRN = 0x05  # report DTC Snapshot Record By Record Number
    PUDS_SVC_PARAM_RDTCI_RDTCEDRBDN = 0x06  # report DTC Extended Data Record By DTC Number
    PUDS_SVC_PARAM_RDTCI_RNODTCBSMR = 0x07  # report Number Of DTC By Severity Mask Record
    PUDS_SVC_PARAM_RDTCI_RDTCBSMR = 0x08  # report DTC By Severity Mask Record
    PUDS_SVC_PARAM_RDTCI_RSIODTC = 0x09  # report Severity Information Of DTC
    PUDS_SVC_PARAM_RDTCI_RSUPDTC = 0x0A  # report Supported DTC
    PUDS_SVC_PARAM_RDTCI_RFTFDTC = 0x0B  # report First Test Failed DTC
    PUDS_SVC_PARAM_RDTCI_RFCDTC = 0x0C  # report First Confirmed DTC
    PUDS_SVC_PARAM_RDTCI_RMRTFDTC = 0x0D  # report Most Recent Test Failed DTC
    PUDS_SVC_PARAM_RDTCI_RMRCDTC = 0x0E  # report Most Recent Confirmed DTC
    PUDS_SVC_PARAM_RDTCI_RMMDTCBSM = 0x0F  # report Mirror Memory DTC By Status Mask
    PUDS_SVC_PARAM_RDTCI_RMMDEDRBDN = 0x10  # report Mirror Memory DTC Extended Data Record By DTC Number
    PUDS_SVC_PARAM_RDTCI_RNOMMDTCBSM = 0x11  # report Number Of Mirror MemoryDTC By Status Mask
    PUDS_SVC_PARAM_RDTCI_RNOOBDDTCBSM = 0x12  # report Number Of Emissions Related OBD DTC By Status Mask
    PUDS_SVC_PARAM_RDTCI_ROBDDTCBSM = 0x13  # report Emissions Related OBD DTC By Status Mask
    PUDS_SVC_PARAM_RDTCI_RDTCEDBR = 0x16  # report DTC Ext Data Record By Record Number
    PUDS_SVC_PARAM_RDTCI_RUDMDTCBSM = 0x17  # report User Def Memory DTC By Status Mask
    PUDS_SVC_PARAM_RDTCI_RUDMDTCSSBDTC = 0x18  # report User Def Memory DTC Snapshot Record By DTC Number
    PUDS_SVC_PARAM_RDTCI_RUDMDTCEDRBDN = 0x19  # report User Def Memory DTC Ext Data Record By DTC Number
    PUDS_SVC_PARAM_RDTCI_RDTCEDI = 0x1A  # report report DTC Extended Data Record Identification (ISO_14229-1 2020)
    PUDS_SVC_PARAM_RDTCI_RWWHOBDDTCBMR = 0x42  # report WWHOBD DTC By Mask Record
    PUDS_SVC_PARAM_RDTCI_RWWHOBDDTCWPS = 0x55  # report WWHOBD DTC With Permanent Status
    PUDS_SVC_PARAM_RDTCI_RDTCBRGI = 0x56  # report DTC Information By DTC Readiness Group Identifier (ISO_14229-1 2020)
    # Reminder: following parameters were not defined as they are NOT in ISO-15765-3 :
    PUDS_SVC_PARAM_RDTCI_RDTCFDC = 0x14  # report DTC Fault Detection Counter
    PUDS_SVC_PARAM_RDTCI_RDTCWPS = 0x15  # report DTC With Permanent Status

    # DTCSeverityMask (DTCSVM): ISO-14229-1:2013 D.3 p.366
    PUDS_SVC_PARAM_RDTCI_DTCSVM_NSA = 0x00  # DTC severity bit definitions: no SeverityAvailable
    PUDS_SVC_PARAM_RDTCI_DTCSVM_MO = 0x20  # DTC severity bit definitions: maintenance Only
    PUDS_SVC_PARAM_RDTCI_DTCSVM_CHKANH = 0x40  # DTC severity bit definitions: check At Next Halt
    PUDS_SVC_PARAM_RDTCI_DTCSVM_CHKI = 0x80  # DTC severity bit definitions: check Immediately

    def SvcReadDTCInformation_2013(
            self,
            channel,
            request_config,
            out_msg_request,
            PUDS_SVC_PARAM_RDTCI_Type,
            dtc_status_mask):
        """
        This service allows a client to read the status of server-resident Diagnostic Trouble Code (DTC) information.
        Only reportNumberOfDTCByStatusMask, reportDTCByStatusMask, reportMirrorMemoryDTCByStatusMask,
        reportNumberOfMirrorMemoryDTCByStatusMask, reportNumberOfEmissionsRelatedOBDDTCByStatusMask,
        reportEmissionsRelatedOBDDTCByStatusMask Sub-functions are allowed.
        
        parameters:
         channel : A PCANTP channel handle representing a PUDS channel
         request_config : Request configuration (uds_msgconfig)
         out_msg_request : (out) request message created and sent by the function (uds_msg)
         PUDS_SVC_PARAM_RDTCI_Type : Subfunction parameter: ReadDTCInformation type, use one of the following:
            PUDS_SVC_PARAM_RDTCI_RNODTCBSM, PUDS_SVC_PARAM_RDTCI_RDTCBSM,
            PUDS_SVC_PARAM_RDTCI_RMMDTCBSM, PUDS_SVC_PARAM_RDTCI_RNOMMDTCBSM,
            PUDS_SVC_PARAM_RDTCI_RNOOBDDTCBSM, PUDS_SVC_PARAM_RDTCI_ROBDDTCBSM
         dtc_status_mask : Contains eight DTC status bit.
        returns: A uds_status code. PUDS_STATUS_OK is returned on success
        """
        try:
            res = self.__m_dllUds.UDS_SvcReadDTCInformation_2013(channel, request_config, byref(out_msg_request),
                                                                 PUDS_SVC_PARAM_RDTCI_Type, dtc_status_mask)
            return uds_status(res)
        except:
            print("Exception")
            raise

    def SvcReadDTCInformationRDTCSSBDTC_2013(
            self,
            channel,
            request_config,
            out_msg_request,
            dtc_mask,
            dtc_snapshot_record_number):
        """
        This service allows a client to read the status of server-resident Diagnostic Trouble Code (DTC) information.
        The sub-function reportDTCSnapshotRecordByDTCNumber (PUDS_SVC_PARAM_RDTCI_RDTCSSBDTC) is implicit.
        
        parameters:
         channel : A PCANTP channel handle representing a PUDS channel
         request_config : Request configuration (uds_msgconfig)
         out_msg_request : (out) request message created and sent by the function (uds_msg)
         dtc_mask : a unique identification number (three byte value) for a specific diagnostic trouble code
         dtc_snapshot_record_number : the number of the specific DTCSnapshot data records
        returns: A uds_status code. PUDS_STATUS_OK is returned on success
        """
        try:
            res = self.__m_dllUds.UDS_SvcReadDTCInformationRDTCSSBDTC_2013(channel, request_config,
                                                                           byref(out_msg_request), dtc_mask,
                                                                           dtc_snapshot_record_number)
            return uds_status(res)
        except:
            print("Exception")
            raise

    def SvcReadDTCInformationRDTCSSBRN_2013(
            self,
            channel,
            request_config,
            out_msg_request,
            dtc_snapshot_record_number):
        """
        This service allows a client to read the status of server-resident Diagnostic Trouble Code (DTC) information.
        The sub-function reportDTCSnapshotByRecordNumber (PUDS_SVC_PARAM_RDTCI_RDTCSSBRN) is implicit.
        
         channel : A PCANTP channel handle representing a PUDS channel
         request_config : Request configuration (uds_msgconfig)
         out_msg_request : (out) request message created and sent by the function (uds_msg)
         dtc_snapshot_record_number : the number of the specific DTCSnapshot data records
        returns: A uds_status code. PUDS_STATUS_OK is returned on success
        """
        try:
            res = self.__m_dllUds.UDS_SvcReadDTCInformationRDTCSSBRN_2013(channel, request_config,
                                                                          byref(out_msg_request),
                                                                          dtc_snapshot_record_number)
            return uds_status(res)
        except:
            print("Exception")
            raise

    def SvcReadDTCInformationReportExtended_2013(
            self,
            channel,
            request_config,
            out_msg_request,
            PUDS_SVC_PARAM_RDTCI_Type,
            dtc_mask,
            dtc_extended_data_record_number):
        """
        This service allows a client to read the status of server-resident Diagnostic Trouble Code (DTC) information.
        Only reportDTCExtendedDataRecordByDTCNumber and reportMirrorMemoryDTCExtendedDataRecordByDTCNumber Sub-functions are allowed.
        
        parameters:
         channel : A PCANTP channel handle representing a PUDS channel
         request_config : Request configuration (uds_msgconfig)
         out_msg_request : (out) request message created and sent by the function (uds_msg)
         PUDS_SVC_PARAM_RDTCI_Type : Subfunction parameter: ReadDTCInformation type, use one of the following:
            PUDS_SVC_PARAM_RDTCI_RDTCEDRBDN, PUDS_SVC_PARAM_RDTCI_RMMDEDRBDN
         dtc_mask : a unique identification number (three byte value) for a specific diagnostic trouble code
         dtc_extended_data_record_number : the number of the specific DTCExtendedData record requested.
        returns: A uds_status code. PUDS_STATUS_OK is returned on success
        """
        try:
            res = self.__m_dllUds.UDS_SvcReadDTCInformationReportExtended_2013(channel, request_config,
                                                                               byref(out_msg_request),
                                                                               PUDS_SVC_PARAM_RDTCI_Type, dtc_mask,
                                                                               dtc_extended_data_record_number)
            return uds_status(res)
        except:
            print("Exception")
            raise

    def SvcReadDTCInformationReportSeverity_2013(
            self,
            channel,
            request_config,
            out_msg_request,
            PUDS_SVC_PARAM_RDTCI_Type,
            dtc_severity_mask,
            dtc_status_mask):
        """
        This service allows a client to read the status of server-resident Diagnostic Trouble Code (DTC) information.
        Only reportNumberOfDTCBySeverityMaskRecord and reportDTCSeverityInformation Sub-functions are allowed.
        
        parameters:
         channel : A PCANTP channel handle representing a PUDS channel
         request_config : Request configuration (uds_msgconfig)
         out_msg_request : (out) request message created and sent by the function (uds_msg)
         PUDS_SVC_PARAM_RDTCI_Type : Subfunction parameter: ReadDTCInformation type, use one of the following:
            PUDS_SVC_PARAM_RDTCI_RNODTCBSMR, PUDS_SVC_PARAM_RDTCI_RDTCBSMR
         dtc_severity_mask : a mask of eight (8) DTC severity bits (see PUDS_SVC_PARAM_RDTCI_DTCSVM_xxx)
         dtc_status_mask : a mask of eight (8) DTC status bits
        returns: A uds_status code. PUDS_STATUS_OK is returned on success
        """
        try:
            res = self.__m_dllUds.UDS_SvcReadDTCInformationReportSeverity_2013(channel, request_config,
                                                                               byref(out_msg_request),
                                                                               PUDS_SVC_PARAM_RDTCI_Type,
                                                                               dtc_severity_mask, dtc_status_mask)
            return uds_status(res)
        except:
            print("Exception")
            raise

    def SvcReadDTCInformationRSIODTC_2013(
            self,
            channel,
            request_config,
            out_msg_request,
            dtc_mask):
        """
        This service allows a client to read the status of server-resident Diagnostic Trouble Code (DTC) information.
        The sub-function reportSeverityInformationOfDTC (PUDS_SVC_PARAM_RDTCI_RSIODTC) is implicit.
        
        parameters:
         channel : A PCANTP channel handle representing a PUDS channel
         request_config : Request configuration (uds_msgconfig)
         out_msg_request : (out) request message created and sent by the function (uds_msg)
         dtc_mask : a unique identification number for a specific diagnostic trouble code
        returns: A uds_status code. PUDS_STATUS_OK is returned on success
        """
        try:
            res = self.__m_dllUds.UDS_SvcReadDTCInformationRSIODTC_2013(channel, request_config, byref(out_msg_request),
                                                                        dtc_mask)
            return uds_status(res)
        except:
            print("Exception")
            raise

    def SvcReadDTCInformationNoParam_2013(
            self,
            channel,
            request_config,
            out_msg_request,
            PUDS_SVC_PARAM_RDTCI_Type):
        """
        This service allows a client to read the status of server-resident Diagnostic Trouble Code _2013(DTC) information.
        Only reportSupportedDTC, reportFirstTestFailedDTC, reportFirstConfirmedDTC, reportMostRecentTestFailedDTC,
        reportMostRecentConfirmedDTC, reportDTCFaultDetectionCounter, reportDTCWithPermanentStatus,
        and reportDTCSnapshotIdentification Sub-functions are allowed.
        
        parameters:
         channel : A PCANTP channel handle representing a PUDS channel
         request_config : Request configuration (uds_msgconfig)
         out_msg_request : (out) request message created and sent by the function (uds_msg)
         PUDS_SVC_PARAM_RDTCI_Type : Subfunction parameter: ReadDTCInformation type, use one of the following:
            PUDS_SVC_PARAM_RDTCI_RFTFDTC, PUDS_SVC_PARAM_RDTCI_RFCDTC,
            PUDS_SVC_PARAM_RDTCI_RMRTFDTC, PUDS_SVC_PARAM_RDTCI_RMRCDTC,
            PUDS_SVC_PARAM_RDTCI_RSUPDTC, PUDS_SVC_PARAM_RDTCI_RDTCWPS,
            PUDS_SVC_PARAM_RDTCI_RDTCSSI, PUDS_SVC_PARAM_RDTCI_RDTCFDC
        returns: A uds_status code. PUDS_STATUS_OK is returned on success
        """
        try:
            res = self.__m_dllUds.UDS_SvcReadDTCInformationNoParam_2013(channel, request_config, byref(out_msg_request),
                                                                        PUDS_SVC_PARAM_RDTCI_Type)
            return uds_status(res)
        except:
            print("Exception")
            raise

    def SvcReadDTCInformationRDTCEDBR_2013(
            self,
            channel,
            request_config,
            out_msg_request,
            dtc_extended_data_record_number):
        """
        This service allows a client to read the status of server-resident Diagnostic Trouble Code (DTC) information.
        The sub-function reportDTCExtDataRecordByRecordNumber (PUDS_SVC_PARAM_RDTCI_RDTCEDBR) is implicit.
        
        parameters:
         channel : A PCANTP channel handle representing a PUDS channel
         request_config : Request configuration (uds_msgconfig)
         out_msg_request : (out) request message created and sent by the function (uds_msg)
         dtc_extended_data_record_number : DTC extended data record number
        returns: A uds_status code. PUDS_STATUS_OK is returned on success
        """
        try:
            res = self.__m_dllUds.UDS_SvcReadDTCInformationRDTCEDBR_2013(channel, request_config,
                                                                         byref(out_msg_request),
                                                                         dtc_extended_data_record_number)
            return uds_status(res)
        except:
            print("Exception")
            raise

    def SvcReadDTCInformationRUDMDTCBSM_2013(
            self,
            channel,
            request_config,
            out_msg_request,
            dtc_status_mask,
            memory_selection):
        """
        This service allows a client to read the status of server-resident Diagnostic Trouble Code (DTC) information.
        The sub-function reportUserDefMemoryDTCByStatusMask (PUDS_SVC_PARAM_RDTCI_RUDMDTCBSM) is implicit.
        
        parameters:
         channel : A PCANTP channel handle representing a PUDS channel
         request_config : Request configuration (uds_msgconfig)
         out_msg_request : (out) request message created and sent by the function (uds_msg)
         dtc_status_mask : a mask of eight (8) DTC status bits
         memory_selection : Memory selection
        returns: A uds_status code. PUDS_STATUS_OK is returned on success
        """
        try:
            res = self.__m_dllUds.UDS_SvcReadDTCInformationRUDMDTCBSM_2013(channel, request_config,
                                                                           byref(out_msg_request), dtc_status_mask,
                                                                           memory_selection)
            return uds_status(res)
        except:
            print("Exception")
            raise

    def SvcReadDTCInformationRUDMDTCSSBDTC_2013(
            self,
            channel,
            request_config,
            out_msg_request,
            dtc_mask,
            user_def_dtc_snapshot_record_number,
            memory_selection):
        """
        This service allows a client to read the status of server-resident Diagnostic Trouble Code (DTC) information.
        The sub-function reportUserDefMemoryDTCSnapshotRecordByDTCNumber (PUDS_SVC_PARAM_RDTCI_RUDMDTCSSBDTC) is implicit.
        
        parameters:
         channel : A PCANTP channel handle representing a PUDS channel
         request_config : Request configuration (uds_msgconfig)
         out_msg_request : (out) request message created and sent by the function (uds_msg)
         dtc_mask : a unique identification number (three byte value) for a specific diagnostic trouble code
         user_def_dtc_snapshot_record_number : User DTC snapshot record number
         memory_selection : Memory selection
        returns: A uds_status code. PUDS_STATUS_OK is returned on success
        """
        try:
            res = self.__m_dllUds.UDS_SvcReadDTCInformationRUDMDTCSSBDTC_2013(channel, request_config,
                                                                              byref(out_msg_request), dtc_mask,
                                                                              user_def_dtc_snapshot_record_number,
                                                                              memory_selection)
            return uds_status(res)
        except:
            print("Exception")
            raise

    def SvcReadDTCInformationRUDMDTCEDRBDN_2013(
            self,
            channel,
            request_config,
            out_msg_request,
            dtc_mask,
            dtc_extended_data_record_number,
            memory_selection):
        """
        This service allows a client to read the status of server-resident Diagnostic Trouble Code (DTC) information.
        The sub-function reportUserDefMemoryDTCExtDataRecordByDTCNumber (PUDS_SVC_PARAM_RDTCI_RUDMDTCEDRBDN) is implicit.
        
        parameters:
         channel : A PCANTP channel handle representing a PUDS channel
         request_config : Request configuration (uds_msgconfig)
         out_msg_request : (out) request message created and sent by the function (uds_msg)
         dtc_mask : a unique identification number (three byte value) for a specific diagnostic trouble code
         dtc_extended_data_record_number : DTC extened data record number
         memory_selection : Memory selection
        returns: A uds_status code. PUDS_STATUS_OK is returned on success
        """
        try:
            res = self.__m_dllUds.UDS_SvcReadDTCInformationRUDMDTCEDRBDN_2013(channel, request_config,
                                                                              byref(out_msg_request), dtc_mask,
                                                                              dtc_extended_data_record_number,
                                                                              memory_selection)
            return uds_status(res)
        except:
            print("Exception")
            raise

    def SvcReadDTCInformationRDTCEDI_2020(
            self,
            channel,
            request_config,
            out_msg_request,
            dtc_extended_data_record_number):
        """
        ISO_14229-1 2020
        This service allows a client to read the status of server-resident Diagnostic Trouble Code (DTC) information.
        The sub-function reportSupportedDTCExtDataRecord (PUDS_SVC_PARAM_RDTCI_RDTCEDI) is implicit.
        
        parameters:
         channel : A PCANTP channel handle representing a PUDS channel
         request_config : Request configuration (uds_msgconfig)
         out_msg_request : (out) request message created and sent by the function (uds_msg)
         dtc_extended_data_record_number : DTC extended data record number
        returns: A uds_status code. PUDS_STATUS_OK is returned on success
        """
        try:
            res = self.__m_dllUds.UDS_SvcReadDTCInformationRDTCEDI_2020(channel, request_config, byref(out_msg_request),
                                                                        dtc_extended_data_record_number)
            return uds_status(res)
        except:
            print("Exception")
            raise

    def SvcReadDTCInformationRWWHOBDDTCBMR_2013(
            self,
            channel,
            request_config,
            out_msg_request,
            functional_group_identifier,
            dtc_status_mask,
            dtc_severity_mask):
        """
        This service allows a client to read the status of server-resident Diagnostic Trouble Code (DTC) information.
        The sub-function reportWWHOBDDTCByMaskRecord (PUDS_SVC_PARAM_RDTCI_RWWHOBDDTCBMR) is implicit.
        
         channel : A PCANTP channel handle representing a PUDS channel
         request_config : Request configuration (uds_msgconfig)
         out_msg_request : (out) request message created and sent by the function (uds_msg)
         functional_group_identifier : Functional group identifier
         dtc_status_mask : a mask of eight (8) DTC status bits
         dtc_severity_mask : a mask of eight (8) DTC severity bits (see PUDS_SVC_PARAM_RDTCI_DTCSVM_xxx)
        returns: A uds_status code. PUDS_STATUS_OK is returned on success
        """
        try:
            res = self.__m_dllUds.UDS_SvcReadDTCInformationRWWHOBDDTCBMR_2013(channel, request_config,
                                                                              byref(out_msg_request),
                                                                              functional_group_identifier,
                                                                              dtc_status_mask, dtc_severity_mask)
            return uds_status(res)
        except:
            print("Exception")
            raise

    def SvcReadDTCInformationRWWHOBDDTCWPS_2013(
            self,
            channel,
            request_config,
            out_msg_request,
            functional_group_identifier):
        """
        This service allows a client to read the status of server-resident Diagnostic Trouble Code (DTC) information.
        The sub-function reportWWHOBDDTCWithPermanentStatus (PUDS_SVC_PARAM_RDTCI_RWWHOBDDTCWPS ) is implicit.
        
        parameters:
         channel : A PCANTP channel handle representing a PUDS channel
         request_config : Request configuration (uds_msgconfig)
         out_msg_request : (out) request message created and sent by the function (uds_msg)
         functional_group_identifier : Functional group identifier
        returns: A uds_status code. PUDS_STATUS_OK is returned on success
        """
        try:
            res = self.__m_dllUds.UDS_SvcReadDTCInformationRWWHOBDDTCWPS_2013(channel, request_config,
                                                                              byref(out_msg_request),
                                                                              functional_group_identifier)
            return uds_status(res)
        except:
            print("Exception")
            raise

    def SvcReadDTCInformationRDTCBRGI_2020(
            self,
            channel,
            request_config,
            out_msg_request,
            functional_group_identifier,
            dtc_readiness_group_identifier):
        """
        ISO_14229-1 2020
        This service allows a client to read the status of server-resident Diagnostic Trouble Code (DTC) information.
        The sub-function reportDTCInformationByDTCReadinessGroupIdentifier (PUDS_SVC_PARAM_RDTCI_RDTCBRGI ) is implicit.
        
        parameters:
         channel : A PCANTP channel handle representing a PUDS channel
         request_config : Request configuration (uds_msgconfig)
         out_msg_request : (out) request message created and sent by the function (uds_msg)
         functional_group_identifier : Functional group identifier
         dtc_readiness_group_identifier : DTC readiness group identifier
        returns: A uds_status code. PUDS_STATUS_OK is returned on success
        """
        try:
            res = self.__m_dllUds.UDS_SvcReadDTCInformationRDTCBRGI_2020(channel, request_config,
                                                                         byref(out_msg_request),
                                                                         functional_group_identifier,
                                                                         dtc_readiness_group_identifier)
            return uds_status(res)
        except:
            print("Exception")
            raise

    # ISO-14229-1:2013 E.1 p.374
    PUDS_SVC_PARAM_IOCBI_RCTECU = 0x00  # inputOutputControlParameter: returnControlToECU (0 controlState bytes in request)
    PUDS_SVC_PARAM_IOCBI_RTD = 0x01  # inputOutputControlParameter: resetToDefault (0 controlState bytes in request)
    PUDS_SVC_PARAM_IOCBI_FCS = 0x02  # inputOutputControlParameter: freezeCurrentState (0 controlState bytes in request)
    PUDS_SVC_PARAM_IOCBI_STA = 0x03  # inputOutputControlParameter: shortTermAdjustment

    def SvcInputOutputControlByIdentifier_2013(
            self,
            channel,
            request_config,
            out_msg_request,
            data_identifier,
            control_option_record,
            control_option_record_size,
            control_enable_mask_record=None,
            control_enable_mask_record_size=0):
        """
        The InputOutputControlByIdentifier service is used by the client to substitute a value for an input signal,
        internal server function and/or control an output (actuator) of an electronic system.
        
        parameters:
         channel : A PCANTP channel handle representing a PUDS channel
         request_config : Request configuration (uds_msgconfig) (PUDS_MSGTYPE_FLAG_NO_POSITIVE_RESPONSE is ignored)
         out_msg_request : (out) request message created and sent by the function (uds_msg)
         data_identifier : a two-byte Data Identifier (see PUDS_SVC_PARAM_DI_xxx)
         control_option_record : First byte can be used as either an inputOutputControlParameter
            that describes how the server shall control its inputs or outputs (see PUDS_SVC_PARAM_IOCBI_xxx),
            or as an additional controlState byte
         control_option_record_size : Size in bytes of the control_option_record buffer
         control_enable_mask_record : The control_enable_mask_record shall only be supported when
            the inputOutputControlParameter is used (see control_option_record) and the dataIdentifier to be controlled consists
            of more than one parameter (i.e. the dataIdentifier is bit-mapped or packeted by definition).
            There shall be one bit in the control_enable_mask_record corresponding to each individual parameter
            defined within the dataIdentifier.
         control_enable_mask_record_size : Size in bytes of the control_enable_mask_record buffer
        returns: A uds_status code. PUDS_STATUS_OK is returned on success
        """
        try:
            res = self.__m_dllUds.UDS_SvcInputOutputControlByIdentifier_2013(channel, request_config,
                                                                             byref(out_msg_request), data_identifier,
                                                                             byref(control_option_record), \
                                                                             control_option_record_size,
                                                                             None if control_enable_mask_record == None else byref(
                                                                                 control_enable_mask_record),
                                                                             control_enable_mask_record_size)
            return uds_status(res)
        except:
            print("Exception")
            raise

    # ISO-14229-1:2013 13.2.2.2 p.262
    PUDS_SVC_PARAM_RC_STR = 0x01  # Start Routine
    PUDS_SVC_PARAM_RC_STPR = 0x02  # Stop Routine
    PUDS_SVC_PARAM_RC_RRR = 0x03  # Request Routine Results
    # routineIdentifier: ISO-14229-1:2013 F.1 p.375
    PUDS_SVC_PARAM_RC_RID_DLRI_ = 0xE200  # routineIdentifier: DeployLoopRoutineID
    PUDS_SVC_PARAM_RC_RID_EM_ = 0xFF00  # routineIdentifier: eraseMemory
    PUDS_SVC_PARAM_RC_RID_CPD_ = 0xFF01  # routineIdentifier: checkProgrammingDependencies
    PUDS_SVC_PARAM_RC_RID_EMMDTC_ = 0xFF02  # routineIdentifier: eraseMirrorMemoryDTCs

    def SvcRoutineControl_2013(
            self,
            channel,
            request_config,
            out_msg_request,
            routine_control_type,
            routine_identifier,
            routine_control_option_record=None,
            routine_control_option_record_size=0):
        """
        The RoutineControl service is used by the client to start/stop a routine,
        and request routine results.
        
        parameters:
         channel : A PCANTP channel handle representing a PUDS channel
         request_config : Request configuration (uds_msgconfig)
         out_msg_request : (out) request message created and sent by the function (uds_msg)
         routine_control_type : Subfunction parameter: RoutineControl type (see PUDS_SVC_PARAM_RC_xxx)
         routine_identifier : Server Local Routine Identifier (see PUDS_SVC_PARAM_RC_RID_xxx)
         routine_control_option_record : buffer containing the Routine Control Options (only with start and stop routine sub-functions)
         routine_control_option_record_size : Size in bytes of the buffer
        returns: A uds_status code. PUDS_STATUS_OK is returned on success
        """
        try:
            res = self.__m_dllUds.UDS_SvcRoutineControl_2013(channel, request_config, byref(out_msg_request),
                                                             routine_control_type, routine_identifier, \
                                                             None if routine_control_option_record == None else byref(
                                                                 routine_control_option_record),
                                                             routine_control_option_record_size)
            return uds_status(res)
        except:
            print("Exception")
            raise

    # ISO-14229-1:2013 14.2 p.270
    def SvcRequestDownload_2013(
            self,
            channel,
            request_config,
            out_msg_request,
            compression_method,
            encrypting_method,
            memory_address_buffer,
            memory_address_size,
            memory_size_buffer,
            memory_size_size):
        """
        The requestDownload service is used by the client to initiate a data transfer
        from the client to the server (download).
        
        parameters:
         channel : A PCANTP channel handle representing a PUDS channel
         request_config : Request configuration (uds_msgconfig) (PUDS_MSGTYPE_FLAG_NO_POSITIVE_RESPONSE is ignored)
         out_msg_request : (out) request message created and sent by the function (uds_msg)
         compression_method : A nibble-value that specifies the "compressionMethod",
            The value 0x0 specifies that no compressionMethod is used.
         encrypting_method : A nibble-value that specifies the "encryptingMethod",
            The value 0x0 specifies that no encryptingMethod is used.
         memory_address_buffer : starting address of server memory to which data is to be written
         memory_address_size : Size in bytes of the memory_address_buffer buffer (max.: 0xF)
         memory_size_buffer : used by the server to compare the uncompressed memory size with
            the total amount of data transferred during the TransferData service
         memory_size_size : Size in bytes of the memory_size_buffer buffer (max.: 0xF)
        returns: A uds_status code. PUDS_STATUS_OK is returned on success
        """
        try:
            res = self.__m_dllUds.UDS_SvcRequestDownload_2013(channel, request_config, byref(out_msg_request), \
                                                              compression_method, encrypting_method,
                                                              byref(memory_address_buffer), memory_address_size,
                                                              byref(memory_size_buffer), memory_size_size)
            return uds_status(res)
        except:
            print("Exception")
            raise

    # ISO-14229-1:2013 14.3 p.275
    def SvcRequestUpload_2013(
            self,
            channel,
            request_config,
            out_msg_request,
            compression_method,
            encrypting_method,
            memory_address_buffer,
            memory_address_size,
            memory_size_buffer,
            memory_size_size):
        """
        The requestUpload service is used by the client to initiate a data transfer
        from the server to the client (upload).
        
        parameters:
         channel : A PCANTP channel handle representing a PUDS channel
         request_config : Request configuration (uds_msgconfig) (PUDS_MSGTYPE_FLAG_NO_POSITIVE_RESPONSE is ignored)
         out_msg_request : (out) request message created and sent by the function (uds_msg)
         compression_method : A nibble-value that specifies the "compressionMethod",
            The value 0x0 specifies that no compressionMethod is used.
         encrypting_method : A nibble-value that specifies the "encryptingMethod",
            The value 0x0 specifies that no encryptingMethod is used.
         memory_address_buffer : starting address of server memory from which data is to be retrieved
         memory_address_size : Size in bytes of the memory_address_buffer buffer (max.: 0xF)
         memory_size_buffer : used by the server to compare the uncompressed memory size with
            the total amount of data transferred during the TransferData service
         memory_size_size : Size in bytes of the memory_size_buffer buffer (max.: 0xF)
        returns: A uds_status code. PUDS_STATUS_OK is returned on success
        """
        try:
            res = self.__m_dllUds.UDS_SvcRequestUpload_2013(channel, request_config, byref(out_msg_request),
                                                            compression_method, encrypting_method, \
                                                            byref(memory_address_buffer), memory_address_size,
                                                            byref(memory_size_buffer), memory_size_size)
            return uds_status(res)
        except:
            print("Exception")
            raise

    # ISO-14229-1:2013 14.4 p.280
    def SvcTransferData_2013(
            self,
            channel,
            request_config,
            out_msg_request,
            block_sequence_counter,
            transfer_request_parameter_record=None,
            transfer_request_parameter_record_size=0):
        """
        The TransferData service is used by the client to transfer data either from the client
        to the server (download) or from the server to the client (upload).
        
        parameters:
         channel : A PCANTP channel handle representing a PUDS channel
         request_config : Request configuration (uds_msgconfig) (PUDS_MSGTYPE_FLAG_NO_POSITIVE_RESPONSE is ignored)
         out_msg_request : (out) request message created and sent by the function (uds_msg)
         block_sequence_counter : The blockSequenceCounter parameter value starts at 01 hex
            with the first TransferData request that follows the RequestDownload (34 hex)
            or RequestUpload (35 hex) service. Its value is incremented by 1 for each subsequent
            TransferData request. At the value of FF hex, the blockSequenceCounter rolls over
            and starts at 00 hex with the next TransferData request message.
         transfer_request_parameter_record : buffer containing the required transfer parameters
         transfer_request_parameter_record_size : Size in bytes of the buffer
        returns: A uds_status code. PUDS_STATUS_OK is returned on success
        """
        try:
            res = self.__m_dllUds.UDS_SvcTransferData_2013(channel, request_config, byref(out_msg_request),
                                                           block_sequence_counter, \
                                                           None if transfer_request_parameter_record == None else byref(
                                                               transfer_request_parameter_record),
                                                           transfer_request_parameter_record_size)
            return uds_status(res)
        except:
            print("Exception")
            raise

    # ISO-14229-1:2013 14.5 p.285
    def SvcRequestTransferExit_2013(
            self,
            channel,
            request_config,
            out_msg_request,
            transfer_request_parameter_record=None,
            transfer_request_parameter_record_size=0):
        """
        The RequestTransferExit service is used by the client to terminate a data
        transfer between client and server (upload or download).
        
        parameters:
         channel : A PCANTP channel handle representing a PUDS channel
         request_config : Request configuration (uds_msgconfig) (PUDS_MSGTYPE_FLAG_NO_POSITIVE_RESPONSE is ignored)
         out_msg_request : (out) request message created and sent by the function (uds_msg)
         transfer_request_parameter_record : buffer containing the required transfer parameters
         transfer_request_parameter_record_size : Size in bytes of the buffer
        returns: A uds_status code. PUDS_STATUS_OK is returned on success
        """
        try:
            res = self.__m_dllUds.UDS_SvcRequestTransferExit_2013(channel, request_config, byref(out_msg_request), \
                                                                  None if transfer_request_parameter_record == None else byref(
                                                                      transfer_request_parameter_record),
                                                                  transfer_request_parameter_record_size)
            return uds_status(res)
        except:
            print("Exception")
            raise

    # See ISO-14229-1:2013 9.7.2.2 p.62 table 74
    PUDS_SVC_PARAM_ATP_RETPS = 0x01  # Read Extended Timing Parameter Set
    PUDS_SVC_PARAM_ATP_STPTDV = 0x02  # Set Timing Parameters To Default Values
    PUDS_SVC_PARAM_ATP_RCATP = 0x03  # Read Currently Active Timing Parameters
    PUDS_SVC_PARAM_ATP_STPTGV = 0x04  # Set Timing Parameters To Given Values

    def SvcAccessTimingParameter_2013(
            self,
            channel,
            request_config,
            out_msg_request,
            access_type,
            request_record,
            request_record_size):
        """
         AccessTimingParameter service.
        
        parameters:
         channel : A PCANTP channel handle representing a PUDS channel
         request_config : Request configuration (uds_msgconfig)
         out_msg_request : (out) request message created and sent by the function (uds_msg)
         access_type : Access type, see PUDS_SVC_PARAM_ATP_* values
         request_record : Timing parameter request record
         request_record_size : Size in byte of the request record
        returns: A uds_status code. PUDS_STATUS_OK is returned on success
        """
        try:
            res = self.__m_dllUds.UDS_SvcAccessTimingParameter_2013(channel, request_config, byref(out_msg_request),
                                                                    access_type, byref(request_record),
                                                                    request_record_size)
            return uds_status(res)
        except:
            print("Exception")
            raise

    # See ISO-14229-1:2013 Annex G p.376 table G.1
    PUDS_SVC_PARAM_RFT_MOOP_ADDFILE = 0x1  # Add File
    PUDS_SVC_PARAM_RFT_MOOP_DELFILE = 0x2  # Delete File
    PUDS_SVC_PARAM_RFT_MOOP_REPLFILE = 0x3  # Replace File
    PUDS_SVC_PARAM_RFT_MOOP_RDFILE = 0x4  # Read File
    PUDS_SVC_PARAM_RFT_MOOP_RDDIR = 0x5  # Read Dir
    PUDS_SVC_PARAM_RFT_MOOP_RSFILE = 0x6  # Resume File (ISO-14229-1:2020 Annex G p.447 table G.1)

    def SvcRequestFileTransfer_2013(
            self,
            channel,
            request_config,
            out_msg_request,
            mode_of_operation,
            file_path_and_name_size,
            file_path_and_name,
            compression_method=0,
            encrypting_method=0,
            file_size_parameter_size=0,
            file_size_uncompressed=None,
            file_size_compressed=None):
        """
         RequestFileTransfer service.
        
        parameters:
         channel : A PCANTP channel handle representing a PUDS channel
         request_config : Request configuration (uds_msgconfig) (PUDS_MSGTYPE_FLAG_NO_POSITIVE_RESPONSE is ignored)
         out_msg_request : (out) request message created and sent by the function (uds_msg)
         mode_of_operation : Mode of operation (add, delete, replace, read), see PUDS_SVC_PARAM_RFT_MOOP_* values
         file_path_and_name_size : Size in bytes of file_path_and_name buffer
         file_path_and_name : File path and name string
         compression_method : A nibble-value that specifies the "compressionMethod", the value 0x0 specifies that no compressionMethod is used.
         encrypting_method : A nibble-value that specifies the "encryptingMethod", the value 0x0 specifies that no encryptingMethod is used.
         file_size_parameter_size : Size in byte of file_size_uncompressed and file_size_compressed parameters
         file_size_uncompressed : Buffer for Uncompressed file size
         file_size_compressed : Buffer for Compressed file size
        returns: A uds_status code. PUDS_STATUS_OK is returned on success
        """
        try:
            res = self.__m_dllUds.UDS_SvcRequestFileTransfer_2013(channel, request_config, byref(out_msg_request),
                                                                  mode_of_operation, \
                                                                  file_path_and_name_size, byref(file_path_and_name),
                                                                  compression_method, encrypting_method,
                                                                  file_size_parameter_size, \
                                                                  None if file_size_uncompressed == None else byref(
                                                                      file_size_uncompressed), \
                                                                  None if file_size_compressed == None else byref(
                                                                      file_size_compressed))
            return uds_status(res)
        except:
            print("Exception")
            raise

    # Represents the subfunction parameter for UDS service Authentication (see ISO 14229-1:2020 10.6.5.2 Table 74 Request message SubFunction parameter definition p.76)
    uds_svc_authentication_subfunction = c_uint32
    PUDS_SVC_PARAM_AT_DA = uds_svc_authentication_subfunction(0x00)  # DeAuthenticate
    PUDS_SVC_PARAM_AT_VCU = uds_svc_authentication_subfunction(0x01)  # VerifyCertificateUnidirectional
    PUDS_SVC_PARAM_AT_VCB = uds_svc_authentication_subfunction(0x02)  # VerifyCertificateBidirectional
    PUDS_SVC_PARAM_AT_POWN = uds_svc_authentication_subfunction(0x03)  # ProofOfOwnership
    PUDS_SVC_PARAM_AT_TC = uds_svc_authentication_subfunction(0x04)  # TransmitCertificate
    PUDS_SVC_PARAM_AT_RCFA = uds_svc_authentication_subfunction(0x05)  # RequestChallengeForAuthentication
    PUDS_SVC_PARAM_AT_VPOWNU = uds_svc_authentication_subfunction(0x06)  # VerifyProofOfOwnershipUnidirectional
    PUDS_SVC_PARAM_AT_VPOWNB = uds_svc_authentication_subfunction(0x07)  # VerifyProofOfOwnershipBidirectional
    PUDS_SVC_PARAM_AT_AC = uds_svc_authentication_subfunction(0x08)  # AuthenticationConfiguration

    # Represents the return parameter for UDS service Authentication (see ISO 14229-1:2020 B.5 AuthenticationReturnParameter definitions p.403)
    uds_svc_authentication_return_parameter = c_uint32
    PUDS_SVC_PARAM_AT_RV_RA = uds_svc_authentication_return_parameter(0x00)  # Request Accepted
    PUDS_SVC_PARAM_AT_RV_GR = uds_svc_authentication_return_parameter(0x01)  # General Reject
    PUDS_SVC_PARAM_AT_RV_ACAPCE = uds_svc_authentication_return_parameter(0x02)  # Authentication Configuration APCE
    PUDS_SVC_PARAM_AT_RV_ACACRAC = uds_svc_authentication_return_parameter(
        0x03)  # Authentication Configuration ACR with Asymmetric Cryptography
    PUDS_SVC_PARAM_AT_RV_ACACRSC = uds_svc_authentication_return_parameter(
        0x04)  # Authentication Configuration ACR with Symmetric Cryptography
    PUDS_SVC_PARAM_AT_RV_DAS = uds_svc_authentication_return_parameter(0x10)  # DeAuthentication Successful
    PUDS_SVC_PARAM_AT_RV_CVOVN = uds_svc_authentication_return_parameter(
        0x11)  # Certificate Verified, Ownership Verification Necessary
    PUDS_SVC_PARAM_AT_RV_OVAC = uds_svc_authentication_return_parameter(
        0x12)  # Ownership Verified, Authentication Complete
    PUDS_SVC_PARAM_AT_RV_CV = uds_svc_authentication_return_parameter(0x13)  # Certificate Verified

    def SvcAuthenticationDA_2020(
            self,
            channel,
            request_config,
            out_msg_request):
        """
         Sends Authentication service request with deAuthenticate subfunction.
        
        remarks: 
         API provides uds_svc_authentication_subfunction and uds_svc_authentication_return_parameter
         enumerations to help user to decode Authentication service responses.
        
        parameters:
         channel : A PCANTP channel handle representing a PUDS channel
         request_config : Request configuration (uds_msgconfig)
         out_msg_request : (out) request message created and sent by the function (uds_msg)
        returns: A uds_status code. PUDS_STATUS_OK is returned on success
        """
        try:
            res = self.__m_dllUds.UDS_SvcAuthenticationDA_2020(channel, request_config, byref(out_msg_request))
            return uds_status(res)
        except:
            print("Exception")
            raise

    def SvcAuthenticationVCU_2020(
            self,
            channel,
            request_config,
            out_msg_request,
            communication_configuration,
            certificate_client,
            certificate_client_size,
            challenge_client=None,
            challenge_client_size=0):
        """
         Sends Authentication service request with verifyCertificateUnidirectional subfunction.
        
        remarks: 
         API provides uds_svc_authentication_subfunction and uds_svc_authentication_return_parameter
         enumerations to help user to decode Authentication service responses.
        
        parameters:
         channel : A PCANTP channel handle representing a PUDS channel
         request_config : Request configuration (uds_msgconfig)
         out_msg_request : (out) request message created and sent by the function (uds_msg)
         communication_configuration : Configuration information about communication
         certificate_client : Buffer containing the certificate of the client
         certificate_client_size : Size in bytes of the certificate buffer
         challenge_client : Buffer containing the challenge of the client
         challenge_client_size : Size in bytes of the challenge buffer
        returns: A uds_status code. PUDS_STATUS_OK is returned on success
        """
        try:
            res = self.__m_dllUds.UDS_SvcAuthenticationVCU_2020(channel, request_config, byref(out_msg_request),
                                                                communication_configuration, byref(certificate_client), \
                                                                certificate_client_size,
                                                                None if challenge_client == None else byref(
                                                                    challenge_client), challenge_client_size)
            return uds_status(res)
        except:
            print("Exception")
            raise

    def SvcAuthenticationVCB_2020(
            self,
            channel,
            request_config,
            out_msg_request,
            communication_configuration,
            certificate_client,
            certificate_client_size,
            challenge_client,
            challenge_client_size):
        """
         Sends Authentication service request with verifyCertificateBidirectional subfunction.
        
        remarks: 
         API provides uds_svc_authentication_subfunction and uds_svc_authentication_return_parameter
         enumerations to help user to decode Authentication service responses.
        
        parameters:
         channel : A PCANTP channel handle representing a PUDS channel
         request_config : Request configuration (uds_msgconfig)
         out_msg_request : (out) request message created and sent by the function (uds_msg)
         communication_configuration : Configuration information about communication
         certificate_client : Buffer containing the certificate of the client
         certificate_client_size : Size in bytes of the certificate buffer
         challenge_client : Buffer containing the challenge of the client
         challenge_client_size : Size in bytes of the challenge buffer
        returns: A uds_status code. PUDS_STATUS_OK is returned on success
        """
        try:
            res = self.__m_dllUds.UDS_SvcAuthenticationVCB_2020(channel, request_config, byref(out_msg_request), \
                                                                communication_configuration, byref(certificate_client),
                                                                certificate_client_size, byref(challenge_client),
                                                                challenge_client_size)
            return uds_status(res)
        except:
            print("Exception")
            raise

    def SvcAuthenticationPOWN_2020(
            self,
            channel,
            request_config,
            out_msg_request,
            proof_of_ownership_client,
            proof_of_ownership_client_size,
            ephemeral_public_key_client=None,
            ephemeral_public_key_client_size=0):
        """
         Sends Authentication service request with proofOfOwnership subfunction.
        
        remarks: 
         API provides uds_svc_authentication_subfunction and uds_svc_authentication_return_parameter
         enumerations to help user to decode Authentication service responses.
        
        parameters:
         channel : A PCANTP channel handle representing a PUDS channel
         request_config : Request configuration (uds_msgconfig)
         out_msg_request : (out) request message created and sent by the function (uds_msg)
         proof_of_ownership_client : Buffer containing the proof of ownership of the client
         proof_of_ownership_client_size : Size in bytes of the proof of ownership buffer
         ephemeral_public_key_client : Buffer containing the ephemeral public key of the client
         ephemeral_public_key_client_size : Size in bytes of the ephemeral public key buffer
        returns: A uds_status code. PUDS_STATUS_OK is returned on success
        """
        try:
            res = self.__m_dllUds.UDS_SvcAuthenticationPOWN_2020(channel, request_config, byref(out_msg_request),
                                                                 byref(proof_of_ownership_client), \
                                                                 proof_of_ownership_client_size,
                                                                 None if ephemeral_public_key_client == None else byref(
                                                                     ephemeral_public_key_client),
                                                                 ephemeral_public_key_client_size)
            return uds_status(res)
        except:
            print("Exception")
            raise

    def SvcAuthenticationRCFA_2020(
            self,
            channel,
            request_config,
            out_msg_request,
            communication_configuration,
            algorithm_indicator):
        """
         Sends Authentication service request with requestChallengeForAuthentication subfunction.
        
        remarks: 
         API provides uds_svc_authentication_subfunction and uds_svc_authentication_return_parameter
         enumerations to help user to decode Authentication service responses.
        
        parameters:
         channel : A PCANTP channel handle representing a PUDS channel
         request_config : Request configuration (uds_msgconfig)
         out_msg_request : (out) request message created and sent by the function (uds_msg)
         communication_configuration : Configuration information about communication
         algorithm_indicator : Buffer of 16 bytes containing the algorithm indicator
        returns: A uds_status code. PUDS_STATUS_OK is returned on success
        """
        try:
            res = self.__m_dllUds.UDS_SvcAuthenticationRCFA_2020(channel, request_config, byref(out_msg_request),
                                                                 communication_configuration,
                                                                 byref(algorithm_indicator))
            return uds_status(res)
        except:
            print("Exception")
            raise

    def SvcAuthenticationVPOWNU_2020(
            self,
            channel,
            request_config,
            out_msg_request,
            algorithm_indicator,
            proof_of_ownership_client,
            proof_of_ownership_client_size,
            challenge_client=None,
            challenge_client_size=0,
            additional_parameter=None,
            additional_parameter_size=0):
        """
         Sends Authentication service request with verifyProofOfOwnershipUnidirectional subfunction.
        
        remarks: 
         API provides uds_svc_authentication_subfunction and uds_svc_authentication_return_parameter
         enumerations to help user to decode Authentication service responses.
        
        parameters:
         channel : A PCANTP channel handle representing a PUDS channel
         request_config : Request configuration (uds_msgconfig)
         out_msg_request : (out) request message created and sent by the function (uds_msg)
         algorithm_indicator : Buffer of 16 bytes containing the algorithm indicator
         proof_of_ownership_client : Buffer containing the proof of ownership of the client
         proof_of_ownership_client_size : Size in bytes of the proof of ownership buffer
         challenge_client : Buffer containing the challenge of the client
         challenge_client_size : Size in bytes of the challenge buffer
         additional_parameter : Buffer containing additional parameters
         additional_parameter_size : Size in bytes of the additional parameter buffer
        returns: A uds_status code. PUDS_STATUS_OK is returned on success
        """
        try:
            res = self.__m_dllUds.UDS_SvcAuthenticationVPOWNU_2020(channel, request_config, byref(out_msg_request),
                                                                   byref(algorithm_indicator), \
                                                                   byref(proof_of_ownership_client),
                                                                   proof_of_ownership_client_size,
                                                                   None if challenge_client == None else byref(
                                                                       challenge_client), \
                                                                   challenge_client_size,
                                                                   None if additional_parameter == None else byref(
                                                                       additional_parameter), additional_parameter_size)
            return uds_status(res)
        except:
            print("Exception")
            raise

    def SvcAuthenticationVPOWNB_2020(
            self,
            channel,
            request_config,
            out_msg_request,
            algorithm_indicator,
            proof_of_ownership_client,
            proof_of_ownership_client_size,
            challenge_client,
            challenge_client_size,
            additional_parameter=None,
            additional_parameter_size=0):
        """
         Sends Authentication service request with verifyProofOfOwnershipBidirectional subfunction.
        
        remarks: 
         API provides uds_svc_authentication_subfunction and uds_svc_authentication_return_parameter
         enumerations to help user to decode Authentication service responses.
        
        parameters:
         channel : A PCANTP channel handle representing a PUDS channel
         request_config : Request configuration (uds_msgconfig)
         out_msg_request : (out) request message created and sent by the function (uds_msg)
         algorithm_indicator : Buffer of 16 bytes containing the algorithm indicator
         proof_of_ownership_client : Buffer containing the proof of ownership of the client
         proof_of_ownership_client_size : Size in bytes of the proof of ownership buffer
         challenge_client : Buffer containing the challenge of the client
         challenge_client_size : Size in bytes of the challenge buffer
         additional_parameter : Buffer containing additional parameters
         additional_parameter_size : Size in bytes of the additional parameter buffer
        returns: A uds_status code. PUDS_STATUS_OK is returned on success
        """
        try:
            res = self.__m_dllUds.UDS_SvcAuthenticationVPOWNB_2020(channel, request_config, byref(out_msg_request),
                                                                   byref(algorithm_indicator), \
                                                                   byref(proof_of_ownership_client),
                                                                   proof_of_ownership_client_size,
                                                                   byref(challenge_client), challenge_client_size, \
                                                                   None if additional_parameter == None else byref(
                                                                       additional_parameter), additional_parameter_size)
            return uds_status(res)
        except:
            print("Exception")
            raise

    def SvcAuthenticationAC_2020(
            self,
            channel,
            request_config,
            out_msg_request):
        """
         Sends Authentication service request with authenticationConfiguration subfunction.
        
        remarks: 
         API provides uds_svc_authentication_subfunction and uds_svc_authentication_return_parameter
         enumerations to help user to decode Authentication service responses.
        
         channel : A PCANTP channel handle representing a PUDS channel
         request_config : Request configuration (uds_msgconfig)
         out_msg_request : (out) request message created and sent by the function (uds_msg)
        returns: A uds_status code. PUDS_STATUS_OK is returned on success
        """
        try:
            res = self.__m_dllUds.UDS_SvcAuthenticationAC_2020(channel, request_config, byref(out_msg_request))
            return uds_status(res)
        except:
            print("Exception")
            raise
