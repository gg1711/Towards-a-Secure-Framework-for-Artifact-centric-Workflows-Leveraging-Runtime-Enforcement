import rsa
import os

path = os.path.join(os.getcwd(), 'private_public_keys')


class Peers:
    def __init__(self, name, is_group = False):
        self.name = name
        self.groups = set()
        self.is_group = is_group

    def add_user(self):
        pubkey, privkey = rsa.newkeys(512)
        # print(dir(pubkey))
        # print(dir(privkey))
        # print(dir(rsa.PrivateKey))
        privkey_name = os.path.join(path, self.name + '_private')
        pubkey_name = os.path.join(path, self.name + '_public')

        privkey = rsa.PrivateKey.save_pkcs1(privkey)
        pubkey = rsa.PublicKey.save_pkcs1(pubkey)

        with open(privkey_name, 'wb') as writer:
            writer.write(privkey)

        with open(pubkey_name, 'wb') as writer:
            writer.write(pubkey)

    def add_group(self, group_name):
        '''Used to add group name to a group'''
        if self.is_group:
            print('This method not avaliable for groups')
        else:
            self.groups.add(group_name)


    def get_private_key(self):
        privkey_name = os.path.join(path, self.name + '_private')
        with open(privkey_name, 'r') as reader:
            keydata = reader.read()
        privkey = rsa.PrivateKey.load_pkcs1(keydata)
        return privkey

    def get_public_key(self):
        pubkey_name = os.path.join(path, self.name + '_public')
        with open(pubkey_name, 'r') as reader:
            keydata = reader.read()
        pubkey = rsa.PublicKey.load_pkcs1(keydata)
        return pubkey
