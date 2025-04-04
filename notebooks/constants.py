GENERATOR_PROMPT = """
Create a solution with clear implementation and tests.
Dont return code in a md block, just return code by itself
Format with:
<thoughts>Implementation strategy and approach</thoughts>
<CODE>Implementation code - implementation.py </CODE>
<UNIT_TESTS>Unit tests - test_implementation.py</UNIT_TESTS>
<GHERKIN>Behavior scenarios behavior.feature</GHERKIN>
<STEP_IMPL>Step implementations step.py</STEP_IMPL>

Code is:
project/
  ├── src/
  │   ├── __init__.py
  │   └── implementation.py
  ├── tests/
  │   ├── __init__.py
  │   ├── test_implementation.py
  └── features/
      ├── behavior.feature
      └── steps/
          └── steps.py

"""

EVALUATOR_PROMPT = """
### **Evaluation Criteria**
- **<CODE>**: Check correctness, efficiency, readability, and adherence to best practices.
- **<UNIT_TESTS>**: Assess test coverage, clarity, and effectiveness.
- **<GHERKIN>**: Ensure it clearly defines behavior and aligns with the task.
- **<STEP_IMPL>**: Verify it properly integrates the Gherkin steps with the code.

<evaluation>PASS/NEEDS_IMPROVEMENT/FAIL</evaluation>
<feedback>Specific improvements needed</feedback>
"""
MAX_RETRIES = 3
RETRY_DELAY = 1