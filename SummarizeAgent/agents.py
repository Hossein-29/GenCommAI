from autogen import AssistantAgent as AA
from . import config, base
from typing import Tuple
from concurrent.futures import ThreadPoolExecutor


class SummarizeAgent(base.Agent):
    """Summarizer Agent"""

    name = "Summarizer Agent"
    def run(self, **kwargs):
        budgetman, qualityman, wiseman, main = SummarizeAgent.load_agents()

        response = SummarizeAgent.generate_response(budgetman, qualityman, wiseman)
        return response
    
    @staticmethod
    def load_agents() -> Tuple[AA, AA, AA, AA]:
        """Load agents."""

        config = config.llmconfig()

        def create_budgetman() -> AA:
            return AA(
                code_execution_config={"use_docker": False},
                llm_config=config["llm_config"],
                name="budgetman",
                system_message="You look for affordable products all the time. Saving money if your life goal. give me a summary and review then evaluate the product, should user buy it or no?, talk to user",
            )

        def create_qualityman() -> AA:
            return AA(
            code_execution_config={"use_docker": False},
            llm_config=config["llm_config"],
            name="qualityman",
            system_message="You look for high quality products all the time. Just quality and reliabilty are important. You look for well known brands, give me a summary, review then evaluate the product, should user buy it?, talk to user",
            )

        def create_wiseman() -> AA:
            return AA(
            code_execution_config={"use_docker": False},
            llm_config=config["llm_config"],
            name="wiseman",
            system_message="You are wiseman so your choice are logical and based on facts in all aspects. give me a summary, review then evaluate the product, should user buy it?, talk to user",
            )

        def create_main() -> AA:
            return AA(
            code_execution_config={"use_docker": False},
            llm_config=config["llm_config"],
            name="Coordinator",
            system_message=
                "You are a coordinator that receives the outputs of multiple agents and creates a final summary report."
                + "Make sure to integrate all perspectives into a unified output."
                + "Evaluate the product, guide user and suggest the product if it meets the needs."
                + "you suggest it, give user tips and advices"
                + "Response with one sentence for reiview, one for advices and one for conclusion that who should buy this product and who should avoid it"
            )
        
        with ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(create_budgetman),
                executor.submit(create_qualityman),
                executor.submit(create_wiseman),
                executor.submit(create_main),
            ]
            budgetman, qualityman, wiseman, main = [f.result() for f in futures]

        return (budgetman, qualityman, wiseman, main)

    @staticmethod
    def generate_response(budgetman_agent: AA
                       , qualityman_agent: AA
                       , wiseman_agent: AA
                       , main_agent: AA
                       , search_result: str) -> str:
        """Generate response from the agents."""

        def get_reply(agent: AA) -> str:
            return agent.generate_reply([{"role": "user", "content": search_result}])

        with ThreadPoolExecutor() as executor:
            futures = {
                "budgetman": executor.submit(get_reply, budgetman_agent),
                "qualityman": executor.submit(get_reply, qualityman_agent),
                "wiseman": executor.submit(get_reply, wiseman_agent)
            }

            bresponse = futures["budgetman"].result()
            qresponse = futures["qualityman"].result()
            wresponse = futures["wiseman"].result()

        combined_input = (
            f"budgetman: {bresponse}\n"
            f"qualityman: {qresponse}\n"
            f"wiseman: {wresponse}"
        )

        final_response = main_agent.generate_reply([{"role": "user", "content": combined_input}])
        return final_response
