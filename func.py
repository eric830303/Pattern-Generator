#---------------------------------------------------------------------
def isDataBinary( DATA ):
    assert type( DATA ) == str, "DATA should be present in string format"
    DATA = DATA.lower()
    length = len( DATA.replace( "_", "" ) )
    hex_list = [ "2", "3", "4", "5", "6", "7", "8", "9", "a", "b", "c", "d", "e", "f" ]
    if  ( DATA[0:2] != "0x" ) and ( DATA[0:2] != "0X"):
        return True#Bin
    elif( "_" in DATA ):
        return True#Bin
    elif( length > 10 ):
        return True#Bin
    else:
        for c in hex_list:
            if c in DATA:
                return False
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
#----------------------------------------------------------------------------
def isDataMoreThan16( DATA ):
    result = False
    if isDataBinary( DATA ):
        result = True if len( DATA ) > 16 else False
    #Hex
    else:
        length = len( bin( int( DATA, 16 ) )[2:] )
        result = True if length > 16 else False

    return result
