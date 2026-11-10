import random
from collections.abc import Callable

from kavunbet_optimizer.domain.reel_set import ReelSet
from kavunbet_optimizer.schemas.optimization import MoveWeights

Mutation = Callable[[ReelSet], bool]


class CandidateMutator:
    def __init__(
        self,
        weights: MoveWeights,
        composition_symbols: list[str],
        random_source: random.Random,
    ) -> None:
        self._weights = weights
        self._composition_symbols = tuple(composition_symbols)
        self._random = random_source

    def mutate(self, candidate: ReelSet) -> bool:
        choices: tuple[tuple[float, Mutation], ...] = (
            (self._weights.within_reel, self._within_reel),
            (self._weights.cross_reel, self._cross_reel),
            (self._weights.composition, self._composition),
        )
        enabled_choices = tuple(choice for choice in choices if choice[0] > 0)
        total_weight = sum(weight for weight, _ in enabled_choices)
        threshold = self._random.random() * total_weight

        running_weight = 0.0
        for weight, mutation in enabled_choices:
            running_weight += weight
            if threshold < running_weight:
                return mutation(candidate)

        return enabled_choices[-1][1](candidate)

    def _within_reel(self, candidate: ReelSet) -> bool:
        reel = self._random.choice(candidate.reels)
        first_stop = self._random.randrange(len(reel))
        alternatives = [index for index, symbol in enumerate(reel) if symbol != reel[first_stop]]
        if not alternatives:
            return False

        second_stop = self._random.choice(alternatives)
        reel[first_stop], reel[second_stop] = reel[second_stop], reel[first_stop]
        return True

    def _cross_reel(self, candidate: ReelSet) -> bool:
        if candidate.reel_count < 2:
            return False

        first_index, second_index = self._random.sample(range(candidate.reel_count), 2)
        first_reel = candidate.reels[first_index]
        second_reel = candidate.reels[second_index]
        first_stop = self._random.randrange(len(first_reel))
        alternatives = [
            index for index, symbol in enumerate(second_reel) if symbol != first_reel[first_stop]
        ]
        if not alternatives:
            return False

        second_stop = self._random.choice(alternatives)
        first_reel[first_stop], second_reel[second_stop] = (
            second_reel[second_stop],
            first_reel[first_stop],
        )
        return True

    def _composition(self, candidate: ReelSet) -> bool:
        if len(self._composition_symbols) < 2:
            return False

        positions = [
            (reel_index, stop_index)
            for reel_index, reel in enumerate(candidate.reels)
            for stop_index, symbol in enumerate(reel)
            if symbol in self._composition_symbols
        ]
        if not positions:
            return False

        reel_index, stop_index = self._random.choice(positions)
        current_symbol = candidate.reels[reel_index][stop_index]
        replacements = [symbol for symbol in self._composition_symbols if symbol != current_symbol]
        candidate.reels[reel_index][stop_index] = self._random.choice(replacements)
        return True
