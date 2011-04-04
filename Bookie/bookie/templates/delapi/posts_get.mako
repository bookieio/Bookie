# -*- coding: utf-8 -*-
<?xml version="1.0" encoding="UTF-8"?>
<posts user="none" dt="${datefound}" tag="">
    % for post in posts:
        <post href="${post.url}"
            hash="---"
            description="${escape(post.description)}"
            extended="${escape(post.extended)}"
            tag="${escape(post.tag_string())}" time="${post.stored}"
            others="--"></post>
    % endfor
</posts>
