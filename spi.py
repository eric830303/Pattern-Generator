from protocol import *
import pandas as pd
#---------------------------------------------------------------------
class SPI( protocol ):
    def __init__( self, name, ifdo, fname ):
        super().__init__( name, ifdo, fname )
        self.dumycycle = 8
    def cSet_RW_Format( self, cmd ):
        _Set_RW_Format( self, cmd )
    def cSet_Reg_Addr( self, cmd ):
        _Set_Reg_Addr( self, cmd )
    def cSet_Port_Value( self, ss, scl, di, do, note="" ):
        _Set_Port_Value( self, ss, scl, di, do, note )
    def cSet_RW_Data( self, cmd ):
        _Set_RW_Data( self, cmd )
#---------------------------------------------------------------------
def _Set_RW_Format( self, cmd ):
    if ( cmd.COMMAND not in self.cmd_list ) or ( not self.ifdo ):
        return
    else:
        self.cGenATP_Idle(10)
        #------OP-Write-----------------------
        self.f.write("//(SPI) Start! SPI_CSI 1 -> 0 \n")
        self.f.write("//(SPI) Start writing OP code\n")
        self.cSet_Port_Value( 0, 0, 0, 0 )
        self.cSet_Port_Value( 0, 0, 0, 0 )
        self.cSet_Port_Value( 0, 0, 0, 0 )
        self.cSet_Port_Value( 0, 0, 0, 0 )
        self.cSet_Port_Value( 0, 0, 0, 0 )
        self.cSet_Port_Value( 0, 0, 0, 0 )
        self.cSet_Port_Value( 0, 0, 1, 0 )
        if ( cmd.COMMAND == "R" ) or ( cmd.COMMAND == "RH" ) or ( cmd.COMMAND == "RL" ) :
            self.cSet_Port_Value( 0, 0, 1, 0 )
            self.f.write("//(SPI) End writing OP code for Read 8'h03\n")
        else:
            self.cSet_Port_Value( 0, 0, 0, 0 )
            self.f.write("//(SPI) End writing OP code for Read 8'h02\n")
        #------Write 24 bits Address-----------
        self.cSet_Reg_Addr( cmd )
        #------Dummy if Read-------------------
        if ( cmd.COMMAND == "R" ) or ( cmd.COMMAND == "RH" ) or ( cmd.COMMAND == "RL" ) :
            for i in range( self.dumycycle ):
                self.cSet_Port_Value( 0, 0, 0, 0, "(spi) Dummy Cycle" )
            
        #------RW Data-------------------------
        self.cSet_RW_Data( cmd )
#---------------------------------------------------------------------
def _Set_Reg_Addr( self, cmd ):
    #The address must be present in hex format
    adrr = bin(int(cmd.REGISTER,16))[2:].zfill(24)[::-1]
    adrr = adrr[16:24][::-1] + adrr[8:16][::-1] + adrr[0:8][::-1]
    for b in adrr:
        self.cSet_Port_Value( 0, 0, b, 0, "(spi) 24 Reg Addr = %s " % (cmd.REGISTER) )       
    
#---------------------------------------------------------------------
def _Set_Port_Value( self, ss, scl, di, do, note="" ):
    for p in self.vector:
        if p.protocol == "spi-ss":
            p.value = ss
        if p.protocol == "spi-clk":
            p.value = scl
        if p.protocol == "spi-di":
            p.value = di
        if p.protocol == "spi-do":
            p.value = do
    self.cGenATPbyValue( note )
#---------------------------------------------------------------------
def _Set_RW_Data( self, cmd ):
    rw = cmd.COMMAND
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
    #RH/RL/R/W
    if(   cmd.COMMAND == "RH" ):
        #value = value[24:32][::-1] + value[16:24][::-1] + "X" * 16 
        value =  value[8:16][::-1] + value[0:8][::-1] + "X" * 16 
    elif( cmd.COMMAND == "RL" ):
        value = "X" * 16 + value[8:16][::-1] + value[0:8][::-1]
    else:#R/W
        value =  value[24:32][::-1] + value[16:24][::-1] + value[8:16][::-1] + value[0:8][::-1]
    
    for v in value:
        if "R" in rw :
            if v == "1":
                v = "H"
            elif v == "0":
                v = "L"
            self.cSet_Port_Value( 0, 0, 0, v, "(SPI) %s data = %s" % ( rw, cmd.DATA ) )
        else:
            self.cSet_Port_Value( 0, 0, v, 0, "(SPI) %s data = %s" % ( rw, cmd.DATA ) )
