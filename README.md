# audiogen-eval-protocols

Music-generation evaluation protocols for audio generation models.

## Installation

```bash
pip install .
```

Requires Python 3.10+ and PyYAML.

## Usage

```python
from pathlib import Path

import audiogen_eval_protocols
from audiogen_eval_protocols import LoaderConfig, ProtocolLoader

root = Path(audiogen_eval_protocols.__file__).parent / "protocols"
loader_cfg = LoaderConfig(
    protocol_file="protocol.yaml",
    family_file="family.yaml",
    metric_file="metrics.yaml",
    eval_file="evaluations.yaml",
)
protocol = ProtocolLoader(loader_cfg).load_protocol(root)
cell = protocol.get_cell("audiox-maf", "audiocaps", "fd_pann")
```

## Protocols

| Model | AudioCaps | MusicCaps |
|---|---|---|
| audiox-maf | ✓ | ✓ |
| tango-music-af-ft-mc | | ✓ |


