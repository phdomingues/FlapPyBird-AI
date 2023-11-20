import numpy as np
import torch
import torch.nn.modules as nn
import torch.nn.functional as F
from typing import Optional

class FF(nn.Module):
    # Inputs:
    #   - Flappy Y coord 
    #   - Bottom pipe X coord
    #   - Bottom pipe Y coord
    #   - Top pipe X coord
    #   - Top pipe Y coord
    # Outputs: 
    #   - Jump

    def __init__(self, chromosome:Optional[torch.Tensor]=None):
        super().__init__()
        self.input_size = 5
        self.num_classes = 1
        self.fc1 = nn.Linear(self.input_size, 6)
        self.fc2 = nn.Linear(6, 3)
        self.fc3 = nn.Linear(3, self.num_classes)
        self.fc1.requires_grad_(False)
        self.fc2.requires_grad_(False)
        self.fc3.requires_grad_(False)
        if chromosome is not None:
            self.load_chromosome(chromosome)

    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = F.sigmoid(self.fc3(x))
        return x

    def to_chromosome(self):
        ### Encode the neural network weights and bias into a 1d vector 
        w1 = self.fc1.weight.flatten()
        b1 = self.fc1.bias.flatten()
        w2 = self.fc2.weight.flatten()
        b2 = self.fc2.bias.flatten()
        w3 = self.fc3.weight.flatten()
        b3 = self.fc3.bias.flatten()
        return torch.cat((w1,b1,w2,b2,w3,b3), dim=0)

    def chromosome2dict(self, data):
        ### Decode the 1d vector into a dictionary format
        w1_idx = np.prod(self.fc1.weight.shape) # count the number of weights on layer fc1
        b1_idx = w1_idx + np.prod(self.fc1.bias.shape) # count the number of bias values on layer fc1
        w2_idx = b1_idx + np.prod(self.fc2.weight.shape)
        b2_idx = w2_idx + np.prod(self.fc2.bias.shape)
        w3_idx = b2_idx + np.prod(self.fc3.weight.shape)
        b3_idx = w3_idx + np.prod(self.fc3.bias.shape)

        return {
            'w1': torch.reshape(data[0:w1_idx], self.fc1.weight.shape),
            'b1': torch.reshape(data[w1_idx:b1_idx], self.fc1.bias.shape),
            'w2': torch.reshape(data[b1_idx:w2_idx], self.fc2.weight.shape),
            'b2': torch.reshape(data[w2_idx:b2_idx], self.fc2.bias.shape),
            'w3': torch.reshape(data[b2_idx:w3_idx], self.fc3.weight.shape),
            'b3': torch.reshape(data[w3_idx:b3_idx], self.fc3.bias.shape),
        }

    def load_from_dict(self, wb:dict) -> None:
        self.fc1.weight = torch.nn.parameter.Parameter(wb['w1'])
        self.fc1.bias = torch.nn.parameter.Parameter(wb['b1'])
        self.fc2.weight = torch.nn.parameter.Parameter(wb['w2'])
        self.fc2.bias = torch.nn.parameter.Parameter(wb['b2'])
        self.fc3.weight = torch.nn.parameter.Parameter(wb['w3'])
        self.fc3.bias = torch.nn.parameter.Parameter(wb['b3'])

    def load_chromosome(self, chromosome:torch.Tensor) -> None:
        self.load_from_dict(self.chromosome2dict(chromosome))