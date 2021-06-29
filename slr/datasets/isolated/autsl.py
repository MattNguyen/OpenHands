import os
import pandas as pd
from .base import BaseIsolatedDataset


class AUTSLDataset(BaseIsolatedDataset):
    def __init__(
        self,
        class_mappings_file_path,
        **kwargs):

        self.class_mappings_file_path = class_mappings_file_path
        super(AUTSLDataset, self).__init__(**kwargs)

    def read_index_file(self, index_file_path, splits, modality):

        class_mappings_df = pd.read_csv(self.class_mappings_file_path)
        self.id_to_glosses = dict(
            zip(class_mappings_df["ClassId"], class_mappings_df["TR"])
        )
        self.glosses = sorted(self.id_to_glosses.values())

        df = pd.read_csv(index_file_path, header=None)

        if modality == "rgb":
            file_suffix = "color.mp4"
        elif modality == "pose":
            file_suffix = "color.pkl"
            
        for i in range(len(df)):
            instance_entry = df[0][i] + "_" + file_suffix, df[1][i]
            self.data.append(instance_entry)

    def read_data(self, index):
        video_name, label = self.data[index]
        video_path = os.path.join(self.root_dir, video_name)
        imgs = self.load_frames_from_video(video_path)
        return imgs, label, video_name