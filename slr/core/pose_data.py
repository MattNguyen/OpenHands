import pytorch_lightning as pl
from omegaconf import OmegaConf
import hydra
from slr.datasets import pose_transforms


def create_transform(transforms_cfg):
    all_transforms = []
    for transform in transforms_cfg:
        for transform_name, transform_args in transform.items():
            if not transform_args:
                transform_args = {}
            new_trans = getattr(pose_transforms, transform_name)(**transform_args)
            all_transforms.append(new_trans)
    return pose_transforms.Compose(all_transforms)


class PoseDataModule(pl.LightningDataModule):
    def __init__(self, data_cfg):
        super().__init__()
        self.data_cfg = data_cfg

    def setup(self, stage=None):
        self.train_dataset = self._instantiate_dataset(self.data_cfg.train_pipeline)
        self.valid_dataset = self._instantiate_dataset(self.data_cfg.valid_pipeline)
        print("Train set size:", len(self.train_dataset))
        print("Valid set size:", len(self.valid_dataset))

    def train_dataloader(self):
        dataloader = hydra.utils.instantiate(
            self.data_cfg.train_pipeline.dataloader,
            dataset=self.train_dataset,
            collate_fn=self.train_dataset.collate_fn,
        )
        return dataloader

    def val_dataloader(self):
        dataloader = hydra.utils.instantiate(
            self.data_cfg.valid_pipeline.dataloader,
            dataset=self.valid_dataset,
            collate_fn=self.valid_dataset.collate_fn,
        )
        return dataloader

    def _instantiate_dataset(self, pipeline_cfg):
        if getattr(pipeline_cfg, "dataset", None):

            transforms_cfg = pipeline_cfg.transforms
            if transforms_cfg:
                transforms = create_transform(transforms_cfg)
            else:
                transforms = None

            dataset = hydra.utils.instantiate(
                pipeline_cfg.dataset, transforms=transforms
            )
        else:
            raise ValueError(f"`dataset` section missing in pipeline config")

        return dataset
