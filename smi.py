from protocol import *
import copy
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
    def c32DataCallBack( self, cmd ):
        _32DataCallBack( self, cmd )

def _32DataCallBack( self, cmd ):
    ori = copy.deepcopy( cmd.DATA )
    cmd1 = copy.deepcopy( cmd )
    if not isDataMoreThan16( cmd.DATA ): return
    else:
        if isDataBinary( cmd.DATA ):
            full_data = cmd.DATA.zfill(32) if( "W" in cmd.COMMAND ) else cmd.DATA.rjust(32,"x")
            cmd1.DATA = full_data[-16:]
            cmd.DATA  = cmd.DATA[:16]
            self.cSet_RW_Format( cmd1 )
        else:
            bin_data  = bin( int( cmd.DATA, 16 ) )[2:]
            full_data = bin_data.zfill(32) if( "W" in cmd.COMMAND ) else bin_data.rjust(32,"x")
            cmd1.DATA = full_data[-16:]
            cmd.DATA  = full_data[:16]
            self.cSet_RW_Format(cmd1)
        print("[Warning] DATA length larger then 16 bit (based on SPEC)")
        print("\tAuto Partition in the tool")
        print("\tAt sheet  = ", self.current_sheet )
        print("\tAt row    = ", self.current_row   )
        print("\tCOMMAND   = ", cmd.COMMAND )
        print("\tOri DATA  = ", ori )
        print("\tDATA1     = ", cmd1.DATA, "(Auto partitioned)" )
        print("\tDATA2     = ",  cmd.DATA, "(Auto partitioned)" )
            
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
    cmd1 = copy.deepcopy(cmd)
    cmd2 = copy.deepcopy(cmd)
    cmd3 = copy.deepcopy(cmd)
    cmd4 = copy.deepcopy(cmd)
    #DATA
    full_data = ""
    if isDataBinary( cmd.DATA ):
        full_data = cmd.DATA.zfill(32) if ("W" in cmd.COMMAND) else cmd.DATA.rjust(32, "x")
    else:
        bin_data = bin(int(cmd.DATA, 16))[2:]
        full_data = bin_data.zfill(32) if ("W" in cmd.COMMAND) else bin_data.rjust(32, "x")
    #REGISTER
    bin_reg  = bin(int(cmd.REGISTER, 16))[2:]
    full_reg = bin_reg.zfill(32)
    full_reg = "10000001"+ full_reg[8:]
   
    cmd1.DATA = full_data[-16:]
    cmd2.DATA = full_data[:16]
    cmd3.DATA = full_reg[-16:]
    cmd4.DATA = full_reg[:16]
    cmd1.REGISTER = "0x00"
    cmd2.REGISTER = "0x02"
    cmd3.REGISTER = "0x04"
    cmd4.REGISTER = "0x06"
    
    _Set_RW_Format2( self, cmd1 )
    _Set_RW_Format2( self, cmd2 )
    _Set_RW_Format2( self, cmd3 )
    _Set_RW_Format2( self, cmd4 )
    
def _Set_RW_Format2( self, cmd ):
    if ( cmd.COMMAND not in self.cmd_list ) or ( not self.ifdo ):
        return
    else:
        #self.c32DataCallBack( cmd )
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
    for b in addr:
        self.cSet_Port_Value( 0, b, "(SMI) Offset = %s (Reg Addr)" % cmd.REGISTER )
    
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

    for v in value:
        if "R" in rw:
            if v == "1":
                v = "H"
            elif v == "0":
                v = "L"
        self.cSet_Port_Value( 0, v, "(smi) %s data = %s" % ( rw, cmd.DATA ) )
    
#----------------------------------------------------------------------------