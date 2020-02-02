<?php
// round 11 internally
// round 8 to display

require 'actions.php';
require 'code-generator.php';
require 'parser.php';

function run_php_code($php_code)
{
    if (! $function = create_function('', $php_code)) {
        // $error = error_get_last();
        throw new Exception('syntax error');
    }

    return $function();
}


$ti57_code = '
        500 STO 1
        0.015 STO 2
        3 STO 3
        RCL 1 *
        ( RCL 2 /
        ( 1 - ( 1 + RCL 2 )
        Y^X RCL 3 +/- ) ) =
        45 2nd sin =
        ';

$ti57_code = '
        10.25 EE 2 * 3 =
        ';

$ti57_code = '
        1 y^x 2 y^x 3 INV y^x 4 y^x 5 =
        ';

$ti57_code = '
        1 * 3 + 4 * 5 y^x 2 - 7 / 8 =
        ';

$ti57_code = '
        2 y^x 3 / 2 =
        ';

// 27
$ti57_code = '
        (1+2) * (4+5) =
        ';

// [x] => 4.916523412787E-10
$ti57_code = '
        1 * 2 / 3 y^x 4 y^x 5 * 6 / 7 =
        ';

$ti57_code = '
        90 2nd sin =
        1 +/- INV 2nd cos =
        ';

$ti57_code = '
        5 STO 7
        2 2nd Exc 7
        RCL 7
        ';

$ti57_code = '
        5 STO 7
        2 x<>t
        RCL 7
        ';

$ti57_code = '
        5 STO 7
        2 + 3 * ( 5 + 6
        CLR
        1+2=
        RCL 7
        ';

$ti57_code = '5 STO 1 INV 2nd Ct RCL 1';

$ti57_code = '
        45.153030 +/-
        2nd D.MS
        ';

$ti57_code = '
        45.153030
        2nd D.MS
        INV 2nd D.MS
        ';

$ti57_code = '
        10 x<>t 120 2nd P->R x<>t
        ';

$ti57_code = '
        3 2nd Fix
        1 x<>t 2 +/- INV 2nd P->R x<>t
        ';

$ti57_code = '2nd pi 2nd Int ';
$ti57_code = '2nd pi INV 2nd Int';

$ti57_code = '
        2.5 +/- STO 0
        2nd Dsz
        4
        5
        ';

$ti57_code = '
        2 x<>t 10 2nd S+
        3 x<>t 20 2nd S+
        5 x<>t 30 2nd S+
        6 x<>t 40 2nd S+
        10 x<>t 2 2nd S+
        INV 2nd x
        2nd x
        INV 2nd s2
        2nd s2
        ';

$ti57_code = '
        5 STO 4
        SBR 1
        2nd Lbl 0
        3 STO 4
        INV SBR
        2nd Lbl 1
        2 STO 4
        SBR 0
        INV SBR
        ';

try {
    $_ti57_tokens = require 'tokens.php';
    $_lower_case_tokens = set_lower_case_tokens($_ti57_tokens);
    $token_pattern = set_token_pattern($_ti57_tokens);
    $_parsed_tokens = parse_tokens($token_pattern, $ti57_code);
    $code = generate_code(true);
    echo $code;
    echo "\n\n";
    $result = run_php_code($code);
    print_r($result);

} catch (Exception $e) {
    echo 'Error: ' . $e->getMessage() . "\n";
}

$stop = 1;