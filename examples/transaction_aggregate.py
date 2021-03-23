#!/usr/bin/env python

#
# Reads utf-8 encoded files with names "part<id>.txt".
# Creates aggregate transaction where each files is a message inside embedded transfers.
# Signs aggregate transaction using private key provided in file specified via `--private` switch.
#

import argparse
from binascii import hexlify, unhexlify
from pathlib import Path
from symbolchain.core.AccountDescriptorRepository import AccountDescriptorRepository
from symbolchain.core.CryptoTypes import Hash256, PrivateKey
from symbolchain.core.sym.KeyPair import KeyPair
from symbolchain.core.sym.MerkleHashBuilder import MerkleHashBuilder
from symbolchain.core.sym.Network import Address
from symbolchain.core.facade.SymFacade import SymFacade

from symbolchain.core.sym.TransactionFactory import TransactionFactory

from symbol_catbuffer.NetworkTypeDto import NetworkTypeDto
from symbol_catbuffer.EmbeddedTransactionBuilderFactory import EmbeddedTransactionBuilderFactory
from symbol_catbuffer.TransactionBuilderFactory import AggregateCompleteTransactionBuilder

import sha3


def read_private_key(private_filename):
    with open(private_filename, 'rt') as inFile:
        return KeyPair(PrivateKey(unhexlify(inFile.read().strip())))


def read_contents(filepath):
    with open(filepath, 'rt', encoding='utf-8') as inFile:
        return inFile.read()


def main():
    parser = argparse.ArgumentParser(description='create aggregate')
    parser.add_argument('--private', help='path to file with private key', required=True)
    args = parser.parse_args()

    facade = SymFacade('public_test', AccountDescriptorRepository(''))
    keyPair = read_private_key(args.private)

    # direct all transfers to 'self'
    recipient = facade.network.public_key_to_address(keyPair.public_key)
    embeddedTransactions = []
    for filepath in sorted(Path(__file__).parent.glob('part*.txt')):
        msg = read_contents(filepath)
        embedded = EmbeddedTransactionBuilderFactory.createByName('embeddedTransfer', keyPair.public_key.bytes, NetworkTypeDto.PUBLIC)
        embedded.recipientAddress = recipient.bytes
        embedded.message = bytes(1) + msg.encode('utf-8')

        embeddedTransactions.append(embedded)

        print("----> {} length in bytes: {}".format(filepath.name, len(embedded.message)))

    hashBuilder = MerkleHashBuilder()
    for embeddedTransaction in embeddedTransactions:
        embeddedTransactionHash = sha3.sha3_256(embeddedTransaction.serialize()).digest()
        hashBuilder.update(Hash256(embeddedTransactionHash))

    merkleHash = hashBuilder.final()

    aggregate = AggregateCompleteTransactionBuilder(keyPair.public_key.bytes, NetworkTypeDto.PUBLIC)
    aggregate.fee = 0
    aggregate.deadline = 1
    aggregate.transactionsHash = merkleHash.bytes
    for embeddedTransaction in embeddedTransactions:
        aggregate.transactions.append(embeddedTransaction)

    signature = facade.sign_transaction(keyPair, aggregate)
    aggregate.signature = signature.bytes

    print(aggregate)
    with open('transaction.bin', 'wb') as outFile:
        outFile.write(aggregate.serialize())

if __name__ == '__main__':
    main()
