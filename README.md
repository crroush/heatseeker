# Decoding the IRG format from the TC004
First special thanks to Terence Eden and his
[blog](https://shkspr.mobi/blog/2023/02/reverse-engineering-the-irg-infrared-thermal-imaging-format-help-needed/)
The work done by him and others helped me get started with the project.  

# Mostly decoded IRG format
| Bytes (Hex) | Description             | Type   | Notes                   |
|-------------|-------------------------|--------|-------------------------|
| 0x00-0x03   | Unknown Header          |        |                         |
| 0x04-0x07   | First Image Size        | uint32 |                         |
| 0x08-0x09   | First Image Width       |  uint8 |                         |
| 0x0A-0x0B   | First Image Height      |  uint8 |                         |
| 0x0C        | Pad                     |        |                         |
| 0x0D-0x10   | Second Image Size       | uint32 |                         |
| 0x11-0x12   | Second Image Width      |  uint8 |                         |
| 0x13-0x14   | Second Image Height     |  uint8 |                         |
| 0x15        | Pad                     |        |                         |
| 0x16-0x19   | Third Image Size        | uint32 | Total number elements   |
| 0x1A-0x1B   | Third Image Width       |  uint8 |                         |
| 0x1C-0x1D   | Third Image Height      |  uint8 |                         |
| 0x1E-0x21   | Emissivity              | uint32 | divide by 10000         |
| 0x22-0x25   | Reflective Temp (K)     | uint32 | divide by 10000         |
| 0x26-0x29   | Ambient Temp (K)        | uint32 | divide by 10000         |
| 0x2A-0x2D   | Distance (meters)       | uint32 | divide by 10000         |
| 0x2E-0x31   | Unknown                 |        | Value is 4000?          |
| 0x32-0x33   | Transmissivity          | uint32 | divide by 10000         |
| 0x34-0x37   | Padding                 |        |                         |
| 0x38-0x3B   | Unknown                 | uint16 | Value is 10000,maybe lsb|
| 0x3B-0x41   | Padding                 |        |                         |
| 0x42        | Temperature unit 0,1,2  |  uint8 | Enum: 0:°C, 1:°K, 2:°F  |
| 0x43-0xFD   | Padding??               |        |                         |
| 0xFE        | 0xAC? or 0x0?           |        | if 0xFE/FF data offset  |
| 0xFF        | 0xCA? or 0x0?           |        | data is at 0x100,or 0x120|
| 0x100       | First image black/white |  uint8 | size from 0x04-0x07     |
| prev  + size| Thermal Image (K)       |  uint16| divide by 10            |
| prev  + size| JPG (until end of file? |  uint8 | always green?           |

Couple of notes is the ICD isn't 100% complete, but it captures how you can read
the basic data format.  Couple notes is from others that dug into this, is there
is two different starting locations for the first image.  I also only own a
TC004 so I am limited to IRG formats that I can test.
# Example
Here is the original jpg file I pulled off the TC004 of my dogs sitting on the couch
![231022095408](https://github.com/crroush/heatseeker/assets/9982203/5261b108-a047-4aa9-a080-302a278f40a2)

Now here is after running the `python python/extract_irg.py /path/to/my/irg/file`
![image](https://github.com/crroush/heatseeker/assets/9982203/89d1b418-990b-4320-b671-896c31df21da)


