from typing import Optional, Tuple, Dict, List
import os
import subprocess
import shutil
from pathlib import Path
from contextlib import contextmanager
from datetime import datetime

from classes import Config, GenerationResult

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def validate_dependencies() -> List[str]:
    """Validate required test dependencies are installed"""
    missing = []
    try:
        import pytest
    except ImportError:
        missing.append("pytest")
    try:
        import behave
    except ImportError:
        missing.append("behave")
    return missing

def validate_file_content(content: Optional[str], file_type: str) -> bool:
    """Basic validation of file contents"""
    if not content:
        return False
    if file_type == "implementation":
        return "class" in content or "def" in content
    elif file_type == "unit_tests":
        return "test" in content and "assert" in content
    elif file_type == "feature":
        return "Feature:" in content and "Scenario:" in content
    elif file_type == "steps":
        return "given" in content.lower() or "when" in content.lower()
    return False


@contextmanager
def setup_test_env():
    """Setup and cleanup test environment"""
    try:
        # Cleanup previous files
        if os.path.exists(Config.TEST_DIR):
            shutil.rmtree(Config.TEST_DIR)
            
        # Create directories
        for dir_path in [Config.SRC_DIR, Config.TEST_DIR_UNIT, 
                         Config.FEATURE_DIR, Config.STEPS_DIR]:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
            init_file_path = Path(dir_path) / "__init__.py"
            if not init_file_path.exists():
                init_file_path.touch()  # Create an empty __init__.py file if it doesn't exist

        
        # Check dependencies
        missing = validate_dependencies()
        if missing:
            raise EnvironmentError(f"Missing dependencies: {', '.join(missing)}")
            
        yield
    finally:
        if os.path.exists(Config.TEST_DIR):
            # shutil.rmtree(Config.TEST_DIR)
            pass

def run_tests(files: Dict[str, str]) -> Tuple[bool, str]:
    """Run pytest and behave tests with timeout"""
    output = []
    success = True

    def run_subprocess(cmd: List[str], name: str) -> Tuple[bool, str]:
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=Config.TEST_TIMEOUT
            )
            return result.returncode == 0, result.stdout
        except subprocess.TimeoutExpired:
            return False, f"{name} timed out after {Config.TEST_TIMEOUT}s"
        except Exception as e:
            return False, f"{name} error: {str(e)}"

    if "unit_tests" in files:
        success_pytest, out_pytest = run_subprocess(
            ["pytest", files["unit_tests"]], "PyTest")
        output.append(f"PyTest Results:\n{out_pytest}")
        success &= success_pytest

    if "feature" in files:
        success_behave, out_behave = run_subprocess(
            ["behave", Config.FEATURE_DIR], "Behave")
        output.append(f"Behave Results:\n{out_behave}")
        success &= success_behave

    return success, "\n".join(output)

def save_test_files(result: GenerationResult, iteration: int) -> Dict[str, str]:
    """Save generated code and tests to versioned files."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    iter_dir = f"{Config.TEST_DIR}/iteration_{iteration}_{timestamp}"
    
    os.makedirs(iter_dir, exist_ok=True)
    
    file_mapping = {
        "implementation": (result["code"], f"{Config.SRC_DIR}/implementation.py"),
        "unit_tests": (result["unit_tests"], f"{Config.TEST_DIR_UNIT}/test_implementation.py"),
        "feature": (result["gherkin"], f"{Config.FEATURE_DIR}/behavior.feature"),
        "steps": (result["step_impl"], f"{Config.STEPS_DIR}/steps.py")
    }

    files = {}
    for file_type, (content, path) in file_mapping.items():
        if validate_file_content(content, file_type):
            try:
                with open(path, "w") as f:
                    f.write(content)
                files[file_type] = path
            except IOError as e:
                logger.error(f"Failed to write {file_type}: {e}")
        else:
            logger.warning(f"Invalid {file_type} content, skipping")

    return files, iter_dir
