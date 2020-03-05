#--------------------------------------------------------------------
#  Import API
#--------------------------------------------------------------------
import os
import pandas   as pd
import argparse as ag
import time     as t
from spi      import *
from i2c      import *
from smi      import *
from protocol import *
from func     import *
#---------------------------------------------------------------------
class converter:
    def __init__( self ):
        self.args        = ''
        self.unknown     = ''
        self.input       = ''
        self.intf        = ''
    #-----Parser-------------------------------------
    def cParseArgs( self ):
        _ParseArgs( self )
    def cRun( self ):
        _Run( self )
#----------------------------------------------------------------------------
def _ParseArgs( self ):
    print( t.asctime( t.localtime( t.time() ) ) )
    example = "\
    Example: \n\
    1. I2C \n\
    => python generator.py -input pattern.xlsx -i2c                       \n\
    => python generator.py -input pattern.xlsx -i2c -i2c_ctrlbyte 1010100 \n\
    2. SPI \n\
    => python generator.py -input pattern.xlsx -spi                       \n\
    => python generator.py -input pattern.xlsx -spi -spi_dummy 8          \n\
    2. SMI \n\
    => python generator.py -input pattern.xlsx -smi                       \n\
    => python generator.py -input pattern.xlsx -smi -smi_phy_adr 0x18     \n\
    "

    help_in    = "Your excel input"
    help_spi   = "Convert the SPI to ATP based on SPI protocol"
    help_i2c   = "Convert the I2C to ATP based on I2C protocol"
    help_smi   = "Convert the MDIO/MDC to ATP based on smi protocol"
    help_out   = "Specify your output ATP filename"
    help_ctrl  = "Specify your I2c ctrl byte, 1010100 at default."
    help_dummy = "Specify your SPI dummy cycle"
    parser     = ag.ArgumentParser( epilog=example, formatter_class=ag.RawTextHelpFormatter )
    parser.add_argument( "-input"               ,help=help_in        ,dest="infname"            ,default="" )
    parser.add_argument( "-spi"                 ,help=help_spi       ,dest="ifspi"              ,default=False          ,action="store_true")
    parser.add_argument( "-i2c"                 ,help=help_i2c       ,dest="ifi2c"              ,default=False          ,action="store_true")
    parser.add_argument( "-smi"                 ,help=help_smi       ,dest="ifsmi"              ,default=False          ,action="store_true")
    parser.add_argument( "-i2c_ctrlbyte"        ,help=help_ctrl      ,dest="ctrlbyte"           ,default="1010100")
    parser.add_argument( "-spi_dummy"           ,help=help_dummy     ,dest="dumycycle"          ,default=8              ,type=int)
    parser.add_argument( "-smi_phy_adr"         ,help=help_dummy     ,dest="phy_adr"            ,default="0x18")
    self.args, self.unknown = parser.parse_known_args()
    #----------------Checker------------------------------------------
    if ( self.args.infname == "" ):
        print( "[Error] Your input excel file is not specify by arg -input" )
        exit(-1)
    if   ( self.args.ifi2c ):
        self.intf = I2C( "i2c", True, self.args.infname )
        self.intf.ctrlbyte = self.args.ctrlbyte
    elif ( self.args.ifspi ):
        self.intf = SPI( "spi", True, self.args.infname )
        self.intf.dumycycle = self.args.dumycycle
    elif ( self.args.ifsmi ):
        self.intf = SMI( "smi", True, self.args.infname )
        self.intf.phy_addr = self.args.phy_adr
    else:
        print( "[Error] No protocol is specify. Please specify -spi, -i2c, or -smi." )
        exit(-1)
    #-------------------------------------------------------------------
    print( "[Setting] Input     : %s"    % self.args.infname )
    print( "[Setting] I2C -> ATP:" , self.args.ifi2c)
    print( "[Setting] SPI -> ATP:" , self.args.ifspi )
    print( "[Setting] SMI -> ATP:" , self.args.ifsmi )

def _Run( self ):
    self.intf.cParseDataFrame()
    self.intf.cGenATP()
    
if __name__ == '__main__':
    myconvt = converter()
    myconvt.cParseArgs()
    myconvt.cRun()
    
