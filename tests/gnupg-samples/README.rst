The dirs inhere contain complete configured GnuPG homes.

The passphrase of all secret keys is ``secret``.

`empty`:
   a configuration without any keys, not public, nor secret.

`public-only`:
  contains one public key, no secret ones.

`one-secret`:
  contains one public key and one secret, including a subkey.

`two-secret`:
   contains one public key and one secret with two subkeys.

`three-secret-two-uid`:
   contains one public key, one secret one with three subkeys and two
   user ids.

`two-users`:
   contains the same as `three-secret-two-uid` and an additional
   keypair (public/private) for ``bob@example.org``. Also Bob's
   secret passphrase is ``secret``.
