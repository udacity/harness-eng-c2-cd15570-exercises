"""Deterministic tests for the completed skill-tool boundary."""

import json
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from agent import SKILL_TOOL, resolve_skill_call


class SkillToolContractTests(unittest.TestCase):
    def test_schema_is_strict_and_closed(self) -> None:
        parameters = SKILL_TOOL["parameters"]
        self.assertTrue(SKILL_TOOL["strict"])
        self.assertEqual(parameters["required"], ["skill_name"])
        self.assertFalse(parameters["additionalProperties"])

    def test_valid_call_loads_the_allowlisted_skill(self) -> None:
        item = SimpleNamespace(
            name="load_skill",
            arguments=json.dumps({"skill_name": "brand_voice"}),
            call_id="call-valid",
        )
        with patch(
            "agent.load_skill",
            return_value=("skill instructions", Path("skills/brand_voice/SKILL.md")),
        ) as loader:
            record, output = resolve_skill_call(item, {"brand_voice": {}})

        loader.assert_called_once_with("brand_voice", {"brand_voice": {}})
        self.assertTrue(record["loaded"])
        self.assertEqual(record["skill"], "brand_voice")
        self.assertEqual(output["output"], "skill instructions")

    def test_extra_argument_is_rejected_before_file_loading(self) -> None:
        item = SimpleNamespace(
            name="load_skill",
            arguments=json.dumps(
                {"skill_name": "brand_voice", "unexpected": "value"}
            ),
            call_id="call-extra",
        )
        with patch("agent.load_skill") as loader:
            record, output = resolve_skill_call(item, {"brand_voice": {}})

        loader.assert_not_called()
        self.assertFalse(record["loaded"])
        self.assertIsNone(record["path"])
        self.assertEqual(record["chars"], 0)
        self.assertIn("arguments must contain only skill_name", output["output"])

    def test_non_object_arguments_are_rejected_before_file_loading(self) -> None:
        item = SimpleNamespace(
            name="load_skill",
            arguments=json.dumps(["brand_voice"]),
            call_id="call-list",
        )
        with patch("agent.load_skill") as loader:
            record, output = resolve_skill_call(item, {"brand_voice": {}})

        loader.assert_not_called()
        self.assertFalse(record["loaded"])
        self.assertTrue(output["output"].startswith("ERROR:"))


if __name__ == "__main__":
    unittest.main()
