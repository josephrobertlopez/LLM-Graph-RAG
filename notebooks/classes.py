from typing import TypedDict, Optional, Tuple, Dict, List


class Config:
    TEST_DIR = "test_output"
    SRC_DIR = f"{TEST_DIR}/src"
    TEST_DIR_UNIT = f"{TEST_DIR}/tests"
    FEATURE_DIR = f"{TEST_DIR}/features"
    STEPS_DIR = f"{FEATURE_DIR}/steps"
    TEST_TIMEOUT = 30  # seconds

# TypedDict for generation results
class GenerationResult(TypedDict):
    thoughts: str
    code: str  # Required
    unit_tests: Optional[str]  
    gherkin: Optional[str]
    step_impl: Optional[str]
