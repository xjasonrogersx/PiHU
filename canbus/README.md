#CanBus

Mcp2515 CAN Bus Module TJA1050 Receiver SPI Module

![alt text](image.png)

The plan is to connect this to PI via

| MCP2515 Pin | Raspberry Pi Pin Name | Physical Pin Number | Function                                   |
| ----------- | --------------------- | ------------------- | ------------------------------------------ |
| VCC         | 3.3V Power            | Pin 17              | Powers the board with safe 3.3V logic      |
| GND         | Ground                | Pin 20 or 25        | Common Ground reference                    |
| CS          | SPI0 CE0 (GPIO 8)     | Pin 24              | Chip Select / Slave Select                 |
| SO (MISO)   | SPI0 MISO (GPIO 9)    | Pin 21              | Master In, Slave Out (Data to Pi)          |
| SI (MOSI)   | SPI0 MOSI (GPIO 10)   | Pin 19              | Master Out, Slave In (Data from Pi)        |
| SCK         | SPI0 SCLK (GPIO 11)   | Pin 23              | Serial Clock signal                        |
| INT         | GPIO 25               | Pin 22              | Hardware Interrupt (Tells Pi data arrived) |

![alt text](image-1.png)
