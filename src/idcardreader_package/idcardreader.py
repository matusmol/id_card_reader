import queue
import re
from datetime import datetime
from time import sleep

import pywinusb.hid as hid

GLOBAL = False
q = queue.Queue()
q.put([])


def sample_handler(data):
    global q
    global GLOBAL

    tuple_data = []
    empty_row = [0, 48, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    if data not in [empty_row]:
        for symbol in data:
            tuple_data.append(symbol)

        queue_data = q.get()
        queue_data.append(tuple_data[3:])
        q.put(queue_data)
        GLOBAL = True


def get_raw_data():
    error_code = 0
    exit_counter = 0
    ocr_reader = "DESKO GmbH Desk0 USB-Device"
    all_hids = hid.find_all_hid_devices()
    if all_hids:
        while True:
            for index, devices in enumerate(all_hids):

                device_name = str("{0.vendor_name} {0.product_name}" \
                                  "(vID=0x{1:04x}, pID=0x{2:04x})" \
                                  "".format(devices, devices.vendor_id, devices.product_id))

                if ocr_reader in device_name:
                    device = all_hids[index]
                    try:
                        device.set_raw_data_handler(sample_handler)
                        device.open()
                        global GLOBAL
                        while device.is_plugged():
                            exit_counter += 1
                            sleep(0.5)
                            if GLOBAL or exit_counter == 30:
                                GLOBAL = False
                                break
                    except:
                        error_code = 2
                    finally:

                        device.close()
                        return error_code
            else:
                error_code = 2
                return error_code
    else:
        print("There's not any non system HID class device available")
        error_code = 2
        return error_code


class IDScanner:
    def __init__(self, raw_data):
        self.raw_data = raw_data
        self.user_data = {}
        self.error_code = 0

    def converttostring(self, row):
        result = ""
        for chars in row:
            result += chr(chars)
        return result

    def parser_row1_P(self, row_string):
        try:

            match_group = re.search('[P][\w<]([\w<]{3})(\w*)<<(\w*).*', row_string)

            issuing_country = match_group.group(1).replace('<', '')
            last_name = match_group.group(2).replace('<', '')
            first_name = match_group.group(3).replace('<', '')

            self.user_data['issuing_country'] = issuing_country
            self.user_data['last_name'] = last_name
            self.user_data['first_name'] = first_name

        except Exception as e:
            raise

    def parser_row2_P(self, row_string):
        try:
            match_group = re.search('([\w<]{9})[\d]([\w<]{3})([\d]{6})[\d]([MF<])([\d]{6})[\d]([\d]*).*', row_string)

            document_id = match_group.group(1).replace('<', '')
            country = match_group.group(2).replace('<', '')
            date_birth = match_group.group(3).replace('<', '')
            sex = match_group.group(4).replace('<', '')
            date_expiration = match_group.group(5).replace('<', '')
            personal_id = match_group.group(6).replace('<', '')

            date_birth_datetime = datetime.strptime(date_birth, '%y%m%d')
            date_expiration_datetime = datetime.strptime(date_expiration, '%y%m%d')

            self.user_data['document_id'] = document_id
            self.user_data['date_birth'] = date_birth_datetime
            self.user_data['sex'] = sex
            self.user_data['date_expiration'] = date_expiration_datetime
            self.user_data['country'] = country
            self.user_data['personal_id'] = personal_id

        except Exception as e:
            print(e)
            raise

    def parser_row1_ID(self, row_string):
        try:

            match_group = re.search('[IAC][\w<]([\w<]{3})([\w<]{9})[\d<]([\w<]{10}).*', row_string)

            issuing_country = match_group.group(1).replace('<', '')
            document_id = match_group.group(2).replace('<', '')
            personal_id = match_group.group(3).replace('<', '')

            self.user_data['issuing_country'] = issuing_country
            self.user_data['document_id'] = document_id
            self.user_data['personal_id'] = personal_id


        except Exception as e:
            print(e)
            raise

    def parser_row2_ID(self, row_string):
        try:
            match_group = re.search('([\d]{6})\d([MF<])([\d]{6})[\d<]([\w<]{3}).*', row_string)

            date_birth = match_group.group(1).replace('<', '')
            sex = match_group.group(2).replace('<', '')
            date_expiration = match_group.group(3).replace('<', '')
            country = match_group.group(4).replace('<', '')

            date_birth_datetime = datetime.strptime(date_birth, '%y%m%d')
            date_expiration_datetime = datetime.strptime(date_expiration, '%y%m%d')

            self.user_data['date_birth'] = date_birth_datetime
            self.user_data['sex'] = sex
            self.user_data['date_expiration'] = date_expiration_datetime
            self.user_data['country'] = country

        except Exception as e:
            print(e)
            raise

    def parser_row3_ID(self, row_string):
        try:

            match_group = re.search('(\w*)<<(\w*).*', row_string)

            last_name = match_group.group(1).replace('<', '')
            first_name = match_group.group(2).replace('<', '')

            self.user_data['last_name'] = last_name
            self.user_data['first_name'] = first_name

        except Exception as e:
            raise

    def parse_data(self):
        try:
            row1 = self.raw_data[1]
            row2 = self.raw_data[2]

            document_type = row1[0]
            self.user_data['document_type'] = document_type

            if document_type == "P":
                # PASSPORT
                self.parser_row1_P(row1)
                self.parser_row2_P(row2)

            elif document_type == "I":
                # ID
                row3 = self.raw_data[3]

                self.parser_row1_ID(row1)
                self.parser_row2_ID(row2)
                self.parser_row3_ID(row3)
            else:
                self.error_code = 1

        except Exception as e:
            self.error_code = 1

    def get_data(self):
        return self.user_data

    def get_error_code(self):
        return self.error_code


def createBoudle(raw_data):
    result = []

    for data in raw_data:
        result += data

    return result


def getImportantData(raw_data):
    start_text = raw_data.index(2) + 1
    end_text = raw_data.index(3)

    return raw_data[start_text:end_text]


def splitToLineAndConvert(raw_data):
    result = {}
    line = ""
    counter = 1

    for char in raw_data:
        if char == 13:
            result[counter] = line
            counter += 1
            line = ""
            continue
        line += chr(char)

    return result


def decodeRawData(raw_data):
    raw_data = createBoudle(raw_data)
    raw_data = getImportantData(raw_data)
    lined_data = splitToLineAndConvert(raw_data)

    return lined_data


def get_user_data():
    data = {}
    try:
        error_value = get_raw_data()

        if error_value == 0:
            raw_data = q.get()

            result = decodeRawData(raw_data)

            id_scanner = IDScanner(result)
            id_scanner.parse_data()

            error_value = id_scanner.get_error_code()
            data = id_scanner.get_data()

    except Exception as e:
        print("ERROR {}".format(e))
        error_value = 2

    return data, error_value
