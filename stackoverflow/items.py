# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy import Field

class StackoverflowItem(scrapy.Item):
    stack_question_id = Field()
    question_title = Field()
    question_content = Field()
    question_url = Field()
    date_posted = Field()
    upvote = Field()
    view = Field()
    answers_count = Field()
    tags = Field()
    answers = Field()
    user = Field()
    question_comments = Field()

    pass
