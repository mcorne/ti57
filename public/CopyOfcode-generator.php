<?php
function add_addition()
{
    process_prev_equality();
    add_operation();
}

function add_closing_parenthesis()
{
    global $operators, $prev_operator;

    process_prev_equality();

    if ($prev_operator != '(') {
        throw new Exception('unexpected closing parenthesis');
    }

    array_pop($operators);
}

function add_equality()
{
    global $code_line, $prev_operator;

    process_prev_equality();

    if (empty($prev_operator)) {
        $code_line[] =  '';
    }
}

function add_multiplication()
{
    process_prev_multiplication();
    add_operation();
}

function add_numeric()
{
    global $code_line, $token;

    $code_line[] = sprintf('$x = %s;', $token['token']);
}

function add_open_parenthesis()
{
    global $code_line, $operators, $token;

    $code_line[] =  '';
    $operators[] = $token['type'];
}

function add_operation()
{
    global $code_line, $operators, $token;

    $code_line[] = '$reg[] = $x;';
    $operators[] = $token['type'];
}

function add_php_code()
{
    global $code_line, $token;

    $code_line[] =  $token['line'];
}

function add_power()
{
    process_prev_power();
    add_operation();
}

function add_scientific_notation()
{
    global $code_line;

    $code_line[] = '$ee = true;';
    add_operation();
}

function generate_code()
{
    $format = '
require_once "internal-functions.php";
global $ee, $fix, $mem, $reg, $step, $trace, $unit, $x;
init_calculator();

%s

return calculator_state();
';

    $code_lines = process_tokens();
    $code = implode_code_lines($code_lines);

    return sprintf($format, $code);
}

function implode_code_lines($code_lines)
{
    foreach($code_lines as &$lines_set) {
        $lines_set = implode("\n", (array)$lines_set);
    }

    return implode("\n\n", $code_lines);
}

function process_prev_equality()
{
    global $code_line, $operators, $prev_operator;

    process_prev_multiplication();

    if($prev_operator == '+' or $prev_operator == '-') {
        array_pop($operators);
        $code_line[] = '$y = array_pop($reg);';
        $code_line[] = sprintf('$x = $y %s $x;', $prev_operator);
        $prev_operator = end($operators);
    }
}

function process_prev_multiplication()
{
    global $code_line, $operators, $prev_operator;

    process_prev_power();

    if($prev_operator == '*' or $prev_operator == '/') {
        array_pop($operators);
        $code_line[] = '$y = array_pop($reg);';
        $code_line[] = sprintf('$x = $y %s $x;', $prev_operator);
        $prev_operator = end($operators);
    }
}

function process_prev_power()
{
    global $code_line, $operators, $prev_operator;

    process_prev_scientific_notation();

    if($prev_operator == 'power' or $prev_operator == 'root') {
        array_pop($operators);
        $code_line[] = '$y = array_pop($reg);';
        $exponent_sign = $prev_operator == 'root'? '-' : '';
        $code_line[] = sprintf('$x = pow($y, %s$x);', $exponent_sign);
        $prev_operator = end($operators);
    }
}

function process_prev_scientific_notation()
{
    global $code_line, $operators, $prev_operator;

    $prev_operator = end($operators);

    if($prev_operator == 'EE') {
        array_pop($operators);
        $code_line[] = '$y = array_pop($reg);';
        $code_line[] = sprintf('$x = $y * pow(10, $x);');
        $prev_operator = end($operators);
    }
}

function process_tokens($debug = true)
{
    global $code_line, $token;

    $operators = array();

    while(true) {
        $token = get_next_token();

        if (is_null($token)) {
            break;
        }

        $code_line = null;
        $action = $token['action'];
        $action();

        if (isset($code_line)) {
            $ti_code = isset($token['ti-code']) ? $token['ti-code'] : null;
            $code_line[0] = sprintf('%-27s // %-12s #%-2s %s', $code_line[0], $token['token'], $token['step'], $ti_code);
            $debug and $code_line[] = '$trace[] = $x;';
            $code_lines[] = $code_line;
        }
    }

    return $code_lines;
}


