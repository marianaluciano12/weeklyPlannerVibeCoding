import json
from urllib.request import urlopen


def get_random_quote() -> dict:
    url = "http://api.quotable.io/random"
    with urlopen(url) as response:
        data = response.read().decode("utf-8")
    return json.loads(data)


def main() -> None:
    quote = get_random_quote()
    text = quote.get("content", "No quote found.")
    author = quote.get("author", "Unknown")
    print(f"\n\"{text}\"\n— {author}\n")


if __name__ == "__main__":
    main()
