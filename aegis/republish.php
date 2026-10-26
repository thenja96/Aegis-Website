<?php
// Re-apply the backend's saved edits to every page. Run after each deployment from GitHub,
// because a deploy copies the repository's (unedited) pages over the live ones.
//   php aegis/republish.php
if (PHP_SAPI !== 'cli') { http_response_code(404); exit; }
define('AEGIS', 1);
require __DIR__ . '/lib.php';
$failed = publish_all();
echo $failed ? 'Could not write: ' . implode(', ', $failed) . "\n" : "Edits re-applied to all pages.\n";
exit($failed ? 1 : 0);
