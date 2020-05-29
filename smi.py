from protocol import *
import pandas as pd
#---------------------------------------------------------------------
class SMI( protocol ):
    def __init__( self, name, ifdo, fname ):
        super().__init__( name, ifdo, fname )
        self.phy_adr = "0x18"
    def cSet_RW_Format( self, cmd ):
        _Set_RW_Format( self, cmd )
    def cSet_Reg_Addr( self, cmd ):
        _Set_Reg_Addr( self, cmd )
    def cSet_Port_Value( self, mdc, mdio ):
        _Set_Port_Value( self, mdc, mdio )
    def cSet_RW_Data( self, cmd ):
        _Set_RW_Data( self, cmd )
    #Dedicated func
    def cSet_Phy_Addr( self, cmd ):
        _Set_Phy_Addr( self, cmd )

#----------------------------------------------------------------------------
def _Set_Port_Value( self, mdc, mdio ):
    for p in self.vector:
        if p.protocol == "smi-mdc":
            p.value = mdc
        if p.protocol == "smi-mdio":
            p.value = mdio
    self.cGenATPbyValue()
#----------------------------------------------------------------------------
def _Set_RW_Format( self, cmd ):
    if ( cmd.COMMAND not in self.cmd_list ) or ( not self.ifdo ):
        return
    else:   
        #--Preamble------------------
        self.f.write("//(SMI) Begin writing Preamble\n")
        for i in range(0,32):
            self.cSet_Port_Value( 0, 1 )
        self.f.write("//(SMI) Finish writing Preamble\n")
        #--Start-------------- 
        self.f.write("//(SMI) Start\n")
        self.cSet_Port_Value( 0, 0 )
        self.cSet_Port_Value( 0, 1 )
        #--OP-----------------
        self.f.write("//(SMI) Begin writing OP\n")
        if "R" in cmd.COMMAND:
            self.cSet_Port_Value( 0, 1 )
            self.cSet_Port_Value( 0, 0 )
        else:
            self.cSet_Port_Value( 0, 0 )
            self.cSet_Port_Value( 0, 1 )
        self.f.write("//(SMI) Finish writing OP\n")
        #--Write PHY Addr---------
        self.cSet_Phy_Addr( cmd )
        #--Write Reg Addr---------
        self.cSet_Reg_Addr( cmd )
        #--Turn Around------------
        self.f.write("//(SMI) Begin writing TA\n")
        if "R" in cmd.COMMAND:
            self.cSet_Port_Value( 0, 0 )#High-Z
            self.cSet_Port_Value( 0, 0 )
        else:
            self.cSet_Port_Value( 0, 1 )
            self.cSet_Port_Value( 0, 0 )
        self.f.write("//(SMI) Begin writing TA\n")
        #--RW Data----------------
        self.cSet_RW_Data( cmd )
        #--End---------------------
        self.cGenATP_Idle(10)
#----------------------------------------------------------------------------
def _Set_Reg_Addr( self, cmd ):
    self.f.write("//(SMI) Begin writing Reg Address\n")
    self.f.write("//(SMI) Reg Address = %s \n" % cmd.REGISTER )

    addr = bin( int(cmd.REGISTER,16) )[2:].zfill(5)

    for b in addr:
        self.cSet_Port_Value( 0, b )
    self.f.write("//(SMI) Finish writing Reg Address\n")
#----------------------------------------------------------------------------
def _Set_Phy_Addr( self, cmd ):
    self.f.write("//(SMI) Begin writing PHY Address\n")
    self.f.write("//(SMI) PHY Address = %s \n" % self.phy_adr ) 

    addr = bin(int(self.phy_adr,16))[2:].zfill(5)
    if( len(addr) > 5 ):
        print( "[Error] The PHY Address Length for SMI is larger than 5 bits" )
    for b in addr:
        self.cSet_Port_Value( 0, b )
    self.f.write("//(SMI) Finish writing PHY Reg Address\n")
#----------------------------------------------------------------------------
def _Set_RW_Data( self, cmd ):
    rw = cmd.COMMAND
    ack= 0 if ( "R" in cmd.COMMAND ) else "L"
    self.f.write("//(SMI) Begin %s data\n" % rw)
    self.f.write("//(SMI) Data = %s \n" % cmd.DATA )

    value = 0
    #Hex format (Must be 32 bit)
    
    if not isDataBinary( cmd.DATA ):
        if( "W" in cmd.COMMAND ):
            value =  bin(int(cmd.DATA,16))[2:].zfill(16)
        else:
            value =  bin(int(cmd.DATA,16))[2:].rjust(16,"x")
    #Binary format
    else:
        if( "W" in cmd.COMMAND ):
            value = cmd.DATA.replace( "_", "" ).zfill(16)
        else:#R, RL, RH
            value = cmd.DATA.replace( "_", "" ).rjust(16,"x")

    if( len(value) > 16 ):
        print( "[Warning] The SMI DATA Length for SMI is larger than 16 (It should be 16 bits, based on SPEC)" )
        print( "\tSMI DATA     is ", value )
        print( "\tYour COMMAND is ", cmd.COMMAND )
        print( "\tYour DATA    is ", cmd.DATA )

    for v in value:
        if "R" in rw:
            if v == "1":
                v = "H"
            elif v == "0":
                v = "L"
        self.cSet_Port_Value( 0, v )
    self.f.write("//(Finish) Finish %s data\n" % rw)
#----------------------------------------------------------------------------