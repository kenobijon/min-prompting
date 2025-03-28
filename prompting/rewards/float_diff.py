import time
from typing import List

import numpy as np
from sympy.parsing.sympy_parser import parse_expr

from prompting.rewards.reward import BaseRewardModel, BatchRewardOutput
from shared.dendrite import DendriteResponseEvent


class FloatDiffModel(BaseRewardModel):
    @property
    def name(self) -> str:
        return "float_diff"

    def __init__(self, **kwargs):
        super().__init__()

    @staticmethod
    def extract_number(text: str) -> float:
        """Extract a number from a string."""
        # loop over all words reversed and try to cast as a float, break when you find the first one
        words = text.split()
        for word in reversed(words):
            cleaned = word.strip(".").replace(",", "")
            try:
                return float(parse_expr(cleaned).evalf())
            except Exception:
                # fall back to simpler parsing if required
                try:
                    return float(cleaned)
                except Exception:
                    continue

    @staticmethod
    def math_score(reference: str, completion: str) -> float:
        """Compute a score based on the difference between a reference and a completion."""
        # Convert the strings to a float
        reference = float(reference)
        pred = FloatDiffModel.extract_number(completion)
        if pred is None:
            return 0.0

        try:
            if pred == reference:
                return 1.0
            # Compute the difference
            diff = (reference - pred) / (reference + 1e-10)
            # Make sure the difference is between 0 and 1
            diff = min(abs(diff), 1)
            # Clip any very small scores
            if diff > 0.999:
                diff = 1.0
            return 1.0 - diff
        except Exception:
            return 0.0

    async def reward(self, reference: str, response_event: DendriteResponseEvent, **kwargs) -> BatchRewardOutput:
        """Compute difference scores given a completion and reference pair."""
        rewards = []
        timings = []
        completions: List[str] = response_event.completions

        for completion in completions:
            t0 = time.time()
            reward = self.math_score(reference, completion)
            timings.append(time.time() - t0)
            rewards.append(reward)

        output = BatchRewardOutput(
            rewards=np.array(rewards),
            timings=np.array(timings),
        )
        return output
