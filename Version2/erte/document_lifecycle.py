import rsa
import os
import ast
import hashlib
from key_generation_peers import Peers

delimiter = '$ $'


class Document:

    def __init__(self, filename):
        self.filename = filename

    def create_new_file(self):
        if os.path.isfile(self.filename):
            print("FileName already exists...concatenating")
            f = open(self.filename, 'a')
            #f.write(f'Document {self.filename} created\n')
            f.close()
        else:
            f = open(self.filename, 'a')
            f.write(f'Document {self.filename} created\n')
            f.close()

    def write_file(self, peer, group, action):

        if group.name not in peer.groups:
            print(f"Write {action} by {peer.name} not possible thorugh {group.name} group")

        with open(self.filename, 'r') as reader:
            line = reader.readlines()
            last_line = line[-1]
            last_digest = self.extract_digest(last_line)
            # print(line, " ", str(last_digest))

        with open(self.filename, 'a') as writer:
            encrypted_action = str(rsa.encrypt(action.encode(), group.get_public_key()))
            hashed = self.compute_digest(last_digest, encrypted_action.encode('utf-8'), group.name.encode('utf-8'))
            digest = rsa.sign(hashed.digest(), peer.get_private_key(), 'SHA-256')
            sequence = [encrypted_action, peer.name, group.name, str(digest)]
            line = delimiter.join(sequence)     # '$ $' is used as delimiter because space can't be used as delimiter
            writer.write(line + '\n')
            #writer.write(action + '\n')

    def num_lines(self):
        with open(self.filename, 'r') as reader:
            return len(reader.readlines())

    def read_file(self, peer):
        print('reading file')
        if(self.verify_digest()!=1):
            print("Can't read tampered document")
            return
        with open(self.filename, 'r') as reader:
            reader.readline()
            for line in reader.readlines():
                sequence = line.split(delimiter)
                crypted_text = ast.literal_eval(sequence[0])
                # print(crypted_text)
                peer_name = sequence[1]
                group_name = sequence[2]
                digest = sequence[3]
                # print(peer_name, group_name)
                if group_name in peer.groups:
                    message = rsa.decrypt(crypted_text, Peers(group_name).get_private_key()).decode('utf-8')
                else:
                    message = "message can't be decrypted by non-group member"
                print(message, ' ', peer_name, ' ', group_name, digest)

    def compute_digest(self, *args):
        hashed = hashlib.sha256()
        for arg in args:
            hashed.update(arg)
        return hashed

    def extract_digest(self, line):
        sequences = line.split(delimiter)
        if len(sequences) == 1:   # if it is first action..only one line about file will be written
            return b''
        last_digest = sequences[-1][:-1]
        return ast.literal_eval(last_digest)

    def verify_digest(self):
        try:
            with open(self.filename, 'r') as reader:
                lines = reader.readlines()
                for idx, line in enumerate((lines[1:])):
                    sequence = line.split(delimiter)
                    # print(sequence)
                    crypto_digest_sign = sequence[-1][:-1] # last character skipped bcz of '\n' added in line
                    crypto_digest_sign = ast.literal_eval(crypto_digest_sign)
                    # print(crypto_digest_sign)
                    encrypted_action = sequence[0]
                    peer_name = sequence[1]
                    group_name = sequence[2]
                    # hashed_digest = rsa.decrypt(crypto_digest, Peers(peer_name).get_public_key())
                    last_digest = self.extract_digest(lines[idx])  # idx will be one less of that lines bcz started from 1
                    # print(peer_name, group_name, last_digest, hashed_digest)
                    recomputed_digest = self.compute_digest(last_digest, encrypted_action.encode('utf-8'), group_name.encode('utf-8')).digest()
                    # print("\n", peer_name," \n", group_name, "\n", last_digest,"\n", crypto_digest_sign, "\n",recomputed_digest,"\n")
                    rsa.verify(recomputed_digest, crypto_digest_sign, Peers(peer_name).get_public_key())

            print('No error found in digest || Document not tampered')
            print('Digest verification completed')
        except Exception as e:
            print(f'Error detected in line {idx} \n Error: {e}')
            print("Digest verification failed")
            return 0
        return 1
            

    def get_lifecycle(self,peer,groups):
        if(self.verify_digest()!=1):
            return  ["Can't read tampered document"]
        
        required_groups = [group.name for group in groups]
        for group in required_groups:
            if group not in peer.groups:
                return [f"{peer.name} has no rights to access group {group}"]

        actions = list()

        with open(self.filename, 'r') as reader:
            reader.readline()
            for line in reader.readlines():
                sequence = line.split(delimiter)
                crypted_text = ast.literal_eval(sequence[0])
                peer_name = sequence[1]
                group_name = sequence[2]

                if group_name in required_groups:
                    message = rsa.decrypt(crypted_text, Peers(group_name).get_private_key()).decode('utf-8')
                    actions.append(f"{peer_name} written {message}")

        return actions
