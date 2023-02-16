import datetime
import logging
import unittest
from ski.coordinate import DMSCoordinate
import ski.gsd as undertest

undertest.log.setLevel(logging.DEBUG)


class MockedFile():

    def __init__(self, data) -> None:
        self.data = data
        self.index = 0

    def readline(self) -> str:
        if self.index >= len(self.data):
            return None
        line = self.data[self.index]
        self.index += 1
        return line
    
    def seek(self, index) -> None:
        self.index = index
    
    def write(self, line:str) -> None:
        self.data.append(line)


class TestGsdFileFormatPointsLine(unittest.TestCase):

    def test_format_points_line_invalid_line(self):
        point = ['value1', 'value2', 'value3', 'value4', 'value5']
        self.assertIsNone(undertest.GSDFile.format_points_line(point))

    def test_format_points_line_valid_line(self):
        point = ['value1', 'value2', 'value3', 'value4', 'value5', 'value6']
        self.assertEqual('value1,value2,value3,value4,value5,value6', undertest.GSDFile.format_points_line(point))


class TestGsdFileIsBlank(unittest.TestCase):

    def test_is_blank_empty_string(self):
        self.assertTrue(undertest.GSDFile.is_blank(''))

    def test_is_blank_none(self):
        self.assertTrue(undertest.GSDFile.is_blank(None))

    def test_is_blank_not_a_string(self):
        self.assertFalse(undertest.GSDFile.is_blank(123))

    def test_is_blank_string(self):
        self.assertFalse(undertest.GSDFile.is_blank('x'))


class TestGsdFileIsEof(unittest.TestCase):

    def test_is_eof_newline(self):
        self.assertFalse(undertest.GSDFile.is_eof('\n'))

    def test_is_eof_none(self):
        self.assertTrue(undertest.GSDFile.is_eof(None))

    def test_is_eof_string(self):
        self.assertFalse(undertest.GSDFile.is_eof('x'))

    def test_is_eof_stripped_newline(self):
        self.assertTrue(undertest.GSDFile.is_eof('\n'.strip()))
    

class TestGsdFileIsSectionHeader(unittest.TestCase):

    def test_is_section_header_empty_string(self):
        self.assertFalse(undertest.GSDFile.is_section_header(''))

    def test_is_section_header_none(self):
        self.assertFalse(undertest.GSDFile.is_section_header(None))

    def test_is_section_header_not_a_string(self):
        self.assertFalse(undertest.GSDFile.is_section_header(123))

    def test_is_section_header_string(self):
        self.assertFalse(undertest.GSDFile.is_section_header('x'))

    def test_is_section_header_valid_header(self):
        self.assertTrue(undertest.GSDFile.is_section_header('[x]'))


class TestGsdFileParseHeaderLine(unittest.TestCase):

    def test_parse_header_invalid_line(self):
        result = undertest.GSDFile.parse_header_line('001,test_header')
        self.assertIsNone(result)

    def test_parse_header_line_none(self):
        self.assertIsNone(undertest.GSDFile.parse_header_line(None))

    def test_parse_header_line_valid_line(self):
        index, name = undertest.GSDFile.parse_header_line('1=001,test_header')
        self.assertEqual(1, index, 'index')
        self.assertEqual('test_header', name, 'name')


class TestGsdFileParsePointsLine(unittest.TestCase):

    def test_parse_points_line_invalid_line(self):
        result = undertest.GSDFile.parse_points_line('01=value1,value2,value3,value4,value5')
        self.assertIsNone(result)

    def test_parse_points_line_none(self):
        self.assertIsNone(undertest.GSDFile.parse_points_line(None))

    def test_parse_points_line_valid_line(self):
        result = undertest.GSDFile.parse_points_line('01=value1,value2,value3,value4,value5,value6')
        self.assertListEqual(['value1', 'value2', 'value3', 'value4', 'value5', 'value6'], result)

    def test_parse_points_line_valid_line_more_than_6_elements(self):
        result = undertest.GSDFile.parse_points_line('01=value1,value2,value3,value4,value5,value6,value7')
        self.assertListEqual(['value1', 'value2', 'value3', 'value4', 'value5', 'value6'], result)
    

class TestGsdFileParseSectionName(unittest.TestCase):

    def test_parse_section_name_none(self):
        self.assertEqual((None, None), undertest.GSDFile.parse_section_name(None))

    def test_parse_section_name_numeric_index(self):
        result = undertest.GSDFile.parse_section_name('[001,2018-02-15:16:16:55]')
        self.assertEqual((1, '2018-02-15:16:16:55'), result)

    def test_parse_section_name_string_index(self):
        result = undertest.GSDFile.parse_section_name('[abc,2018-02-15:16:16:55]')
        self.assertEqual(('abc', '2018-02-15:16:16:55'), result)

    def test_parse_section_name_valid_name_without_index(self):
        result = undertest.GSDFile.parse_section_name('[TP]')
        self.assertEqual((None, 'TP'), result)


class TestGsdFileLoadGsdHeader(unittest.TestCase):

    def test_load_gsd_header_to_next_section(self):
        f = MockedFile(data=['[TP]\n', '\n', '1=001,2018-02-15:16:16:55\n', '\n', '2=002,2018-02-15:16:29:23\n', '\n', '[Next]\n'])
        gsd = undertest.GSDFile(f, load_header=False)
        gsd.load_gsd_header()
        self.assertListEqual([(1,'2018-02-15:16:16:55'), (2,'2018-02-15:16:29:23')], gsd.sections)

    def test_load_gsd_header_to_eof(self):
        f = MockedFile(data=['[TP]\n', '\n', '1=001,2018-02-15:16:16:55\n', '\n', '2=002,2018-02-15:16:29:23\n'])
        gsd = undertest.GSDFile(f, load_header=False)
        gsd.load_gsd_header()
        self.assertListEqual([(1,'2018-02-15:16:16:55'), (2,'2018-02-15:16:29:23')], gsd.sections)

    def test_load_gsd_header_tp_not_found(self):
        f = MockedFile(data=['\n', '1=001,2018-02-15:16:16:55\n', '\n', '2=002,2018-02-15:16:29:23'])
        gsd = undertest.GSDFile(f, load_header=False)
        self.assertRaises(EOFError, lambda: gsd.load_gsd_header())

    def test_load_gsd_header_with_invalid_header(self):
        f = MockedFile(data=['[TP]\n', '\n', '1=001,2018-02-15:16:16:55\n', '\n', '002,2018-02-15:16:29:23\n'])
        gsd = undertest.GSDFile(f, load_header=False)
        gsd.load_gsd_header()
        self.assertListEqual([(1,'2018-02-15:16:16:55')], gsd.sections)


class TestGsdFileLoadGsdPoints(unittest.TestCase):

    def test_load_gsd_points_named_section_to_next_section(self):
        f = MockedFile(data=['[Test]\n', '\n', '1=39531388,-105457814,161655,150218,180,27760000\n', '\n', '2=39531308,-105457804,161720,150218,120,27760000\n', '\n', '3=39531339,-105457776,161730,150218,260,27780000\n', '\n', '[Next]\n'])
        gsd = undertest.GSDFile(f, load_header=False)
        output = gsd.load_gsd_points(section_name='Test')
        self.assertListEqual([['39531388','-105457814','161655','150218','180','27760000'], ['39531308','-105457804','161720','150218','120','27760000'], ['39531339','-105457776','161730','150218','260','27780000']], output)

    def test_load_gsd_points_named_section_to_eof(self):
        f = MockedFile(data=['[Test]\n', '\n', '1=39531388,-105457814,161655,150218,180,27760000\n', '\n', '2=39531308,-105457804,161720,150218,120,27760000\n', '\n', '3=39531339,-105457776,161730,150218,260,27780000\n', ''])
        gsd = undertest.GSDFile(f, load_header=False)
        output = gsd.load_gsd_points(section_name='Test')
        self.assertListEqual([['39531388','-105457814','161655','150218','180','27760000'], ['39531308','-105457804','161720','150218','120','27760000'], ['39531339','-105457776','161730','150218','260','27780000']], output)

    def test_load_gsd_points_named_section_not_found(self):
        f = MockedFile(data=['\n', '1=39531388,-105457814,161655,150218,180,27760000\n', '\n', '2=39531308,-105457804,161720,150218,120,27760000\n', '\n', '3=39531339,-105457776,161730,150218,260,27780000\n'])
        gsd = undertest.GSDFile(f, load_header=False)
        self.assertRaises(EOFError, lambda: gsd.load_gsd_points('Test'))

    def test_load_gsd_points_next_section_to_eof(self):
        f = MockedFile(data=['\n', '1=39531388,-105457814,161655,150218,180,27760000\n', '\n', '2=39531308,-105457804,161720,150218,120,27760000\n', '\n', '3=39531339,-105457776,161730,150218,260,27780000\n', ''])
        gsd = undertest.GSDFile(f, load_header=False)
        output = gsd.load_gsd_points()
        self.assertListEqual([['39531388','-105457814','161655','150218','180','27760000'], ['39531308','-105457804','161720','150218','120','27760000'], ['39531339','-105457776','161730','150218','260','27780000']], output)

    def test_load_gsd_points_with_invalid_point(self):
        f = MockedFile(data=['[Test]\n', '\n', '1=39531388,-105457814,161655,150218,180,27760000\n', '\n', '2=39531308,-105457804,161720,150218,120\n', '\n', '3=39531339,-105457776,161730,150218,260,27780000\n'])
        gsd = undertest.GSDFile(f, load_header=False)
        output = gsd.load_gsd_points(section_name='Test')
        self.assertListEqual([['39531388','-105457814','161655','150218','180','27760000'], ['39531339','-105457776','161730','150218','260','27780000']], output)


class TestGsdFileWriteSection(unittest.TestCase):

    def test_write_section_single_entry(self):
        f = MockedFile([])
        gsd = undertest.GSDFile(f, load_header=False)
        gsd.write_section('Test Section', entries=['Test entry'])
        self.assertListEqual(['[Test Section]', '', '1=Test entry', ''], f.data)

    def test_write_section_multiple_entries(self):
        f = MockedFile([])
        gsd = undertest.GSDFile(f, load_header=False)
        gsd.write_section('Test Section', entries=['Test entry 1', 'Test entry 2'])
        self.assertListEqual(['[Test Section]', '', '1=Test entry 1', '', '2=Test entry 2', ''], f.data)

    def test_write_section_points(self):
        f = MockedFile([])
        gsd = undertest.GSDFile(f, load_header=False)
        gsd.write_section('Test Section', points=[['a','b','c','d','e','f']])
        self.assertListEqual(['[Test Section]', '', '1=a,b,c,d,e,f', ''], f.data)


class TestConvertGsdAlt(unittest.TestCase):

    def test_convert_alt(self):
        self.assertEqual(12, undertest.convert_gsd_alt('123456'))

    def test_convert_alt_not_number(self):
        self.assertEqual(0, undertest.convert_gsd_alt('1234ab'))


class TestConvertGsdCoord(unittest.TestCase):

    def test_convert_coord_7digits(self):
        coord = undertest.convert_gsd_coord('9531388')
        self.assertEqual(9, coord[0], 'Degrees')
        self.assertEqual(53, coord[1], 'Minutes')
        self.assertAlmostEqual(0.1388 * 60.0, coord[2], msg='Seconds')
        self.assertIsNotNone(DMSCoordinate(*coord, 0, 0, 0), 'Parses as latitude')

    def test_convert_coord_7digits_signed(self):
        coord = undertest.convert_gsd_coord('-9531388')
        self.assertEqual(-9, coord[0], 'Degrees')
        self.assertEqual(53, coord[1], 'Minutes')
        self.assertAlmostEqual(0.1388 * 60.0, coord[2], msg='Seconds')
        self.assertIsNotNone(DMSCoordinate(*coord, 0, 0, 0), 'Parses as latitude')

    def test_convert_coord_8digits(self):
        coord = undertest.convert_gsd_coord('39531388')
        self.assertEqual(39, coord[0], 'Degrees')
        self.assertEqual(53, coord[1], 'Minutes')
        self.assertAlmostEqual(0.1388 * 60.0, coord[2], msg='Seconds')
        self.assertIsNotNone(DMSCoordinate(*coord, 0, 0, 0), 'Parses as latitude')

    def test_convert_coord_8digits_signed(self):
        coord = undertest.convert_gsd_coord('-39531388')
        self.assertEqual(-39, coord[0], 'Degrees')
        self.assertEqual(53, coord[1], 'Minutes')
        self.assertAlmostEqual(0.1388 * 60.0, coord[2], msg='Seconds')
        self.assertIsNotNone(DMSCoordinate(*coord, 0, 0, 0), 'Parses as latitude')

    def test_convert_coord_10digits_signed(self):
        coord = undertest.convert_gsd_coord('-105457814')
        self.assertEqual(-105, coord[0], 'Degrees')
        self.assertEqual(45, coord[1], 'Minutes')
        self.assertAlmostEqual(0.7814 * 60.0, coord[2], msg='Seconds')
        self.assertIsNotNone(DMSCoordinate(0, 0, 0, *coord), 'Parses as longitude')

    def test_convert_coord_not_number(self):
        self.assertIsNone(undertest.convert_gsd_coord('123456ab'))


class TestConvertGsdDate(unittest.TestCase):

    def test_convert_date(self):
        date = undertest.convert_gsd_date('011020', '091011')
        self.assertEqual(2020, date.year, 'Year')
        self.assertEqual(10, date.month, 'Month')
        self.assertEqual(1, date.day, 'Day')
        self.assertEqual(9, date.hour, 'Hour')
        self.assertEqual(10, date.minute, 'Minute')
        self.assertEqual(11, date.second, 'Second')

    def test_convert_date_date_not_number(self):
        self.assertIsNone(undertest.convert_gsd_date('1234ab', '091011'))

    def test_convert_date_time_not_number(self):
        self.assertIsNone(undertest.convert_gsd_date('011020', '091011ab'))

    def test_convert_date_date_invalid(self):
        self.assertIsNone(undertest.convert_gsd_date('987654', '091011'))

    def test_convert_date_time_invalid(self):
        self.assertIsNone(undertest.convert_gsd_date('011020', '234567'))


class TestConvertGsdSpeed(unittest.TestCase):

    def test_convert_speed(self):
        self.assertEqual(12.34, undertest.convert_gsd_speed('1234'))

    def test_convert_speed_not_number(self):
        self.assertEqual(0, undertest.convert_gsd_speed('1234ab'))


class TestBuildGroupHeader(unittest.TestCase):
    
    def test_build_header_from_dt(self):
        points = [{'dt': datetime.datetime(2018, 2, 15, 16, 16, 55)}]
        result = undertest.build_group_header(points)
        self.assertEqual('001,2018-02-15-16:16:55', result)

    def test_build_header_from_ts(self):
        points = [{'ts': 1518711415}]
        result = undertest.build_group_header(points)
        self.assertEqual('001,2018-02-15-16:16:55', result)

    def test_build_header_from_gsd(self):
        points = [['0', '0', '161655', '150218', '0', '0']]
        result = undertest.build_group_header(points)
        self.assertEqual('001,2018-02-15-16:16:55', result)

    def test_build_header_none(self):
        points = [{}]
        result = undertest.build_group_header(points)
        self.assertIsNone(result)

    def test_build_header_empty_list(self):
        points = []
        result = undertest.build_group_header(points)
        self.assertIsNone(result)


class TestGroupPoints(unittest.TestCase):

    def test_group_points_single_group(self):
        points = [x for x in range(1, 10)]
        result = list(undertest.group_points(points,section_size=20))
        self.assertEqual(1, len(result))

    def test_group_points_multiple_group(self):
        points = [x for x in range(1, 10)]
        result = list(undertest.group_points(points, section_size=5))
        self.assertEqual(2, len(result))


class TestWriteGsd(unittest.TestCase):

    def test_write_gsd(self):
        f = MockedFile([])
        data = [['39531388','-105457814','161655','150218','180','27760000']]
        undertest.write_gsd(f, data)
        self.assertEqual('[Date]', f.readline(), 'Line 1')
        self.assertEqual('', f.readline(), 'Line 2')
        self.assertIsNotNone(f.readline(), 'Line 3')
        self.assertEqual('', f.readline(), 'Line 4')
        
        self.assertEqual('[TP]', f.readline(), 'Line 5')
        self.assertEqual('', f.readline(), 'Line 6')
        self.assertEqual('1=001,2018-02-15-16:16:55', f.readline(), 'Line 7')
        self.assertEqual('', f.readline(), 'Line 8')
        
        self.assertEqual('[001,2018-02-15-16:16:55]', f.readline(), 'Line 9')
        self.assertEqual('', f.readline(), 'Line 10')
        self.assertEqual('1=39531388,-105457814,161655,150218,180,27760000', f.readline(), 'Line11')
        self.assertEqual('', f.readline(), 'Line 12')

    def test_write_gsd_from_generator(self):
        f = MockedFile([])
        data = [
            ['39531388','-105457814','161655','150218','180','27760000'],
            ['39531308','-105457804','161720','150218','120','27760000']
        ]
        undertest.write_gsd(f, (x for x in data))
        self.assertEqual('[Date]', f.readline(), 'Line 1')
        self.assertEqual('', f.readline(), 'Line 2')
        self.assertIsNotNone(f.readline(), 'Line 3')
        self.assertEqual('', f.readline(), 'Line 4')
        
        self.assertEqual('[TP]', f.readline(), 'Line 5')
        self.assertEqual('', f.readline(), 'Line 6')
        self.assertEqual('1=001,2018-02-15-16:16:55', f.readline(), 'Line 7')
        self.assertEqual('', f.readline(), 'Line 8')
        
        self.assertEqual('[001,2018-02-15-16:16:55]', f.readline(), 'Line 9')
        self.assertEqual('', f.readline(), 'Line 10')
        self.assertEqual('1=39531388,-105457814,161655,150218,180,27760000', f.readline(), 'Line11')
        self.assertEqual('', f.readline(), 'Line 12')