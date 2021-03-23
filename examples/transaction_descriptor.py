#!/usr/bin/env python

#
# Shows how to create transaction manually using TransactionFactory.
#

from binascii import unhexlify
from symbolchain.core.CryptoTypes import PrivateKey
from symbolchain.core.sym.KeyPair import KeyPair
from symbolchain.core.sym.Network import Address
from symbolchain.core.facade.SymFacade import SymFacade
from symbolchain.core.sym.TransactionFactory import TransactionFactory

def main():
    facade = SymFacade('public_test')
    keyPair = KeyPair(PrivateKey(bytes(range(1, 33))))

    factory = TransactionFactory(facade.network)
    transaction = factory.create({
        'type': 'transfer',
        'signerPublicKey': keyPair.public_key.bytes,
        'recipientAddress': Address('NBQMNBY7Z3YTT2V7Y32CKSVQPJ3YDAD4RLQJEEI').bytes,
        'fee': 0,
        'deadline': 1,
        'message': 'V belom plashche s krovavym podboyem, sharkayushchey kavaleriyskoy pokhodkoy,'.encode('utf-8'),
        'mosaics': [
            (0x4F8E3FB75C77C83E, 12345_000000),
            (0x4F8E3FB75C77C83E, 10)
        ]
    })

    print(transaction)


if __name__ == '__main__':
    main()
