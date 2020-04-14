<?php
function calculator_state()
{
    global $ee, $fix, $mem, $reg, $trace, $unit, $x;

    $display = fix($x);

    return compact('display', 'ee', 'fix', 'mem', 'reg', 'trace', 'unit', 'x');
}

function dms2degrees($dms)
{
    preg_match('~(-?\d+)\.?(\d{1,2})?(\d{1,2})?(\d*)~', $dms, $match);
    @list(, $degrees, $minutes, $seconds, $remainder) = $match;

    $is_positive = $degrees >= 0;
    $degrees = abs($degrees);

    if ($minutes) {
        strlen($minutes) == 1 and $minutes *= 10;
        $degrees += $minutes / 60;
    }

    if ($seconds) {
        strlen($seconds) == 1 and $seconds *= 10;
        $degrees += $seconds / 3600;
    }

    if ($remainder) {
        $remainder = "0.$remainder";
        $degrees += $remainder / 3600;
    }

    return $is_positive? $degrees : -$degrees;
}

function degrees2dms($degrees)
{
    $is_positive = $degrees >= 0;
    $degrees = abs($degrees);

    $int_degrees = (int)$degrees;
    $remainder = ($degrees - $int_degrees) * 60;
    $minutes = (int)$remainder;
    $seconds = ($remainder - $minutes) * 60;
    $seconds = str_replace('.', '', $seconds);

    $dms = (float)sprintf('%d.%d%s', $int_degrees, $minutes, $seconds);

    return $is_positive? $dms : -$dms;
}

function fix($number)
{
    global $fix;

    return is_null($fix)? $number : round($number, $fix);
}

function grd2rad($number)
{
    return ($number / 200) * M_PI;
}

function init_calculator()
{
    global $ee, $fix, $mem, $reg, $trace, $unit, $x;

    $ee    = false;               // disables the scientific notation
    $fix   = null;                // resets the number of decimal digits to round to
    $mem   = array_fill(0, 8, 0); // resets the memory
    $reg   = array();             // resets the internal registers
    $trace = array();             // resets the debug trace
    $unit  = "Deg";               // sets the angles unit to radians
    $x     = 0;                   // resets the display register
}

function rad2grd($number)
{
    return ($number / M_PI) * 200;
}

function rad2unit($number)
{
    global $unit;

    if ($unit == "Deg") {
        $number = rad2deg($number);
    } else if ($unit == "Grd") {
        $number = rad2grd($number);
    }

    return $number;
}

function unit2rad($number)
{
    global $unit;

    if ($unit == "Deg") {
        $number = deg2rad($number);
    } else if ($unit == "Grd") {
        $number = grd2rad($number);
    }

    return $number;
}
