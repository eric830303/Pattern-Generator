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
            self.cSet_Port_Value( 0, 1, "Start (Read)" )
            self.cSet_Port_Value( 1, 0 )
            #--Ctrl byte--------------
            self.cSet_Ctrl_Byte( ctrl, "r" )
        #--RW Data-------------
        self.cSet_RW_Data( cmd )
        #--End---------------------
        self.cSet_End()
#---------------------------------------------------------------------
def _Set_Reg_Addr( self, cmd ):
    adrr = bin(int(cmd.REGISTER,16))[2:].zfill(24)[::-1]
    adrr = adrr[0:8][::-1] + adrr[8:16][::-1] + adrr[16:24][::-1]
    sub  = 0
    for ( id, b ) in enumerate( adrr ):
        id2 = 0
        sub = 0 if( sub == 8 ) else sub
        id2 =  7 - sub if id <=  7 else\
              15 - sub if id <= 15 else\
              23 - sub if id <= 23 else 0
       
        sub = sub + 1
        self.cSet_Port_Value( 0, b, "Write Addr [%2d], Addr = %s" % ( id2, cmd.REGISTER ) )
        if ( id+1 ) %8 == 0:
            self.cSet_Port_Value( 0, "L", "ACK" )#Ack from slave  

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
    ack= 0 if ( "R" in cmd.COMMAND ) else "L"
    
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
        value =  "X" * 16  + value[0:8][::-1] + value[8:16][::-1]
    elif cmd.COMMAND == "RL":
        value = value[0:8][::-1] + value[8:16][::-1] +  "X" * 16
    else:
        value = value[0:8][::-1] + value[8:16][::-1] + value[16:24][::-1] + value[24:32][::-1]
  
    byte  = 1
    sub   = 0 
    for id, v in enumerate( value ):
        if "R" in rw:
            if v == "1":
                v = "H"
            elif v == "0":
                v = "L"

        id2 = 0
        sub = 0 if( sub == 8 ) else sub
        id2 =  7 - sub if id <=  7 else\
              15 - sub if id <= 15 else\
              23 - sub if id <= 23 else\
              31 - sub if id <= 31 else 0
        sub = sub + 1
        
        self.cSet_Port_Value( 0, v, "%s Data[%2d], Data = %s" % (rw, id2, cmd.DATA) )
        if ( id + 1 ) % 8 == 0:
            self.cSet_Port_Value( 0, ack, "ACK" )
            
    
#---------------------------------------------------------------------
def _Set_Ctrl_Byte( self, ctrl_byte, rw ):
    rwb = 0 if (rw == "w") else 1
    for i, ctrl in enumerate( ctrl_byte ):
        self.cSet_Port_Value( 0, ctrl, "Ctrl [%d]" % (7-i) )
    self.cSet_Port_Value    ( 0, rwb,  "Ctrl [0]"  ) #R/W, Write
    self.cSet_Port_Value    ( 0, "L",  "ACK, End writing ctrl bytes" )#--ACK from DUT
#---------------------------------------------------------------------
def _Set_Start( self ):
    self.cSet_Port_Value( 1, 1, "I2C Start!" )
    self.cSet_Port_Value( 1, 0 )
#---------------------------------------------------------------------
def _Set_End( self ):
    self.cSet_Port_Value( 0, 0, "I2C End" )
    for i in range(100):
        self.cSet_Port_Value( 1, 1, "Idle %3d" % (i) )
    
