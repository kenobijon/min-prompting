from prompting.mock import MockPipeline
from prompting.llms.vllm_llm import vLLM_LLM, vLLMPipeline


def mock_llm_pipeline():
    return MockPipeline("This is just another test.")


def llms():
    pipeline = MockPipeline("This is just another test.")
    llms = [vLLM_LLM(pipeline, "")]
    return llms


def pipelines():
    # Return pipeline types to be instantiated downstream
    return [vLLMPipeline]
