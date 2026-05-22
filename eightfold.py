from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


FIXED_OUTPUT_FIELDS = (
    "First_name_last_name",
    "Education",
    "Experiences",
    "Skills",
    "About",
)
LIST_OUTPUT_FIELDS = {"Education", "Experiences", "Skills"}
STRING_OUTPUT_FIELDS = {"First_name_last_name", "About"}


class TransformationError(Exception):
    """Raised when an input payload cannot be matched or transformed."""


@dataclass(slots=True)
class ConfigMatch:
    name: str
    score: int
    config: dict[str, Any]


class SafeDict(dict[str, Any]):
    def __missing__(self, key: str) -> str:
        return ""


class ResumeTransformer:
    def __init__(self, config_dir: str | Path) -> None:
        self.config_dir = Path(config_dir)
        self.configs = self._load_configs()
        self.operations = {
            "copy": self._op_copy,
            "join_non_empty": self._op_join_non_empty,
            "listify": self._op_listify,
            "merge_lists": self._op_listify,
            "combine_education": self._op_listify,
            "template": self._op_template,
            "count_items": self._op_count_items,
            "literal": self._op_literal,
        }

    def transform(self, payload: dict[str, Any]) -> dict[str, Any]:
        match = self.identify_config(payload)
        transformed = self._empty_output()

        for field in FIXED_OUTPUT_FIELDS:
            spec = match.config.get("output", {}).get(field)
            if spec is None:
                continue
            value = self._evaluate_mapping(spec, payload)
            transformed[field] = self._normalize_output(field, value)

        return transformed

    def identify_config(self, payload: dict[str, Any]) -> ConfigMatch:
        matches: list[ConfigMatch] = []

        for config in self.configs:
            score = self._calculate_match_score(config, payload)
            if score >= 0:
                matches.append(ConfigMatch(config["name"], score, config))

        if not matches:
            known = ", ".join(config["name"] for config in self.configs)
            raise TransformationError(
                f"Could not identify a matching config for payload keys {sorted(payload.keys())}. "
                f"Known configs: {known}"
            )

        return max(matches, key=lambda item: item.score)

    def _load_configs(self) -> list[dict[str, Any]]:
        if not self.config_dir.exists():
            raise TransformationError(f"Config directory not found: {self.config_dir}")

        configs: list[dict[str, Any]] = []
        for file_path in sorted(self.config_dir.glob("*.json")):
            with file_path.open("r", encoding="utf-8") as file:
                config = json.load(file)
            config.setdefault("name", file_path.stem)
            config.setdefault("match", {})
            config.setdefault("output", {})
            configs.append(config)

        if not configs:
            raise TransformationError(f"No config files found in {self.config_dir}")

        return configs

    def _calculate_match_score(self, config: dict[str, Any], payload: dict[str, Any]) -> int:
        match_rules = config.get("match", {})
        required_fields = match_rules.get("required_fields", [])
        optional_fields = match_rules.get("optional_fields", [])

        if any(not self._has_value(payload, field) for field in required_fields):
            return -1

        score = len(required_fields) * 100
        score += sum(10 for field in optional_fields if self._has_value(payload, field))
        return score

    def _evaluate_mapping(self, spec: Any, payload: dict[str, Any]) -> Any:
        if isinstance(spec, str):
            return self._resolve_source(payload, spec)

        if not isinstance(spec, dict):
            return spec

        operation_name = spec.get("operation", "copy")
        operation = self.operations.get(operation_name)
        if operation is None:
            raise TransformationError(f"Unsupported operation: {operation_name}")

        return operation(payload, spec)

    def _resolve_source(self, payload: dict[str, Any], source: Any) -> Any:
        if isinstance(source, list):
            for candidate in source:
                value = self._resolve_source(payload, candidate)
                if self._is_non_empty(value):
                    return value
            return None

        if not isinstance(source, str):
            return source

        current: Any = payload
        for part in source.split("."):
            if not isinstance(current, dict) or part not in current:
                return None
            current = current[part]
        return current

    def _has_value(self, payload: dict[str, Any], source: Any) -> bool:
        return self._is_non_empty(self._resolve_source(payload, source))

    @staticmethod
    def _is_non_empty(value: Any) -> bool:
        if value is None:
            return False
        if isinstance(value, str):
            return bool(value.strip())
        if isinstance(value, (list, tuple, set, dict)):
            return bool(value)
        return True

    def _op_copy(self, payload: dict[str, Any], spec: dict[str, Any]) -> Any:
        for source in spec.get("sources", []):
            value = self._resolve_source(payload, source)
            if self._is_non_empty(value):
                return value
        return spec.get("default", "")

    def _op_join_non_empty(self, payload: dict[str, Any], spec: dict[str, Any]) -> str:
        separator = spec.get("separator", " ")
        parts = [
            self._stringify(self._resolve_source(payload, source))
            for source in spec.get("sources", [])
        ]
        return separator.join(part for part in parts if part)

    def _op_listify(self, payload: dict[str, Any], spec: dict[str, Any]) -> list[str]:
        items: list[str] = []
        for source in spec.get("sources", []):
            items.extend(self._flatten_to_strings(self._resolve_source(payload, source)))
        return self._dedupe(items)

    def _op_template(self, payload: dict[str, Any], spec: dict[str, Any]) -> str:
        context: dict[str, Any] = {}
        for key, value_spec in spec.get("context", {}).items():
            if isinstance(value_spec, dict):
                context[key] = self._evaluate_mapping(value_spec, payload)
            else:
                context[key] = self._resolve_source(payload, value_spec)

        normalized_context = {
            key: self._stringify(value) if not isinstance(value, int) else value
            for key, value in context.items()
        }
        return spec.get("template", "").format_map(SafeDict(normalized_context))

    def _op_count_items(self, payload: dict[str, Any], spec: dict[str, Any]) -> int:
        items: list[str] = []
        for source in spec.get("sources", []):
            items.extend(self._flatten_to_strings(self._resolve_source(payload, source)))
        return len(items)

    @staticmethod
    def _op_literal(_: dict[str, Any], spec: dict[str, Any]) -> Any:
        return spec.get("value")

    def _normalize_output(self, field: str, value: Any) -> Any:
        if field in LIST_OUTPUT_FIELDS:
            return self._flatten_to_strings(value)
        if field in STRING_OUTPUT_FIELDS:
            return self._stringify(value)
        return value

    @staticmethod
    def _empty_output() -> dict[str, Any]:
        return {
            "First_name_last_name": "",
            "Education": [],
            "Experiences": [],
            "Skills": [],
            "About": "",
        }

    def _flatten_to_strings(self, value: Any) -> list[str]:
        if value is None:
            return []

        if isinstance(value, (list, tuple, set)):
            items: list[str] = []
            for item in value:
                items.extend(self._flatten_to_strings(item))
            return self._dedupe(items)

        text = self._stringify(value)
        return [text] if text else []

    @staticmethod
    def _dedupe(items: list[str]) -> list[str]:
        seen: set[str] = set()
        ordered: list[str] = []
        for item in items:
            if item not in seen:
                seen.add(item)
                ordered.append(item)
        return ordered

    def _stringify(self, value: Any) -> str:
        if value is None:
            return ""
        if isinstance(value, str):
            return value.strip()
        if isinstance(value, bool):
            return str(value)
        if isinstance(value, (int, float)):
            return str(value)
        if isinstance(value, dict):
            parts = [
                f"{key}: {self._stringify(item)}"
                for key, item in value.items()
                if self._is_non_empty(item)
            ]
            return ", ".join(part for part in parts if part)
        if isinstance(value, (list, tuple, set)):
            return ", ".join(part for part in (self._stringify(item) for item in value) if part)
        return str(value)


def load_payload(file_path: str | Path) -> dict[str, Any]:
    path = Path(file_path)
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def demo_payloads() -> list[dict[str, Any]]:
    return [
        {
            "First_name": "abc",
            "Last_name": "def",
            "Education_details": ["B.Tech - Computer Science"],
            "Master_degree": "M.Tech - AI",
            "Experiences": ["Intern - SE", "Software Engineer"],
            "Skills": ["Python", "SQL", "FastAPI"],
        },
        {
            "Full_name": "Jane Doe",
            "Education_details": ["B.Sc - Information Systems"],
            "Master_degree": "M.Sc - Data Science",
            "Experiences": [
                {"company": "Acme", "role": "Backend Engineer", "years": 2},
                {"company": "Globex", "role": "Senior Engineer", "years": 3},
            ],
            "Programming_languages": ["Python", "Java"],
            "Webframekwroos": ["Django", "React"],
            "Summary": "Backend-focused engineer with product and platform experience.",
        },
    ]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Identify the correct resume config and transform input payloads into a fixed output schema."
    )
    parser.add_argument(
        "--config-dir",
        default=Path(__file__).with_name("eightfold_configs"),
        type=Path,
        help="Directory containing JSON transformation configs.",
    )
    parser.add_argument(
        "--input",
        type=Path,
        help="Path to a JSON input payload. If omitted, built-in demo payloads are transformed.",
    )
    args = parser.parse_args()

    transformer = ResumeTransformer(args.config_dir)
    payloads = [load_payload(args.input)] if args.input else demo_payloads()

    for index, payload in enumerate(payloads, start=1):
        match = transformer.identify_config(payload)
        transformed = transformer.transform(payload)
        print(f"Payload {index} matched config: {match.name}")
        print(json.dumps(transformed, indent=2, ensure_ascii=False))
        print("-" * 60)


if __name__ == "__main__":
    main()
