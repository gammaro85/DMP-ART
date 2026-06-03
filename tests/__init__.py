"""Control unittest discovery so script-style diagnostics are not imported as tests."""

import importlib
import unittest


DISCOVERABLE_MODULES = (
    'tests.test_session_history',
    'tests.test_extractor_optimization',
    'tests.test_placeholder_functionality',
)


def load_tests(loader, standard_tests, pattern):
    suite = unittest.TestSuite()

    for module_name in DISCOVERABLE_MODULES:
        module = importlib.import_module(module_name)
        suite.addTests(loader.loadTestsFromModule(module))

    return suite
