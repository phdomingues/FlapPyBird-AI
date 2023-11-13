import torch.nn.modules as nn
import torch.nn.functional as F

class FF(nn.Module):
    # Inputs:
    #   - Flappy Y coord 
    #   - Bottom pipe X coord
    #   - Bottom pipe Y coord
    #   - Top pipe X coord
    #   - Top pipe Y coord
    # Outputs: 
    #   - Jump

    def __init__(self):
        super().__init__()
        self.input_size = 5
        self.num_classes = 1
        self.fc1 = nn.Linear(self.input_size, 6)
        self.fc2 = nn.Linear(6, 3)
        self.fc3 = nn.Linear(3, self.num_classes)

    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = F.sigmoid(self.fc3(x))
        return x
