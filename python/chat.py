import os

from openai import OpenAI


def main():
    client = OpenAI(
        api_key=os.environ["REDROUTER_API_KEY"],
        base_url="https://redrouter.org/v1",
        timeout=120,
        max_retries=0,
    )
    response = client.chat.completions.create(
        model="glm-5.3-flash-red",
        max_tokens=256,
        messages=[{"role": "user", "content": "Give three access-control checks for my own API."}],
    )
    print(response.choices[0].message.content)


if __name__ == "__main__":
    main()
