from protocol import *
import pandas as pd
#---------------------------------------------------------------------
class I2C( protocol ):
    def __init__( self, name, ifdo, fname ):
        super().__init__( name, ifdo, fname )
        self.ctrlbyte = "1010100"
    #Inherit from virtual class
    def cSet_RW_Format( self, cmd ):
        _Set_RW_Format( self, cmd )
    def cSet_Reg_Addr( self, cmd ):
        _Set_Reg_Addr( self, cmd )
    def cSet_Port_Value( self, SCL, SDA, note="" ):
        _Set_Port_Value( self, SCL, SDA, note )
    def cSet_RW_Data( self, cmd ):
        _Set_RW_Data( self, cmd )
    #Dedicated func
    def cSet_Start( self ):
        _Set_Start( self )
    def cSet_End( self ):
        _Set_End( self )
    def cSet_Ctrl_Byte( self, ctrl, rw ):
        _Set_Ctrl_Byte( self, ctrl, rw )
#---------------------------------------------------------------------
def _Set_RW_Format( self, cmd ):
    if ( cmd.COMMAND not in self.cmd_list ) or ( not self.ifdo ):
        return
    else:
        ctrl = self.ctrlbyte #Ctrl byte
        #--Start------------------
        self.cSet_Start()
        #--Ctrl byte--------------
        self.cSet_Ctrl_Byte( ctrl, "w" )
        #--Write Reg Addr---------
        self.cSet_Reg_Addr( cmd )
        if "R" in cmd.COMMAND:
            #--Set Start--------------
            self.cSet_Port_Value( 0, 1 )
            self.cSet_Port_Value( 1, 0 )
            #--Ctrl byte--------------
            self.cSet_Ctrl_Byte( ctrl, "r" )
        #--RW Data-------------
        self.cSet_RW_Data( cmd )
        #--End---------------------
        self.cSet_End()
#---------------------------------------------------------------------
def _Set_Reg_Addr( self, cmd ):
    self.f.write("//(I2C) Begin writing 24-bit Reg Address\n")
    self.f.write("//(I2C) Address = %s \n" % cmd.REGISTER )
    adrr = bin(int(cmd.REGISTER,16))[2:].zfill(24)[::-1]
    adrr = adrr[0:8][::-1] + adrr[8:16][::-1] + adrr[16:24][::-1]
    ctr  = 1
    for b in adrr:
        self.cSet_Port_Value( 0, b )
        if ctr == 8:
            ctr = 1
            self.cSet_Port_Value( 0, "L" )#Ack from slave
            self.f.write("//(I2C) ACK from slave to master, due to one byte/8 bits\n")
        else:
            ctr += 1
    self.f.write("//(I2C) End writing 24-bit Reg Address\n")
#---------------------------------------------------------------------
def _Set_Port_Value( self, SCL, SDA, note="" ):
    for p in self.vector:
        if p.protocol == "i2c-scl":
            p.value = SCL
        if p.protocol == "i2c-sda":
            p.value = SDA
    self.cGenATPbyValue( note )
#---------------------------------------------------------------------
def _Set_RW_Data( self, cmd ):
    rw = cmd.COMMAND
    ack= 1 if ( "R" in cmd.COMMAND ) else "L"
    self.f.write("//(I2C) Begin %s data = %s\n" % rw, cmd.DATA )
    value = 0
    #Hex format (Must be 32 bit)
    cmd.DATA = cmd.DATA.upper()
    if not isDataBinary( cmd.DATA ):
        if( "W" in cmd.COMMAND ):
            value =  bin(int(cmd.DATA,16))[2:].zfill(32)[::-1]
        else:
            value =  bin(int(cmd.DATA,16))[2:].rjust(32,"X")[::-1]
    #Binary format
    else:
        if( "W" in cmd.COMMAND ):
            value = cmd.DATA.replace( "_", "" ).zfill(32)[::-1]
        else:#R, RL, RH
            value = cmd.DATA.replace( "_", "" ).rjust(32,"X")[::-1]
    #RH/RL/R
    if(  cmd.COMMAND == "RH" ):
        value = "X" * 16 + value[16:24][::-1] + value[24:32][::-1]
    elif cmd.COMMAND == "RL":
        value = value[0:8][::-1] + value[8:16][::-1] + "X" * 16
    else:
        value = value[0:8][::-1] + value[8:16][::-1] + value[16:24][::-1] + value[24:32][::-1]
    ctr   = 1
    byte  = 1
    for v in value:
        if "R" in rw:
            if v == "1":
                v = "H"
            elif v == "0":
                v = "L"

        self.cSet_Port_Value( 0, v )
        if ctr == 8:
            ctr = 1
            self.cSet_Port_Value( 0, ack )#Ack from master to slave
            self.f.write("//(I2C) ACK from master to slave, due to one byte/8 bits\n")
            byte += 1
        else:
            ctr += 1
    self.f.write("//(I2C) End %s data\n" % rw)
#---------------------------------------------------------------------
def _Set_Ctrl_Byte( self, ctrl_byte, rw ):
    self.f.write("//(I2C) Begin writing ctrl bytes\n")
    rwb = 0 if (rw == "w") else 1
    for ctrl in ctrl_byte:
        self.cSet_Port_Value( 0, ctrl )
    self.cSet_Port_Value( 0, rwb   ) #R/W, Write
    self.cSet_Port_Value( 0, "L" )#--ACK from DUT
    self.f.write("//(I2C) End writing ctrl bytes\n")
#---------------------------------------------------------------------
def _Set_Start( self ):
    self.f.write("//I2C Start\n")
    self.cSet_Port_Value( 1, 1 )
    self.cSet_Port_Value( 1, 0 )
#---------------------------------------------------------------------
def _Set_End( self ):
    self.f.write("//I2C End\n")
    self.cSet_Port_Value( 0, 0 )
    self.cSet_Port_Value( 1, 1 )
    self.cSet_Port_Value( 1, 1 )
    self.cSet_Port_Value( 1, 1 )