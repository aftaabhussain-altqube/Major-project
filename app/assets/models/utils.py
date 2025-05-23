import torch
from torch import nn
from torchvision import transforms as T, models

from PIL import Image

device = "cpu"


class SiameseVGG16(nn.Module):
    transform = T.Compose([
        T.Resize((224, 224)),
        T.ToTensor(),
    ])

    @classmethod
    def from_pretrained(cls, path: str):
        model = cls()
        model.load_state_dict(torch.load(path, map_location=device))
        return model

    def __init__(self):
        super(SiameseVGG16, self).__init__()
        self.base_model = models.vgg16(weights="VGG16_Weights.IMAGENET1K_V1").features
        self.fc = nn.Sequential(
            nn.Linear(25088, 4096),
            nn.ReLU(),
            nn.Dropout(),
            nn.Linear(4096, 1024)
        )

    def inference(self, f: "Image.Image", s: "Image.Image", r: "Image.Image"):
        F = self.transform(f.convert('RGB')).unsqueeze(0).to("cpu")
        S = self.transform(s.convert('RGB')).unsqueeze(0).to("cpu")
        R = self.transform(r.convert('RGB')).unsqueeze(0).to("cpu")

        F_out = self(F)
        S_out = self(S)
        R_out = self(R)

        F_dist = nn.functional.pairwise_distance(S_out, F_out)
        R_dist = nn.functional.pairwise_distance(S_out, R_out)
        # s = math.ceil(max(F_dist, R_dist) / 10)

        return bool(-1 <= F_dist - R_dist <= 1)

    def forward(self, x):
        x = self.base_model(x)
        x = x.view(x.size(0), -1)  # Flatten
        x = self.fc(x)
        return x


def getClassName(results):
    if results is None:
        return None
    class_name = None
    for box in results[0].boxes:
        class_id = int(box.cls)
        class_name = results[0].names[
            class_id
        ]
    return class_name
