from autogen import AssistantAgent as AA
from  moro import config, base
from typing import Tuple
from concurrent.futures import ThreadPoolExecutor
import re, json


class SummarizeAgent(base.Agent):
    """Summarizer Agent"""

    def __init__(self, search_result: str):
        super().__init__()
        self.name = "Summarizer Agent"
        self.search_result = search_result

    def run(self, **kwargs) -> Tuple[str, str]:
        budgetman, qualityman, wiseman, main = self.load_agents()

        response = self.generate_response(budgetman, qualityman, wiseman, main, self.search_result)
        # return self.format_scores(response)
        return self.parse_review(response)
    
    @staticmethod
    def load_agents() -> Tuple[AA, AA, AA, AA]:
        """Load agents."""

        llmconfig = config.llmconfig()

        def create_budgetman() -> AA:
            return AA(
                code_execution_config={"use_docker": False},
                llm_config=llmconfig["llm_config"],
                name="budgetman",
                system_message="You look for affordable products all the time. Saving money if your life goal. give me a summary and review then evaluate the product, should user buy it or no?, talk to user"
                + "keep the number and mention them at the end"
            )

        def create_qualityman() -> AA:
            return AA(
            code_execution_config={"use_docker": False},
            llm_config=llmconfig["llm_config"],
            name="qualityman",
            system_message="You look for high quality products all the time. Just quality and reliabilty are important. You look for well known brands, give me a summary, review then evaluate the product, should user buy it?, talk to user"
            + "keep the number and mention them at the end"
            )

        def create_wiseman() -> AA:
            return AA(
            code_execution_config={"use_docker": False},
            llm_config=llmconfig["llm_config"],
            name="wiseman",
            system_message="You are wiseman so your choice are logical and based on facts in all aspects. give me a summary, review then evaluate the product, should user buy it?, talk to user"
            + "keep the number and mention them at the end"
            )

        def create_main() -> AA:
            return AA(
            code_execution_config={"use_docker": False},
            llm_config=llmconfig["llm_config"],
            name="Coordinator",
            system_message=
                "You are a coordinator that receives the outputs of multiple agents and creates a final summary report."
                + "Make sure to integrate all perspectives into a unified output."
                + "Evaluate the product, guide user and suggest the product if it meets the needs."
                + "you suggest it, give user tips and advices"
                + "Response with one sentence for reiview, one for advices and one for conclusion that who should buy this product and who should avoid it"
                + "Response with following instruction 'Review: (...)\nTips:(...)\nOverall score:(give me a number between 0 and 5, no other characters)'"
                + "mention numbers at the end in the list with following format{field(quality user satisfaction features value for money): score(give me a number between 40 to 100 please check and give the insightful score and not zeroß)}"
                + "Generate the response in Persian, except for the overall score which must be in English."
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
    
    @staticmethod
    def format_scores(review: str) -> Tuple[str, str]:
        """Extract the score block using regex"""
        match = re.search(r"\{.*\}", review, re.DOTALL)
        if not match:
            return review

        score_block = match.group(0)

        
        score_dict = {}
        for item in score_block.strip('{}').split('} {'):
            for pair in item.split(','):
                if ':' in pair:
                    key, value = pair.split(':')
                    score_dict[key.strip()] = value.strip()

        
        formatted_scores = json.dumps(score_dict, indent=2)

        return (review.replace(score_block, ""), formatted_scores)
    
    @staticmethod
    def parse_review(text: str):
        """Capture Review, Tips, Overall score, and all {...} score blocks"""
        pattern = re.compile(
            r"Review:\s*(.*?)\s*Tips:\s*(.*?)\s*Overall score:\s*(.*?)\s*((?:\{.*?\}\s*)+)",
            re.DOTALL
        )
        match = pattern.search(text)
        if not match:
            raise ValueError("Text format does not match expected pattern")

        review = match.group(1).strip()
        tips = match.group(2).strip()
        overall = match.group(3).strip()
        scores_text = match.group(4).strip()

        # Extract individual {key: value} blocks
        score_blocks = re.findall(r"\{([^}]+)\}", scores_text)

        scores = {}
        for block in score_blocks:
            # Each block can contain one or more key: value pairs separated by commas or spaces
            pairs = re.split(r",\s*|\s{2,}", block)
            for pair in pairs:
                if ':' in pair:
                    key, value = pair.split(':', 1)
                    scores[key.strip()] = value.strip()

        # Compose final dict or JSON
        result = {
            "Review": review,
            "Tips": tips,
            "Overall score": overall,
            "Scores": scores
        }

        return result


if __name__ == "__main__":
    # result1, result2 = SummarizeAgent("Macbook Air 2019, 12GB RAM, 512GB storage, score on Amazon=3/5").run()
    # print(result1)
    # print("---------------------")
    # print(result2)
    result = SummarizeAgent("Macbook Air 2019, 12GB RAM, 512GB storage, score on Amazon=3/5").run()
    print(type(result))
    print(result)
