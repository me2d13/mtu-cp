# copied & inspired by https://github.com/Chr157i4n/TMC2209_Raspberry_Pi

"""
TMC_UART stepper driver uart module
"""

import time
import struct
import busio
import config
from log import pdebug, perror

#pylint: disable=invalid-name
"""
this file contains:
1. hexadecimal address of the different registers
2. bitposition and bitmasks of the different values of each register

Example:
the register IOIN has the address 0x06 and the first bit shows
whether the ENABLE (EN/ENN) Pin is currently HIGH or LOW
"""

#addresses
GCONF           =   0x00
GSTAT           =   0x01
IFCNT           =   0x02
IOIN            =   0x06
IHOLD_IRUN      =   0x10
TSTEP           =   0x12
VACTUAL         =   0x22
TCOOLTHRS       =   0x14
SGTHRS          =   0x40
SG_RESULT       =   0x41
MSCNT           =   0x6A
CHOPCONF        =   0x6C
DRVSTATUS       =   0x6F

#GCONF
i_scale_analog      = 1<<0
internal_rsense     = 1<<1
en_spreadcycle      = 1<<2
shaft               = 1<<3
index_otpw          = 1<<4
index_step          = 1<<5
pdn_disable         = 1<<6
mstep_reg_select    = 1<<7

#GSTAT
reset               = 1<<0
drv_err             = 1<<1
uv_cp               = 1<<2

#CHOPCONF
toff0               = 1<<0
toff1               = 1<<1
toff2               = 1<<2
toff3               = 1<<3
vsense              = 1<<17
msres0              = 1<<24
msres1              = 1<<25
msres2              = 1<<26
msres3              = 1<<27
intpol              = 1<<28

#IOIN
io_enn              = 1<<0
io_step             = 1<<7
io_spread           = 1<<8
io_dir              = 1<<9

#DRVSTATUS
stst                = 1<<31
stealth             = 1<<30
cs_actual           = 31<<16
t157                = 1<<11
t150                = 1<<10
t143                = 1<<9
t120                = 1<<8
olb                 = 1<<7
ola                 = 1<<6
s2vsb               = 1<<5
s2vsa               = 1<<4
s2gb                = 1<<3
s2ga                = 1<<2
ot                  = 1<<1
otpw                = 1<<0

#IHOLD_IRUN
ihold               = 31<<0
irun                = 31<<8
iholddelay          = 15<<16

#SGTHRS
sgthrs              = 255<<0

#others
mres_256 = 0
mres_128 = 1
mres_64 = 2
mres_32 = 3
mres_16 = 4
mres_8 = 5
mres_4 = 6
mres_2 = 7
mres_1 = 8

class TMC_UART:
    """TMC_UART

    this class is used to communicate with the TMC via UART
    it can be used to change the settings of the TMC.
    like the current or the microsteppingmode
    """
    mtr_id = 0
    ser = None
    r_frame  = bytearray([0x55, 0, 0, 0  ]) # sync, 0, addr, crc
    w_frame  = bytearray([0x55, 0, 0, 0 , 0, 0, 0, 0 ]) # sync, 0, addr, 4xdata, crc
    communication_pause = 0
    error_handler_running = False



    def __init__(self,
                 baudrate, mtr_id = 0
                 ):
        """constructor

        Args:
            tmc_logger (class): TMCLogger class
            serialport (string): serialport path
            baudrate (int): baudrate
            mtr_id (int, optional): driver address [0-3]. Defaults to 0.
        """
        try:
            self.ser = busio.UART(config.UART_TX, config.UART_RX, baudrate=baudrate)
        except Exception as e:
            errnum = e.args[0]
            pdebug(f"SERIAL ERROR: {e}")
            if errnum == 2:
                pdebug(f""""{serialport} does not exist.
                      You need to activate the serial port with \"sudo raspi-config\"""")
            if errnum == 13:
                pdebug("""you have no permission to use the serial port.
                                    You may need to add your user to the dialout group
                                    with \"sudo usermod -a -G dialout pi\"""")

        self.mtr_id = mtr_id
        # adjust per baud and hardware. Sequential reads without some delay fail.
        self.communication_pause = 500 / baudrate

        if self.ser is None:
            return

        #self.ser.BYTESIZES = 1
        #self.ser.PARITIES = serial.PARITY_NONE
        #self.ser.STOPBITS = 1

        # adjust per baud and hardware. Sequential reads without some delay fail.
        self.ser.timeout = 20000/baudrate

        #self.ser.reset_output_buffer()
        self.ser.reset_input_buffer()



    def __del__(self):
        """""destructor"""""
        if self.ser is not None:
            self.ser.deinit()



    def compute_crc8_atm(self, datagram, initial_value=0):
        """this function calculates the crc8 parity bit

        Args:
            datagram (list): datagram
            initial_value (int): initial value (Default value = 0)
        """
        crc = initial_value
        # Iterate bytes in data
        for byte in datagram:
            # Iterate bits in byte
            for _ in range(0, 8):
                if (crc >> 7) ^ (byte & 0x01):
                    crc = ((crc << 1) ^ 0x07) & 0xFF
                else:
                    crc = (crc << 1) & 0xFF
                # Shift to next bit
                byte = byte >> 1
        return crc



    def read_reg(self, register):
        """reads the registry on the TMC with a given address.
        returns the binary value of that register

        Args:
            register (int): HEX, which register to read
        """
        if self.ser is None:
            pdebug("Cannot read reg, serial is not initialized", Loglevel.ERROR)
            return False

        #self.ser.reset_output_buffer()
        self.ser.reset_input_buffer()

        self.r_frame[1] = self.mtr_id
        self.r_frame[2] = register
        self.r_frame[3] = self.compute_crc8_atm(self.r_frame[:-1])

        rtn = self.ser.write(self.r_frame)
        if rtn != len(self.r_frame):
            pdebug("Err in write", Loglevel.ERROR)
            return False

        # adjust per baud and hardware. Sequential reads without some delay fail.
        time.sleep(self.communication_pause)

        rtn = self.ser.read(12)
        #pdebug(f"received {len(rtn)} bytes; {len(rtn*8)} bits")
        #pdebug(rtn.hex())

        time.sleep(self.communication_pause)

        return rtn



    def read_int(self, register, tries=10):
        """this function tries to read the registry of the TMC 10 times
        if a valid answer is returned, this function returns it as an integer

        Args:
            register (int): HEX, which register to read
            tries (int): how many tries, before error is raised (Default value = 10)
        """
        if self.ser is None:
            perror("Cannot read int, serial is not initialized")
            return -1
        while True:
            tries -= 1
            rtn = self.read_reg(register)
            rtn_data = rtn[7:11]
            not_zero_count = len([elem for elem in rtn if elem != 0])

            if(len(rtn)<12 or not_zero_count == 0):
                perror(f"""UART Communication Error:
                                    {len(rtn_data)} data bytes |
                                    {len(rtn)} total bytes""")
            elif rtn[11] != self.compute_crc8_atm(rtn[4:11]):
                perror("UART Communication Error: CRC MISMATCH")
            else:
                break

            if tries<=0:
                perror("after 10 tries not valid answer")
                pdebug(f"snd:\t{bytes(self.r_frame)}")
                pdebug(f"rtn:\t{rtn}")
                self.handle_error()
                return -1

        val = struct.unpack(">i",rtn_data)[0]
        pdebug(f"From regiter {hex(register)} read value {hex(val)}")
        return val



    def write_reg(self, register, val):
        """this function can write a value to the register of the tmc
        1. use read_int to get the current setting of the TMC
        2. then modify the settings as wished
        3. write them back to the driver with this function

        Args:
            register (int): HEX, which register to write
            val (int): value for that register
        """
        if self.ser is None:
            perror("Cannot write reg, serial is not initialized")
            return False

        #self.ser.reset_output_buffer()
        self.ser.reset_input_buffer()

        self.w_frame[1] = self.mtr_id
        self.w_frame[2] =  register | 0x80  # set write bit

        self.w_frame[3] = 0xFF & (val>>24)
        self.w_frame[4] = 0xFF & (val>>16)
        self.w_frame[5] = 0xFF & (val>>8)
        self.w_frame[6] = 0xFF & val

        self.w_frame[7] = self.compute_crc8_atm(self.w_frame[:-1])

        pdebug(f"Writing to reg {hex(register)} value {hex(val)}")

        rtn = self.ser.write(self.w_frame)
        if rtn != len(self.w_frame):
            perror("Err in write")
            return False

        time.sleep(self.communication_pause)

        return True



    def write_reg_check(self, register, val, tries=10):
        """this function als writes a value to the register of the TMC
        but it also checks if the writing process was successfully by checking
        the InterfaceTransmissionCounter before and after writing

        Args:
            register: HEX, which register to write
            val: value for that register
            tries: how many tries, before error is raised (Default value = 10)
        """
        if self.ser is None:
            perror("Cannot write reg check, serial is not initialized")
            return False
        ifcnt1 = self.read_int(IFCNT)

        if ifcnt1 == 255:
            ifcnt1 = -1

        while True:
            self.write_reg(register, val)
            tries -= 1
            ifcnt2 = self.read_int(IFCNT)
            if ifcnt1 >= ifcnt2:
                perror("writing not successful!")
                pdebug(f"ifcnt: {ifcnt1}, {ifcnt2}")
            else:
                return True
            if tries<=0:
                perror("after 10 tries no valid write access")
                self.handle_error()
                return -1



    def flush_serial_buffer(self):
        """this function clear the communication buffers of the Raspberry Pi"""
        if self.ser is None:
            return
        #self.ser.reset_output_buffer()
        self.ser.reset_input_buffer()



    def set_bit(self, value, bit):
        """this sets a specific bit to 1

        Args:
            value: value on which the bit should be set
            bit: which bit to set
        """
        return value | (bit)



    def clear_bit(self, value, bit):
        """this sets a specific bit to 0

        Args:
            value: value on which the bit should be cleared
            bit: which bit to clear
        """
        return value & ~(bit)



    def handle_error(self):
        """error handling"""
        if self.error_handler_running:
            return
        self.error_handler_running = True
        gstat = self.read_int(GSTAT)
        pdebug("GSTAT Error check:")
        if gstat == -1:
            pdebug("No answer from Driver")
        elif gstat == 0:
            pdebug("Everything looks fine in GSTAT")
        else:
            if gstat & reset:
                pdebug("The Driver has been reset since the last read access to GSTAT",
                                    Loglevel.DEBUG)
            if gstat & drv_err:
                pdebug("""The driver has been shut down due to overtemperature or short
                      circuit detection since the last read access""")
            if gstat & uv_cp:
                pdebug("""Undervoltage on the charge pump.
                      The driver is disabled in this case""")
        #pdebug("EXITING!", Loglevel.INFO)
        #raise SystemExit



    def test_uart(self, register):
        """test UART connection

        Args:
            register (int):  HEX, which register to read
        """

        if self.ser is None:
            pdebug("Cannot test UART, serial is not initialized", Loglevel.ERROR)
            return False

        #self.ser.reset_output_buffer()
        self.ser.reset_input_buffer()

        self.r_frame[1] = self.mtr_id
        self.r_frame[2] = register
        self.r_frame[3] = self.compute_crc8_atm(self.r_frame[:-1])

        pdebug(f"Writing hex: {self.r_frame.hex()}")
        rtn = self.ser.write(self.r_frame)
        if rtn != len(self.r_frame):
            pdebug("Err in write", Loglevel.ERROR)
            return False

        # adjust per baud and hardware. Sequential reads without some delay fail.
        time.sleep(self.communication_pause)

        rtn = self.ser.read(12)
        pdebug(f"received {len(rtn)} bytes; {len(rtn)*8} bits")
        pdebug(f"hex: {rtn.hex()}")
        #rtn_bin = format(int(rtn.hex(),16), f"0>{len(rtn)*8}b")
        #pdebug(f"bin: {rtn_bin}")

        time.sleep(self.communication_pause)

        return bytes(self.r_frame), rtn