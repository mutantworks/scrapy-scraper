from pathlib import Path
from stackoverflow.items import StackoverflowItem

import scrapy


class StackOverflow(scrapy.Spider):
    name = "stackoverflowspider"
    start_urls = ["https://stackoverflow.com/questions/tagged/"]

    def __init__(self, domain='', *args, **kwargs):
        if domain is not None:
            self.start_urls[0] = self.start_urls[0] + domain
        else:
            self.start_urls = []
        super(StackOverflow, self).__init__(*args, **kwargs)

    def parse(self, response):
        questions = response.css('.js-post-summary')

        for q in questions:
            stack_question_id = q.css('.s-link::attr(href)').extract_first().split("/")[2]
            question_title = q.css('.s-link::text').extract_first()
            question_content = q.css('.s-post-summary--content-excerpt::text').extract_first()
            question_url = q.css('.s-link::attr(href)').extract_first()
            date_posted = q.css('.relativetime::attr(title)').extract_first()
            stats = q.css('.s-post-summary--stats-item-number::text').extract()
            tags = q.css('.mt0::text').extract()

            stackoverflow = {
                'stack_question_id': stack_question_id,
                'question_title': question_title,
                'question_content': question_content,
                'question_url': question_url,
                'date_posted': date_posted,
                'upvote': stats[0],
                'answers_count': stats[1],
                'view': stats[2],
                'tags': tags
            }


            question_url = q.css('.s-link::attr(href)').get()
            yield response.follow(question_url, self.parse_answer, meta={'stackoverflow': stackoverflow})

            next_page = response.css(
                '.s-pagination--item__clear~ .js-pagination-item+ .js-pagination-item::attr(href)').extract_first()
            next_page_text = \
                response.css(
                    '.s-pagination--item__clear~ .js-pagination-item+ .js-pagination-item::attr(title)').extract()[
                    0].split(' ')[3]
            if next_page is not None and int(next_page_text) < 6:
                next_page_url = "https://stackoverflow.com" + next_page
                yield scrapy.Request(next_page_url, callback=self.parse)

    def parse_answer(self, response):
        item = StackoverflowItem()
        stackoverflow = response.meta['stackoverflow']

        # Fill User Details
        stack_user_id = response.css('#question .user-details a::attr(href)').extract_first().split("/")[2]
        user_name = response.css('#question .user-details a::text').extract_first()
        user_reputation_score = response.css('#question .reputation-score::text').extract_first()
        user_gold_badges = response.css('#question .badge1+ .badgecount::text').extract_first()
        user_silver_badges = response.css('#question .badge2+ .badgecount::text').extract_first()
        user_bronze_badges = response.css('#question .badge3+ .badgecount::text').extract_first()

        question_user = {
            'stack_user_id': stack_user_id,
            'name': user_name,
            'reputation_score': user_reputation_score if user_reputation_score else 0,
            'gold_badges': user_gold_badges if user_gold_badges else 0,
            'silver_badges': user_silver_badges if user_silver_badges else 0,
            'bronze_badges': user_bronze_badges if user_bronze_badges else 0

        }

        stackoverflow['user'] = question_user

        # Get Question Comments

        questionComments = response.css('#question .js-comment')
        q_comments = []
        for qc in questionComments:
            try:
                stack_question_comment_id = qc.css('.js-comment::attr(data-comment-id)').extract_first()
                comment_content = qc.css('.comment-copy::text').extract_first()
                username = qc.css('.comment-user::text').extract_first()

                comment = {
                    'stack_question_id': stackoverflow['stack_question_id'],
                    'stack_question_comment_id': stack_question_comment_id,
                    'comment_content': comment_content if comment_content else ' ',
                    'username': username if username else ''
                }

                q_comments.append(comment)

            except Exception as e:
                self.logger.error(f"Question's comment parsing failed [{e}]")

        # Get Answers.

        answers = list()
        anss = response.css('.js-answer')

        for a in anss:
            try:
                stack_answer_id = a.css('.answer::attr(id)').extract_first().split("-")[1]
                answer_content = a.css('.js-post-body *::text').getall()
                date_posted = a.css('.relativetime::attr(title)').extract_first()
                upvote = a.css('.ai-center::text').extract_first()
                accepted = a.css('.d-none::attr(title)').extract_first()

                stack_user_id = a.css('.user-details a::attr(href)').extract_first().split("/")[2]
                user_name = a.css('.user-details a::text').extract_first()
                user_reputation_score = a.css('.reputation-score::text').extract_first()
                user_gold_badges = a.css('.badge1+ .badgecount::text').extract_first()
                user_silver_badges = a.css('.badge2+ .badgecount::text').extract_first()
                user_bronze_badges = a.css('.badge3+ .badgecount::text').extract_first()

                answer_user = {
                    'stack_user_id': stack_user_id,
                    'name': user_name,
                    'reputation_score': user_reputation_score if user_reputation_score else 0,
                    'gold_badges': user_gold_badges if user_gold_badges else 0,
                    'silver_badges': user_silver_badges if user_silver_badges else 0,
                    'bronze_badges': user_bronze_badges if user_bronze_badges else 0

                }

                # Get Answer Comments.

                answerComments = a.css('.js-comment')
                a_comments = []

                for ac in answerComments:
                    stack_answer_comment_id = ac.css('.js-comment::attr(data-comment-id)').extract_first()
                    comment_content = ac.css('.comment-copy::text').extract_first()
                    username = ac.css('.comment-user::text').extract_first()

                    comment = {
                        'stack_answer_id': stack_answer_id,
                        'stack_answer_comment_id': stack_answer_comment_id,
                        'comment_content': comment_content if comment_content else ' ',
                        'username': username if username else ''
                    }

                    a_comments.append(comment)

                answer = {
                    'stack_answer_id': stack_answer_id,
                    'answer_content': " ".join(answer_content),
                    'date_posted': date_posted,
                    'upvote': upvote,
                    'accepted': "YES" if accepted else "NO",
                    'user': answer_user,
                    'answer_comments': a_comments
                }

                answers.append(answer)

            except Exception as e:
                self.logger.error(f"Answer parsing failed [{e}]")

            # ANSWER COMMENT GATHERING END

        stackoverflow['answers'] = answers
        stackoverflow['question_comments'] = q_comments

        item['stack_question_id'] = stackoverflow['stack_question_id']
        item['question_title'] = stackoverflow['question_title']
        item['question_content'] = stackoverflow['question_content']
        item['question_url'] = stackoverflow['question_url']
        item['date_posted'] = stackoverflow['date_posted']
        item['upvote'] = stackoverflow['upvote']
        item['view'] = stackoverflow['view']
        item['tags'] = stackoverflow['tags']
        item['answers_count'] = stackoverflow['answers_count']
        item['answers'] = stackoverflow['answers']
        item['user'] = stackoverflow['user']
        item['question_comments'] = stackoverflow['question_comments']

        yield item

        # yield stackoverflow