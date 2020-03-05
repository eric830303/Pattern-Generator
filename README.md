# ATP Generator
The Python-based script is used to convert an Excel to input vectors (ATP files), for testing chips.
The protocol supported by the script:
- I2C
- SPI
- SMI (MDC/MDIO)

## Installation

It requires [Python](https://www.python.org/downloads/) v3.7+ and [Pandas](https://pandas.pydata.org/) to run.
No need to intall them individually. It is recommended to install [Anaconda](https://www.anaconda.com/distribution/), which has involved both of them.

## Run on Windows
Launch your Windows prompt and enter the directory where the script is located.
#### Help 
```zsh
$ python generator.py -h
```
#### I2C
Convert the Excel file based on I2C protocol
```sh
$ python generator.py -i2c -input pattern_example.xlsx
```
Convert the Excel file based on I2C protocol, with the specified output filename and the specified 5-bit control byte in binary format
```sh
$ python generator.py -i2c -input pattern_example.xlsx -ctrlbyte 1010111
```
#### SPI
Convert the Excel file based on SPI protocol
```sh
$ python generator.py -spi -input pattern_example.xlsx
```
Convert the Excel file based on SPI protocol, with the specified dummy cycle count
```sh
$ python generator.py -spi -input pattern_example.xlsx -spi_dummy 8
```
#### SMI (MDC/MDIO)
Convert the Excel file based on SMI protocol
```sh
$ python generator.py -smi -input pattern_example.xlsx
```
Convert the Excel file based on SMI protocol, with the specified PHY Addr, which cannot be more than 5 bits and must be present in hex format.
```sh
$ python generator.py -smi -input pattern_example.xlsx -smi_phy_adr 0x18
```




