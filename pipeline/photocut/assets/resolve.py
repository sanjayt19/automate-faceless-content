"""Turn the asset maps into the URLs a build needs.

    resolve.py <key> <out-urls.json>     # writes the still map, prints narration URL

The signed links expire two days after generation, which is why the maps store
ids and signatures rather than whole URLs, and why this file is deleted once a
batch has been rendered.
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = "https://pikaso.cdnpk.net/private/production/"
TOK = "?token=exp=1789516800~hmac="


def url(pair, leaf):
    return f"{BASE}{pair[0]}/{leaf}{TOK}{pair[1]}"


def main():
    key, out = sys.argv[1], sys.argv[2]
    urls = json.load(open(os.path.join(HERE, "urls.json")))
    stills = json.load(open(os.path.join(HERE, "stills.json")))
    narr = json.load(open(os.path.join(HERE, "narration.json")))
    json.dump({n: url(urls[i], "render.png") for n, i in stills[key].items()},
              open(out, "w"))
    print(url(narr[key], "audio.mp3"))


if __name__ == "__main__":
    main()
