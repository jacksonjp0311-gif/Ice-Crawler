import math
from dataclasses import dataclass
from typing import Iterable, List, Sequence, Tuple

GOLDEN_RATIO = (1 + math.sqrt(5)) / 2
INVERSE_GOLDEN_RATIO = 1 / GOLDEN_RATIO

@dataclass(frozen=True)
class Partition:
    items: List[dict]
    total_size: float
    depth: int


def _split_index(sizes: Sequence[float], target: float) -> int:
    accum = 0.0
    for idx, size in enumerate(sizes):
        if accum + size > target and idx > 0:
            return idx
        accum += size
    return max(1, len(sizes) // 2)


def _partition_recursive(
    items: Sequence[dict],
    sizes: Sequence[float],
    max_size: float,
    depth: int,
) -> List[Partition]:
    total = float(sum(sizes))
    if total <= max_size or len(items) <= 1:
        return [Partition(list(items), total, depth)]

    target = total * INVERSE_GOLDEN_RATIO
    split_at = _split_index(sizes, target)

    left_items = items[:split_at]
    right_items = items[split_at:]
    left_sizes = sizes[:split_at]
    right_sizes = sizes[split_at:]

    partitions: List[Partition] = []
    for sub_items, sub_sizes in ((left_items, left_sizes), (right_items, right_sizes)):
        if not sub_items:
            continue
        partitions.extend(_partition_recursive(sub_items, sub_sizes, max_size, depth + 1))
    return partitions


def phi_partition(
    items: Iterable[dict],
    size_key: str,
    max_size: float,
) -> Tuple[List[Partition], List[dict]]:
    """Partition items using a golden-ratio split until partitions fit max_size.

    Returns (partitions, oversize_items).
    """
    normalized = sorted(items, key=lambda x: x["path"])
    oversize = [item for item in normalized if item[size_key] > max_size]
    bounded = [item for item in normalized if item[size_key] <= max_size]

    if not bounded:
        return [], oversize

    sizes = [item[size_key] for item in bounded]
    partitions = _partition_recursive(bounded, sizes, max_size, depth=0)
    return partitions, oversize
