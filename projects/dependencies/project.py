def clean_tags(tags_string):
    tags = tags_string.split(",")
    tags = [tag.strip().lower() for tag in tags if len(tag.strip()) > 0]
    return tags