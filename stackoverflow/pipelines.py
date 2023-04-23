# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from sqlalchemy import update
from sqlalchemy.orm import sessionmaker
from stackoverflow.models import db_connect, create_table, User, Tag, Question, Answer, QuestionComment, AnswerComment


class StackoverflowPipeline:
    def __init__(self):
        """
        Initializes database connection and sessionmaker
        Creates tables
        """
        engine = db_connect()
        create_table(engine)
        self.Session = sessionmaker(bind=engine)

    def process_item(self, item, spider):

        session = self.Session()
        question = Question()
        question_user = User()
        answer_user = User()

        exist_qs = session.query(Question).filter_by(stack_question_id=item['stack_question_id']).first()
        if exist_qs is not None:
            print("already exist")
            question = exist_qs

        question_user.stack_user_id = item['user']['stack_user_id']
        question_user.name = item['user']['name']
        question_user.reputation_score = item['user']['reputation_score']
        question_user.gold_badges = item['user']['gold_badges']
        question_user.silver_badges = item['user']['silver_badges']
        question_user.bronze_badges = item['user']['bronze_badges']

        # Check the user exists or not !!!
        question_exist_user = session.query(User).filter_by(stack_user_id=question_user.stack_user_id).first()
        if question_exist_user is not None:
            question.user = question_exist_user
        else:
            question.user = question_user

        for tag_name in item['tags']:
            tag = Tag(name=tag_name)
            # Check whether the current tag already exists in the database
            exist_tag = session.query(Tag).filter_by(name=tag.name).first()
            if exist_tag is not None:
                tag = exist_tag
            question.tags.append(tag)
            print(tag)

        # Assign comments of question to particular question
        for cmt in item['question_comments']:
            if cmt['comment_content'] == ' ':
                continue
            else:
                exist_cmt = session.query(QuestionComment).filter_by(
                    stack_question_comment_id=cmt['stack_question_comment_id']).first()
                if exist_cmt is not None:
                    continue
                else:
                    comment = QuestionComment(stack_question_comment_id=cmt['stack_question_comment_id'],
                                              comment_content=cmt['comment_content'], username=cmt['username'],
                                              stack_question_id=cmt['stack_question_id'])
                    question.comments.append(comment)

        # Assign answers to particular question
        for ans in item['answers']:

            exist_ans = session.query(Answer).filter_by(stack_answer_id=ans['stack_answer_id']).first()
            if exist_ans is not None:
                continue
            else:
                answer = Answer()

                answer_user.stack_user_id = ans['user']['stack_user_id']
                answer_user.name = ans['user']['name']
                answer_user.reputation_score = ans['user']['reputation_score']
                answer_user.gold_badges = ans['user']['gold_badges']
                answer_user.silver_badges = ans['user']['silver_badges']
                answer_user.bronze_badges = ans['user']['bronze_badges']

                answer_user_exist = session.query(User).filter_by(stack_user_id=answer_user.stack_user_id).first()
                if answer_user_exist is not None:  # Check the user exists or not !!!
                    answer.user = answer_user_exist
                else:
                    answer.user = answer_user  # Answer user assignment

                # Assign comments of answer to particular answer
                for cmt in ans['answer_comments']:
                    print(cmt)
                    if cmt['comment_content'] == ' ':
                        continue
                    else:
                        exist_cmt = session.query(AnswerComment).filter_by(
                            stack_answer_comment_id=cmt['stack_answer_comment_id']).first()
                        if exist_cmt is not None:
                            continue
                        else:
                            comment = AnswerComment(stack_answer_comment_id=cmt['stack_answer_comment_id'],
                                                    comment_content=cmt['comment_content'], username=cmt['username'],
                                                    stack_answer_id=cmt['stack_answer_id'])
                            answer.comments.append(comment)

                answer.stack_answer_id = ans['stack_answer_id']
                answer.answer_content = ans['answer_content']
                answer.date_posted = ans['date_posted']
                answer.upvote = ans['upvote']
                answer.accepted = ans['accepted']
                question.answers.append(answer)  # Append each question to their respective quesstion

        question.stack_question_id = item['stack_question_id']
        question.question_title = item['question_title']
        question.question_content = item['question_content']
        question.question_url = item['question_url']
        question.answers_count = item['answers_count']
        question.date_posted = item['date_posted']
        question.view = item['view']
        question.upvote = item['upvote']

        try:
            if exist_qs:
                session.commit()
            else:
                session.add(question)
                session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

        return item

