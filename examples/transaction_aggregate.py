import argparse
from binascii import hexlify, unhexlify
from symbolchain.core.AccountDescriptorRepository import AccountDescriptorRepository
from symbolchain.core.CryptoTypes import PrivateKey
from symbolchain.core.sym.KeyPair import KeyPair
from symbolchain.core.sym.Network import Address
from symbolchain.core.facade.SymFacade import SymFacade
from symbolchain.core.MerkleHashBuilder import MerkleHashBuilder

from symbolchain.core.sym.TransactionFactory import TransactionFactory

from symbol_catbuffer.NetworkTypeDto import NetworkTypeDto
from symbol_catbuffer.EmbeddedTransactionBuilderFactory import EmbeddedTransactionBuilderFactory
from symbol_catbuffer.TransactionBuilderFactory import AggregateCompleteTransactionBuilder

import pathlib
import sha3

def read_private_key(private_filename):
    with open(private_filename, 'rt') as inFile:
        return KeyPair(PrivateKey(unhexlify(inFile.read().strip())))

def read_contents(id):
    dirname = pathlib.Path(__file__).parent.absolute()
    with open(dirname / 'part{}.txt'.format(id)) as inFile:
        return inFile.read()

def main():
    parser = argparse.ArgumentParser(description='create aggregate')
    parser.add_argument('--private', help='path to file with private key', required=True)
    args = parser.parse_args()

    facade = SymFacade('public', AccountDescriptorRepository(''))
    keyPair = read_private_key(args.private)

    embeddedTransactions = []
    for id in range(1, 7):
        msg = read_contents(id)
        embedded = EmbeddedTransactionBuilderFactory.createByName('embeddedTransfer', keyPair.public_key.bytes, NetworkTypeDto.PUBLIC)

        recipient = facade.network.public_key_to_address(keyPair.public_key)
        embedded.recipientAddress = recipient.bytes
        embedded.message = bytes(1) + msg.encode('utf-8')

        embeddedTransactions.append(embedded)

        print("----> ", id, len(embedded.message))

    hashBuilder = MerkleHashBuilder()
    for embeddedTransaction in embeddedTransactions:
        embeddedTransactionHash = sha3.sha3_256(embeddedTransaction.serialize()).digest()
        hashBuilder.update(embeddedTransactionHash)

    merkleHash = hashBuilder.final()


    aggregate = AggregateCompleteTransactionBuilder(keyPair.public_key.bytes, NetworkTypeDto.PUBLIC)
    aggregate.fee = 0
    aggregate.deadline = 1
    aggregate.transactionsHash = merkleHash
    for embeddedTransaction in embeddedTransactions:
        aggregate.transactions.append(embeddedTransaction)


    signature = facade.sign_transaction(keyPair, aggregate)
    aggregate.signature = signature.bytes

    print(aggregate)
    with open('000_greetings.bin', 'wb') as outFile:
        outFile.write(aggregate.serialize())

if __name__ == '__main__':
    main()
