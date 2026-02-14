from dataclasses import dataclass, field, InitVar
from abc import ABC, abstractmethod

DISCOUNT_PERCENTS = 15


@dataclass(frozen=True, order=True)
class Item:
    item_id: int = field(compare=False)
    title: str
    cost: int

    def __post_init__(self):
        assert self.title
        assert self.cost > 0


@dataclass
class Position(ABC):
    item: Item

    @property
    @abstractmethod
    def cost(self):
        pass


@dataclass
class CountedPosition(Position):
    count: int = 1

    @property
    def cost(self):
        return self.count * self.item.cost


@dataclass
class WeightedPosition(Position):
    weight: float = 1.0

    @property
    def cost(self):
        return self.weight * self.item.cost


@dataclass
class Order:
    order_id: int
    positions: list[Position] = field(default_factory=list)
    cost: int = field(init=False)
    have_promo: InitVar[bool] = False

    def __post_init__(self, have_promo: bool):
        total = sum(p.cost for p in self.positions)
        if have_promo:
            total *= (1 - DISCOUNT_PERCENTS / 100)
        self.cost = int(total)
