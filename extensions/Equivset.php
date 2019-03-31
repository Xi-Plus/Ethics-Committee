<?php
require(__DIR__."/../vendor/autoload.php");

use Wikimedia\Equivset\Equivset;

$equivset = new Equivset();

$input = "";
while($f = fgets(STDIN)){
    $input .= $f;
}

echo $equivset->normalize( $input );
