from key_generation_peers import Peers
from document_lifecycle import Document


groups = ['G1', 'G2', 'G3', 'G4', 'G5']

group1 = Peers(groups[0], is_group = True)
group2 = Peers(groups[1], is_group = True)
group3 = Peers(groups[2], is_group = True)
group4 = Peers(groups[3], is_group = True)
group5 = Peers(groups[4], is_group = True)

group_objects = dict()
group_objects['G1'] = group1
group_objects['G2'] = group2
group_objects['G3'] = group3
group_objects['G4'] = group4
group_objects['G5'] = group5


arg = input('Want to generate new keys for Groups YES/NO: ')

if arg == 'YES':
    group1.add_user()
    group2.add_user()
    group3.add_user()
    group4.add_user()
    group5.add_user()
print(f"groups available are:  {group1.name} and {group2.name} and {group3.name} and {group4.name} and {group5.name}")

users = ['A','B','C', 'D','E']
user_objects = dict()

for user in users:
    user_objects[user] = Peers(user)

print("Users available are: ", end="")
print(users)

user_groups = [[group1], [group2], [group3], [group5], [group4]]
arg = input('Want to generate new keys for Users YES/NO: ')

if arg == 'YES':
    for user in users:
        user_objects[user].add_user()

index = dict()
rev_index = dict()

for user, groups in zip(users, user_groups):
    for group in groups:
        user_objects[user].add_group(group.name)
        rev_index[len(index)] = (user, group.name)
        index[(user, group.name)] = len(index)
        

print("Indexing: ")
for k,v in index.items():
    print(k,"->",v)

filename = input('Enter name of document: ')
doc = Document(filename)
doc.create_new_file()


def parse_actions():
    ''' It will parse actions from actions.txt file.
        It will return actions list to main file. 
        We will call write_action function to execute actions one by one later. 
    '''
    action_filename = 'actions.txt'
    actions = list()
    with open(action_filename, 'r') as reader:
        line = reader.readlines()
        for l in line:
            action = l.split(',')
            action = [a.strip() for a in action]
            actions.append(action)
        # print(actions)
    
    return actions


def get_peer_index(action):
    ''' Based on the details of the action, we will return mapped index 
        Format: (peer_name, group_name, text_to_write)
    '''
    print("Action: ", action)
    peer_name = action[0]
    group_name = action[1]

    return index[(peer_name, group_name)]


def write_action(action):
    ''' Write action will be done based on input received.
        Format: (peer_name, group_name, text_to_write)
    '''
    peer_name = action[0]
    group_name = action[1]
    text = action[1]

    doc.write_file(user_objects[peer_name], group_objects[group_name], text)

    return index[(peer_name, group_name)]


def verify_digest():
    '''It will be used for verifying digest. 
       If document is tampered, we can easily detect using this cryptographic method.
    '''
    print("\n---Starting Document verification---")
    print("Number of lines in doc: ", doc.num_lines())
    doc.verify_digest()
    return 1


def read_document(idx):
    ''' Reads document based on index received from C file. 
        It will use same mapping of (user_name, group_name) used for performing action.
    '''
    peer_name, group_name = rev_index[idx]
    actions = doc.get_lifecycle(user_objects[peer_name], [group_objects[group_name]])
    
    print(f"\nactions performed in {group_name} group")
    for action in actions:
        print(action)

    return 1

