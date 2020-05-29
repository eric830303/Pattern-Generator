#---------------------------------------------------------------------
def isDataBinary( DATA ):
    assert type( DATA ) == str, "DATA should be present in string format"
    length = len( DATA.replace( "_", "" ) )
    
    if  ( DATA[0:2] != "0x" ) and ( DATA[0:2] != "0X"):
        return True
    elif( "_" in DATA ):
        return True
    elif( length == 16 ) or ( length == 32 ):
        return True
    else:
        return False #Hex
#----------------------------------------------------------------------------
def check_CMD( cmd ):
    result = True
    
    if( type(cmd.REGISTER) != str ):
        print("[Error] The reg addr must be present in string format")
        result = False
    elif( type(cmd.DATA) != str ):
        print("[Error] The reg value must be present in string format")
        result = False
    elif( "0x" not in cmd.REGISTER ):
        print("[Error] The reg addr must be present in hex, e.g., 0x...")
        result = False
    else:
        result = True
    if (not result):
        print("[Error] The folowing cmd cause error:")
        print( cmd )
    return result