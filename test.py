import torch

db_test = torch.load(r'data\features_database_test.pt')
db = torch.load(r'data\features_database.pt')

for entry in db:
    print(entry['embedding'].shape)

for entry in db_test:
    print(entry['embedding'].shape)