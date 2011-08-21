# -*- coding: utf-8 -*-
<?xml version="1.0" encoding="UTF-8"?>
<tags>
    % if tags:
        % for tag in tags:
            <tag>${tag.name}</tag>
        % endfor
    % endif
</tags>
