import json
import tempfile
import unittest
from pathlib import Path

from scripts.validate_topic import validate_topic_candidate, mark_topic_used, load_used_topic_ids


VALID_TOPIC = {
    "id": "chaos-rising-competence-before-rebellion",
    "book_slug": "chaos-rising",
    "official_title": "Chaos Rising",
    "official_year": 2082,
    "topic": "Competence before rebellion",
    "thesis": "Chaos Rising frames resistance as earned competence before it ever becomes open revolt.",
    "source_chunks": ["chaos-rising:0000", "chaos-rising:0001"],
    "concrete_details": ["curfew pressure", "technical study", "Freemen recruitment"],
    "why_readers_care": "This sells the book as survival fiction built on skill and pressure.",
}


class TopicValidationTests(unittest.TestCase):
    def test_validate_topic_rejects_reused_topic_id(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "used_topics.json"
            ledger.write_text(json.dumps({"used_topics": [{"id": VALID_TOPIC["id"]}]}), encoding="utf-8")

            result = validate_topic_candidate(VALID_TOPIC, used_topics_path=ledger, available_chunk_ids=set(VALID_TOPIC["source_chunks"]))

            self.assertFalse(result["ok"])
            self.assertIn("already used", "\n".join(result["errors"]))

    def test_validate_topic_requires_two_chunks_three_details_and_specific_thesis(self):
        topic = dict(VALID_TOPIC)
        topic["source_chunks"] = ["chaos-rising:0000"]
        topic["concrete_details"] = ["curfew"]
        topic["thesis"] = "This book has themes."

        result = validate_topic_candidate(topic, used_topics_path=None, available_chunk_ids={"chaos-rising:0000"})

        self.assertFalse(result["ok"])
        joined = "\n".join(result["errors"])
        self.assertIn("at least 2 source chunks", joined)
        self.assertIn("at least 3 concrete details", joined)
        self.assertIn("non-generic thesis", joined)

    def test_mark_topic_used_persists_ledger(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "used_topics.json"
            mark_topic_used(VALID_TOPIC, ledger)

            self.assertEqual(load_used_topic_ids(ledger), {VALID_TOPIC["id"]})
    def test_mark_topic_used_accepts_published_draft_topic_id(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "used_topics.json"
            draft = dict(VALID_TOPIC)
            draft["topic_id"] = draft.pop("id")
            mark_topic_used(draft, ledger)

            self.assertEqual(load_used_topic_ids(ledger), {VALID_TOPIC["id"]})


if __name__ == "__main__":
    unittest.main()
