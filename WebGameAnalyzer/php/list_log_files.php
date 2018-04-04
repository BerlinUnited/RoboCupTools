<?php
// Var definition
$logDirectory = '../logs';
$logExtension = '.tc.json';
$logSortFn = function($a, $b) {
	if($a == $b) { return 0; }
  return $a < $b ? -1 : 1;
};
// REGEX: preg_match('/teamcomm_(?P<date>[\d-]+)_(?P<time>[\d-]+)_(?P<team1>[^_]+)_(?P<team2>[^_]+)_(?P<half>[\w\d]+)/', $log, $log_matches);

// read log directory files
$logFiles = [];
$dir = new DirectoryIterator($logDirectory);
foreach ($dir as $fileinfo) {
    if ($fileinfo->isFile() && strtolower(substr($fileinfo->getFilename(), -strlen($logExtension))) === $logExtension) {
    	// replace 'incorrect' relative path
    	$logFiles[] = str_replace('../', '', $logDirectory) . '/' . $fileinfo->getFilename();
    }
}

// sort log files
usort($logFiles, $logSortFn);

// send as json
header('Content-Type: application/json');
echo json_encode($logFiles);