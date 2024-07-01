import random
import bittensor as bt
from dataclasses import dataclass
from prompting.tasks import Task
import difflib


def diff(query, reference):
    """Get the diff between two strings."""
    return "\n".join(difflib.unified_diff(query.splitlines(), reference.splitlines()))


@dataclass
class DebuggingTask(Task):
    name = "debugging"
    desc = "get help with debugging"
    goal = "ask for help fixing broken code."

    reward_definition = [dict(name="diff", weight=1.0)]

    penalty_definition = []

    static_reference = True
    static_query = True

    def __init__(self, llm_pipeline, context, create_reference=True):
        self.context = context

        # No LLM involved in generating the query, we just apply some language-independent corruption to the code
        self.query = corrupt(
            context.content,
            n_remove=random.randint(1, 3),
            n_swap=random.randint(0, 2),
            sep=random.choices(["", " ", "\n"], weights=[0.3, 0.6, 0.1], k=1)[0],
        )
        self.reference = context.content
        self.delimiter = "```"
        self.topic = context.title
        self.subtopic = context.subtopic
        self.tags = context.tags

    def format_challenge(self, challenge):
        return f"{challenge}\n{self.delimiter}\n{self.query}\n{self.delimiter}"
