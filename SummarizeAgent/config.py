import json

def llmconfig() -> dict:
    with open("./config.json", "r") as f:
        config = json.load(f)
    
    config = {
        "llm_config": {
            "model": config["model"],
            "base_url": config["base_url"],
            "api_key": config["api_key"],
            "api_type": config["api_type"],
            "temperature": config["temperature"],
        }
    }

    return config


if __name__ == "__main__":
    config = llmconfig()
    print(config)