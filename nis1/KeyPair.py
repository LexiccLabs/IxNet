import sha3

import nis1.external.ed25519 as ed25519
from core.CryptoTypes import PublicKey, Signature


class KeyPair:
    """Represents an ED25519 private and public key."""

    def __init__(self, private_key):
        """Creates a key pair from a private key."""
        self.__sk = private_key.bytes[::-1]
        self.__pk = ed25519.publickey_hash_unsafe(self.__sk, sha3.keccak_512)

    @property
    def public_key(self):
        """Gets public key."""
        return PublicKey(self.__pk)

    def sign(self, message):
        """Signs a message with the private key."""
        return Signature(ed25519.signature_hash_unsafe(message, self.__sk, self.__pk, sha3.keccak_512))


class Verifier:
    """Verifies signatures signed by a single key pair."""

    # pylint: disable=too-few-public-methods

    def __init__(self, public_key):
        """Creates a verifier from a public key."""
        self.__pk = public_key.bytes

    def verify(self, message, signature):
        """Verifies a message signature."""
        try:
            ed25519.checkvalid_hash(signature.bytes, message, self.__pk, sha3.keccak_512)
            return True
        except (ValueError, ed25519.SignatureMismatch):
            return False
