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
import typing
import bittensor as bt

# Bittensor Miner Template:
from prompting.protocol import PromptingSynapse

# import base miner class which takes care of most of the boilerplate
from prompting.base.prompting_miner import BasePromptingMiner


class MockMiner(BasePromptingMiner):
    """
    This little fella responds with a static message.
    """

    def __init__(self, config=None):
        super().__init__(config=config)

    async def forward(self, synapse: PromptingSynapse) -> PromptingSynapse:
        synapse.completion = f"Hey you reached mock miner {self.config.wallet.hotkey!r}. Please leave a message after the tone.. Beep!"
        bt.logging.success(f"✅ Mock miner replied with {synapse.completion}")

        return synapse

    async def blacklist(self, synapse: PromptingSynapse) -> typing.Tuple[bool, str]:
        return False, "All good here"

    async def priority(self, synapse: PromptingSynapse) -> float:
        return 1e6