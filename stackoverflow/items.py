# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field


class StackoverflowItem(Item):

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

    def __str__(self):
        return ""

    pass
