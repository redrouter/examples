import os

from anthropic import Anthropic


def main():
    client = Anthropic(
        api_key=os.environ["REDROUTER_API_KEY"],
        base_url="https://redrouter.org",
        timeout=120,
        max_retries=0,
    )
    response = client.messages.create(
        model="glm-5.3-flash-rr",
        max_tokens=256,
        messages=[{"role": "user", "content": "Give three access-control checks for my own API."}],
    )
    for block in response.content:
        if block.type == "text":
            print(block.text)


if __name__ == "__main__":
    main()
