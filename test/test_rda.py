import unittest

import rda
import a6

class TestEscaper(unittest.TestCase):
    def test_escaper(self):
        self.assertEqual(rda.escaper(b''), bytes())
        self.assertEqual(rda.escaper(bytes([0x00])), bytes([0x00]))
        self.assertEqual(rda.escaper(bytes([0x11])), bytes([0x5C,0xEE]))
        self.assertEqual(rda.escaper(bytes([0x13])), bytes([0x5C,0xEC]))
        self.assertEqual(rda.escaper(bytes([0x5C])), bytes([0x5C,0xA3]))


    def test_unescaper(self):
        self.assertEqual(a6.unescaper(b''), bytes())
        self.assertEqual(a6.unescaper(bytes([0x00])), bytes([0x00]))
        self.assertEqual(a6.unescaper(bytes([0x5C, 0xEE])), bytes([0x11]))
        self.assertEqual(a6.unescaper(bytes([0x5C, 0xEC])), bytes([0x13]))
        self.assertEqual(a6.unescaper(bytes([0x5C, 0xA3])), bytes([0x5C]))

class TestRdaDebugFrame(unittest.TestCase):
    def test_compute_check(self):
        self.assertEqual(a6.compute_check(b''), bytes([0x00]))
        self.assertEqual(a6.compute_check(bytes([0x00])), bytes([0x00]))
        self.assertEqual(a6.compute_check(bytes([0x00])), bytes([0x00]))
        self.assertEqual(a6.compute_check(bytes([0x00,0xff])), bytes([0xff]))
        self.assertEqual(a6.compute_check(bytes([0x01,0x02])), bytes([0x03]))
        self.assertEqual(a6.compute_check(bytes([0x01,0x02,0xff])), bytes([0xfc]))
        self.assertEqual(a6.compute_check(bytes([0xff,0x80,0x01])), bytes([0x7e]))

    def test_rda_debug_frame(self):
        self.assertEqual(a6.rda_debug_frame(bytes([0xFF]), bytes([0x00]), bytes([0x10,0x00,0x00,0x82,0x01])),
                         bytes([0xad,0x00,0x07,0xff,0x00,0x10,0x00,0x00,0x82,0x01, 0x6c]))
        self.assertEqual(a6.rda_debug_frame(bytes([0xFF]), bytes([0x02]), bytes([0x10,0x00,0x00,0x82,0x01])),
                         bytes([0xad,0x00,0x07,0xff,0x02,0x10,0x00,0x00,0x82,0x01, 0x6e]))

    def test_read_word(self):
        self.assertEqual(a6.read_word(0x82000010, 1), bytes([0xad,0x00,0x07,0xff,0x02,0x10,0x00,0x00,0x82,0x01, 0x6e]))

    def test_write_block(self):
        self.assertEqual(a6.write_block(0x82000010, bytes.fromhex('aabbccdd')), bytes.fromhex('ad000aff8310000082aabbccddee'))


class TestA6Commands(unittest.TestCase):
    def test_h2p_command(self):
        self.assertEqual(a6.h2p_command(0x00), bytes.fromhex('ad0007ff8405000000007e'))
        self.assertEqual(a6.h2p_command(0xa5), bytes.fromhex('ad0007ff8405000000a5db'))

    def test_set_uart_to_host(self):
        self.assertEqual(a6.set_uart_to_host(), bytes.fromhex('ad0007ff840300000080f8'))

    def test_read_uart_to_host(self):
        self.assertEqual(a6.read_uart_to_host(), bytes.fromhex('ad0007ff040300000001f9'))

    def test_ate_command(self):
        self.assertEqual(a6.ate_command('AT+DMOCONNECT', 0x8201ff9c), bytes.fromhex('ad0016ff839cff01820000b7'))

    def test_cps_command(self):
        self.assertEqual(a6.cps_command(bytes.fromhex('002b'), 0x8201ff9c), bytes.fromhex('ad0007ff040300000001f9'))




if __name__ == '__main__':
    unittest.main()
