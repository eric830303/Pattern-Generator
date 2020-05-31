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
    def cSet_Port_Value( self, mdc, mdio, note="" ):
        _Set_Port_Value( self, mdc, mdio, note    )
    def cSet_RW_Data( self, cmd ):
        _Set_RW_Data( self, cmd )
    #Dedicated func
    def cSet_Phy_Addr( self, cmd ):
        _Set_Phy_Addr( self, cmd )

#----------------------------------------------------------------------------
def _Set_Port_Value( self, mdc, mdio, note="" ):
    for p in self.vector:
        if p.protocol == "smi-mdc":
            p.value = mdc
        if p.protocol == "smi-mdio":
            p.value = mdio
    self.cGenATPbyValue( note )
#----------------------------------------------------------------------------
def _Set_RW_Format( self, cmd ):
    if ( cmd.COMMAND not in self.cmd_list ) or ( not self.ifdo ):
        return
    else:   
        #--Preamble------------------
        for i in range(0,32):
            self.cSet_Port_Value( 0, 1, "(smi) %2d/32 Preamble" % (i+1) )

        #--Start-------------- 
        self.cSet_Port_Value( 0, 0, "(SMI) Start=01" )
        self.cSet_Port_Value( 0, 1 )
        #--OP-----------------
        if "R" in cmd.COMMAND:
            self.cSet_Port_Value( 0, 1, "(SMI) OP=10 (Read)" )
            self.cSet_Port_Value( 0, 0 )
        else:
            self.cSet_Port_Value( 0, 0, "(SMI) OP=01 (Write)" )
            self.cSet_Port_Value( 0, 1 )    
        #--Write PHY Addr---------
        self.cSet_Phy_Addr( cmd )
        #--Write Reg Addr---------
        self.cSet_Reg_Addr( cmd )
        #--Turn Around------------
        if "R" in cmd.COMMAND:
            self.cSet_Port_Value( 0, 0, "(SMI) TA=00 (READ)"  )#High-Z
            self.cSet_Port_Value( 0, 0 )
        else:
            self.cSet_Port_Value( 0, 1, "(SMI) TA=10 (READ)" )
            self.cSet_Port_Value( 0, 0 )
        
        #--RW Data----------------
        self.cSet_RW_Data( cmd )
        #--End---------------------
        self.cGenATP_Idle(10)
#----------------------------------------------------------------------------
def _Set_Reg_Addr( self, cmd ):

    addr = bin( int(cmd.REGISTER,16) )[2:].zfill(5)
    #if( len(addr) > 5 ):
    #    print( "[Warning] The PHY Address Length for SMI is larger than 5 bits" )
    #    print( "\tsheet   =", self.current_sheet )
    #    print( "\trow     =", self.current_row+2 )
    #    print( "\tCOMMAND =", cmd.COMMAND )
    #    print( "\tDATA    =", cmd.DATA )
    for b in addr:
        self.cSet_Port_Value( 0, b, "(SMI) Reg Addr = %s" % cmd.REGISTER )
    
#----------------------------------------------------------------------------
def _Set_Phy_Addr( self, cmd ):
    
    addr = bin(int(self.phy_adr,16))[2:].zfill(5)
    if( len(addr) > 5 ):
        print( "[Warning] The PHY Address Length for SMI is larger than 5 bits" )
        print( "\tsheet   =", self.current_sheet )
        print( "\trow     =", self.current_row+2 )
        print( "\tCOMMAND =", cmd.COMMAND )
        print( "\tDATA    =", cmd.DATA )
    for b in addr:
        self.cSet_Port_Value( 0, b, "(SMI) PHY Reg Addr = %s" % self.phy_adr)
   
#----------------------------------------------------------------------------
def _Set_RW_Data( self, cmd ):
    rw = cmd.COMMAND
    ack= 0 if ( "R" in cmd.COMMAND ) else "L"
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
        print( "\tBinary SMI DATA     is ", value )
        print( "\tsheet   =", self.current_sheet )
        print( "\trow     =", self.current_row+2 )
        print( "\tCOMMAND =", cmd.COMMAND )
        print( "\tDATA    =", cmd.DATA )
       

    for v in value:
        if "R" in rw:
            if v == "1":
                v = "H"
            elif v == "0":
                v = "L"
        self.cSet_Port_Value( 0, v, "(smi) %s data = %s" % ( rw, cmd.DATA ) )
    
#----------------------------------------------------------------------------