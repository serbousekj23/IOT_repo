# Ulozit jako: pico_i2c_lcd.py
import time
from lcd_api import LcdApi

class I2cLcd(LcdApi):
    def __init__(self, i2c, i2c_addr, num_lines, num_columns):
        self.i2c = i2c
        self.i2c_addr = i2c_addr
        time.sleep_ms(20)
        self.hal_write_init_nibble(0x03)
        time.sleep_ms(5)
        self.hal_write_init_nibble(0x03)
        time.sleep_ms(1)
        self.hal_write_init_nibble(0x03)
        time.sleep_ms(1)
        self.hal_write_init_nibble(0x02)
        time.sleep_ms(1)
        self.hal_write_command(0x28)
        self.hal_write_command(0x0C)
        self.hal_write_command(0x06)
        self.clear()
        super().__init__(num_lines, num_columns)

    def hal_write_init_nibble(self, nibble):
        byte = ((nibble >> 4) & 0x0F) << 4
        self.i2c.writeto(self.i2c_addr, bytes([byte | 0x04 | 0x08]))
        self.i2c.writeto(self.i2c_addr, bytes([byte | 0x08]))

    def hal_backlight_on(self):
        self.i2c.writeto(self.i2c_addr, bytes([0x08]))

    def hal_write_command(self, cmd):
        byte = (cmd & 0xF0) | 0x08
        self.i2c.writeto(self.i2c_addr, bytes([byte | 0x04]))
        self.i2c.writeto(self.i2c_addr, bytes([byte]))
        byte = ((cmd << 4) & 0xF0) | 0x08
        self.i2c.writeto(self.i2c_addr, bytes([byte | 0x04]))
        self.i2c.writeto(self.i2c_addr, bytes([byte]))

    def hal_write_data(self, data):
        byte = (data & 0xF0) | 0x08 | 0x01
        self.i2c.writeto(self.i2c_addr, bytes([byte | 0x04]))
        self.i2c.writeto(self.i2c_addr, bytes([byte]))
        byte = ((data << 4) & 0xF0) | 0x08 | 0x01
        self.i2c.writeto(self.i2c_addr, bytes([byte | 0x04]))
        self.i2c.writeto(self.i2c_addr, bytes([byte]))