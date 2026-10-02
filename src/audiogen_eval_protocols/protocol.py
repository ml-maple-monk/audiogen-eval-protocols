from .types import Cell, EvalSuite, MetricSuite


class Protocol:
    def __init__(
        self,
        name: str,
        family_dict: dict[str, tuple[str, ...]],
        cell_dict: dict[tuple[str, str, str], Cell],
        metric_suite: MetricSuite,
        eval_suite: EvalSuite,
    ):
        self.name = name
        self.cell_dict = cell_dict
        self.metric_suite = metric_suite
        self.eval_suite = eval_suite
        self.owner_dict = self.make_owner_dict(family_dict)

    # Map each model name to the family listing it.
    def make_owner_dict(self, family_dict: dict[str, tuple[str, ...]]):
        owner_dict = {}
        for family_item, model_tuple in family_dict.items():
            for model_item in model_tuple:
                owner_dict[model_item] = family_item
        return owner_dict

    # The family whose model list names this model.
    def get_family(self, model: str):
        family = self.owner_dict[model]
        return family

    # One pinned cell for this model, dataset and metric.
    def get_cell(self, model: str, dataset: str, metric: str):
        family = self.get_family(model)
        cell = self.cell_dict[(family, dataset, metric)]
        return cell
