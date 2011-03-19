<div>

<h2>Found ${result_count} results for ${phrase}:</h2>
<ul>
% for res in search_results:
    % if res:
        <li>${res.bid}: ${res.description}</li>
    % endif
% endfor
</ul>
</div>
