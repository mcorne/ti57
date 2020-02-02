<?php
function add_operation()
{
    global $code_line, $operators, $token;

    $code_line[] = '$reg[] = $x;';
    $operators[] = $token['type'];
}

function add_subroutines($code)
{
    $format = '
function sbr_%s()            // %s
{
global $ee, $fix, $mem, $reg, $trace, $unit, $x;
%s

';

    if (preg_match_all('~sbr_(\d+)~', $code, $matches)) {
        foreach($matches[1] as $number) {
            if (preg_match("~lbl_$number: +// +([^\n]+)(.+?} +// INV SBR [^\n]+)~s", $code, $match)) {
                $code = str_replace($match[0], '', $code);
                $subroutine = sprintf($format, $number, $match[1], $match[2]);
                $code = $subroutine . $code;
            }
        }
    }

    return $code;
}

function generate_code($debug)
{
    $format = '
require_once "internal-functions.php";
global $ee, $fix, $mem, $reg, $trace, $unit, $x;
init_calculator();

%s

return calculator_state();
';

    $code_lines = process_tokens($debug);
    $code = implode_code_lines($code_lines);
    $code = add_subroutines($code);

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
    $is_statement_group = false;
    $code_lines = array();

    while(true) {
        $token = get_next_token();

        if (is_null($token)) {
            break;
        }

        $code_line = array();
        $action = $token['action'];
        $action();

        if (empty($code_line)) {
            $code_line[] =  '';
        }

        $ti_code = isset($token['ti-code']) ? $token['ti-code'] : null;
        $code_line[0] = sprintf('%-27s // %-12s #%-2s %s', $code_line[0], $token['token'], $token['step'], $ti_code);

        if ($debug) {
            $code_line[] = sprintf('$trace[%d] = fix($x);', $token['step']);
        }

        if ($is_statement_group) {
            // TODO: indent statements 4 spaces
            $code_line[] = '}';
            $is_statement_group = false;
        }

        if (isset($token['statement'])) {
            $is_statement_group = substr($token['statement'], -1) == '{';
        }

        $prev_token = $token['token'];
        $code_lines[] = $code_line;
    }

    return $code_lines;
}


