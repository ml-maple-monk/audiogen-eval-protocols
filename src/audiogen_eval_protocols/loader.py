from dataclasses import dataclass, fields, is_dataclass
from pathlib import Path
from typing import get_args, get_origin

import yaml

from .protocol import Protocol
from .types import Cell, EvalSuite, MetricSuite


@dataclass(frozen=True)
class LoaderConfig:
    protocol_file: str
    family_file: str
    metric_file: str
    eval_file: str


@dataclass(frozen=True)
class FamilyEntry:
    family: str
    model_tuple: tuple[str, ...]


class ProtocolLoader:
    def __init__(self, cfg: LoaderConfig):
        self.cfg = cfg

    # Parse one YAML file whose top level is a mapping.
    def read_mapping(self, path: Path):
        text = path.read_text()
        mapping_dict = yaml.safe_load(text)
        return mapping_dict

    # One value built as its declared field type.
    def build_value(self, kind: type, value: object):
        built = value
        origin = get_origin(kind)
        if is_dataclass(kind):
            built = self.build_record(kind, value)
        elif origin is tuple:
            arg_tuple = get_args(kind)
            item_kind = arg_tuple[0]
            item_list = []
            for value_item in value:
                item = self.build_value(item_kind, value_item)
                item_list.append(item)
            built = tuple(item_list)
        elif kind is float:
            built = float(value)
        return built

    # One dataclass from a mapping, each field typed.
    def build_record(self, cls: type, data_dict: dict):
        value_dict = {}
        field_tuple = fields(cls)
        for field_item in field_tuple:
            value = data_dict[field_item.name]
            built = self.build_value(field_item.type, value)
            value_dict[field_item.name] = built
        record = cls(**value_dict)
        return record

    # Family key and model names from one family file.
    def load_family(self, family_dir: Path):
        path = family_dir / self.cfg.family_file
        entry_dict = self.read_mapping(path)
        model_tuple = tuple(entry_dict["models"])
        entry = FamilyEntry(family=entry_dict["family"], model_tuple=model_tuple)
        return entry

    # Every cell one family directory pins.
    def load_family_cells(self, family: str, family_dir: Path):
        cell_dict = {}
        path_iter = family_dir.glob("*.yaml")
        path_list = sorted(path_iter)
        for path_item in path_list:
            if path_item.name != self.cfg.family_file:
                block_dict = self.read_mapping(path_item)
                for metric_item, block_item in block_dict.items():
                    cell = self.build_record(Cell, block_item)
                    cell_dict[(family, path_item.stem, metric_item)] = cell
        return cell_dict

    # Family directories under the root, sorted.
    def get_family_dir_list(self, root: Path):
        family_dir_list = []
        path_iter = root.iterdir()
        path_list = sorted(path_iter)
        for path_item in path_list:
            if path_item.is_dir() and not path_item.name.startswith("."):
                family_dir_list.append(path_item)
        return family_dir_list

    # Read the protocol, metric and evaluation files under root.
    def load_protocol(self, root: Path):
        protocol_path = root / self.cfg.protocol_file
        head_dict = self.read_mapping(protocol_path)
        family_dict = {}
        cell_dict = {}
        family_dir_list = self.get_family_dir_list(root)
        for family_dir_item in family_dir_list:
            entry = self.load_family(family_dir_item)
            family_dict[entry.family] = entry.model_tuple
            family_cell_dict = self.load_family_cells(entry.family, family_dir_item)
            cell_dict.update(family_cell_dict)
        metric_path = root / self.cfg.metric_file
        metric_dict = self.read_mapping(metric_path)
        metric_suite = self.build_record(MetricSuite, metric_dict)
        eval_path = root / self.cfg.eval_file
        eval_dict = self.read_mapping(eval_path)
        eval_suite = self.build_record(EvalSuite, eval_dict)
        protocol = Protocol(head_dict["name"], family_dict, cell_dict, metric_suite, eval_suite)
        return protocol
