import os
import tempfile
import unittest

import qrcode

from core.CryptoTypes import Signature
from core.QrSignatureStorage import QrSignatureStorage
from tests.test.NemTestUtils import NemTestUtils

# (32 + 64*X) * 8/5 > 1852 [version 40, max]; X = 18
# https://www.qrcode.com/en/about/version.html
MAX_SIGNATURES_PER_QRCODE = 17


def write_random_qrcode(directory, name, data_size):
    # this works because transaction_hash size is not checked
    QrSignatureStorage(directory).save(name, NemTestUtils.randbytes(data_size), [])


class QrSignatureStorageTest(unittest.TestCase):
    # region save

    def _assert_can_save_signatures(self, num_signatures):
        # Arrange:
        with tempfile.TemporaryDirectory() as temp_directory:
            storage = QrSignatureStorage(temp_directory)

            transaction_hash = NemTestUtils.randbytes(32)
            signatures = [Signature(NemTestUtils.randbytes(64)) for _ in range(0, num_signatures)]

            # Act:
            storage.save('foo', transaction_hash, signatures)

            # Assert:
            self.assertEqual(1, len(os.listdir(temp_directory)))
            self.assertTrue(os.path.exists(os.path.join(temp_directory, 'foo.png')))

    def test_can_save_zero_signatures(self):
        self._assert_can_save_signatures(0)

    def test_can_save_single_signature(self):
        self._assert_can_save_signatures(1)

    def test_can_save_multiple_signatures(self):
        self._assert_can_save_signatures(5)

    def test_can_save_max_signatures(self):
        self._assert_can_save_signatures(MAX_SIGNATURES_PER_QRCODE)

    def test_cannot_save_more_than_allowable_number_of_signatures(self):
        # Arrange:
        with tempfile.TemporaryDirectory() as temp_directory:
            storage = QrSignatureStorage(temp_directory)

            transaction_hash = NemTestUtils.randbytes(32)
            signatures = [Signature(NemTestUtils.randbytes(64)) for _ in range(0, MAX_SIGNATURES_PER_QRCODE + 1)]

            # Act + Assert:
            with self.assertRaises(qrcode.exceptions.DataOverflowError):
                storage.save('foo', transaction_hash, signatures)

    # endregion

    # region load

    def _assert_can_roundtrip_signatures(self, num_signatures):
        # Arrange:
        with tempfile.TemporaryDirectory() as temp_directory:
            storage = QrSignatureStorage(temp_directory)

            transaction_hash = NemTestUtils.randbytes(32)
            signatures = [Signature(NemTestUtils.randbytes(64)) for _ in range(0, num_signatures)]
            storage.save('foo', transaction_hash, signatures)

            # Act:
            (loaded_transaction_hash, loaded_signatures) = storage.load('foo')

            # Assert:
            self.assertEqual(transaction_hash, loaded_transaction_hash)
            self.assertEqual(signatures, loaded_signatures)

    def test_can_roundtrip_zero_signatures(self):
        self._assert_can_roundtrip_signatures(0)

    def test_can_roundtrip_single_signature(self):
        self._assert_can_roundtrip_signatures(1)

    def test_can_roundtrip_multiple_signatures(self):
        self._assert_can_roundtrip_signatures(5)

    def test_cannot_load_qrcode_that_does_not_exist(self):
        # Arrange:
        with tempfile.TemporaryDirectory() as temp_directory:
            storage = QrSignatureStorage(temp_directory)

            transaction_hash = NemTestUtils.randbytes(32)
            storage.save('foo', transaction_hash, [])

            # Sanity:
            self.assertEqual(1, len(os.listdir(temp_directory)))

            # Act + Assert:
            with self.assertRaises(FileNotFoundError):
                storage.load('bar')

    def _assert_cannot_load_qrcode(self, data_size):
        # Arrange:
        with tempfile.TemporaryDirectory() as temp_directory:
            write_random_qrcode(temp_directory, 'foo', data_size)
            storage = QrSignatureStorage(temp_directory)

            with self.assertRaises(ValueError):
                storage.load('foo')

    def test_cannot_load_qrcode_containing_insufficient_data(self):
        self._assert_cannot_load_qrcode(31)  # less than transaction_hash

    def test_cannot_load_qrcode_containing_partial_signature(self):
        self._assert_cannot_load_qrcode(32 + 64 * 2 + 32)  # 2.5 signatures

    # endregion
