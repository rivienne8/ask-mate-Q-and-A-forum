--
-- PostgreSQL database dump
--

-- Dumped from database version 9.5.6
-- Dumped by pg_dump version 9.5.6
CREATE EXTENSION pgcrypto;

ALTER TABLE IF EXISTS ONLY public.question DROP CONSTRAINT IF EXISTS pk_question_id CASCADE;
ALTER TABLE IF EXISTS ONLY public.question DROP CONSTRAINT IF EXISTS fk_user_id CASCADE;
ALTER TABLE IF EXISTS ONLY public.answer DROP CONSTRAINT IF EXISTS pk_answer_id CASCADE;
ALTER TABLE IF EXISTS ONLY public.answer DROP CONSTRAINT IF EXISTS fk_question_id CASCADE;
ALTER TABLE IF EXISTS ONLY public.answer DROP CONSTRAINT IF EXISTS fk_user_id CASCADE;
ALTER TABLE IF EXISTS ONLY public.comment DROP CONSTRAINT IF EXISTS pk_comment_id CASCADE;
ALTER TABLE IF EXISTS ONLY public.comment DROP CONSTRAINT IF EXISTS fk_question_id CASCADE;
ALTER TABLE IF EXISTS ONLY public.comment DROP CONSTRAINT IF EXISTS fk_answer_id CASCADE;
ALTER TABLE IF EXISTS ONLY public.comment DROP CONSTRAINT IF EXISTS fk_user_id CASCADE;
ALTER TABLE IF EXISTS ONLY public.question_tag DROP CONSTRAINT IF EXISTS pk_question_tag_id CASCADE;
ALTER TABLE IF EXISTS ONLY public.question_tag DROP CONSTRAINT IF EXISTS fk_question_id CASCADE;
ALTER TABLE IF EXISTS ONLY public.tag DROP CONSTRAINT IF EXISTS pk_tag_id CASCADE;
ALTER TABLE IF EXISTS ONLY public.question_tag DROP CONSTRAINT IF EXISTS fk_tag_id CASCADE;
ALTER TABLE IF EXISTS ONLY public.forum_user DROP CONSTRAINT IF EXISTS pk_user_id CASCADE;
ALTER TABLE IF EXISTS ONLY public.question_image DROP CONSTRAINT IF EXISTS pk_question_image_id CASCADE;
ALTER TABLE IF EXISTS ONLY public.question_image DROP CONSTRAINT IF EXISTS fk_question_id CASCADE;
ALTER TABLE IF EXISTS ONLY public.answer_image DROP CONSTRAINT IF EXISTS pk_answer_image_id CASCADE;
ALTER TABLE IF EXISTS ONLY public.answer_image DROP CONSTRAINT IF EXISTS fk_answer_id CASCADE;

DROP TABLE IF EXISTS public.question;
CREATE TABLE question (
    id serial NOT NULL,
    submission_time timestamp without time zone,
    view_number integer,
    vote_number integer,
    title text,
    message text,
    image integer,
    user_id integer --NOT NULL
);

DROP TABLE IF EXISTS public.answer;
CREATE TABLE answer (
    id serial NOT NULL,
    submission_time timestamp without time zone,
    vote_number integer,
    question_id integer,
    message text,
    image integer,
    user_id integer, --NOT NULL
    accepted boolean
);

DROP TABLE IF EXISTS public.comment;
CREATE TABLE comment (
    id serial NOT NULL,
    question_id integer,
    answer_id integer,
    user_id integer, --NOT NULL,
    message text,
    submission_time timestamp without time zone,
    edited_count integer
);


DROP TABLE IF EXISTS public.question_tag;
CREATE TABLE question_tag (
    question_id integer NOT NULL,
    tag_id integer NOT NULL
);

DROP TABLE IF EXISTS public.tag;
CREATE TABLE tag (
    id serial NOT NULL,
    name text
);

DROP TABLE IF EXISTS public.forum_user;
CREATE TABLE forum_user (
    id serial NOT NULL,
    mail text,
    submission_time timestamp without time zone,
    number_of_question int DEFAULT 0,
    number_of_answer int DEFAULT 0,
    number_of_comment int DEFAULT 0,
    reputation int DEFAULT 0,
    hash_pass text
);

DROP TABLE IF EXISTS public.question_image;
CREATE TABLE question_image (
    question_id integer NOT NULL,
    image text
);

DROP TABLE IF EXISTS public.answer_image;
CREATE TABLE answer_image (
    answer_id integer NOT NULL,
    image text
);

ALTER TABLE ONLY answer
    ADD CONSTRAINT pk_answer_id PRIMARY KEY (id);

ALTER TABLE ONLY comment
    ADD CONSTRAINT pk_comment_id PRIMARY KEY (id);

ALTER TABLE ONLY question
    ADD CONSTRAINT pk_question_id PRIMARY KEY (id);


ALTER TABLE ONLY question_tag
    ADD CONSTRAINT pk_question_tag_id PRIMARY KEY (question_id, tag_id);

ALTER TABLE ONLY tag
    ADD CONSTRAINT pk_tag_id PRIMARY KEY (id);

ALTER TABLE ONLY forum_user
    ADD CONSTRAINT pk_user_id PRIMARY KEY (id);

ALTER TABLE ONLY comment
    ADD CONSTRAINT fk_answer_id FOREIGN KEY (answer_id) REFERENCES answer(id);

ALTER TABLE ONLY comment
    ADD CONSTRAINT fk_user_id FOREIGN KEY (user_id) REFERENCES forum_user(id);

ALTER TABLE ONLY answer
    ADD CONSTRAINT fk_question_id FOREIGN KEY (question_id) REFERENCES question(id);

ALTER TABLE ONLY answer
    ADD CONSTRAINT fk_user_id FOREIGN KEY (user_id) REFERENCES forum_user(id);

ALTER TABLE ONLY question_tag
    ADD CONSTRAINT fk_question_id FOREIGN KEY (question_id) REFERENCES question(id);

ALTER TABLE ONLY comment
    ADD CONSTRAINT fk_question_id FOREIGN KEY (question_id) REFERENCES question(id);

ALTER TABLE ONLY question_tag
    ADD CONSTRAINT fk_tag_id FOREIGN KEY (tag_id) REFERENCES tag(id);

ALTER TABLE ONLY question
    ADD CONSTRAINT fk_user_id FOREIGN KEY (user_id) REFERENCES forum_user(id);

ALTER TABLE ONLY question_image
    ADD CONSTRAINT pk_question_image_id PRIMARY KEY (question_id, image);

ALTER TABLE ONLY answer_image
    ADD CONSTRAINT pk_answer_image_id  PRIMARY KEY (answer_id, image);

ALTER TABLE ONLY question_image
    ADD CONSTRAINT fk_question_id FOREIGN KEY (question_id) REFERENCES question(id);

ALTER TABLE ONLY answer_image
    ADD CONSTRAINT fk_answer_id FOREIGN KEY (answer_id) REFERENCES answer(id);


INSERT INTO forum_user VALUES (0, 'witam@gmail.com', '2017-04-28 16:49:00', 4, 5, 8, 12, crypt('asd123', gen_salt('bf', 8)));
INSERT INTO forum_user VALUES (1, 'matiw@gmail.com', '2016-04-28 16:49:00', 4, 5, 5, 46, crypt('asd123', gen_salt('bf', 8)));
INSERT INTO forum_user VALUES (2, 'korek@gmail.com', '2020-04-28 16:49:00', 0, 0, 0, 0, crypt('asd123', gen_salt('bf', 8)));


SELECT pg_catalog.setval('forum_user_id_seq', 2, true);


INSERT INTO question VALUES (0, '2017-04-28 08:29:00', 29, 7, 'How to make lists in Python?', 'I am totally new to this, any hints?', 1, 0);
INSERT INTO question VALUES (1, '2017-04-29 09:19:00', 15, 9, 'Wordpress loading multiple jQuery Versions', 'I developed a plugin that uses the jquery booklet plugin (http://builtbywill.com/booklet/#/) this plugin binds a function to $ so I cann call $(".myBook").booklet();

I could easy managing the loading order with wp_enqueue_script so first I load jquery then I load booklet so everything is fine.

BUT in my theme i also using jquery via webpack so the loading order is now following:

jquery
booklet
app.js (bundled file with webpack, including jquery)', 1, 0);
INSERT INTO question VALUES (2, '2017-05-01 10:41:00', 1364, 57, 'Drawing canvas with an image picked with Cordova Camera Plugin', 'I''m getting an image from device and drawing a canvas with filters using Pixi JS. It works all well using computer to get an image. But when I''m on IOS, it throws errors such as cross origin issue, or that I''m trying to use an unknown format.
', 0, 0);
INSERT INTO question VALUES (3, '2017-09-01 12:49:00', 553, 98, 'Best way to do baked potatoes?', 'I''m going to do up 2 racks of ribs and to simplify cooking i was thinking of doing some baked potatoes. Is there a good easy way to make them on the smoker over the last 2 hours the ribs are cooking? If not i can dice up potatoes in the oven, it''d just be nice to not have to run back and forth.', 0, 0);
INSERT INTO question VALUES (4, '2017-10-01 12:12:00', 553, 98, 'Helpful tips to better sleep with babies', 'Hi mummies

I have read different theories on how to put babies to sleep, some advise not to rock, just put on cot, some said can rock...

I am now trying to put my girl (11 Month) to sleep by going thru bedtime ritual which include bath, milk, book...then I would put her in her cot awake and sit by the cot. She would get up and stand in the cot, then I put her down and we would "wrestle" like that for 45 mins, 30 mins, 20 mins etc.. (wow, tiring!)...the few nights she would then finally remain in bed and doze off...so my question is am I doing the right thing? Will I make my baby detest sleeping?

At this point I am very sure I cannot just put her down and walk out of the room, she would definitely cry...

So any mummies have same experience? Pls advise.

Thanks.', 0, 2);

INSERT INTO question VALUES (5, '2018-04-28 08:29:00', 3, 7, 'How to keep the header static, always on top while scrolling?', 'How would I go about keeping my header from scrolling with the rest of the page? I thought about utilizing frame-sets and iframes, just wondering if there is a easier and more user friendly way, what would be the best-practice for doing this?', 1, 1);
INSERT INTO question VALUES (6, '2018-05-29 09:19:00', 5, 19, 'Is there a CSS parent selector?','How do I select the <li> element that is a direct parent of the anchor element?
As an example, my CSS would be something like this:
li < a.active {
    property: value;
}
Obviously there are ways of doing this with JavaScript, but I''m hoping that there is some sort of workaround that exists native to CSS Level 2.
The menu that I am trying to style is being spewed out by a CMS, so I can''t move the active element to the <li> element... (unless I theme the menu creation module which I''d rather not do).
Any ideas?', 1, 1);
INSERT INTO question VALUES (7, '2020-05-01 10:41:00', 14, 57, 'How do I create a folder in a GitHub repository?', 'I want to create a folder in a GitHub repository and want to add files in that folder. How do I achieve this?
', 1, 2);


SELECT pg_catalog.setval('question_id_seq', 7, true);


INSERT INTO answer VALUES (1, '2017-04-28 16:49:00', 4, 1, 'You need to use brackets: my_list = []', 1, 2, False);
INSERT INTO answer VALUES (2, '2017-04-25 14:42:00', 35, 1, 'Look it up in the Python docs', 1, 1, False);
INSERT INTO answer VALUES (3, '2017-09-01 14:42:00', 1, 3, 'you could start them in the micro wave for 5 or ten minutes then just through them in the smoker to finish, you could wrap them foil if you don''t want the smoke on them, but I don''t know why you wouldn''t good luck', 1, 2, False);
INSERT INTO answer VALUES (4, '2017-09-01 20:24:00', 2, 3, 'Rub them down with butter, salt/pepper them, wrap them completely in foil and throw them on the smoker. You''re probably looking at 4 hours of cook time at 250 degree smoker temp.', 0, 1, False);
INSERT INTO answer VALUES (5, '2017-10-01 20:24:00', 5, 4, 'Hey, i have the same problem as you. I will put my son and wrestle with him on our bed when i know it is nearly his time to sleep like bout 9plus. And because he always sleep on our bed, he knows when i lift him up to put him in his cot and he cries and so end up will be back on our bed. I have no ides how to stop this cos i think it has been a habit and i think we will have a problem making him sleep alone next time.', 0, 0, False);
INSERT INTO answer VALUES (6, '2017-10-01 20:37:00', 2, 4, 'You have to do it the hard way. My mum is a baby sitter, currently looking after 2 kids. She had looked after more than 5 kids and have 4 kids of her own. You have to break the habit. At their bedtime, put them to bed and leave the room. If they are crying, you have to let them cry. The 1st few days you can walk in and look at them at different intervals but do not carry them. Make the intervals longer and longer. It''s really heart breaking at first. But after sometime, they will realise it''s no use crying, they will fall asleep on their own. Most of the time after 1 week you will see the effect.', 0, 1, False);
INSERT INTO answer VALUES (7, '2020-04-28 16:49:00', 4, 5, 'Use position: fixed on the div that contains your header. when #content starts off 100px below #header, but as the user scrolls, #header stays in place. Of course it goes without saying that you''ll want to make sure #header has a background so that its content will actually be visible when the two divs overlap.', 1, 0, False);
INSERT INTO answer VALUES (8, '2020-04-25 14:42:00', 35, 6, 'There is currently no way to select the parent of an element in CSS.
If there was a way to do it, it would be in either of the current CSS selectors specs:
Selectors Level 3 Spec
CSS 2.1 Selectors Spec
That said, the Selectors Level 4 Working Draft includes a :has() pseudo-class that will provide this capability. It will be similar to the jQuery implementation.', 1, 2, False);

INSERT INTO answer VALUES (9, '2020-04-15 14:42:00', 35, 7, 'You cannot create an empty folder and then add files to that folder, but rather creation of a folder must happen together with adding of at least a single file. On GitHub you can do it this way:
Go to the folder inside which you want to create another folder
Click on New file
On the text field for the file name, first write the folder name you want to create
Then type /. This creates a folder
You can add more folders similarly
Finally, give the new file a name (for example, .gitkeep which is conventionally used to make Git track otherwise empty folders; it is not a Git feature though)
Finally, click Commit new file', 0, 0, False);
INSERT INTO answer VALUES (10, '2020-04-15 14:42:00', 5, 7, 'Git doesn''t store empty folders. Just make sure there''s a file in the folder like doc/foo.txt and run git add doc or git add doc/foo.txt, and the folder will be added to your local repository once you''ve committed (and appear on GitHub once you''ve pushed it).', 0, 1, False);


SELECT pg_catalog.setval('answer_id_seq', 10, true);



INSERT INTO comment VALUES (1, 0, NULL, 2, 'Please clarify the question as it is too vague!', '2017-05-01 05:49:00');
INSERT INTO comment VALUES (2, NULL, 1, 0, 'I think you could use my_list = list() as well.', '2017-05-02 16:55:00');
INSERT INTO comment VALUES (3, NULL, 4, 2, 'If you wrap them in foil, then what''s the point in putting them in the smoker?', '2017-09-02 16:55:00');
INSERT INTO comment VALUES (4, NULL, 6, 2, 'Wow, i really cannot bear to do that. I tried and it is so torturing to see my son really crying and i will quickly carry him in my arms again. Sigh, i know this is bad, but got no choice, heart too soft. I will try see if got other methods not.', '2017-10-02 16:55:00');
INSERT INTO comment VALUES (5, NULL, 6, 0, 'No choice ma. This method is the most effective one I know. Work for all the babies so far. But really heart breaking.', '2017-10-02 18:52:00');

INSERT INTO comment VALUES (6, 5, NULL, 0, 'What do you mean by header? Of a page? Of a table?', '2017-02-01 05:49:00');
INSERT INTO comment VALUES (7, NULL,7, 0, 'Do you know of a way to let it scroll until it hits the top and then "position: fixed;"? If your header started below the top?', '2017-06-01 05:49:00');
INSERT INTO comment VALUES (8, NULL,7, 0, 'This solution requires defining a hard-coded size. Is there a way doing it without a hard-coded size? Perhaps by defining one div to be below another? Perhaps some relationship between the header and content without hard-coded values?', '2017-08-01 05:49:00');

INSERT INTO comment VALUES (9, 6, NULL, 1, 'Per my comment on the accepted answer, it looks like the polyfill may be required even in the near future after all, because the subject indicator may never be implemented by browsers in CSS.', '2017-05-11 05:49:00');
INSERT INTO comment VALUES (10, 6, NULL, 2, 'There is no parent selector; just the way there is no previous sibling selector. One good reason for not having these selectors is because the browser has to traverse through all children of an element to determine whether or not a class should be applied. For example, if you wrote:
body:contains-selector(a.active) { background: red; }', '2017-05-11 05:49:00');
INSERT INTO comment VALUES (11, NULL, 8, 1, 'Looks like the subject selector has been revisited, except by using a ! now: The subject of the selector can be explicitly identified by appending an exclamation mark (!) to one of the compound selectors in a selector.', '2017-05-12 16:55:00');


INSERT INTO comment VALUES (12, 7, NULL, 2, 'I know this is very old question but still might save time for someone The below link is to an answer mentioning how to create folder on Github website itself.', '2018-02-21 05:49:00');
INSERT INTO comment VALUES (13, NULL,10, 0, 'If you set up your repository on github the way the site suggests, it''d be "git push origin master" - origin being the default name for the remote repository and master being the default name of your branch.', '2018-03-01 05:49:00');


SELECT pg_catalog.setval('comment_id_seq', 13, true);


INSERT INTO tag VALUES (1, 'python');
INSERT INTO tag VALUES (2, 'sql');
INSERT INTO tag VALUES (3, 'css');
SELECT pg_catalog.setval('tag_id_seq', 3, true);

INSERT INTO question_tag VALUES (0, 1);
INSERT INTO question_tag VALUES (1, 3);
INSERT INTO question_tag VALUES (2, 3);

INSERT INTO question_image VALUES (0, 'uploads/translate.png');
INSERT INTO question_image VALUES (1, 'uploads/images1.jpg');
INSERT INTO question_image VALUES (4, 'uploads/birds_rainbow-lorakeets.png');
INSERT INTO question_image VALUES (5, 'uploads/kwiatki1.jfif');
INSERT INTO question_image VALUES (6, 'uploads/magnolia.jfif');
INSERT INTO question_image VALUES (7, 'uploads/narcyz.jfif');

INSERT INTO answer_image VALUES (1, 'uploads/bananas.jpg');
INSERT INTO answer_image VALUES (2, 'uploads/strawberries.jpg');
INSERT INTO answer_image VALUES (3, 'https://www.kasandbox.org/programming-images/landscapes/mountain_matterhorn.png');
INSERT INTO answer_image VALUES (7, 'uploads/niezapominajki.jfif');
INSERT INTO answer_image VALUES (8, 'https://1.bp.blogspot.com/-kGcxwneCgiM/Xseae3AuoYI/AAAAAAAAcHc/nJBKSBJXYKw2ZGGwj46OZ1cTWrXPlCZmwCLcBGAsYHQ/s1600/IMG_3162.jpg');

