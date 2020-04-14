<?php
function get_next_token()
{
    global $_lower_case_tokens, $_parsed_tokens, $_ti57_tokens;
    static $step = 0;

    if (! isset($_parsed_tokens[$step])) {
        return null;
    }

    $token = $_parsed_tokens[$step];

    if (is_numeric($token)) {
        $token_details['action'] = 'numeric';

    } else {
        $lower_case_token = mb_strtolower($token, 'utf-8');

        if (! isset($_lower_case_tokens[$lower_case_token])) {
            throw new Exception('invalid token: ' . $token);
        }

        $ref_token = $_lower_case_tokens[$lower_case_token];
        $token_details = $_ti57_tokens[$ref_token];

        if (! isset($token_details['action'])) {
            throw new Exception('unavailable token: ' . $token);
        }
    }

    $token_details['step'] = $step;
    $token_details['token'] = $token;

    $step++;

    return $token_details;
}

function parse_tokens($token_pattern, $ti57_code)
{
    return preg_match_all($token_pattern, $ti57_code, $matches)? $matches[1] : false;
}

function set_lower_case_tokens($tokens)
{
    foreach(array_keys($tokens) as $token) {
        $lower_case_token = mb_strtolower($token, 'utf-8');
        $lower_case_tokens[$lower_case_token] = $token;
    }

    return $lower_case_tokens;
}

function set_token_pattern($tokens)
{
    foreach(array_keys($tokens) as $token) {
        $token = preg_replace('~[()\^|+*.]~', '\\\\$0', $token);
        $token = str_replace(' ', ' +', $token);
        $pattern[] = $token;
    }

    // captures numerics, see php.net/manual/en/language.types.float.php
    $pattern[] = '[0-9]*[\.][0-9]+|[0-9]+[\.][0-9]*'; // DNUM
    $pattern[] = '[0-9]+'; // LNUM

    // adds pattern to captures anything else that is not spaces
    $pattern[] = '[^\s]+';

    return '~(' . implode('|', $pattern) . ')~iu';
}
