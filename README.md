# Convert posts.json + posts to CSV + flat images dir

This utility takes the output from [gg_mhtml_to_site](https://github.com/fadend/gg_mhtml_to_site)
and converts it into a CSV file containing both post metadata and content
plus a flat directory of images.

Renames images (changing references in the HTML) to avoid conflicts. The aim
is to create something more easy to work with in importing the site into
WordPress or similar.

## Acknowledgments

Used [poetry](https://python-poetry.org/) to generate package skeleton.

Formatting Python with [black](https://github.com/psf/black).