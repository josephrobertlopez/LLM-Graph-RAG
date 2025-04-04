from classes import GenerationResult
from constants import *
from typing import Optional, Tuple
from time import sleep
from util import *
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate(prompt: str, task: str, context: str = "") -> GenerationResult:
    """Generate solution via separate LLM calls per component."""
    full_prompt = f"{prompt}\n{context}\nTask: {task}" if context else f"{prompt}\nTask: {task}"
    
    # Get required components first
    thoughts = get_tag_content(full_prompt, "thoughts", required=True) or ""
    code = get_tag_content(full_prompt, "CODE", required=True) or ""
    
    # Get optional components
    result = GenerationResult(
        thoughts=thoughts,
        code=code,
        unit_tests=get_tag_content(full_prompt, "UNIT_TESTS"),
        gherkin=get_tag_content(full_prompt, "GHERKIN"),
        step_impl=get_tag_content(full_prompt, "STEP_IMPL")
    )
    
    logger.info("=== Generated Solution ===")
    for key, value in result.items():
        if value:
            logger.info(f"{key}:\n{value}\n")
            
    return result

def evaluate(result: GenerationResult, task: str) -> Tuple[str, str]:
    """Evaluate the generated solution."""
    eval_prompt = f"{EVALUATOR_PROMPT}\nTask: {task}\nImplementation:\n{result['code']}"
    
    status = get_tag_content(eval_prompt, "evaluation") or "FAIL"
    feedback = get_tag_content(eval_prompt, "feedback") or "Evaluation failed"
    
    logger.info(f"Evaluation: {status}")
    logger.info(f"Feedback: {feedback}")
    
    return status, feedback
def loop(task: str, max_iterations: int = 3) -> GenerationResult:
    """Main improvement loop."""
    if not task:
        raise ValueError("Task cannot be empty")
        
    solution = generate(GENERATOR_PROMPT, task)
    iterations = 0
    
    while iterations < max_iterations:
        status, feedback = evaluate(solution, task)
        if status == "PASS":
            return solution
            
        context = f"Previous attempt:\n{solution['code']}\nFeedback: {feedback}"
        solution = generate(GENERATOR_PROMPT, task, context)
        iterations += 1
        
    logger.warning(f"Max iterations ({max_iterations}) reached")
    return solution
# Configure logging

def get_tag_content(prompt: str, tag: str, required: bool = False) -> Optional[str]:
    """Make LLM call for specific tag with retries.
    
    Args:
        prompt: Base prompt
        tag: XML tag to extract
        required: Whether tag content is required
        
    Returns:
        Extracted content or None if failed/not required
    """
    tag_prompt = f"{prompt}\nProvide content for <{tag}> tag"
    
    for attempt in range(MAX_RETRIES):
        try:
            response = llm_call(tag_prompt)
            content = extract_xml(response, tag)
            if content:
                return content
            elif required:
                raise ValueError(f"Required tag {tag} not found")
            return None
        except Exception as e:
            logger.warning(f"Attempt {attempt + 1} failed for {tag}: {e}")
            if attempt < MAX_RETRIES - 1:
                sleep(RETRY_DELAY)
    return None