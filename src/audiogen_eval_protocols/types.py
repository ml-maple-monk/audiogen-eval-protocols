from dataclasses import dataclass


@dataclass(frozen=True)
class GenArm:
    steps: int
    cfg_scale: float
    seconds_start: float
    seconds_total: float
    level_policy: str


@dataclass(frozen=True)
class Cell:
    arm: GenArm
    downmix: str
    band_rate: int
    paper_fd: str


@dataclass(frozen=True)
class PannSpec:
    sample_rate: int
    window_samples: int
    checkpoint_name: str
    window_size: int
    hop_size: int
    mel_bins: int
    fmin: int
    fmax: int
    classes: int
    isc_splits: int
    isc_seed: int
    kl_eps: float


@dataclass(frozen=True)
class FadSpec:
    sample_rate: int
    checkpoint_name: str
    use_activation: bool
    remove_dc: bool


@dataclass(frozen=True)
class AudioboxSpec:
    sample_rate: int
    checkpoint_name: str
    axis_list: tuple[str, ...]


@dataclass(frozen=True)
class MetricSpec:
    name: str
    backbone: str
    protocol_metric: str
    per_source: bool
    weight_name_list: tuple[str, ...]


@dataclass(frozen=True)
class MetricSuite:
    pann: PannSpec
    fad: FadSpec
    audiobox: AudioboxSpec
    pann_logit_list: tuple[str, ...]
    fd_eps: float
    spec_list: tuple[MetricSpec, ...]

    # One metric spec by name.
    def get_metric_spec(self, name: str):
        found = None
        for spec_item in self.spec_list:
            if spec_item.name == name:
                found = spec_item
        return found

    # Protocol cells these metrics score under.
    def get_protocol_metric_set(self, name_list: tuple[str, ...]):
        protocol_metric_set = set()
        for name_item in name_list:
            spec = self.get_metric_spec(name_item)
            protocol_metric_set.add(spec.protocol_metric)
        return protocol_metric_set


@dataclass(frozen=True)
class EvalSpec:
    name: str
    exp_name: str
    pair_list: tuple[tuple[str, ...], ...]
    source: str
    gt_downmix: str
    metric_list: tuple[str, ...]
    sampling_field_list: tuple[str, ...]
    summary_field_list: tuple[str, ...]


@dataclass(frozen=True)
class DatasetSpec:
    name: str
    subset: str


@dataclass(frozen=True)
class EvalSuite:
    default_metric: str
    protocol_metric_list: tuple[str, ...]
    eval_list: tuple[EvalSpec, ...]
    dataset_list: tuple[DatasetSpec, ...]

    # One evaluation spec by name.
    def get_eval_spec(self, name: str):
        found = None
        for eval_item in self.eval_list:
            if eval_item.name == name:
                found = eval_item
        return found

    # Empty picks the dataset default, 'all' every split.
    def get_subset(self, dataset: str, subset: str):
        resolved = subset
        if not subset:
            for dataset_item in self.dataset_list:
                if dataset_item.name == dataset:
                    resolved = dataset_item.subset
        if resolved in ("all", ""):
            resolved = None
        return resolved
