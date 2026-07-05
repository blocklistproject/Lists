import unittest
from unittest.mock import patch

from scripts.remove_domain import DomainRemover


class TestDomainRemover(unittest.TestCase):
    def test_get_buildable_lists_skips_non_build_targets(self):
        remover = DomainRemover()
        remover.affected_lists = {"abuse", "everything", "malware"}

        with patch("scripts.remove_domain.load_config", return_value={"lists": {"abuse": {}, "malware": {}}}):
            self.assertEqual(remover.get_buildable_lists(), {"abuse", "malware"})


if __name__ == "__main__":
    unittest.main()
