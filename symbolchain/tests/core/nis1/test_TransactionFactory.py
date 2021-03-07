import unittest
from functools import reduce

from symbolchain.core.CryptoTypes import PublicKey, Signature
from symbolchain.core.nis1.Network import Address, Network
from symbolchain.core.nis1.TransactionFactory import TransactionFactory
from symbolchain.tests.test.NemTestUtils import NemTestUtils

FOO_NETWORK = Network('foo', 0x54)


class MockTransaction:
    # pylint: disable=too-few-public-methods

    def __init__(self, buffer):
        self.buffer = buffer

    def serialize(self):
        return self.buffer


class TransactionFactoryTest(unittest.TestCase):
    # region create

    def test_can_create_transfer(self):
        # Arrange:
        factory = TransactionFactory(FOO_NETWORK)

        # Act:
        transaction = factory.create('transfer')

        # Assert:
        self.assertEqual(0x0101, transaction.type)
        self.assertEqual(0x54000001, transaction.version)

    def test_cannot_create_non_transfer(self):
        # Arrange:
        factory = TransactionFactory(FOO_NETWORK)

        # Act + Assert:
        with self.assertRaises(ValueError):
            factory.create('multisig')

    # endregion

    # region create_from_descriptor

    def test_can_create_from_descriptor(self):
        # Arrange:
        factory = TransactionFactory(FOO_NETWORK)

        # Act:
        transaction = factory.create_from_descriptor({'type': 'transfer'})

        # Assert:
        self.assertEqual(0x0101, transaction.type)
        self.assertEqual(0x54000001, transaction.version)

    def test_can_create_from_descriptor_with_simple_property_override(self):
        # Arrange:
        factory = TransactionFactory(FOO_NETWORK)

        # Act:
        transaction = factory.create_from_descriptor({
            'type': 'transfer',
            'recipient': 'recipient_name'
        })

        # Assert:
        self.assertEqual(0x0101, transaction.type)
        self.assertEqual('recipient_name', transaction.recipient)

    def test_can_create_from_descriptor_with_custom_setter_override(self):
        # Arrange:
        factory = TransactionFactory(FOO_NETWORK)

        # Act:
        transaction = factory.create_from_descriptor({
            'type': 'transfer',
            'message': 'hello world',
        })

        # Assert:
        self.assertEqual(0x0101, transaction.type)
        self.assertEqual(b'hello world', transaction.message)

    def test_can_create_from_descriptor_with_custom_rule_override(self):
        # Arrange:
        factory = TransactionFactory(FOO_NETWORK, {
            Address: lambda address: address + ' ADDRESS'
        })

        # Act:
        transaction = factory.create_from_descriptor({
            'type': 'transfer',
            'recipient': 'recipient_name'
        })

        # Assert:
        self.assertEqual(0x0101, transaction.type)
        self.assertEqual('recipient_name ADDRESS', transaction.recipient)

    def test_can_create_from_descriptor_with_multiple_overrides(self):
        # Arrange:
        factory = TransactionFactory(FOO_NETWORK, {
            Address: lambda address: address + ' ADDRESS',
            PublicKey: lambda address: address + ' PUBLICKEY'
        })

        # Act:
        transaction = factory.create_from_descriptor({
            'type': 'transfer',
            'timestamp': 98765,
            'signer': 'signer_name',
            'recipient': 'recipient_name',
            'message': 'hello world',
        })

        # Assert:
        self.assertEqual(0x0101, transaction.type)
        self.assertEqual(0x54000001, transaction.version)
        self.assertEqual(98765, transaction.timestamp)
        self.assertEqual('signer_name PUBLICKEY', transaction.signer)

        self.assertEqual('recipient_name ADDRESS', transaction.recipient)
        self.assertEqual(b'hello world', transaction.message)

    # endregion

    # region attach_signature

    def test_can_attach_signature_to_transaction(self):
        # Arrange:
        transaction = MockTransaction(bytes([0x44, 0x55, 0x98, 0x12, 0x71, 0xAB, 0x72]))
        signature = Signature(NemTestUtils.randbytes(64))

        # Act:
        signed_transaction_buffer = TransactionFactory.attach_signature(transaction, signature)

        # Assert:
        expected_buffers = [
            [0x07, 0x00, 0x00, 0x00],  # transaction length
            [0x44, 0x55, 0x98, 0x12, 0x71, 0xAB, 0x72],  # transaction
            [0x40, 0x00, 0x00, 0x00],  # signature length
            signature.bytes  # signature
        ]
        expected_buffer = reduce(lambda x, y: bytes(x) + bytes(y), expected_buffers)
        self.assertEqual(expected_buffer, signed_transaction_buffer)

    # endregion