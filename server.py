from flask import Flask, render_template, url_for, redirect,\
    request, send_from_directory, make_response, session, \
    escape, flash
import data_manager, util
import os
from bcrypt import checkpw, hashpw, gensalt

app = Flask(__name__)
app.secret_key = os.urandom(16)
app.config['UPLOAD_PATH'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # maksymalna wielkosc uploadowanego obrazu
headers = ["Title", "Message", "Submission Time", "Views", "Votes"]
story_keys = ["title", "message", "submission_time", "view_number", "vote_number"]
tag_headers = ["Tag name", "Number of question"]
tag_keys = ["name", "count"]
question_tag = ["title", "message"]

FORM_USERNAME = 'username'
FORM_PASSWORD = 'password'
SESSION_USERNAME = 'username'
SESSION_ID = 'user_id'
SESSION_REPUTATION = 'reputation'


def swap_image(uploaded_file):
    """function to use when user can upload file"""
    if uploaded_file.filename != '':
        unique_filename = util.make_unique(uploaded_file.filename)
        uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], unique_filename))
        return os.path.join(app.config['UPLOAD_PATH'], unique_filename)  # question['image'] = ...


@app.route("/")
def main_page():
    questions = data_manager.get_questions(5)
    response = make_response(render_template("index.html", user_id=SESSION_ID,
                            username=SESSION_USERNAME, headers=headers,
                            questions=questions, story_keys=story_keys))
    return response


@app.route("/list")
def question_page():
    questions = data_manager.get_questions(None)
    if len(request.args) != 0:
        questions = data_manager.get_questions_by_order(request.args.get("order_by"),
                                                        request.args.get("order_direction"))
    response = make_response(
        render_template("question_list.html", username=SESSION_USERNAME, headers=headers, questions=questions,
                        story_keys=story_keys))
    return response


@app.route("/search")
def display_search_question():
    search_phrase = request.args.get("search")
    questions = data_manager.get_questions_by_phrase(search_phrase)
    answers = data_manager.get_answers_by_phrase(search_phrase)
    answers_test = {}
    if len(search_phrase) == 0:
        return redirect(url_for("main_page"))
    for answer in answers:
        if not answer["question_id"] in answers_test.keys():
            answers_test[answer["question_id"]] = [answer]
        else:
            answers_test[answer["question_id"]].append(answer)
        if not answer["question_id"] in [x["id"] for x in questions]:
            questions.append(data_manager.get_question_by_id(answer["question_id"]))

    response = make_response(
        render_template("search_page.html", username=SESSION_USERNAME, questions=questions, answers=answers_test,
                        search_phrase=search_phrase))
    return response


@app.route("/uploads/<filename>")
def get_img(filename):
    return send_from_directory(app.config['UPLOAD_PATH'], filename)


def get_filename(path):
    file_name = os.path.split(path)[1]
    return file_name


app.jinja_env.globals.update(get_filename=get_filename)


@app.route("/question/<question_id>")
def display_question(question_id):
    if request.referrer != request.url:
        data_manager.views_updated(question_id)

    question = data_manager.get_question_by_id(question_id)
    answers = data_manager.get_answers_by_question_id(question_id)
    question_comments = data_manager.get_comments_by_question_id(question_id)
    answer_comments = data_manager.get_answer_comments_by_question_id(question_id)
    answers_headers = ["Votes' number", "Answer", "Submission time"]
    comment_headers = ["Submission time", "Message", "Edition counter"]
    question_tag = data_manager.get_tag_by_question_id(question_id)
    # users = data_manager.get_all_users_basic_info()
    question_image = data_manager.get_question_image_by_id(question_id)
    answers_images = util.get_answers_images(answers)

    author_id = data_manager.check_question_author_id(question_id)['user_id']

    response = make_response(render_template("question.html",
                                             username=SESSION_USERNAME,
                                             user_id=SESSION_ID,
                                             question=question,
                                             answers=answers,
                                             answers_headers=answers_headers,
                                             question_comments=question_comments,
                                             comment_headers=comment_headers,
                                             answer_comments=answer_comments,
                                             question_tag=question_tag,
                                             question_image=question_image,
                                             answers_images=answers_images,
                                             author_id=author_id,
                                             # author=author
                                             # users=users
                                             ))
    return response


@app.route("/add")
def add_question_get():
    if session.get(FORM_USERNAME):
        new_question = {
            "id": None,
            "title": "",
            "message": "",
            "image": "",
            "submission_time": None,
            "view_number": 0,
            "vote_number": 0,
            "user_id": SESSION_ID
        }
        response = make_response(render_template("add_update_question.html", user_id=SESSION_ID, username=SESSION_USERNAME,
                                                 question=new_question))
        return response
    else:
        return redirect(url_for('login_user'))


@app.route("/add/post", methods=["POST"])
def add_question_post():
    new_question = dict(request.form)
    new_question['submission_time'] = util.get_current_date_time()
    new_question["view_number"] = 0
    new_question["vote_number"] = 0
    new_question["user_id"] = session[SESSION_ID]

    uploaded_file = request.files.getlist('file')

    if len(uploaded_file[0].filename) != 0 or len(new_question['image_url']) != 0:
        new_question['image'] = 1
        question_id = data_manager.add_question(new_question).get('id')
        if len(uploaded_file[0].filename) != 0:
            for file in uploaded_file:
                data_manager.add_question_image({"question_id": question_id, "image": swap_image(file)})
        if len(new_question['image_url']) != 0:
            data_manager.add_question_image({"question_id": question_id, "image": new_question['image_url']})

    else:
        new_question['image'] = 0
        question_id = data_manager.add_question(new_question).get('id')

    return redirect(url_for("display_question", question_id=question_id))


@app.route("/question/<int:question_id>/edit")
def edit_question_get(question_id):
    user_id = data_manager.get_user_id_by_activity('question', question_id)
    question = data_manager.get_question_by_id(question_id)
    question_image = data_manager.get_question_image_by_id(question_id)
    if session.get(FORM_USERNAME) and session[SESSION_ID] == user_id:
        if question is None:
            return redirect(url_for("display_question", question_id=question_id))
        else:
            response = make_response(
                render_template("add_update_question.html", username=SESSION_USERNAME, question=question, question_image=question_image))
            return response
    else:
        flash("Update option is available only for the author!", "warning")
        return redirect(url_for('display_question', question_id=question_id))


@app.route("/question/<int:question_id>/edit/post", methods=["POST"])
def edit_question_post(question_id):
    edited_question = dict(request.form)

    uploaded_file = request.files.getlist('file')

    if len(uploaded_file[0].filename) != 0 or len(edited_question['image_url']) != 0:
        edited_question['image'] = 1
        data_manager.update_question(edited_question)
        if len(uploaded_file[0].filename) != 0:
            for file in uploaded_file:
                data_manager.add_question_image({"question_id": question_id, "image": swap_image(file)})
        if len(edited_question['image_url']) != 0:
            data_manager.add_question_image({"question_id": question_id, "image": edited_question['image_url']})

    else:
        if len(data_manager.get_question_pictures_paths(question_id)) == 0:
            edited_question['image'] = 0
            data_manager.update_question(edited_question)
        else:
            edited_question['image'] = 1
            data_manager.update_question(edited_question)

    return redirect(url_for("display_question", question_id=question_id))


@app.route("/question/<int:question_id>/edit/post/delete_image/<filename>")
def delete_image(question_id, filename):
    data_manager.delete_question_image_by_name({"question_id": question_id, "filename": filename})
    util.delete_all_images([{'image': f"uploads\\{filename}"}])
    return redirect(url_for('edit_question_get', question_id=question_id))


@app.route("/question/<question_id>/delete")
def delete_question(question_id):
    user_id = data_manager.get_user_id_by_activity('question', question_id)
    if session.get(FORM_USERNAME) and session[SESSION_ID] == user_id:
        answer_pictures_paths = data_manager.get_answer_pictures_paths(question_id)
        for image in answer_pictures_paths:
            data_manager.delete_answer_image(image['answer_id'])
        util.delete_all_images(answer_pictures_paths)

        question_pictures_paths = data_manager.get_question_pictures_paths(question_id)
        data_manager.delete_question_image(question_id)
        util.delete_all_images(question_pictures_paths)

        if data_manager.has_question_comment(question_id) is not None:
            data_manager.delete_comment_for_question(question_id)
        data_manager.delete_question_from_question_tag(question_id)

        data_manager.delete_comment_for_answers_for_question(question_id)
        data_manager.delete_answers_for_question(question_id)

        data_manager.delete_question(question_id)

        return redirect(url_for("question_page"))
    else:
        flash("Delete option is available only for the author!", "rejection")
        return redirect(url_for('display_question', question_id=question_id))


@app.route("/question/<question_id>/new_answer")
def add_answer(question_id):
    if session.get(FORM_USERNAME):
        question = data_manager.get_question_by_id(question_id)
        new_answer = \
            {
                "answer_id": None,
                "submission_time": None,
                "view_number": 0,
                "vote_number": 0,
                "id": None,
                "message": "",
                "image": "",
                "user_id": SESSION_ID
            }
        response = make_response(
            render_template("answer.html", user_id=SESSION_ID, username=SESSION_USERNAME, question=question, answer=new_answer))
        return response
    else:
        return redirect(url_for('login_user'))


@app.route("/question/<int:question_id>/new_answer/post", methods=["POST"])
def add_answer_post(question_id):
    new_answer = dict(request.form)
    new_answer["submission_time"] = util.get_current_date_time()
    new_answer["question_id"] = question_id
    new_answer["vote_number"] = 0
    new_answer["user_id"] = session[SESSION_ID]
    new_answer["accepted"] = False

    uploaded_file = request.files.getlist('file')
    if len(uploaded_file[0].filename) != 0 or len(new_answer['image_url']) != 0:
        new_answer['image'] = 1
        answer_id = data_manager.add_answer(new_answer).get('id')
        if len(uploaded_file[0].filename) != 0:
            for file in uploaded_file:
                data_manager.add_answer_image({"answer_id": answer_id, "image": swap_image(file)})
        if len(new_answer['image_url']) != 0:
            data_manager.add_answer_image({"answer_id": answer_id, "image": new_answer['image_url']})

    else:
        new_answer['image'] = 0
        answer_id = data_manager.add_answer(new_answer).get('id')

    return redirect(url_for("display_question", question_id=question_id, answer_id=answer_id))


@app.route("/question/<int:question_id>/<int:answer_id>/edit-answer")
def edit_answer_get(question_id, answer_id):
    user_id = data_manager.get_user_id_by_activity('answer', answer_id)
    question = data_manager.get_question_by_id(question_id)
    if session.get(FORM_USERNAME) and session[SESSION_ID] == user_id:
        answer = data_manager.get_answer_by_id(answer_id)
        answer_images = util.get_answers_images([answer])
        if answer is None:
            return redirect(url_for("display_question", question_id=question_id))
        else:
            response = make_response(
                render_template("add_update_answer.html", username=SESSION_USERNAME, question=question, answer=answer, answer_images=answer_images))
            return response
    else:
        flash("Update option is available only for the author!", "warning")
        return redirect(url_for('display_question', question_id=question_id))


@app.route("/question/<int:question_id>/<int:answer_id>/edit-answer", methods=["POST"])
def edit_answer_post(question_id, answer_id):
    edited_answer = dict(request.form)

    uploaded_file = request.files.getlist('file')

    if len(uploaded_file[0].filename) != 0 or len(edited_answer['image_url']) != 0:
        edited_answer['image'] = 1
        data_manager.update_answer(answer_id, edited_answer)
        if len(uploaded_file[0].filename) != 0:
            for file in uploaded_file:
                data_manager.add_answer_image({"answer_id": answer_id, "image": swap_image(file)})
        if len(edited_answer['image_url']) != 0:
            data_manager.add_answer_image({"answer_id": answer_id, "image": edited_answer['image_url']})

    else:
        if len(data_manager.get_answer_id_pictures_paths(answer_id)) == 0:
            edited_answer['image'] = 0
            data_manager.update_answer(answer_id, edited_answer)
        else:
            edited_answer['image'] = 1
            data_manager.update_answer(answer_id, edited_answer)

    return redirect(url_for("display_question", question_id=question_id, answer_id=answer_id))


@app.route("/question/<int:question_id>/<int:answer_id>/edit-answer/delete_image/<filename>")
def delete_image_answer(question_id, answer_id, filename):
    data_manager.delete_answer_image_by_name_s(({"answer_id": answer_id, "filename": filename}))
    util.delete_all_images([{'image': f"uploads\\{filename}"}])
    return redirect(url_for('edit_answer_get', question_id=question_id, answer_id=answer_id))


@app.route("/answer/<question_id>/<answer_id>/delete")
def delete_answer(question_id, answer_id):
    user_id = data_manager.get_user_id_by_activity('answer', answer_id)
    if session.get(FORM_USERNAME) and session[SESSION_ID] == user_id:
        answer_pictures_paths = data_manager.get_answer_id_pictures_paths(answer_id)
        util.delete_all_images(answer_pictures_paths)
        data_manager.delete_answer_image(answer_id)
        if data_manager.has_answer_comment(answer_id) is not None:
            data_manager.delete_comment_for_answer(answer_id)

        data_manager.delete_answer_from_answers(answer_id)

        return redirect(url_for("display_question", question_id=question_id))
    else:
        flash("Delete option is available only for the author!", "rejection")
        return redirect(url_for('display_question', question_id=question_id))


@app.route("/question/<question_id>/<forum_user>/vote_up", methods=["POST"])
def question_vote(question_id, forum_user):
    post_result = dict(request.form)["vote_question"]
    difference = util.get_difference_of_votes(post_result)
    data_manager.update_question_votes(question_id, difference)
    data_manager.gain_reputation_by_question("question", forum_user, post_result)
    return redirect(url_for("display_question", question_id=question_id))


@app.route("/answer/<question_id>/<answer_id>/<forum_user>/vote_up", methods=["POST"])
def answer_vote(question_id, answer_id, forum_user):
    post_result = dict(request.form)["vote_answer"]
    # print(post_result)
    difference = util.get_difference_of_votes(post_result)
    data_manager.update_answer_votes(answer_id, difference)
    data_manager.gain_reputation_by_question("answer", forum_user, post_result)
    return redirect(url_for("display_question", question_id=question_id))

@app.route("/question/<question_id>/<answer_id>/post", methods=["POST"])
def accept_answer(question_id, answer_id):
    data_manager.toggle_answer_acceptance(question_id, answer_id)
    answer = data_manager.get_answer_by_id(answer_id)
    data_manager.gain_reputation_by_acceptance(answer['accepted'], answer['user_id'])
    return redirect(url_for("display_question", question_id=question_id))


@app.route('/question/<question_id>/new-comment', methods=["GET", "POST"])
def new_question_comment(question_id):
    if session.get(FORM_USERNAME):
        if request.method == "POST":
            details = dict(request.form)
            details["submission_time"] = util.get_current_date_time()
            if session.get(FORM_USERNAME):
                details["user_id"] = session['user_id']
            data_manager.add_question_comment(details)

            return redirect(url_for("display_question", question_id=question_id))
        if request.method == "GET":
            question = data_manager.get_question_by_id(question_id)
            response = make_response(render_template("add_comment.html",
                                                     username=SESSION_USERNAME,
                                                     item=question,
                                                     item_type="question",
                                                     url=url_for('new_question_comment', question_id=question_id)))

            return response
    else:
        return redirect(url_for('login_user'))


@app.route('/comment/<comment_id>/edit', methods=["POST"])
def update_comment_post(comment_id):
    user_id = data_manager.get_user_id_by_activity('comment', comment_id)
    question_id = data_manager.get_question_id_by_comment_id(comment_id)
    if session.get(FORM_USERNAME) and session[SESSION_ID] == user_id:
        if request.method == "POST":
            details = dict(request.form)
            details["submission_time"] = util.get_current_date_time()

            data_manager.update_comment(details, comment_id)
            return redirect(url_for("display_question", question_id=question_id))
    else:
        flash("Update option is available only for the author!", "warning")
        return redirect(url_for('display_question', question_id=question_id))


@app.route('/comment/<comment_id>/edit', methods=["GET"])
def update_comment_get(comment_id):
    user_id = data_manager.get_user_id_by_activity('comment', comment_id)
    question_id = data_manager.get_question_id_by_comment_id(comment_id)
    if session.get(FORM_USERNAME) and session[SESSION_ID] == user_id:
        comment = data_manager.get_comment_by_id(comment_id)

        if comment.get("question_id") != None:
            question = data_manager.get_question_by_comment_id(comment_id)
            response = make_response(render_template("update_comment.html",
                                                     username=SESSION_USERNAME,
                                                     comment=comment,
                                                     item=question,
                                                     item_type="question"))

            return response

        elif comment.get("answer_id") != None:
            answer = data_manager.get_answer_by_comment_id(comment_id)
            response = make_response(render_template("update_comment.html",
                                                     username=SESSION_USERNAME,
                                                     comment=comment,
                                                     item=answer,
                                                     item_type="answer"))

            return response
    else:
        flash("Update option is available only for the author!", "warning")
        return redirect(url_for('display_question', question_id=question_id))


@app.route('/comments/<comment_id>/delete')
def delete_comment(comment_id):
    user_id = data_manager.get_user_id_by_activity('comment', comment_id)
    question_id = data_manager.get_question_id_by_comment_id(comment_id)
    if session.get(FORM_USERNAME) and session[SESSION_ID] == user_id:
        data_manager.delete_comment(comment_id)
        return redirect(url_for("display_question", question_id=question_id))
    else:
        flash("Delete option is available only for the author!", "rejection")
        return redirect(url_for('display_question', question_id=question_id))


@app.route('/answer/<answer_id>/new-comment', methods=["GET", "POST"])
def new_answer_comment(answer_id):
    if session.get(FORM_USERNAME):
        if request.method == "POST":
            details = dict(request.form)
            details["submission_time"] = util.get_current_date_time()
            details["user_id"] = session['user_id']
            data_manager.add_answer_comment(details)
            question_id = data_manager.get_question_id_by_answer_id(answer_id)
            return redirect(url_for("display_question", question_id=question_id))

        if request.method == "GET":
            answer = data_manager.get_answer_by_id(answer_id)
            response = make_response(render_template("add_comment.html",
                                                     username=SESSION_USERNAME,
                                                     item=answer,
                                                     item_type="answer",
                                                     url=url_for('new_answer_comment', answer_id=answer_id)))

            return response
    else:
        return redirect(url_for('login_user'))


@app.route('/question/<question_id>/new-tag', methods=["GET", "POST"])
def add_tag(question_id):
    if request.method == "POST":
        tag_name = dict(request.form)

        tag_id = data_manager.add_question_tag(tag_name).get('id')
        data_manager.add_question_tag_id(tag_id, question_id)

        return redirect(url_for("display_question", question_id=question_id, tag_id=tag_id))

    if request.method == "GET":
        possible_tags = []
        all_tags = data_manager.get_all_tags()
        tags_in_question = data_manager.get_tag_from_question(question_id)

        for tag in all_tags:
            if tag not in tags_in_question:
                possible_tags.append(tag)

        response = make_response(render_template("add_tag.html", username=SESSION_USERNAME, question_id=question_id,
                                                 possible_tags=possible_tags))
        return response


@app.route('/question/<question_id>/old-tag', methods=["POST"])
def add_old_tag(question_id):
    tag_name = dict(request.form)
    tag_old_id = data_manager.get_tag_id_by_name(tag_name['tag_name']).get('id')
    data_manager.add_question_tag_id(tag_old_id, question_id)

    return redirect(url_for("display_question", question_id=question_id))


@app.route('/tags/<tag_id>/delete')
def delete_tag(tag_id):
    question_id = data_manager.get_question_id_by_tag_id(tag_id)
    data_manager.delete_tag(tag_id, question_id)

    return redirect(url_for("display_question", question_id=question_id))


@app.route("/tags")
def tags_page():
    tags = data_manager.get_tag_to_list()

    if len(request.args) != 0:
        tags = data_manager.get_tags_by_order(request.args.get("order_by"),
                                              request.args.get("order_direction"))

    response = make_response(
        render_template("tag_list.html", username=SESSION_USERNAME, tag_headers=tag_headers, tags=tags,
                        tag_keys=tag_keys))
    return response


@app.route("/tags/<tag_id>")
def tag_questions_search(tag_id):

    questions_by_tag = data_manager.get_questions_by_tag(tag_id)

    response = make_response(
        render_template("tag_questions.html", username=SESSION_USERNAME, tag_id=tag_id, question_tag=question_tag, questions_by_tag=questions_by_tag))
    return response


@app.route('/registration/<ver>')
@app.route('/registration')
def registration_user(ver=None):
    response = make_response(render_template("registration.html", username=SESSION_USERNAME, ver=ver))
    return response


@app.route('/registration/post', methods=["POST"])
def registration_user_post():
    email = dict(request.form)
    email['email'] = email['email'].lower()
    if data_manager.check_for_user(email):
        return redirect(url_for("registration_user", ver="exist"))
    else:
        email['submission_time'] = util.get_current_date_time()
        data_manager.add_new_user(email)
    return redirect(url_for("main_page"))


@app.route('/users', methods=["GET"])
def display_users():
    if session.get(FORM_USERNAME):
        all_users = data_manager.get_all_users()
        response = make_response(render_template('users.html', username=SESSION_USERNAME, users=all_users))
        return response
    else:
        return redirect(url_for('login_user'))


@app.route('/user/<user_id>')
def display_user(user_id):
    if session.get(FORM_USERNAME):
        user = data_manager.get_user_details(user_id)
        activities = data_manager.get_dict_user_activities(user_id)
        response = make_response(
            render_template('user.html', username=SESSION_USERNAME, user=user, activities=activities))
        return response
    else:
        return redirect(url_for('login_user'))


@app.route('/login/<ver>')
@app.route('/login')
def login_user(ver=None):
    response = make_response(render_template('login.html', ver=ver, username=FORM_USERNAME, password=FORM_PASSWORD))
    return response


@app.route('/login/post', methods=['POST'])
def login_user_post():
    email = request.form[FORM_USERNAME]
    pwd = request.form[FORM_PASSWORD]

    check_email = data_manager.validate_login(email, pwd)
    if check_email:
        session[SESSION_USERNAME] = email
        user_id = data_manager.get_user_id_by_mail(email)
        session[SESSION_ID] = user_id
        session[SESSION_REPUTATION] = data_manager.get_reputation_by_id(session[SESSION_ID])
        return redirect(url_for('main_page'))
    else:
        return redirect(url_for('login_user', ver="bad"))


@app.route('/logout/')
def logout():
    session.pop(SESSION_USERNAME, None)
    session.pop(SESSION_ID, None)
    session.pop(SESSION_REPUTATION, None)
    return redirect(url_for('main_page'))


@app.errorhandler(404)
def page_not_found(e):
    response = make_response(render_template('404.html', username=SESSION_USERNAME), 404)
    return response


if __name__ == "__main__":
    app.run()
