from binascii import hexlify, unhexlify

from symbolchain.core.AccountDescriptorRepository import AccountDescriptorRepository
from symbolchain.core.CryptoTypes import PrivateKey
from symbolchain.core.facade.SymFacade import SymFacade
from symbolchain.core.sym.KeyPair import KeyPair
from symbolchain.core.sym.Network import Address
from symbolchain.core.sym.TransactionFactory import TransactionFactory


def main():
    facade = SymFacade('public', AccountDescriptorRepository(''))
    keyPair = KeyPair(PrivateKey(unhexlify('11002233445566778899aabbccddeeff11002233445566778899aabbccddeeff')))

    factory = TransactionFactory(facade.network)
    transaction = factory.create({
        'type': 'transfer',
        'signerPublicKey': keyPair.public_key.bytes,
        'recipientAddress': unhexlify('6822a91a37c5c8e70f98f88ea76f8279e2f1f4679982b718'),
        'fee': 625,
        'deadline': 12345,
        'message': 'Hello world 42'.encode('utf-8'),
        'mosaics': [
            (0x12345678abcdef, 12345)
        ]
    })

    signature = facade.sign_transaction(keyPair, transaction)
    transaction.signature = signature.bytes

    print(hexlify(transaction.serialize()))


if __name__ == '__main__':
    main()
