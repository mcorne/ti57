<?php
function addition()
{
    process_prev_equality();
    add_operation();
}

function clear()
{
    global $code_line, $operators, $prev_operator;

    $code_line[] = '$x = 0;';
    $code_line[] = '$ee = false;';
    $code_line[] = '$reg = array();';

    $operators = array();
    $prev_operator = null;
}

function clear_all()
{
    global $code_line;

    clear();
    $code_line[] = '$mem = array_fill(0, 8, 0);';
}

function closing_parenthesis()
{
    global $operators, $prev_operator;

    process_prev_equality();

    if ($prev_operator != '(') {
        throw new Exception('unexpected closing parenthesis');
    }

    array_pop($operators);
}

function decrement_skip_on_zero()
{
    global $code_line, $token;

    $code_line[] = '$mem[0] = floor($mem[0]);';
    $code_line[] = 'if ($mem[0] != 0) {;';
    $code_line[] = '$mem[0] > 0? $mem[0]-- : $mem[0]++;';
    $code_line[] = '}';
    $code_line[] = $token['statement'];
}

function equality()
{
    global $code_line, $prev_operator;

    process_prev_equality();
}

function exchange_memory()
{
    global $code_line, $token;

    $code_line[] = sprintf('$y = $mem[%d];', $token['number']);
    $code_line[] = sprintf('$mem[%d] = $x;', $token['number']);
    $code_line[] = sprintf('$x = $y;'      , $token['number']);
}

function multiplication()
{
    process_prev_multiplication();
    add_operation();
}

function numeric()
{
    global $code_line, $token;

    $code_line[] = sprintf('$x = %s;', $token['token']);
}

function open_parenthesis()
{
    global $code_line, $operators, $token;

    $code_line[] =  '';
    $operators[] = $token['type'];
}

function php_code()
{
    global $code_line, $token;

    $code_line[] =  $token['statement'];
}

function polar_to_rectangular()
{
    global $code_line;

    $code_line[] =  '$t = $x;';
    $code_line[] =  '$x = $mem[7] * sin(unit2rad($t));';
    $code_line[] =  '$mem[7] = $mem[7] * cos(unit2rad($t));';
}

function power()
{
    process_prev_power();
    add_operation();
}

function rectangular_to_polar()
{
    global $code_line;

    $code_line[] =  '$y = $x;';
    $code_line[] =  '$x = rad2unit(atan2($y, $mem[7]));';
    $code_line[] =  '$mem[7] = sqrt($mem[7] * $mem[7] + $y * $y);';
}

function scientific_notation()
{
    global $code_line;

    $code_line[] = '$ee = true;';
    add_operation();
}

function sum()
{
    global $code_line;

    $code_line[] =  '$mem[0]++;';                    // population
    $code_line[] =  '$mem[1] += $x;';                // sum Y
    $code_line[] =  '$mem[2] += $x * $x;';           // sum Y * Y
    $code_line[] =  '$mem[3] += $mem[7];';           // sum X
    $code_line[] =  '$mem[4] += $mem[7] * $mem[7];'; // sum X * X
    $code_line[] =  '$mem[5] += $mem[7] * $x;';      // sum X * Y
    $code_line[] =  '$mem[7] = $mem[7] + 1;';
}

