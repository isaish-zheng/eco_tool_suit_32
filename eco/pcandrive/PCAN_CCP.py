#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author  : ZYD
# @time    : 2024/6/13 上午9:27
# @version : V1.1.0
# @function: V1.0.0：根据PCCP.dll文档说明，编写Python3.10的PCAN-CCP API，包含实现flash的服务
# @function: V1.1.0：补全其余服务
# CAN Calibration Protocol Version 2.1


##############################
# Module imports
##############################

from ctypes import *
from string import *
import os
import platform
import sys

from .PCANBasic import *


##############################
# Type definitions
##############################

# Represents a PCAN-CCP Connection Handle.
TCCPHandle = c_uint32

# Represents a PCAN-CCP result/error code.
TCCPResult = c_uint32

TCCP_ERROR_ACKNOWLEDGE_OK = TCCPResult(0x00)  # Acknowledge / no error.
TCCP_ERROR_DAQ_OVERLOAD = TCCPResult(0x01)  # DAQ processor overload.
TCCP_ERROR_CMD_PROCESSOR_BUSY = TCCPResult(0x10)  # Command processor busy.
TCCP_ERROR_DAQ_PROCESSOR_BUSY = TCCPResult(0x11)  # DAQ processor busy.
TCCP_ERROR_INTERNAL_TIMEOUT = TCCPResult(0x12)  # Internal timeout.
TCCP_ERROR_KEY_REQUEST = TCCPResult(0x18)  # Key request.
TCCP_ERROR_SESSION_STS_REQUEST = TCCPResult(0x19)  # Session status request.
TCCP_ERROR_COLD_START_REQUEST = TCCPResult(0x20)  # Cold start request.
TCCP_ERROR_CAL_DATA_INIT_REQUEST = TCCPResult(0x21)  # Calibration data initialization request.
TCCP_ERROR_DAQ_LIST_INIT_REQUEST = TCCPResult(0x22)  # DAQ list initialization request.
TCCP_ERROR_CODE_UPDATE_REQUEST = TCCPResult(0x23)  # Code update request.
TCCP_ERROR_UNKNOWN_COMMAND = TCCPResult(0x30)  # Unknown command.
TCCP_ERROR_COMMAND_SYNTAX = TCCPResult(0x31)  # Command syntax.
TCCP_ERROR_PARAM_OUT_OF_RANGE = TCCPResult(0x32)  # Parameter(s) out of range.
TCCP_ERROR_ACCESS_DENIED = TCCPResult(0x33)  # Access denied.
TCCP_ERROR_OVERLOAD = TCCPResult(0x34)  # Overload.
TCCP_ERROR_ACCESS_LOCKED = TCCPResult(0x35)  # Access locked.
TCCP_ERROR_NOT_AVAILABLE = TCCPResult(0x36)  # Resource/function not available.
TCCP_ERROR_PCAN = TCCPResult(0x80000000)  # PCAN-Basic Error FLAG

# Represents the current operation session on a ECU and its status.
TCCPSessionStatus = c_ubyte

TCCP_STS_CALIBRATING = TCCPSessionStatus(0x01)  # Calibration Status.
TCCP_STS_ACQUIRING = TCCPSessionStatus(0x02)  # Data acquisition Status.
TCCP_STS_RESUME_REQUEST = TCCPSessionStatus(0x04)  # Request resuming.
TCCP_STS_STORE_REQUEST = TCCPSessionStatus(0x40)  # Request storing.
TCCP_STS_RUNNING = TCCPSessionStatus(0x80)  # Running status.

# Represents the mode of a data transmission session.
TCCPStartStopMode = c_ubyte

TCCP_SSM_STOP = TCCPStartStopMode(0x00)  # Stops the data transmission.
TCCP_SSM_START = TCCPStartStopMode(0x01)  # Starts the data transmission.
TCCP_SSM_PREPARE_START = TCCPStartStopMode(0x02)  # Prepare for start data transmission.

# Represents the available ECU resources and their status.
TCCPResourceMask = c_ubyte

TCCP_RSM_NONE = TCCPResourceMask(
    0x00)  # Resource: There are no resources available. Protection: All available resources are unlocked.
TCCP_RSM_CALIBRATION = TCCPResourceMask(
    0x01)  # Resource: Calibration resource is available. Protection: Calibration resource needs to be unlocked.
TCCP_RSM_DATA_ADQUISITION = TCCPResourceMask(
    0x02)  # Resource: Data Adquisition resource is available. Protection: Data Adquisition resource needs to be unlocked.
TCCP_RSM_MEMORY_PROGRAMMING = TCCPResourceMask(
    0x40)  # Resource: Flashing resource is available. Protection: Flashing resource needs to be unlocked.

# Represents the category associated with a TCCPResult value.
TCCPErrorCategory = c_ubyte

TCCP_EC_NOT_DEFINED = TCCPErrorCategory(0x00)  # Default/empty value of this enumeration type.
TCCP_EC_WARNING = TCCPErrorCategory(0x01)  # Category 0. Code represents a warning.
TCCP_EC_SPURIOUS = TCCPErrorCategory(0x02)  # Category 1. Code represents a spurious error like comm error, busy, etc.
TCCP_EC_RESOLVABLE = TCCPErrorCategory(
    0x03)  # Category 2. Code represents a resolvable error like temporary power loss, etc.
TCCP_EC_UNRESOLVABLE = TCCPErrorCategory(0x04)  # Category 3. Code represents an unresolvable error like an overload.


##############################
# Structure definitions
##############################

# Represents a data structure used for better handling with the return value of the API functions.
class CCPResult(Structure):
    _pack_ = 8
    _fields_ = [("CCP", TCCPResult),  # Returns the CCP error as a TCCPResult value.
                ("PCAN", c_uint32),
                # Returns the PCAN error (see PCAN-Basic help) as a TPCANStatus value, associated to the represented
                # TCCPResult.
                ("ErrorCategory", TCCPErrorCategory),
                # Returns the error severity as a TCCPErrorCategory value, associated to the represented TCCPResult.
                ]


# Defines the data structure used to get information from an ECU within the function CCP_ExchangeId.
class TCCPExchangeData(Structure):
    _pack_ = 8
    _fields_ = [("IdLength", c_ubyte),  # Length of the Slave Device ID.
                ("DataType", c_ubyte),  # Data type qualifier of the Slave Device ID.
                ("AvailabilityMask", c_ubyte),  # Resource Availability Mask (See TCCPResourceMask).
                ("ProtectionMask", c_ubyte),  # Resource Protection Mask (See TCCPResourceMask).
                ]


# Defines the data structure used to configure data adquisition on an ECU, through CCP_StartStopDataTransmission.
class TCCPStartStopData(Structure):
    _pack_ = 8
    _fields_ = [("Mode", c_ubyte),
                ("ListNumber", c_ubyte),  # DAQ list number to process.
                ("LastODTNumber", c_ubyte),  # ODTs to be transmitted (from 0 to LastODTNumber).
                ("EventChannel", c_ubyte),  # Generic signal source for timing determination.
                ("TransmissionRatePrescaler", c_uint16),  # Transmission rate prescaler.
                ]


# Defines the data structure used to describe the communication parameters of an ECU
# within the function CCP_Connect and CCP_Test.
class TCCPSlaveData(Structure):
    _pack_ = 8
    _fields_ = [("EcuAddress", c_uint16),  # Station (ECU) address in Intel format.
                ("IdCRO", c_uint32),  # CAN ID used for CRO packages.
                ("IdDTO", c_uint32),  # CAN ID used for DTO packages.
                ("IntelFormat", c_bool),  # Format used by the slave (True: Intel, False: Motorola)
                ]


# Defines the data structure for ECU packages received asynchronous.
class TCCPMsg(Structure):
    _pack_ = 8
    _fields_ = [("Source", TCCPHandle),  # Handle of the connection owner of the message.
                ("Length", c_ubyte),  # Data length of the message.
                ("Data", c_ubyte * 8),  # Data bytes (max. 8).
                ]


##############################
# PCAN-CCP API function declarations
##############################

# PCAN-CCP API class implementation
class PcanCCP:
    """
      PCAN-CCP class implementation
    """

    def __init__(self):
        # Loads the PCAN-CCP API
        if platform.system() == 'Windows':
            # Loads the API on Windows
            libpath = r".\PCCP.dll"
            self.__m_dllCcp = windll.LoadLibrary(libpath)
        elif platform.system() == 'Linux':
            # Loads the API on Linux
            self.__m_dllCcp = cdll.LoadLibrary("libpccp.so")
        if self.__m_dllCcp is None:
            msg = f"Exception: The PCCP.dll couldn't be loaded!"
            print(msg)
            raise FileNotFoundError(msg)

    @staticmethod
    def StatusIsOk(
            status: TCCPResult,
            status_expected: TCCPResult = TCCP_ERROR_ACKNOWLEDGE_OK):
        """
        Checks if a PCCP status matches an expected result (default is TCCP_ERROR_ACKNOWLEDGE_OK).

        :param status: The PCCP status to analyze.
        :param status_expected: The expected PCCP status.
        :returns: The return value is true if the status matches expected parameter.
        """
        if status.value == status_expected.value:
            return True

    def Initialize(
            self,
            channel: TPCANHandle,
            baudrate: TPCANBaudrate,
            hw_type=0,
            io_port=0,
            interrupt=0):
        """
        Initializes the CAN communication using PCAN-Basic API.
        Please refer to the PCAN-Basic documentation for more information about the PCAN-Basic API.

        :param channel: The handle of a PCAN Channel (see TPCANHandle).
        :param baudrate: The speed for the communication (BTR0BTR1 code).
        :param hw_type: The type of the Non-Plug-and-Play hardware and its operation mode.
        :param io_port: The I/O address for the parallel port of the Non-Plug-and-Play hardware.
        :param interrupt: The Interrupt number of the parallel port of the Non-Plug-and-Play hardware.
        :returns: The return value is a TCCPResult code. CCP_ERROR_ACKNOWLEDGE_OK is returned on success.
        """

        try:
            res = self.__m_dllCcp.CCP_InitializeChannel(channel, baudrate, hw_type, io_port, interrupt)
            return TCCPResult(res)
        except Exception as ex:
            print("Exception on PCAN-CCP.Initialize", ex)
            raise

    def Uninitialize(
            self,
            channel: TPCANHandle):
        """
        Uninitialize a PCAN-Basic Channel.

        :param channel: The handle of a PCAN Channel (see TPCANHandle).
        :returns: The return value is a TCCPResult code. CCP_ERROR_ACKNOWLEDGE_OK is returned on success.
        """

        try:
            res = self.__m_dllCcp.CCP_UninitializeChannel(channel)
            return TCCPResult(res)
        except Exception as ex:
            print("Exception on PCAN-CCP.Uninitialize:", ex)
            raise

    def ReadMsg(
            self,
            ccp_handle: TCCPHandle,
            msg: TCCPMsg):
        """
        Reads a message from the received queue of a PCAN-CCP connection.
        The queue can allocate up to 32767 messages.
        If the queue is full and a new message is received,
        the oldest messages is took out of the queue and the new message is inserted.
        Errors, such a Queue-Overrun error, are not generated.

        :param ccp_handle: The handle of a PCAN-CCP connection
        :param msg: Buffer for a message. See TCCPMsg
        :returns: The return value is a TCCPResult code. CCP_ERROR_ACKNOWLEDGE_OK is returned on success.
        """

        try:
            res = self.__m_dllCcp.CCP_ReadMsg(ccp_handle, byref(msg))
            return TCCPResult(res)
        except Exception as ex:
            print("Exception on PCAN-CCP.ReadMsg:", ex)
            raise

    def Reset(
            self,
            ccp_handle: TCCPHandle):
        """
        Resets the receive-queue of a PCAN-CCP connection.

        :param ccp_handle: The handle of a PCAN-CCP connection.
        :returns: The return value is a TCCPResult code. CCP_ERROR_ACKNOWLEDGE_OK is returned on success.
        """
        try:
            res = self.__m_dllCcp.CCP_Reset(ccp_handle)
            return TCCPResult(res)
        except Exception as ex:
            print("Exception on PCAN-CCP.Reset:", ex)
            raise

    def Connect(
            self,
            channel: TPCANHandle,
            slave_data: TCCPSlaveData,
            ccp_handle: TCCPHandle,
            timeout: c_uint16):
        """
        Establishes a logical connection between a master application and a slave unit.

        :param channel: The handle of an initialized PCAN Channel.
        :param slave_data: The description data of the slave to be connected.
        :param ccp_handle: A buffer to return the handle of this Master/Channel/Slave connection.
        :param timeout: Wait time (millis) for ECU response. Zero(0) to use the default time.
        :returns: The return value is a TCCPResult code. CCP_ERROR_ACKNOWLEDGE_OK is returned on success.
        """

        try:
            res = self.__m_dllCcp.CCP_Connect(channel, byref(slave_data), byref(ccp_handle), timeout)
            return TCCPResult(res)
        except Exception as ex:
            print("Exception on PCAN-CCP.Connect:", ex)
            raise

    def Disconnect(
            self,
            ccp_handle: TCCPHandle,
            temporary: c_bool,
            timeout: c_uint16):
        """
        Logically disconnects a master application from a slave unit.

        :param ccp_handle: The handle of a PCAN-CCP connection.
        :param temporary: Indicates if the disconnection should be temporary or not.
        :param timeout: Wait time (millis) for ECU response. Zero(0) to use the default time.
        :returns: The return value is a TCCPResult code. CCP_ERROR_ACKNOWLEDGE_OK is returned on success.
        """

        try:
            res = self.__m_dllCcp.CCP_Disconnect(ccp_handle, temporary, timeout)
            return TCCPResult(res)
        except Exception as ex:
            print("Exception on PCAN-CCP.Disconnect:", ex)
            raise

    def Test(
            self,
            channel: TPCANHandle,
            slave_data_buffer: TCCPSlaveData,
            timeout: c_uint16):
        """
        Tests if a slave is available.

        :param channel: The handle of an initialized PCAN Channel.
        :param slave_data_buffer: The description data of the slave to be connected.
        :param timeout: Wait time (millis) for ECU response. Zero(0) to use the default time.
        :returns: The return value is a TCCPResult code. CCP_ERROR_ACKNOWLEDGE_OK is returned on success.
        """

        try:
            res = self.__m_dllCcp.CCP_Test(channel, byref(slave_data_buffer), timeout)
            return TCCPResult(res)
        except Exception as ex:
            print("Exception on PCAN-CCP.Test:", ex)
            raise

    def GetCcpVersion(
            self,
            ccp_handle: TCCPHandle,
            main_buffer: c_ubyte,
            release_buffer: c_ubyte,
            timeout: c_uint16):
        """
        Exchanges the CCP Version used by a master and a slave.
        Both buffers, Main and Release, are bidirectional, i.e. they are used by both Master and Slave.
        The master should call this function placing in these buffers its used version.
        After the function returns, these buffers contain the version used by the connected slave.

        :param ccp_handle: The handle of a PCAN-CCP connection.
        :param main_buffer: Buffer for the CCP Main version used.
        :param release_buffer: Buffer for the CCP Release version used.
        :param timeout: Wait time (millis) for ECU response. Zero(0) to use the default time.
        :returns: The return value is a TCCPResult code. CCP_ERROR_ACKNOWLEDGE_OK is returned on success.
        """

        try:
            res = self.__m_dllCcp.CCP_GetCcpVersion(ccp_handle, byref(main_buffer),
                                                    byref(release_buffer), timeout)
            return TCCPResult(res)
        except Exception as ex:
            print("Exception on PCAN-CCP.GetCcpVersion:", ex)
            raise

    def ExchangeId(
            self,
            ccp_handle: TCCPHandle,
            ecu_data: TCCPExchangeData,
            master_data_buffer: c_buffer,
            master_data_length: c_uint32,
            timeout: c_uint16):
        """
        Exchanges IDs between Master and Slave for automatic session configuration.

        :param ccp_handle: The handle of a PCAN-CCP connection.
        :param ecu_data: Slave ID and Resource Information buffer.
        :param master_data_buffer: Optional master data (ID).
        :param master_data_length: Length of the master data.
        :param timeout: Wait time (millis) for ECU response. Zero(0) to use the default time.
        :returns: The return value is a TCCPResult code. CCP_ERROR_ACKNOWLEDGE_OK is returned on success.
        """

        try:
            res = self.__m_dllCcp.CCP_ExchangeId(ccp_handle, byref(ecu_data), byref(master_data_buffer),
                                                 master_data_length, timeout)
            return TCCPResult(res)
        except Exception as ex:
            print("Exception on PCAN-CCP.ExchangeId:", ex)
            raise

    def GetSeed(
            self,
            ccp_handle: TCCPHandle,
            resource: c_ubyte,
            current_status: c_bool,
            seed_buffer: c_buffer,
            timeout: c_uint16):
        """
        Returns Seed data for a seed&key algorithm to unlock a slave functionality.

        :param ccp_handle: The handle of a PCAN-CCP connection.
        :param resource: The resource being asked. (See TCCPResourceMask)
        :param current_status: Current protection status of the asked resource.
        :param seed_buffer: Seed value for the seed-and-key algorithm.
        :param timeout: Wait time (millis) for ECU response. Zero(0) to use the default time.
        :returns: The return value is a TCCPResult code. CCP_ERROR_ACKNOWLEDGE_OK is returned on success.
        """

        try:
            res = self.__m_dllCcp.CCP_GetSeed(ccp_handle, resource,
                                              byref(current_status), byref(seed_buffer), timeout)
            return TCCPResult(res)
        except Exception as ex:
            print("Exception on PCAN-CCP.GetSeed:", ex)
            raise

    def Unlock(
            self,
            ccp_handle: TCCPHandle,
            key_buffer: c_buffer,
            key_length: c_ubyte,
            privileges: c_ubyte,
            timeout: c_uint16):
        """
        Unlocks the security protection of a resource within a connected slave.

        :param ccp_handle: The handle of a PCAN-CCP connection.
        :param key_buffer: A buffer with the key computed from a seed value obtained through the CCP_GetSeed function.
        :param key_length: The length in bytes of the key buffer value.
        :param privileges: The current privileges status on the slave. (See TCCPResourceMask)
        :param timeout: Wait time (millis) for ECU response. Zero(0) to use the default time.
        :returns: The return value is a TCCPResult code. CCP_ERROR_ACKNOWLEDGE_OK is returned on success.
        """

        try:
            res = self.__m_dllCcp.CCP_Unlock(ccp_handle, byref(key_buffer), key_length,
                                             byref(privileges), timeout)
            return TCCPResult(res)
        except Exception as ex:
            print("Exception on PCAN-CCP.Unlock:", ex)
            raise

    def SetSessionStatus(
            self,
            ccp_handle: TCCPHandle,
            status: TCCPSessionStatus,
            timeout: c_uint16):
        """
        Keeps the connected slave informed about the current state of the calibration session.

        :param ccp_handle: The handle of a PCAN-CCP connection.
        :param status: Current status bits. See 'Session Status' values above.
        :param timeout: Wait time (millis) for ECU response. Zero(0) to use the default time.
        :returns: The return value is a TCCPResult code. CCP_ERROR_ACKNOWLEDGE_OK is returned on success.
        """

        try:
            res = self.__m_dllCcp.CCP_SetSessionStatus(ccp_handle, status, timeout)
            return TCCPResult(res)
        except Exception as ex:
            print("Exception on PCAN-CCP.SetSessionStatus:", ex)
            raise

    def GetSessionStatus(
            self,
            ccp_handle: TCCPHandle,
            status: TCCPSessionStatus,
            timeout: c_uint16):
        """
        Retrieves the information about the current state of the calibration session.

        :param ccp_handle: The handle of a PCAN-CCP connection.
        :param status: Current status bits. See 'Session Status' values above.
        :param timeout: Wait time (millis) for ECU response. Zero(0) to use the default time.
        :returns: The return value is a TCCPResult code. CCP_ERROR_ACKNOWLEDGE_OK is returned on success.
        """

        try:
            res = self.__m_dllCcp.CCP_GetSessionStatus(ccp_handle, byref(status), timeout)
            return TCCPResult(res)
        except Exception as ex:
            print("Exception on PCAN-CCP.GetSessionStatus:", ex)
            raise

    def SetMemoryTransferAddress(
            self,
            ccp_handle: TCCPHandle,
            used_mta: c_ubyte,
            addr_extension: c_ubyte,
            addr: c_uint32,
            timeout: c_uint16):
        """
        Initializes a base pointer for all following memory transfers.

        :param ccp_handle: The handle of a PCAN-CCP connection.
        :param used_mta: Memory Transfer Address (MTA) number (0 or 1).
        :param addr_extension: Address extension.
        :param addr: Address.
        :param timeout: Wait time (millis) for ECU response. Zero(0) to use the default time.
        :returns: The return value is a TCCPResult code. CCP_ERROR_ACKNOWLEDGE_OK is returned on success.
        """

        try:
            res = self.__m_dllCcp.CCP_SetMemoryTransferAddress(ccp_handle, used_mta,
                                                               addr_extension, addr, timeout)
            return TCCPResult(res)
        except Exception as ex:
            print("Exception on PCAN-CCP.SetMemoryTransferAddress:", ex)
            raise

    def Download(
            self,
            ccp_handle: TCCPHandle,
            data_buffer: c_buffer,
            size: c_ubyte,
            mta0_ext: c_ubyte,
            mta0_addr: c_uint32,
            timeout: c_uint16):
        """
        Copies a block of data into memory, starting at the current MTA0.
        MTA0 is post-incremented by the value of "Size".

        :param ccp_handle: The handle of a PCAN-CCP connection.
        :param data_buffer: Buffer with the data to be transferred.
        :param size: Size of the data to be transferred, in bytes.
        :param mta0_ext: MTA0 extension after post-increment.
        :param mta0_addr: MTA0 Address after post-increment.
        :param timeout: Wait time (millis) for ECU response. Zero(0) to use the default time.
        :returns: The return value is a TCCPResult code. CCP_ERROR_ACKNOWLEDGE_OK is returned on success.
        """

        try:
            res = self.__m_dllCcp.CCP_Download(ccp_handle, byref(data_buffer), size,
                                               byref(mta0_ext), byref(mta0_addr), timeout)
            return TCCPResult(res)
        except Exception as ex:
            print("Exception on PCAN-CCP.Download:", ex)
            raise

    def Download_6(
            self,
            ccp_handle: TCCPHandle,
            data_buffer: c_buffer,
            mta0_ext: c_ubyte,
            mta0_addr: c_uint32,
            timeout: c_uint16):
        """
        Copies a block of 6 data bytes into memory, starting at the current MTA0.
        MTA0 is post-incremented by the value of 6.

        :param ccp_handle: The handle of a PCAN-CCP connection.
        :param data_buffer: Buffer with the data to be transferred.
        :param mta0_ext: MTA0 extension after post-increment.
        :param mta0_addr: MTA0 Address after post-increment.
        :param timeout: Wait time (millis) for ECU response. Zero(0) to use the default time.
        :returns: The return value is a TCCPResult code. CCP_ERROR_ACKNOWLEDGE_OK is returned on success.
        """

        try:
            res = self.__m_dllCcp.CCP_Download_6(ccp_handle, byref(data_buffer),
                                                 byref(mta0_ext), byref(mta0_addr), timeout)
            return TCCPResult(res)
        except Exception as ex:
            print("Exception on PCAN-CCP.Download_6:", ex)
            raise

    def Upload(
            self,
            ccp_handle: TCCPHandle,
            size: c_ubyte,
            data_buffer: c_buffer,
            timeout: c_uint16):
        """
        Retrieves a block of data starting at the current MTA0.
        MTA0 will be post-incremented with the value of "Size".

        :param ccp_handle: The handle of a PCAN-CCP connection.
        :param size: Size of the data to be retrieved, in bytes.
        :param data_buffer: Buffer for the requested data.
        :param timeout: Wait time (millis) for ECU response. Zero(0) to use the default time.
        :returns: The return value is a TCCPResult code. CCP_ERROR_ACKNOWLEDGE_OK is returned on success.
        """

        try:
            res = self.__m_dllCcp.CCP_Upload(ccp_handle, size, byref(data_buffer), timeout)
            return TCCPResult(res)
        except Exception as ex:
            print("Exception on PCAN-CCP.Upload:", ex)
            raise

    def ShortUpload(
            self,
            ccp_handle: TCCPHandle,
            size: c_ubyte,
            mta0_ext: c_ubyte,
            mta0_addr: c_uint32,
            data_buffer: c_buffer,
            timeout: c_uint16):
        """
        Retrieves a block of data.
        The amount of data is retrieved from the given address. The MTA0 pointer remains unchanged.

        :param ccp_handle: The handle of a PCAN-CCP connection.
        :param size: Size of the data to be retrieved, in bytes.
        :param mta0_ext: MTA0 extension for the upload.
        :param mta0_addr: MTA0 Address for the upload.
        :param data_buffer: Buffer for the requested data.
        :param timeout: Wait time (millis) for ECU response. Zero(0) to use the default time.
        :returns: The return value is a TCCPResult code. CCP_ERROR_ACKNOWLEDGE_OK is returned on success.
        """

        try:
            res = self.__m_dllCcp.CCP_ShortUpload(ccp_handle, size, mta0_ext, mta0_addr,
                                                  byref(data_buffer), timeout)
            return TCCPResult(res)
        except Exception as ex:
            print("Exception on PCAN-CCP.ShortUpload:", ex)
            raise

    def Move(
            self,
            ccp_handle: TCCPHandle,
            size: c_uint32,
            timeout: c_uint16):
        """
        Copies a block of data from the address MTA0 to the address MTA1.

        :param ccp_handle: The handle of a PCAN-CCP connection.
        :param size: Number of bytes to be moved.
        :param timeout: Wait time (millis) for ECU response. Zero(0) to use the default time.
        :returns: The return value is a TCCPResult code. CCP_ERROR_ACKNOWLEDGE_OK is returned on success.
        """

        try:
            res = self.__m_dllCcp.CCP_Move(ccp_handle, size, timeout)
            return TCCPResult(res)
        except Exception as ex:
            print("Exception on PCAN-CCP.Move:", ex)
            raise

    def SelectCalibrationDataPage(
            self,
            ccp_handle: TCCPHandle,
            timeout: c_uint16):
        """
        Sets the previously initialized MTA0 as the start of the current active calibration data page.

        :param ccp_handle: The handle of a PCAN-CCP connection.
        :param timeout: Wait time (millis) for ECU response. Zero(0) to use the default time.
        :returns: The return value is a TCCPResult code. CCP_ERROR_ACKNOWLEDGE_OK is returned on success.
        """

        try:
            res = self.__m_dllCcp.CCP_SelectCalibrationDataPage(ccp_handle, timeout)
            return TCCPResult(res)
        except Exception as ex:
            print("Exception on PCAN-CCP.SelectCalibrationDataPage:", ex)
            raise

    def GetActiveCalibrationPage(
            self,
            ccp_handle: TPCANHandle,
            mta0_ext: c_ubyte,
            mta0_addr: c_uint32,
            timeout: c_uint16):
        """
        Retrieves the start address of the calibration page that is currently active in the slave device.

        :param ccp_handle: The handle of an initialized PCAN Channel.
        :param mta0_ext: Buffer for the MTAO address extension.
        :param mta0_addr: Buffer for the MTA0 address pointer.
        :param timeout: Wait time (millis) for ECU response. Zero(0) to use the default time.
        :returns: The return value is a TCCPResult code. CCP_ERROR_ACKNOWLEDGE_OK is returned on success.
        """

        try:
            res = self.__m_dllCcp.CCP_GetActiveCalibrationPage(ccp_handle, byref(mta0_ext),
                                                               byref(mta0_addr), timeout)
            return TCCPResult(res)
        except Exception as ex:
            print("Exception on PCAN-CCP.GetActiveCalibrationPage:", ex)
            raise

    def GetDAQListSize(
            self,
            ccp_handle: TCCPHandle,
            list_number: c_ubyte,
            dto_id: c_uint32,
            size: c_ubyte,
            first_pid: c_ubyte,
            timeout: c_uint16):
        """
        Retrieves the size of the specified DAQ List as the number of available Object Descriptor Tables (ODTs)
        and clears the current list. Optionally, sets a dedicated CAN-ID for the DAQ list.
        When die value of the DTOId buffer passed to the function is NULL (nil in Delphi))
        the Api will send the command GET_DAQ_SIZE using as DTOId the value given within the structure "TCCPSlaveData"
        at connect time (function CCP_Connect).
        This is for the case that an ECU doesn't support individual Ids for data acquisition.

        :param ccp_handle: The handle of a PCAN-CCP connection.
        :param list_number: DAQ List number.
        :param dto_id: CAN identifier of DTO dedicated to the given ListNumber.
        :param size: Buffer for the list size (Number of ODTs in the DAQ list).
        :param first_pid: Buffer for the first PID of the DAQ list.
        :param timeout: Wait time (millis) for ECU response. Zero(0) to use the default time.
        :returns: The return value is a TCCPResult code. CCP_ERROR_ACKNOWLEDGE_OK is returned on success.
        """

        try:
            # list_number = c_ubyte(0)
            # dto_id = c_uint32(1)
            # size = c_ubyte()
            # first_pid = c_ubyte()
            # timeout = c_uint16(1000)

            res = self.__m_dllCcp.CCP_GetDAQListSize(ccp_handle, list_number, byref(dto_id),
                                                     byref(size), byref(first_pid), timeout)
            return TCCPResult(res)
        except Exception as ex:
            print("Exception on PCAN-CCP.GetDAQListSize:", ex)
            raise

    def SetDAQListPointer(
            self,
            ccp_handle: TCCPHandle,
            list_number: c_ubyte,
            odt_number: c_ubyte,
            element_number: c_ubyte,
            timeout: c_uint16):
        """
        Initializes the DAQ List pointer for a subsequent write to a DAQ list.

        :param ccp_handle: The handle of a PCAN-CCP connection.
        :param list_number: DAQ List number.
        :param odt_number: Object Descriptor Table number.
        :param element_number: Element number within the ODT.
        :param timeout: Wait time (millis) for ECU response. Zero(0) to use the default time.
        :returns: The return value is a TCCPResult code. CCP_ERROR_ACKNOWLEDGE_OK is returned on success.
        """

        try:
            res = self.__m_dllCcp.CCP_SetDAQListPointer(ccp_handle, list_number, odt_number,
                                                        element_number, timeout)
            return TCCPResult(res)
        except Exception as ex:
            print("Exception on PCAN-CCP.SetDAQListPointer:", ex)
            raise

    def WriteDAQListEntry(
            self,
            ccp_handle: TCCPHandle,
            size_element: c_ubyte,
            addr_ext: c_ubyte,
            addr: c_uint32,
            timeout: c_uint16):
        """
        Writes one entry (DAQ element) to a DAQ list defined by the DAQ list pointer.

        :param ccp_handle: The handle of a PCAN-CCP connection.
        :param size_element: Size of the DAQ elements in bytes {1, 2, 4}.
        :param addr_ext: Address extension of DAQ element.
        :param addr: Address of a DAQ element.
        :param timeout: Wait time (millis) for ECU response. Zero(0) to use the default time.
        :returns: The return value is a TCCPResult code. CCP_ERROR_ACKNOWLEDGE_OK is returned on success.
        """

        try:
            res = self.__m_dllCcp.CCP_WriteDAQListEntry(ccp_handle, size_element, addr_ext, addr, timeout)
            return TCCPResult(res)
        except Exception as ex:
            print("Exception on PCAN-CCP.WriteDAQListEntry:", ex)
            raise

    def StartStopDataTransmission(
            self,
            ccp_handle: TCCPHandle,
            data: TCCPStartStopData,
            timeout: c_uint16):
        """
        Starts/Stops the data acquisition and/or prepares a synchronized start of the specified DAQ list.

        :param ccp_handle: The handle of a PCAN-CCP connection.
        :param data: Contains the data to be applied within the start/stop procedure (See TCCPStartStopData).
        :param timeout: Wait time (millis) for ECU response. Zero(0) to use the default time.
        :returns: The return value is a TCCPResult code. CCP_ERROR_ACKNOWLEDGE_OK is returned on success.
        """

        try:
            res = self.__m_dllCcp.CCP_StartStopDataTransmission(ccp_handle, byref(data), timeout)
            return TCCPResult(res)
        except Exception as ex:
            print("Exception on PCAN-CCP.StartStopDataTransmission:", ex)
            raise

    def StartStopSynchronizedDataTransmission(
            self,
            ccp_handle: TCCPHandle,
            start_or_stop: bool,
            timeout: c_uint16):
        """
        Starts/Stops the periodic transmission of all DAQ lists.
        Starts all DAQs configured as "prepare to start" with a previously CCP_StartStopDataTransmission call.
        Stops all DAQs, included those not started synchronized.

        :param ccp_handle: The handle of a PCAN-CCP connection.
        :param start_or_stop: true: Starts the configured DAQ lists. false: Stops all DAQ lists.
        :param timeout: Wait time (millis) for ECU response. Zero(0) to use the default time.
        :returns: The return value is a TCCPResult code. CCP_ERROR_ACKNOWLEDGE_OK is returned on success.
        """

        try:
            res = self.__m_dllCcp.CCP_StartStopSynchronizedDataTransmission(ccp_handle, start_or_stop, timeout)
            return TCCPResult(res)
        except Exception as ex:
            print("Exception on PCAN-CCP.StartStopSynchronizedDataTransmission:", ex)
            raise

    def ClearMemory(
            self,
            ccp_handle: TCCPHandle,
            memory_size: c_uint32,
            timeout: c_uint16):
        """
        Erases non-volatile memory (FLASH EPROM) prior to reprogramming.

        :param ccp_handle: The handle of a PCAN-CCP connection.
        :param memory_size: Memory size in bytes to be erased.
        :param timeout: Wait time (millis) for ECU response. Zero(0) to use the default time.
        :returns: The return value is a TCCPResult code. CCP_ERROR_ACKNOWLEDGE_OK is returned on success.
        """

        try:
            res = self.__m_dllCcp.CCP_ClearMemory(ccp_handle, memory_size, timeout)
            return TCCPResult(res)
        except Exception as ex:
            print("Exception on PCAN-CCP.ClearMemory:", ex)
            raise

    def Program(
            self,
            ccp_handle: TCCPHandle,
            data_buffer: c_buffer,
            size: c_ubyte,
            mta0_ext: c_ubyte,
            mta0_addr: c_uint32,
            timeout: c_uint16):
        """
        Programms a block of data into non-volatile (FLASH, EPROM) memory, starting at the current MTA0.
        The MTA0 pointer is post-incremented by the value of "Size".

        :param ccp_handle: The handle of a PCAN-CCP connection.
        :param data_buffer: Buffer with the data to be programmed.
        :param size: Size of the Data block to be programmed.
        :param mta0_ext: MTA0 extension after post-increment.
        :param mta0_addr: MTA0 Address after post-increment.
        :param timeout: Wait time (millis) for ECU response. Zero(0) to use the default time.
        :returns: The return value is a TCCPResult code. CCP_ERROR_ACKNOWLEDGE_OK is returned on success.
        """

        try:
            res = self.__m_dllCcp.CCP_Program(ccp_handle, byref(data_buffer), size,
                                              byref(mta0_ext), byref(mta0_addr), timeout)
            return TCCPResult(res)
        except Exception as ex:
            print("Exception on PCAN-CCP.Program:", ex)
            raise

    def Program_6(
            self,
            ccp_handle: TCCPHandle,
            data_buffer: c_buffer,
            mta0_ext: c_ubyte,
            mta0_addr: c_uint32,
            timeout: c_uint16):
        """
        Programs a block of 6 data bytes into non-volatile (FLASH, EPROM) memory, starting at the current MTA0.
        The MTA0 pointer is post-incremented by 6.

        :param ccp_handle: The handle of a PCAN-CCP connection.
        :param data_buffer: Buffer with the data to be programmed.
        :param mta0_ext: MTA0 extension after post-increment.
        :param mta0_addr: MTA0 Address after post-increment.
        :param timeout: Wait time (millis) for ECU response. Zero(0) to use the default time.
        :returns: The return value is a TCCPResult code. CCP_ERROR_ACKNOWLEDGE_OK is returned on success.
        """

        try:
            res = self.__m_dllCcp.CCP_Program_6(ccp_handle, byref(data_buffer),
                                                byref(mta0_ext), byref(mta0_addr), timeout)
            return TCCPResult(res)
        except Exception as ex:
            print("Exception on PCAN-CCP.Program_6:", ex)
            raise

    def BuildChecksum(
            self,
            ccp_handle: TCCPHandle,
            block_size: c_uint32,
            checksum_buffer: c_buffer,
            checksum_size: c_ubyte,
            timeout: c_uint16):
        """
        Calculates a checksum result of the memory block
        that is defined by MTA0 (Memory Transfer Area Start address) and "BlockSize".

        :param ccp_handle: The handle of a PCAN-CCP connection.
        :param block_size: Block size in bytes.
        :param checksum_buffer: Checksum data (implementation specific).
        :param checksum_size: Size of the checksum data.
        :param timeout: Wait time (millis) for ECU response. Zero(0) to use the default time.
        :returns: The return value is a TCCPResult code. CCP_ERROR_ACKNOWLEDGE_OK is returned on success.
        """

        try:
            res = self.__m_dllCcp.CCP_BuildChecksum(ccp_handle, block_size,
                                                    byref(checksum_buffer), byref(checksum_size), timeout)
            return TCCPResult(res)
        except Exception as ex:
            print("Exception on PCAN-CCP.BuildChecksum:", ex)
            raise

    def DiagnosticService(
            self,
            ccp_handle: TCCPHandle,
            diagnostic_number: c_uint16,
            parameters: c_ubyte,
            parameters_length: c_ubyte,
            return_length: c_ubyte,
            return_type: c_ubyte,
            timeout: c_uint16):
        """
        Executes a defined diagnostic procedure and sets the MTA0 pointer to the location
        from where the master can upload the requested information.

        :param ccp_handle: The handle of a PCAN-CCP connection.
        :param diagnostic_number: Diagnostic service number.
        :param parameters: Parameters, if applicable.
        :param parameters_length: Length in bytes of the parameters passed within "Parameters".
        :param return_length: Length of the return information (to be uploaded).
        :param return_type: Data type qualifier of the return information.
        :param timeout: Wait time (millis) for ECU response. Zero(0) to use the default time.
        :returns: The return value is a TCCPResult code. CCP_ERROR_ACKNOWLEDGE_OK is returned on success.
        """

        try:
            res = self.__m_dllCcp.CCP_DiagnosticService(ccp_handle, diagnostic_number,
                                                    parameters, parameters_length, return_length, return_type, timeout)
            return TCCPResult(res)
        except Exception as ex:
            print("Exception on PCAN-CCP.DiagnosticService:", ex)
            raise

    def ActionService(
            self,
            ccp_handle: TCCPHandle,
            action_number: c_uint16,
            parameters: c_ubyte,
            parameters_length: c_ubyte,
            return_length: c_ubyte,
            return_type: c_ubyte,
            timeout: c_uint16):
        """
        Executes a defined diagnostic procedure and sets the MTA0 pointer to the location
        from where the master can upload the requested information.

        :param ccp_handle: The handle of a PCAN-CCP connection.
        :param action_number: Action service number.
        :param parameters: Parameters, if applicable.
        :param parameters_length: Length in bytes of the parameters passed within "Parameters".
        :param return_length: Length of the return information (to be uploaded).
        :param return_type: Data type qualifier of the return information.
        :param timeout: Wait time (millis) for ECU response. Zero(0) to use the default time.
        :returns: The return value is a TCCPResult code. CCP_ERROR_ACKNOWLEDGE_OK is returned on success.
        """

        try:
            res = self.__m_dllCcp.CCP_ActionService(ccp_handle, action_number,
                                                    parameters, parameters_length, return_length, return_type, timeout)
            return TCCPResult(res)
        except Exception as ex:
            print("Exception on PCAN-CCP.ActionService:", ex)
            raise

    def GetErrorText(
            self,
            err_code: TCCPResult):
        """
        Returns a descriptive text for an error code.
        If the error code passed to the function represents a transport channel error (PCAN-Basic result code),
        the errorCode is internally passed to the PCAN-Basic function CAN_GetErrorText
        and its result copied to the textBuffer.

        :param err_code: A TCCPResult error code.
        :returns: The return value 1 is a TCCPResult code. CCP_ERROR_ACKNOWLEDGE_OK is returned on success.
            Typically, CCP_ERROR_PARAM_OUT_OF_RANGE is returned on failure.
            The return value 2 is error text.
        """

        try:
            mybuffer = create_string_buffer(256)
            res = self.__m_dllCcp.CCP_GetErrorText(err_code, byref(mybuffer))
            return TCCPResult(res), mybuffer.value
        except Exception as ex:
            print("Exception on PCAN-CCP.GetErrorText:", ex)
            raise
