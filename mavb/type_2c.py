import itertools

from .ratios import RATIO_1_TO_1, RATIO_2_TO_1
from .levels import create_atrial_level
from .levels import create_pattern_level
from .levels import create_changing_1_to_1_level
from .levels import extend_variable_pattern
from .solver import get_signals_from_intervals
from .solver import forward_simulate_solution
from .solver import fit_parameters


def simulate_signals(solution, l1_block_pattern, l2_block_pattern):
    A = create_propagation_matrix(
        l1_block_pattern, l2_block_pattern, len(l2_block_pattern))
    return forward_simulate_solution(solution, A)


def solve(real_intervals, l1_block_pattern, l2_block_pattern):
    real_signals = get_signals_from_intervals(real_intervals)

    A = create_propagation_matrix(
        l1_block_pattern, l2_block_pattern, len(real_signals))

    return fit_parameters(real_signals, A, levels=2)


def create_propagation_matrix(l1_block_pattern, l2_block_pattern, total_signals):
    atrium_length = sum(l1_block_pattern) + len(l1_block_pattern)
    atrial_constraints = create_atrial_level(atrium_length)

    av_length = sum(l1_block_pattern)
    av_constraints = create_pattern_level(
        atrial_constraints, l1_block_pattern, total_signals=av_length, level=1)

    v_constraints = create_changing_1_to_1_level(
        av_constraints, l2_block_pattern, total_signals=total_signals, level=2)

    return v_constraints


def extend_block_pattern(l1_pattern, l2_pattern):
    return itertools.chain(
        extend_l1_pattern(l1_pattern, [*l2_pattern, RATIO_1_TO_1]),
        extend_l1_pattern(l1_pattern, [*l2_pattern, RATIO_2_TO_1]),
    )


def extend_l1_pattern(l1_pattern, l2_pattern):
    l1_conducted = sum(l1_pattern)
    l2_consumed = len(l2_pattern) + sum(l2_pattern)

    if l2_consumed <= l1_conducted:
        return [(l1_pattern, l2_pattern)]
    else:
        l1_extensions = extend_variable_pattern(l1_pattern)
        extensions = [extend_l1_pattern(l1, l2_pattern)
                      for l1 in l1_extensions]
        return itertools.chain(*extensions)
