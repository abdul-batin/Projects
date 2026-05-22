"""Unit tests for SmartStackingStrategy (OACS)."""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models import Container, Event, Position
from src.yard_state import YardState
from solution.smart_stacking import SmartStackingStrategy, _compute_priority, _port_rank, _parse_dt


# --------------------------------------------------------------------------- fixtures


@pytest.fixture
def layout():
    return {
        "blocks": {
            "A": {"bays": 4, "rows": 2, "tiers": 5},
            "B": {"bays": 4, "rows": 2, "tiers": 5},
        }
    }


@pytest.fixture
def initial_state():
    return {"containers": []}


@pytest.fixture
def strategy(layout, initial_state):
    s = SmartStackingStrategy()
    s.initialize(layout, initial_state)
    return s


@pytest.fixture
def yard(layout):
    return YardState(layout)


def _event(cid, dep_time, port="PORT_01", weight="MEDIUM", etype="DISCHARGE"):
    return Event(
        event_id=1,
        timestamp="2025-01-01T00:00:00",
        type=etype,
        container_id=cid,
        size=20,
        weight_class=weight,
        vessel_id="VSL001",
        port_of_discharge=port,
        departure_time=dep_time,
    )


def _container(cid, dep_time, port="PORT_01", weight="MEDIUM"):
    return Container(
        container_id=cid,
        size=20,
        weight_class=weight,
        vessel_id="VSL001",
        port_of_discharge=port,
        departure_time=dep_time,
    )


# --------------------------------------------------------------------------- priority helpers


def test_port_rank():
    assert _port_rank("PORT_01") == 1
    assert _port_rank("PORT_15") == 15
    assert _port_rank("UNKNOWN") == 98


def test_compute_priority_ordering():
    """Earlier departure → lower priority value → should be nearer to stack top."""
    p_early = _compute_priority("2025-01-05T00:00:00", "PORT_01", "HEAVY")
    p_late = _compute_priority("2025-01-20T00:00:00", "PORT_01", "HEAVY")
    assert p_early < p_late


def test_weight_rank_in_priority():
    """HEAVY leaves first (loaded first) → lower weight_rank → lower priority value."""
    p_heavy = _compute_priority("2025-01-10T00:00:00", "PORT_01", "HEAVY")
    p_medium = _compute_priority("2025-01-10T00:00:00", "PORT_01", "MEDIUM")
    p_light = _compute_priority("2025-01-10T00:00:00", "PORT_01", "LIGHT")
    assert p_heavy < p_medium < p_light


def test_port_rank_in_priority():
    """Lower port number → loaded first → lower priority value."""
    p01 = _compute_priority("2025-01-10T00:00:00", "PORT_01", "MEDIUM")
    p10 = _compute_priority("2025-01-10T00:00:00", "PORT_10", "MEDIUM")
    assert p01 < p10


# --------------------------------------------------------------------------- basic placement


def test_places_on_empty_slot(strategy, yard):
    ev = _event("C001", "2025-01-10T00:00:00")
    strategy.on_event(ev)
    pos = strategy.place_container(yard, ev)

    assert pos is not None
    assert yard.is_position_valid(pos), f"Returned invalid position: {pos}"
    assert pos.tier == 1  # empty yard → tier 1


def test_no_constraint_violation(strategy, yard):
    for i in range(1, 6):
        ev = _event(f"C{i:03d}", "2025-01-10T00:00:00")
        strategy.on_event(ev)
        pos = strategy.place_container(yard, ev)
        assert pos is not None
        assert yard.is_position_valid(pos)
        yard.place_container(ev.to_container(), pos)


def test_returns_valid_position_when_yard_full(layout, initial_state):
    """Strategy must not crash on a nearly-full yard."""
    strat = SmartStackingStrategy()
    strat.initialize(layout, initial_state)
    yard = YardState(layout)

    # Fill all but one slot
    cnt = 0
    for block, bi in layout["blocks"].items():
        for bay in range(1, bi["bays"] + 1):
            for row in range(1, bi["rows"] + 1):
                for tier in range(1, bi["tiers"] + 1):
                    cid = f"FILL{cnt:04d}"
                    c = _container(cid, "2025-01-10T00:00:00")
                    yard.place_container(c, Position(block, bay, row, tier))
                    cnt += 1
                    if cnt >= (bi["bays"] * bi["rows"] * bi["tiers"] * 2) - 1:
                        break  # leave one slot per test
                if cnt >= 39:
                    break
            if cnt >= 39:
                break
        if cnt >= 39:
            break

    ev = _event("CNEW", "2025-01-10T00:00:00")
    strat.on_event(ev)
    # Should not raise, should return something (even if invalid due to full yard)
    try:
        pos = strat.place_container(yard, ev)
    except Exception as e:
        pytest.fail(f"Strategy raised exception on nearly-full yard: {e}")


# --------------------------------------------------------------------------- stacking rule


def test_compatible_placement_preferred(strategy, yard):
    """When a compatible slot exists at the same height as an incompatible one,
    strategy should choose compatible."""
    # Put a LATE-departure container in A, bay 1, row 1, tier 1
    late = _container("LATE", "2025-01-30T00:00:00")
    yard.place_container(late, Position("A", 1, 1, 1))

    # Put an EARLY-departure container in A, bay 2, row 1, tier 1
    early = _container("EARLY", "2025-01-05T00:00:00")
    yard.place_container(early, Position("A", 2, 1, 1))

    # New container departs on Jan 15 (between early and late)
    # Compatible on top of late (Jan 30 base)? Jan 15 < Jan 30 → YES it's compatible
    # Compatible on top of early (Jan 5 base)? Jan 15 > Jan 5 → NOT compatible
    ev = _event("NEW", "2025-01-15T00:00:00")
    strategy.on_event(ev)
    strategy._priority_cache["LATE"] = _compute_priority("2025-01-30T00:00:00", "PORT_01", "MEDIUM")
    strategy._priority_cache["EARLY"] = _compute_priority("2025-01-05T00:00:00", "PORT_01", "MEDIUM")

    pos = strategy.place_container(yard, ev)
    # Strategy should either pick an empty slot (height=0) or the compatible one (bay 1 over LATE)
    # It MUST NOT pick A/bay2/row1 (that would be incompatible since Jan 15 > Jan 5)
    if pos.block == "A" and pos.bay == 2 and pos.row == 1:
        pytest.fail(
            f"Strategy chose incompatible slot on top of EARLY container; got {pos}"
        )


def test_compatibility_check_correct():
    """Verify _compute_priority gives correct ordering for the stacking rule."""
    # If C.priority <= T.priority → compatible (C retrieved no later than T)
    p_c = _compute_priority("2025-01-15T00:00:00", "PORT_01", "MEDIUM")
    p_t = _compute_priority("2025-01-30T00:00:00", "PORT_01", "MEDIUM")
    assert p_c <= p_t  # C leaves sooner → compatible (C can go on top of T)

    p_c2 = _compute_priority("2025-01-30T00:00:00", "PORT_01", "MEDIUM")
    p_t2 = _compute_priority("2025-01-15T00:00:00", "PORT_01", "MEDIUM")
    assert not (p_c2 <= p_t2)  # C leaves later → incompatible (would cause reshuffle)


# --------------------------------------------------------------------------- priority cache


def test_priority_cached_on_event(strategy):
    ev = _event("C001", "2025-01-10T00:00:00")
    strategy.on_event(ev)
    assert "C001" in strategy._priority_cache
    p = strategy._priority_cache["C001"]
    expected = _compute_priority("2025-01-10T00:00:00", "PORT_01", "MEDIUM")
    assert p == expected


def test_priority_cleared_on_retrieval(strategy, yard):
    ev = _event("C001", "2025-01-10T00:00:00")
    strategy.on_event(ev)
    pos = strategy.place_container(yard, ev)
    yard.place_container(ev.to_container(), pos)

    strategy.on_container_retrieved("C001", pos, 0)
    assert "C001" not in strategy._priority_cache


def test_initial_state_priority_seeded():
    """Containers in initial state should have priorities seeded at init."""
    layout = {"blocks": {"A": {"bays": 4, "rows": 2, "tiers": 5}}}
    init = {
        "containers": [
            {
                "container_id": "IC001",
                "position": {"block": "A", "bay": 1, "row": 1, "tier": 1},
                "size": 20,
                "weight_class": "HEAVY",
                "vessel_id": "VSL001",
                "port_of_discharge": "PORT_03",
                "departure_time": "2025-01-15T00:00:00",
            }
        ]
    }
    s = SmartStackingStrategy()
    s.initialize(layout, init)
    assert "IC001" in s._priority_cache
    p = s._priority_cache["IC001"]
    expected = _compute_priority("2025-01-15T00:00:00", "PORT_03", "HEAVY")
    assert p == expected


# --------------------------------------------------------------------------- integration


def test_no_violations_on_100_placements(layout, initial_state):
    """Run 100 placements and verify no hard constraint violations."""
    strat = SmartStackingStrategy()
    strat.initialize(layout, initial_state)
    yard = YardState(layout)

    import random
    random.seed(42)
    vessels = ["VSL001", "VSL002"]
    ports = ["PORT_01", "PORT_02", "PORT_03"]
    weights = ["LIGHT", "MEDIUM", "HEAVY"]
    dates = [
        "2025-01-05T00:00:00",
        "2025-01-10T00:00:00",
        "2025-01-20T00:00:00",
        "2025-01-30T00:00:00",
    ]

    violations = 0
    for i in range(100):
        ev = Event(
            event_id=i,
            timestamp="2025-01-01T00:00:00",
            type="DISCHARGE",
            container_id=f"C{i:03d}",
            size=20,
            weight_class=random.choice(weights),
            vessel_id=random.choice(vessels),
            port_of_discharge=random.choice(ports),
            departure_time=random.choice(dates),
        )
        strat.on_event(ev)
        pos = strat.place_container(yard, ev)
        if not yard.is_position_valid(pos):
            violations += 1
        else:
            yard.place_container(ev.to_container(), pos)

    assert violations == 0, f"{violations} constraint violation(s) out of 100 placements"
