from func import *
import pandas as pd
#---------------------------------------------------------------------
class Port:
    def __init__( self, name, value ):
        self.name     = name
        self.value    = value
        self.protocol = ""
        self.ini_value= value      
#---------------------------------------------------------------------
class protocol:
    def __init__( self, name, ifdo, infname ):
        self.name     = name
        self.vector   = [] #Port vector
        self.f        = "" #File descriptor
        self.ifdo     = ifdo
        self.cmd_list = [ "W", "R", "RH", "RL", "D", "F", "C", "X", "M" ]
        self.skip_cmd = [ "F", "C", "X", "M" ] 
        self.infname  = infname
        self.excel    = ""
        self.df_port  = ""
        self.df_cmd   = ""
        self.current_row   = 0
        self.current_sheet = ""
    def cSet_RW_Format( self, format ):
        pass
    def cSet_Reg_Addr(self):
        pass
    def cSet_Port_Value(self):
        pass
    def cSet_RW_Data(self):
        pass
    def cGenATPbyValue(self, note=""):
        _GenATPbyValue(self, note )
    def cGenATP_Idle( self, cnt ):
        _GenATP_Idle( self, cnt )
    def cGenVectorList( self ):
        return _GenVectorList( self )
    def cGenATP( self ):
        _GenATP( self )
    def cParseDataFrame( self ):
        _ParseDataFrame( self )
    def cPutPortInVector( self, port_list, protocol, value ):
        _PutPortInVector( self, port_list, protocol, value )
#----------------------------------------------------------------------------
def _PutPortInVector( self, port_list, protocol, value ):
    for p in port_list:
        if ( not pd.isna(p) ):
            p_inst = Port( p, value )
            if ( p_inst not in self.vector ):
                p_inst.protocol = protocol
                self.vector.append( p_inst )
            else:
                print( "[Error] Port %s is duplicated" )
#----------------------------------------------------------------------------
def _ParseDataFrame( self ):
    try:
        self.excel   = pd.ExcelFile( self.infname )
        print( "[Info] Reading %s" % self.infname )
    except:
        print( "[Error] Fail to read excel" )
        print( "[Error] Input file must be *.xlsx format. Maybe your input is *.csv or other formates, which is not allowed" )
        exit(-1)
    #----------Parse Port Data---------------------------------------------
    if(   "_start" not in self.excel.sheet_names ):
        print( "[Error] No \"_start\" sheet in your excel" )
        exit(-1)
    elif( "_end"   not in self.excel.sheet_names ):
        print( "[Error] No \"_end\" sheet in your excel" )
        exit(-1)
    elif( "PORT"   not in self.excel.sheet_names ):
        print( "[Error] No \"PORT\" sheet in your excel" )
        exit(-1)
    self.df_port = self.excel.parse("PORT")

    self.cPutPortInVector( self.df_port[ "Tie-1 Port" ]  ,"tie1"  , 1  )
    self.cPutPortInVector( self.df_port[ "Tie-0 Port" ]  ,"tie0"  , 0  )
    self.cPutPortInVector( self.df_port[ "Tie-X Port" ]  ,"tiex"  ,'x' )
    if ( self.name == "i2c" ):
        self.cPutPortInVector( self.df_port[ "I2C-SCL" ] ,"i2c-scl", 1 )
        self.cPutPortInVector( self.df_port[ "I2C-SDA" ] ,"i2c-sda", 1 )
    elif ( self.name == "spi" ):
        self.cPutPortInVector( self.df_port[ "SPI-SS"  ] ,"spi-ss" , 1 )
        self.cPutPortInVector( self.df_port[ "SPI-CLK" ] ,"spi-clk", 1 )
        self.cPutPortInVector( self.df_port[ "SPI-DI"  ] ,"spi-di" , 0 )
        self.cPutPortInVector( self.df_port[ "SPI-DO"  ] ,"spi-do" , 0 )
    elif ( self.name == "smi" ):
        self.cPutPortInVector( self.df_port[ "SMI-MDC" ] ,"smi-mdc"  , 1 )
        self.cPutPortInVector( self.df_port[ "SMI-MDIO"] ,"smi-mdio" , 1 )
    #----------Parse Port Data---------------------------------------------
    print( "[Info] The result parsed from xlsx is concluded below" )
    for p in self.vector:
        print("\tPort: %16s, Protocol = %10s, Value = %3s " % ( p.name, p.protocol, str(p.value) ) )
#----------------------------------------------------------------------------
def _GenATP( self ):
    sheet_list = []
    meet_start = False
    for sheet in self.excel.sheet_names:
        if  ( sheet == "_start" ):
            meet_start = True
            continue
        elif( sheet == "_end"   ):
            break
        if( meet_start ):
            sheet_list.append( sheet )

    if( len(sheet_list) == 0 ):
        print("[ERROR] No sheet is available. Maybe _start or _end sheet is placed in wrong order")
        exit(-1)

    for sheet_name in sheet_list:
       self.current_sheet = sheet_name
       print( "[INFO] Start Parsing Sheet: %s" % sheet_name )
       self.f = open( sheet_name + ".atp" , "w" )
       self.f.write( "import tset frcgen0;\n" )
       self.f.write( "vector \t( $tset, %s ) \n" % self.cGenVectorList() )
       self.f.write( "{\n" )
       self.f.write( "burst_start_0:\n" )
       self.cGenATP_Idle(10)
    #-----------Instruction from Excel---------------------------------------
       self.df_cmd = self.excel.parse( sheet_name )
       row_cnt = self.df_cmd.shape[0]
       for i in range( 0, row_cnt ):
           self.current_row = i
           cmd = self.df_cmd.iloc[i]
           #Check cmd format in xlsx
           cmd.DATA = str( cmd.DATA )

           if  ( cmd.COMMAND == "F" ):
               break
           elif( cmd.COMMAND in self.skip_cmd ) or ( pd.isna(cmd.COMMAND) )  or ( pd.isna(cmd.DATA ) ):
               continue
           elif( cmd.COMMAND == "D" ):
               self.cGenATP_Idle( int( cmd.DATA ) )
               continue
           elif( not check_CMD( cmd ) ):
               print("[Error] Invalid cmd format in row %d of sheet %s" % ( i, sheet_name) )
               exit(-1)

           self.cSet_RW_Format( cmd )
       self.f.write( "burst_stop_0: halt\n" )
       self.f.write( "}\n" )
       self.f.close()
       print( "[INFO] End   Parsing Sheet: %s" % sheet_name )
#---------------------------------------------------------------------
def _GenATPbyValue( self, note="" ):
    vtr = "\t\t\t>frcgen0 "
    for p in self.vector:
        vtr += str( p.value ) + " "
    note = "//%s" % note if note != "" else ""
    self.f.write( "%s; %s\n" % ( vtr, note) )  
#---------------------------------------------------------------------
def _GenATP_Idle( self, cnt ):
    #Reset
    for p in self.vector:
        p.value = p.ini_value
        
    
    for i in range(0,cnt):
        self.cGenATPbyValue( "Idle" )
#----------------------------------------------------------------------------
def _GenVectorList( self ):
    result = ""
    for p in self.vector:
        result += p.name
        if p != self.vector[-1]:
            result += ", "
    return result