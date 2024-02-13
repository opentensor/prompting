# The MIT License (MIT)
# Copyright © 2024 Yuma Rao

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the “Software”), to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of
# the Software.

# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

import time
import bittensor as bt
import argparse

# Bittensor Miner Template:
from prompting.protocol import StreamPromptingSynapse

# import base miner class which takes care of most of the boilerplate
from prompting.base.prompting_miner import BaseStreamPromptingMiner
from dotenv import load_dotenv, find_dotenv
from prompting.miners.agents import SingleActionAgent, ReactAgent
from langchain.callbacks import get_openai_callback
from prompting.miners.utils import OpenAIUtils


class AgentMiner(BaseStreamPromptingMiner, OpenAIUtils):
    """Langchain-based miner which uses OpenAI's API as the LLM. This uses the ReAct framework.

    You should also install the dependencies for this miner, which can be found in the requirements.txt file in this directory.
    """

    @classmethod
    def add_args(cls, parser: argparse.ArgumentParser):
        """
        Adds OpenAI-specific arguments to the command line parser.
        """
        super().add_args(parser)

        parser.add_argument(
            "--use_react_agent",
            type=bool,
            default=False,
            help="Flag to enable the ReAct agent",
        )

    def __init__(self, config=None):
        super().__init__(config=config)

        bt.logging.info(
            f"🤖📖 Initializing wikipedia agent with model {self.config.neuron.model_id}..."
        )

        if self.config.wandb.on:
            self.identity_tags = ("wikipedia_agent_miner",) + (
                self.config.neuron.model_id,
            )

        _ = load_dotenv(find_dotenv())

        if self.config.use_react_agent:
            self.agent = ReactAgent(
                self.config.neuron.model_id, 
                self.config.neuron.temperature,
                self.config.neuron.max_tokens,
                self.config.neuron.load_in_8bits,
                self.config.neuron.load_in_4bits
            )
        else:
            self.agent = SingleActionAgent(
                self.config.neuron.model_id, 
                self.config.neuron.temperature,
                self.config.neuron.max_tokens,
                self.config.neuron.load_in_8bits,
                self.config.neuron.load_in_4bits
            )


        self.accumulated_total_tokens = 0
        self.accumulated_prompt_tokens = 0
        self.accumulated_completion_tokens = 0
        self.accumulated_total_cost = 0

    async def forward(self, synapse: StreamPromptingSynapse) -> StreamPromptingSynapse:
        """
        Processes the incoming synapse by performing a predefined operation on the input data.
        This method should be replaced with actual logic relevant to the miner's purpose.

        Args:
            synapse (PromptingSynapse): The synapse object containing the 'dummy_input' data.

        Returns:
            PromptingSynapse: The synapse object with the '`dummy_output' field set to twice the 'dummy_input' value.

        The 'forward' function is a placeholder and should be overridden with logic that is appropriate for
        the miner's intended operation. This method demonstrates a basic transformation of input data.
        """
        try:
            with get_openai_callback() as cb:
                t0 = time.time()
                bt.logging.debug(f"📧 Message received, forwarding synapse: {synapse}")

                message = synapse.messages[-1]

                bt.logging.debug(f"💬 Querying openai and wikipedia: {message}")

                response = self.agent.run(message)

                synapse.completion = response
                synapse_latency = time.time() - t0

                if self.config.wandb.on:
                    self.log_event(
                        timing=synapse_latency,
                        prompt=message,
                        completion=response,
                        system_prompt="",
                        extra_info=self.get_cost_logging(cb),
                    )

            bt.logging.debug(f"✅ Served Response: {response}")
            return synapse
        except Exception as e:
            bt.logging.error(f"Error in forward: {e}")
            synapse.completion = "Error: " + str(e)
        finally:
            if self.config.neuron.stop_on_forward_exception:
                self.should_exit = True
            return synapse