import argparse
import csv
import json
import os
import re
import shutil

OUTPUT_COLS = ("Title", "Content", "Date", "Image Featured", "Tags")


def read_file(path) -> str:
    with open(path, "rt", encoding="utf8") as f:
        return f.read()


def convert_to_csv(input_dir: str, output_dir: str, max_posts: int = -1):
    with open(os.path.join(input_dir, "posts.json"), "rt", encoding="utf8") as f:
        posts = json.load(f)
    assert isinstance(posts, list)
    if max_posts > 0:
        posts = posts[:max_posts]
    images_dir = os.path.join(output_dir, "images")
    os.makedirs(images_dir, exist_ok=True)
    with open(os.path.join(output_dir, "posts.csv"), "wt", encoding="utf8") as f:
        w = csv.DictWriter(f, fieldnames=OUTPUT_COLS)
        w.writeheader()
        for post in posts:
            sanitized_tags = [tag.replace("|", "") for tag in post["i_text"]]
            row = {
                "Title": post["title"],
                "Date": post["post_date"],
                "Tags": "|".join(sanitized_tags),
            }
            html_file = post["output_file"]
            post_images_dir = post["images_dir"]
            html = read_file(os.path.join(input_dir, html_file))
            html = re.sub(r".*<body>\s*", "", html, flags=re.DOTALL)
            # Strip off title
            html = re.sub(r"<h1 class=\"post-title\">.*?</h1>\s*", "", html, flags=re.DOTALL)
            # Strip off author info, etc. (Can be incorporated in more structured way separately.)
            html = re.sub(r"<p class=\"post-info\">.*?</p>\s*", "", html, flags=re.DOTALL)
            html = re.sub(r"\s*<p class=\"scrape-info\">.*?</p>", "", html, flags=re.DOTALL)
            html = re.sub(r"\s*</body>.*", "", html, flags=re.DOTALL)
            first_image = ""

            def move_image_match(m):
                nonlocal first_image
                src = m[1]
                if not src.endswith((".jpeg", ".jpg")):
                    return m[0]
                if not src.startswith(post_images_dir):
                    raise ValueError(f"{html_file} has src outside {post_images_dir}")
                new_filename = src.replace("/", "_")
                if not first_image:
                    first_image = new_filename
                shutil.copyfile(
                    os.path.join(input_dir, src), os.path.join(images_dir, new_filename)
                )
                before = m.string[m.start() : m.start(1)]
                after = m.string[m.end(1) : m.end()]
                return before + new_filename + after

            row["Content"] = re.sub(r'src="([^"]+)', move_image_match, html)
            row["Image Featured"] = first_image
            w.writerow(row)


def main():
    parser = argparse.ArgumentParser(prog="make_gg_post_csv")
    parser.add_argument("--input_dir", required=True)
    parser.add_argument("--output_dir", required=True)
    parser.add_argument("--max_posts", type=int, default=-1)
    args = parser.parse_args()
    convert_to_csv(args.input_dir, args.output_dir, max_posts=args.max_posts)


if __name__ == "__main__":
    main()
