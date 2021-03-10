from typing import List, Dict

from psycopg2 import sql
from psycopg2.extras import RealDictCursor
import datetime
import database_common



@database_common.connection_handler
def get_questions(cursor: RealDictCursor, limit: (None, int)) -> list:  # all questions: limit is None
    if limit is None:
        query = f"""
                SELECT *
                FROM question
                """
    else:
        query = f"""
                SELECT *
                FROM question
                ORDER BY submission_time DESC
                LIMIT {limit}
                """
    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def get_questions_by_order(cursor: RealDictCursor, order: str, direct: str):
    query = f"""
            SELECT *
            FROM question
            ORDER BY {order} {direct}
            """
    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def get_questions_by_phrase(cursor: RealDictCursor, phrase: str) -> list:
    query = f"""
                SELECT *
                FROM question
                WHERE LOWER(title) LIKE LOWER('%{phrase}%') or LOWER(message) LIKE LOWER('%{phrase}%')
                """
    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def get_answers_by_phrase(cursor: RealDictCursor, phrase: str) -> list:
    query = f"""
                SELECT *
                FROM answer
                WHERE LOWER(message) LIKE LOWER('%{phrase}%')
                """
    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def get_question_by_id(cursor: RealDictCursor, question_id: int) -> list:
    query = f"""
        SELECT question.*, forum_user.id as forum_user_id, 
        forum_user.mail as user_mail, forum_user.reputation as reputation
        FROM question 
        LEFT JOIN forum_user ON question.user_id = forum_user.id
        WHERE question.id = {question_id}
        """
    cursor.execute(query)
    return cursor.fetchone()


@database_common.connection_handler
def get_answers_by_question_id(cursor: RealDictCursor, question_id: int) -> list:
    query = f"""
        SELECT answer.*, forum_user.id as forum_user_id, 
        forum_user.mail as user_mail, forum_user.reputation as reputation
        FROM answer
        LEFT JOIN forum_user ON forum_user.id = answer.user_id
        WHERE answer.question_id = {question_id}
        ORDER BY submission_time DESC
        """
    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def add_question(cursor: RealDictCursor, new_question: dict) -> dict:
    query = f"""
        INSERT INTO question (title, message, image, submission_time, view_number, vote_number, user_id)
        VALUES (%(title)s, %(message)s, %(image)s, %(submission_time)s, %(view_number)s, %(vote_number)s, %(user_id)s)
        RETURNING id
        """
    cursor.execute(query, new_question)
    return cursor.fetchone()


@database_common.connection_handler
def update_question(cursor: RealDictCursor, edited_question: dict):
    query = f"""
        UPDATE question 
        SET title = %(title)s, message = %(message)s, image = %(image)s
        WHERE id = %(id)s
        """
    cursor.execute(query, edited_question)


@database_common.connection_handler
def update_question_votes(cursor: RealDictCursor, question_id, difference: int):
    query = f"""
        UPDATE question
        SET vote_number = vote_number + {difference}
        WHERE id = {question_id}"""
    cursor.execute(query)
    return


@database_common.connection_handler
def views_updated(cursor: RealDictCursor, question_id: int):
    query = f"""
        UPDATE question
        SET view_number = view_number + 1
        WHERE id = {question_id}"""
    cursor.execute(query)

    return


@database_common.connection_handler
def delete_answers_for_question(cursor: RealDictCursor, question_id: int):
    query = f"""
        DELETE from answer
        WHERE question_id = {question_id}"""
    cursor.execute(query)
    return


@database_common.connection_handler
def delete_comment_for_question(cursor: RealDictCursor, question_id: int):
    query = f"""
            DELETE from comment
            WHERE question_id = {question_id}"""
    cursor.execute(query)
    return


@database_common.connection_handler
def delete_comment_for_answers_for_question(cursor: RealDictCursor, question_id: int):
    query = f"""
        DELETE from comment
        WHERE answer_id IN (
        SELECT id 
        FROM answer 
        WHERE question_id = {question_id})"""
    cursor.execute(query)
    return


@database_common.connection_handler
def delete_question_from_question_tag(cursor: RealDictCursor, question_id: int):
    query = f"""
            DELETE from question_tag
            WHERE question_id = {question_id}"""
    cursor.execute(query)
    return


@database_common.connection_handler
def has_question_comment(cursor: RealDictCursor, question_id: int):
    query = f"""
        SELECT id
        FROM comment 
        WHERE question_id = {question_id}"""
    cursor.execute(query)
    return cursor.fetchone()


@database_common.connection_handler
def has_answer_comment(cursor: RealDictCursor, answer_id: int):
    query = f"""
        SELECT id
        FROM comment 
        WHERE answer_id = {answer_id}"""
    cursor.execute(query)
    return cursor.fetchone()


@database_common.connection_handler
def delete_comment_for_answer(cursor: RealDictCursor, answer_id: int):
    query = f"""
        DELETE from comment
        WHERE answer_id = {answer_id}"""
    cursor.execute(query)


@database_common.connection_handler
def delete_answer_from_answers(cursor: RealDictCursor, answer_id: int):
    query = f"""
        DELETE from answer
        WHERE id = {answer_id}"""
    cursor.execute(query)

    return


@database_common.connection_handler
def update_answer_votes(cursor: RealDictCursor, answer_id: int, difference: int):
    query = f"""
        UPDATE answer
        SET vote_number = vote_number + {difference}
        WHERE id = {answer_id}"""
    cursor.execute(query)
    return


@database_common.connection_handler
def get_answer_pictures_paths(cursor: RealDictCursor, question_id: int):
    query = f"""
        SELECT answer_id, i.image
        FROM answer_image as i
        INNER JOIN answer a on a.id = i.answer_id
        WHERE a.question_id = {question_id}"""
    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def get_answer_id_pictures_paths(cursor: RealDictCursor, answer_id):
    query = f"""
            SELECT image
            FROM answer_image
            WHERE answer_id = {answer_id}"""
    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def get_question_pictures_paths(cursor: RealDictCursor, question_id: int):
    query = f"""
        SELECT image 
        FROM question_image
        WHERE question_id = {question_id}"""
    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def delete_question(cursor: RealDictCursor, question_id: int):
    query = f"""
            DELETE from question
            WHERE id = {question_id}"""
    cursor.execute(query)
    return


@database_common.connection_handler
def get_comment_by_id(cursor: RealDictCursor, comment_id: int):
    query = f"""
                SELECT * from comment
                WHERE id = {comment_id}"""
    cursor.execute(query)
    return cursor.fetchone()


@database_common.connection_handler
# def add_question_comment(cursor: RealDictCursor, details: dict, fk_id, column: str):
#     query = f"""
#         INSERT INTO comment ({column}, message, submission_time)
#         VALUES ({fk_id}, {details["comment_message"]}, '{details["submission_time"]}' )
#         """
def add_question_comment(cursor: RealDictCursor, details: dict):
    query = f"""
        INSERT INTO comment (question_id, message, submission_time, user_id )
        VALUES (%(question_id)s, %(comment_message)s, %(submission_time)s , %(user_id)s)
        """
    cursor.execute(query, details)
    return


@database_common.connection_handler
def update_comment(cursor: RealDictCursor, details: dict, comment_id):
    query = f"""
            UPDATE comment 
            SET message = %(comment_message)s, 
                submission_time = %(submission_time)s,
                edited_count = CASE 
                    WHEN edited_count IS NULL  THEN 1
                    ELSE edited_count + 1
                END
            WHERE id = {comment_id}
            """
    cursor.execute(query, details)
    return


@database_common.connection_handler
def delete_comment(cursor: RealDictCursor, comment_id: int):
    query = f"""
        DELETE FROM comment
        WHERE id = {comment_id} """
    cursor.execute(query)
    return


@database_common.connection_handler
def get_question_id_by_answer_id(cursor: RealDictCursor, answer_id: int):
    query = f"""
        SELECT question_id 
        FROM answer
        WHERE id = {answer_id}"""
    cursor.execute(query)
    return cursor.fetchone()["question_id"]


@database_common.connection_handler
def get_question_by_comment_id(cursor: RealDictCursor, comment_id: int):
    query = f"""
        SELECT *
        FROM question
        WHERE id IN (
        SELECT question_id
        FROM comment
        WHERE id = {comment_id})"""
    cursor.execute(query)
    return cursor.fetchone()


@database_common.connection_handler
def get_answer_by_comment_id(cursor: RealDictCursor, comment_id: int):
    query = f"""
        SELECT *
        FROM answer
        WHERE id IN (
        SELECT answer_id
        FROM comment
        WHERE id = {comment_id})"""
    cursor.execute(query)
    return cursor.fetchone()


def get_question_id_by_comment_id(comment_id):
    if get_question_by_comment_id(comment_id) != None:
        return get_question_by_comment_id(comment_id).get("id")
    else:
        answer = get_answer_by_comment_id(comment_id)
        return get_question_id_by_answer_id(answer["id"])


@database_common.connection_handler
def add_answer_comment(cursor: RealDictCursor, details: dict):
    query = f"""
        INSERT INTO comment (answer_id, message, submission_time, user_id)
        VALUES (%(answer_id)s, %(comment_message)s, %(submission_time)s, %(user_id)s) """
    cursor.execute(query, details)
    return


@database_common.connection_handler
def get_comments_by_question_id(cursor: RealDictCursor, question_id: int):
    query = f"""
            SELECT comment.*, 
            forum_user.id as forum_user_id, forum_user.mail as user_mail, 
            forum_user.reputation as reputation
            FROM comment
            LEFT JOIN forum_user ON comment.user_id = forum_user.id
            WHERE comment.question_id = {question_id}
            ORDER BY submission_time DESC"""
    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def get_answer_comments_by_question_id(cursor: RealDictCursor, question_id: int):
    query = f"""
            SELECT comment.*, 
            forum_user.id as forum_user_id, forum_user.mail as user_mail, 
            forum_user.reputation as reputation
            FROM comment LEFT JOIN forum_user 
            on forum_user.id = comment.user_id
            WHERE comment.answer_id IN (
            SELECT id 
            FROM answer 
            WHERE question_id = {question_id})
            ORDER BY submission_time DESC"""

    cursor.execute(query)
    return cursor.fetchall()


# @database_common.connection_handler
# def delete_question_id_form_question_tag(cursor: RealDictCursor, question_id: int):
#     query = f"""
#             DELETE from question_tag
#             WHERE question_id = {question_id}"""
#     cursor.execute(query)
#     return


#
# @database_common.connection_handler
# def get_question_id(cursor: RealDictCursor) -> list:
#     query = f"""
#         SELECT MAX(id)
#         FROM question
#         """
#     cursor.execute(query)
#     return cursor.fetchone().values()

@database_common.connection_handler
def add_answer(cursor: RealDictCursor, new_answer: dict):
    query = f"""
            INSERT INTO  answer (submission_time, vote_number, question_id, message, image, user_id, accepted)
            VALUES (%(submission_time)s, %(vote_number)s, %(question_id)s, %(message)s, %(image)s, %(user_id)s, %(accepted)s)
            RETURNING id
            """
    cursor.execute(query, new_answer)
    return cursor.fetchone()


@database_common.connection_handler
def get_answer_by_id(cursor: RealDictCursor, answer_id: int) -> list:
    query = f"""
        SELECT *
        FROM answer
        WHERE id = {answer_id}
        """
    cursor.execute(query)
    return cursor.fetchone()


@database_common.connection_handler
def update_answer(cursor: RealDictCursor, answer_id: int, edited_answer: dict):
    query = f"""
            UPDATE answer
            SET message = %(message)s, image = %(image)s
            WHERE id = {answer_id}
            """
    cursor.execute(query, edited_answer)


@database_common.connection_handler
def add_question_tag(cursor: RealDictCursor, tag_name: dict):
    query = f"""
        INSERT INTO tag ("name")
        VALUES (%(tag_message)s)
        RETURNING id
        """
    cursor.execute(query, tag_name)
    return cursor.fetchone()


@database_common.connection_handler
def add_question_tag_id(cursor: RealDictCursor, tag_id: int, question_id: int):
    query = f"""
        INSERT INTO question_tag (question_id, tag_id)
        VALUES ({question_id}, {tag_id})
        """
    cursor.execute(query)
    return


@database_common.connection_handler
def get_tag_by_question_id(cursor: RealDictCursor, question_id: int):
    query = f"""
            SELECT *
            FROM tag
            WHERE id IN (
            SELECT tag_id
            FROM question_tag
            WHERE question_id = {question_id})

            """
    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def get_question_id_by_tag_id(cursor: RealDictCursor, tag_id: int):
    query = f"""
        SELECT question_id 
        FROM question_tag
        WHERE tag_id = {tag_id}"""
    cursor.execute(query)
    return cursor.fetchone()["question_id"]


@database_common.connection_handler
def get_tag_id_by_name(cursor: RealDictCursor, tag_name: str):
    query = f"""
        SELECT id 
        FROM tag
        WHERE "name" = '{tag_name}'
        """
    cursor.execute(query)
    return cursor.fetchone()


@database_common.connection_handler
def delete_tag(cursor: RealDictCursor, tag_id, question_id : int):
    query = f"""
        DELETE FROM question_tag
        WHERE tag_id = {tag_id} AND question_id = {question_id} """
    cursor.execute(query)
    return


@database_common.connection_handler
def get_all_tags(cursor: RealDictCursor):
    query = f"""
        select (name)
        from tag
        """
    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def get_tag_to_list(cursor: RealDictCursor):
    query = f"""
        select (name), count (name), t.id
        from tag as t
        inner join question_tag as q on t.id = q.tag_id
        group by ("name"), t.id 
        """
    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def get_tag_from_question(cursor: RealDictCursor, question_id):
    query = f"""
        SELECT "name"
        FROM tag
        INNER JOIN question_tag ON tag.id=question_tag.tag_id
        WHERE question_id = {question_id}
        """
    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def get_tags_by_order(cursor: RealDictCursor, order: str, direct: str):
    query = f"""
            select (name), count (name), id
            from tag as t
            inner join question_tag as q on t.id = q.tag_id
            group by ("name"), id
            ORDER BY {order} {direct}
            """
    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def get_questions_by_tag(cursor: RealDictCursor, tag_id):
    query = f"""
            select q.title, q.message, tag.name, q.id
            from question as q
            left join question_tag as qt on q.id = qt.question_id
            join tag ON tag.id = qt.tag_id
            where tag.id = {tag_id}
            group by q.title, q.message, tag.name, q.id
            """
    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def check_for_user(cursor: RealDictCursor, email: dict):
    query = """
        SELECT *
        FROM forum_user
        WHERE mail = (%(email)s)
        """
    cursor.execute(query, email)
    return cursor.rowcount > 0


@database_common.connection_handler
def get_user_id_by_mail(cursor: RealDictCursor, mail: str):
    query = f"""
        SELECT id 
        FROM forum_user
        WHERE mail = %(mail)s"""

    cursor.execute(query, {'mail': mail})
    return cursor.fetchone()["id"]


@database_common.connection_handler
def get_all_users(cursor: RealDictCursor):
    # query = f"""
    #     SELECT *
    #     FROM forum_user"""

    query = f"""
    select forum_user.id, forum_user.mail, 
    forum_user.submission_time,forum_user.reputation,
    COUNT(DISTINCT question.id) AS questions_number,
    COUNT(DISTINCT answer.id) AS answers_number,
    COUNT(DISTINCT comment.id) AS comments_number
    from forum_user
    LEFT JOIN question ON forum_user.id = question.user_id
    LEFT JOIN answer ON forum_user.id = answer.user_id
    LEFt JOIN comment ON forum_user.id = comment.user_id
    GROUP BY forum_user.id
    """
    cursor.execute(query)
    return cursor.fetchall()


# @database_common.connection_handler
# def get_all_users_basic_info(cursor: RealDictCursor):
#     query = f"""
#         SELECT id, mail, reputation
#         FROM forum_user"""
#     cursor.execute(query)
#     return cursor.fetchall()


@database_common.connection_handler
def add_new_user(cursor: RealDictCursor, new_user: dict):
    query = """
        INSERT INTO forum_user (mail, submission_time, hash_pass)
        VALUES (%(email)s, %(submission_time)s, crypt(%(password)s, gen_salt('bf', 8)))
        """
    cursor.execute(query, new_user)


@database_common.connection_handler
def get_user_details(cursor: RealDictCursor, user_id):
    query = f"""
            SELECT 
            forum_user.id, forum_user.mail, 
            forum_user.submission_time,forum_user.reputation,
            COUNT(DISTINCT question.id) AS questions_number,
            COUNT(DISTINCT answer.id) AS answers_number,
            COUNT(DISTINCT comment.id) AS comments_number
            FROM forum_user
            LEFT JOIN question ON forum_user.id = question.user_id
            LEFT JOIN answer ON forum_user.id = answer.user_id
            LEFT JOIN comment ON forum_user.id = comment.user_id
            WHERE forum_user.id = {user_id}
            GROUP BY forum_user.id"""
    cursor.execute(query)
    return cursor.fetchone()


@database_common.connection_handler
def get_questions_by_user(cursor: RealDictCursor, user_id):
    query = f"""
            SELECT * , id as question_id
            FROM question
            WHERE user_id = {user_id}
            ORDER BY submission_time DESC"""
    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def get_answers_by_user(cursor: RealDictCursor, user_id):
    query = f"""
            SELECT * 
            FROM answer
            WHERE user_id = {user_id}
            ORDER BY submission_time DESC"""
    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def get_comments_by_user(cursor: RealDictCursor, user_id):
    query = f"""
        SELECT comment.id, comment.question_id as quest_id, comment.answer_id, 
                comment.user_id, comment.message, comment.submission_time, comment.edited_count,
        (CASE WHEN comment.question_id IS NULL THEN answer.question_id
        ELSE comment.question_id END) AS question_id
        FROM comment 
        LEFT JOIN answer on answer.id = comment.answer_id
        WHERE comment.user_id = {user_id}
        ORDER BY comment.submission_time DESC
        """

    #
    #
    # query = f"""
    #         SELECT *
    #         FROM comment
    #         WHERE user_id = {user_id}
    #         ORDER BY submission_time DESC"""
    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def validate_login(cursor: RealDictCursor, email: str, pwd: str):  # ten email powinien być dict
    query = """
        SELECT * 
        FROM forum_user 
        WHERE mail=%(mail)s AND hash_pass = crypt(%(password)s, hash_pass);"""
    cursor.execute(query, {'mail': email, 'password': pwd})
    return cursor.rowcount > 0


'''function that prepare dictionary of all questions, 
answers and comments for a given user'''
def get_dict_user_activities(user_id):
    questions = get_questions_by_user(user_id)
    answers = get_answers_by_user(user_id)
    comments = get_comments_by_user(user_id)

    user_activities = { "questions": questions,
                        "answers": answers,
                        "comments": comments}
    return user_activities


@database_common.connection_handler
def gain_reputation_by_question(cursor: RealDictCursor, option: str, forum_user_id: int, post_result: str):
    if post_result == "vote_up" and option == "question":
        query = f"""
            UPDATE forum_user
            SET reputation = reputation + 5
            WHERE id = {forum_user_id}
            """
        cursor.execute(query)
    elif post_result == "vote_up" and option == "answer":
        query = f"""
            UPDATE forum_user
            SET reputation = reputation + 10
            WHERE id = {forum_user_id}
            """
        cursor.execute(query)
    else:
        query = f"""
            UPDATE forum_user
            SET reputation = reputation - 2
            WHERE id = {forum_user_id}
            """
        cursor.execute(query)

@database_common.connection_handler
def get_reputation_by_id(cursor: RealDictCursor, user_id: int):
    query = f"""
                SELECT reputation
                FROM forum_user
                WHERE id = {user_id}
                """
    cursor.execute(query)
    return cursor.fetchone()

@database_common.connection_handler
def get_user_id_by_activity(cursor: RealDictCursor, table, item_id: int):
    query = f"""
        SELECT user_id
        FROM {table}
        WHERE id = {item_id}"""
    cursor.execute(query)
    return cursor.fetchone()['user_id']


@database_common.connection_handler
def add_question_image(cursor: RealDictCursor, new_image: dict) -> dict:
    query = f"""
        INSERT INTO question_image (question_id, image)
        VALUES (%(question_id)s, %(image)s)
        """
    cursor.execute(query, new_image)


@database_common.connection_handler
def get_question_image_by_id(cursor: RealDictCursor, question_id: int):
    query = f"""
        SELECT image
        FROM question_image
        WHERE question_id = {question_id}"""
    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def get_answer_image_by_id(cursor: RealDictCursor, answer_id: int):
    query = f"""
        SELECT image
        FROM answer_image
        WHERE answer_id = {answer_id}"""
    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def add_answer_image(cursor: RealDictCursor, new_image: dict) -> dict:
    query = f"""
        INSERT INTO answer_image (answer_id, image)
        VALUES (%(answer_id)s, %(image)s)
        """
    cursor.execute(query, new_image)


@database_common.connection_handler
def delete_question_image(cursor: RealDictCursor, question_id: int):
    query = f"""
        DELETE FROM question_image
        WHERE question_id = {question_id}
        """
    cursor.execute(query)


@database_common.connection_handler
def delete_answer_image(cursor: RealDictCursor, answer_id: int):
    query = f"""
        DELETE FROM answer_image
        WHERE answer_id = {answer_id}
        """
    cursor.execute(query)

@database_common.connection_handler
def check_question_author_id(cursor: RealDictCursor, question_id: int) -> int:
    query = f"""
        SELECT user_id
        FROM question
        WHERE {question_id} = id
        """

    cursor.execute(query)
    return cursor.fetchone()


@database_common.connection_handler
def toggle_answer_acceptance(cursor: RealDictCursor, question_id: int, answer_id: int):
    query = f"""
        UPDATE answer as a
        SET accepted = NOT accepted
        WHERE {answer_id} = a.id AND {question_id} = a.question_id
        """

    cursor.execute(query)


@database_common.connection_handler
def gain_reputation_by_acceptance(cursor: RealDictCursor, accepted: bool, forum_user_id: int):
    if accepted:
        query = f"""
            UPDATE forum_user
            SET reputation = reputation + 15
            WHERE id = {forum_user_id}
            """
        cursor.execute(query)
    else:
        query = f"""
            UPDATE forum_user
            SET reputation = reputation - 15
            WHERE id = {forum_user_id}
            """
        cursor.execute(query)


@database_common.connection_handler
def delete_question_image_by_name(cursor: RealDictCursor, asd: dict):
    query = f"""
        DELETE FROM question_image
        WHERE question_id = {asd['question_id']} and image LIKE '%{asd['filename']}'
        """
    cursor.execute(query)


@database_common.connection_handler
def delete_answer_image_by_name_s(cursor: RealDictCursor, asd: dict):
    query = f"""
        DELETE FROM answer_image
        WHERE answer_id = {asd['answer_id']} and image LIKE '%{asd['filename']}'
        """
    cursor.execute(query)
