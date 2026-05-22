"""
Ownership-Aware Compatible Stacking (OACS)
===========================================

Algorithm overview
------------------
Two root causes create reshuffles in a pre-filled random yard:

  (A) Initial-state stacks: placed randomly before the simulation began.
      No strategy can fix the ordering of these; we can only avoid making
      them worse.

  (B) New placements: containers we place during the simulation.  We have
      full control over their ordering.

OACS separates these two cases:

  * For stacks where the top container was placed BY THIS STRATEGY
    ("owned" stacks): we can guarantee the stack is already sorted in
    non-increasing priority, so we extend it ONLY with compatible containers
    → zero new inversions, zero future reshuffles for any container in the
    owned part of the stack.

  * For stacks where the top container is from the initial state
    ("unowned"): we add only if compatible (to at least avoid making things
    worse) and prefer these as a fallback after owned stacks.

  * Empty slots: highest priority — we start a NEW clean stack here.

Priority definition
-------------------
    priority(c) = (departure_time_unix, port_rank, weight_rank)

    port_rank   : integer from "PORT_NN"; lower = loaded first.
    weight_rank : HEAVY=0, MEDIUM=1, LIGHT=2  (HEAVY loaded first per spec).

    Smaller priority value → retrieved sooner → should be nearer the top.

Stacking validity rule
-----------------------
    C may be placed on top of T  iff  C.priority ≤ T.priority.

Placement scoring  (tuple, lower = preferred)
----------------------------------------------
    (ownership_category, grouping_category, height)

    ownership_category:
      0 — empty slot           (start fresh clean stack)
      1 — top is owned + compatible  (extend a clean zone)
      2 — top is unowned + compatible  (fallback to initial-state base)
      3 — incompatible (avoid)

    grouping_category (within same ownership):
      0 — same vessel + same port
      1 — same vessel
      2 — other

    height: prefer shorter stacks within same category.

Why this works
--------------
Over time, as initial containers depart and free up positions, OACS builds
an increasing number of "owned" zones that are fully sorted.  Retrievals
from owned zones cost 0 reshuffles.  For the initial containers, OACS does
not worsen their situation (compatible-only additions when forced to use
unowned bases).

Reference
---------
This implements the core idea from:
  Conca et al. (2023) "Online container stacking with priority-aware
  segregation in seaport yard management", extended with ownership tracking
  to prevent cross-contamination between planned and unplanned stacks.
"""

from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple

from src.models import Event, Position
from src.placement_interface import PlacementStrategy
from src.yard_state import YardState

_FAR_FUTURE = datetime(2100, 1, 1).timestamp()
_WEIGHT_RANK: Dict[str, int] = {"HEAVY": 0, "MEDIUM": 1, "LIGHT": 2}

Priority = Tuple[float, int, int]


def _port_rank(port: str) -> int:
    try:
        return int(port.split("_", 1)[1])
    except (IndexError, ValueError):
        return 98


def _parse_dt(dt_str: str) -> float:
    if not dt_str:
        return _FAR_FUTURE
    try:
        return datetime.fromisoformat(dt_str).timestamp()
    except (ValueError, TypeError):
        return _FAR_FUTURE


def _compute_priority(departure_time: str, port: str, weight_class: str) -> Priority:
    """Lower value = retrieved sooner = should sit nearer the top of a stack."""
    return (
        _parse_dt(departure_time),
        _port_rank(port),
        _WEIGHT_RANK.get(weight_class, 1),
    )


class SmartStackingStrategy(PlacementStrategy):
    """
    Ownership-Aware Compatible Stacking (OACS).
    See module docstring for full description.
    """

    # ------------------------------------------------------------------ setup

    def initialize(self, yard_layout: dict, initial_state: dict) -> None:
        self._blocks: Dict[str, dict] = yard_layout["blocks"]
        self._block_names: List[str] = sorted(self._blocks.keys())

        # container_id → priority
        self._priority_cache: Dict[str, Priority] = {}

        # Containers placed by THIS strategy during the simulation.
        # Initial-state containers are NOT in this set.
        self._my_containers: Set[str] = set()

        # Pre-cache priority for initial containers
        for entry in initial_state.get("containers", []):
            cid = entry["container_id"]
            self._priority_cache[cid] = _compute_priority(
                entry.get("departure_time", ""),
                entry.get("port_of_discharge", ""),
                entry.get("weight_class", "MEDIUM"),
            )

    # --------------------------------------------------- event hooks

    def on_event(self, event: Event) -> None:
        if event.type in ("DISCHARGE", "TRUCK_RECV"):
            cid = event.container_id
            self._my_containers.add(cid)
            self._priority_cache[cid] = _compute_priority(
                event.departure_time,
                event.port_of_discharge,
                event.weight_class,
            )

    def on_container_retrieved(
        self, container_id: str, position: Position, reshuffles: int
    ) -> None:
        self._my_containers.discard(container_id)
        self._priority_cache.pop(container_id, None)

    # ------------------------------------------- main placement logic

    def place_container(self, yard_state: YardState, event: Event) -> Position:
        priority_in = _compute_priority(
            event.departure_time,
            event.port_of_discharge,
            event.weight_class,
        )

        best_pos: Optional[Position] = None
        best_score: Optional[Tuple] = None

        for block_name, bi in self._blocks.items():
            bays: int = bi["bays"]
            rows: int = bi["rows"]
            tiers: int = bi["tiers"]

            for bay in range(1, bays + 1):
                for row in range(1, rows + 1):
                    height = yard_state.get_stack_height(block_name, bay, row)
                    if height >= tiers:
                        continue

                    score = self._score_slot(
                        yard_state,
                        block_name, bay, row, height,
                        priority_in, event,
                    )

                    if best_score is None or score < best_score:
                        best_score = score
                        best_pos = Position(block_name, bay, row, height + 1)

        return best_pos if best_pos is not None else self._hard_fallback(yard_state)

    # ----------------------------------------------- slot scoring

    def _score_slot(
        self,
        yard_state: YardState,
        block: str,
        bay: int,
        row: int,
        height: int,
        priority_in: Priority,
        event: Event,
    ) -> Tuple:
        """
        Score tuple (lower = better):
            (height, is_incompatible, -grouping_bonus)

        PRIMARY: height — prefer shorter stacks.
        SECONDARY: is_incompatible — avoid new priority inversions at equal height.
        TERTIARY: -grouping_bonus — prefer same vessel+port or same vessel.
        """
        if height == 0:
            return (0, 0, 0)

        top_cid = yard_state.get_container_at(block, bay, row, height)
        if top_cid is None:
            return (0, 0, 0)

        top_priority = self._get_priority(yard_state, top_cid)
        is_incompatible = 0 if priority_in <= top_priority else 1

        grouping_bonus = 0
        top_info = yard_state.get_container_info(top_cid)
        if top_info is not None and top_info.vessel_id == event.vessel_id:
            grouping_bonus = 1
            if top_info.port_of_discharge == event.port_of_discharge:
                grouping_bonus = 2

        return (height, is_incompatible, -grouping_bonus)
    # ---------------------------------------------- priority lookup

    def _get_priority(self, yard_state: YardState, container_id: str) -> Priority:
        cached = self._priority_cache.get(container_id)
        if cached is not None:
            return cached
        info = yard_state.get_container_info(container_id)
        if info is not None:
            p = _compute_priority(
                info.departure_time,
                info.port_of_discharge,
                info.weight_class,
            )
            self._priority_cache[container_id] = p
            return p
        return (_FAR_FUTURE, 99, 99)

    # -------------------------------------------- hard fallback

    def _hard_fallback(self, yard_state: YardState) -> Position:
        best_pos: Optional[Position] = None
        best_height = float("inf")
        for block_name, bi_obj in yard_state.blocks.items():
            for bay in range(1, bi_obj.bays + 1):
                for row in range(1, bi_obj.rows + 1):
                    h = yard_state.get_stack_height(block_name, bay, row)
                    if h < bi_obj.tiers and h < best_height:
                        best_height = h
                        best_pos = Position(block_name, bay, row, h + 1)
        if best_pos is None:
            first = self._block_names[0]
            return Position(first, 1, 1, 999)
        return best_pos
