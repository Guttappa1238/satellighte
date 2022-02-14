from typing import List, Dict, Tuple
import copy

import torch
from torch.utils.data import Dataset, DataLoader
import numpy as np
import imageio


class BaseDataset(Dataset):
    def __init__(
        self,
        ids: List[str],
        targets: List[Dict],
        transforms=None,
        *args,
        **kwargs,
    ):
        super().__init__()
        assert isinstance(ids, list), "given `ids` must be list"
        assert isinstance(targets, list), "given `targets must be list"
        assert len(ids) == len(targets), "lenght of both lists must be equal"

        self.ids = ids
        self.targets = targets
        self.transforms = transforms

        # set given kwargs to the dataset
        for key, value in kwargs.items():
            if hasattr(self, key):
                continue
            setattr(self, key, value)

    def __getitem__(self, idx: int) -> Tuple:
        img = self._load_image(self.ids[idx])
        img = torch.from_numpy(img).permute(2, 0, 1)
        targets = copy.deepcopy(self.targets[idx])

        # apply transforms
        if self.transforms:
            img, targets = self.transforms(img, targets)
        targets = torch.tensor(targets, dtype=torch.long)

        return (img, targets)

    def __len__(self) -> int:
        return len(self.ids)

    @staticmethod
    def _load_image(img_file_path: str) -> np.ndarray:

        img = imageio.imread(img_file_path)

        if not img.flags["C_CONTIGUOUS"]:
            # if img is not contiguous than fix it
            img = np.ascontiguousarray(img, dtype=img.dtype)

        if len(img.shape) == 4:
            # found RGBA, converting to => RGB
            img = img[:, :, :3]
        elif len(img.shape) == 2:
            # found GRAYSCALE, converting to => RGB
            img = np.stack([img, img, img], axis=-1)
        else:
            img = img[:, :, :3]

        return np.array(img, dtype=np.uint8)
