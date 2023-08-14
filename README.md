# Project Moltres

## Hardware

Microcontroller: Raspberry Pi 3B  
Sensor: Adafruit 1782 - MCP9808 breakout board

### Pinouts

Source: https://learn.adafruit.com/adafruit-mcp9808-precision-i2c-temperature-sensor-guide/pinouts

#### Sensor Pinout

![MCP 9808 pinout](https://cdn-learn.adafruit.com/assets/assets/000/015/726/large1024/adafruit_products_2.png?1396474366)

##### Power Pins

> VIN (VDD on header-only version) - This is the positive power and logic level pin. It can be 2.7-5.5VDC, so fine for use with 3 or 5V logic. Power VIN (VDD) with whatever logic level you plan to use on the i2c lines.

> GND - this is the ground power and logic reference pin.

##### I2C Data Pins

> SCL - this is the I2C clock pin. There's a 10K pull-up already on the board, so connect this directly to the i2c master clock pin on your microcontroller

> SDA - this is the I2C data pin. There's a 10K pull-up already on the board, so connect this directly to the i2c master data pin on your microcontroller

##### Optional Pins

> These are pins you don't need to connect to unless you want to!

> Alert - This is the interrupt/alert pin from the MCP9808. The chip has some capability to 'alert' you if the chip temperature goes above or below a set amount. This output can trigger to let you know. It is open collector so you need to use a pull-up resistor if you want to read signal from this pin.

> A0 (as well as A1 and A2 on the original version) - These are the address select pins. Since you can only have one device with a given address on an i2c bus, there must be a way to adjust the address if you want to put more than one MCP9808 on a shared i2c bus. The A0/A1/A2 pins set the bottom three bits of the i2c address. There are pull-down resistors on the board so connect them to VDD to set the bits to '1'. They are read on power up, so de-power and re-power to reset the address

**The default address is 0x18 and the address can be calculated by 'adding' the A0/A1/A2 to the base of 0x18**

> A0 sets the lowest bit with a value of 1, A1 sets the middle bit with a value of 2 and A2 sets the high bit with a value of 4. The final address is 0x18 + A2 + A1 + A0.  
> So for example if A2 is tied to VDD and A0 is tied to VDD, the address is 0x18 + 4 + 1 = 0x1D.  
> If only A0 is tied to VDD, the address is 0x18 + 1 = 0x19  
> If only A1 is tied to VDD, the address is 0x18 + 2 = 0x1A  
> If only A2 is tied to VDD, the address is 0x18 + 4 = 0x1C

#### Raspberry Pi Pinput

![Raspberry Pi Pinout](https://media.discordapp.net/attachments/1140663336996974623/1140663731022475304/image0.jpg)

#### Connection Plan

| Raspberry Pi     | MCP9808 | Digital Value |
| ---------------- | ------- | ------------- |
| Pin 4 (5V)       | Vdd     | 1             |
| Pin 6 (Ground)   | Gnd     | **0**         |
| Pin 8 (GPIO 14)  | SCL     | variable      |
| Pin 10 (GPIO 15) | SDA     | variable      |
| Pin 12 (GPIO 18) | Alert   | 0             |
| Pin 14 (Ground)  | A0      | **0**         |
| Pin 16 (GPIO 23) | A1      | 0             |
| Pin 18 (GPIO 24) | A2      | 0             |
