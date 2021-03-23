#!/usr/bin/env python

#
# Shows how to use Bip32 interface to derive keys.
#

from symbolchain.core.Bip32 import Bip32
from symbolchain.core.facade.SymFacade import SymFacade


def derive_key(root_node, facade, change, index):
    path = [44, facade.BIP32_COIN_ID, 0, change, index]

    child = root_node.derive_path(path)
    keyPair = facade.bip32_node_to_key_pair(child)

    print(' PATH: {}'.format(path))
    print(' * private key: {}'.format(keyPair.private_key))
    print(' *  public key: {}'.format(keyPair.public_key))
    address = facade.network.public_key_to_address(keyPair.public_key)
    print(' *     address: {}'.format(address))
    print('')


def main():
    facade = SymFacade('public_test')

    bip = Bip32(facade.BIP32_CURVE_NAME)
    root_node = bip.from_mnemonic('axis buzz cycle dynamic eyebrow future gym hybrid ivory just know lyrics', 'correcthorsebatterystaple')

    for change in [0, 1]:
        for index in range(3):
            derive_key(root_node, facade, change, index)


if __name__ == '__main__':
    main()
