<?php
// Contact form handler. Sends the enquiry to the office mailbox and returns to contact.html.
$to = 'aegis@aegiscomm.com.my';

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    header('Location: contact.html');
    exit;
}
// Honeypot: real visitors never fill the hidden "website" field.
if (!empty($_POST['website'])) {
    header('Location: contact.html?sent=1');
    exit;
}
$clean = function ($key, $max = 2000) {
    $v = isset($_POST[$key]) ? trim((string) $_POST[$key]) : '';
    $v = str_replace(["\r", "\n"], ' ', $v);
    return mb_substr($v, 0, $max);
};
$name    = $clean('name', 200);
$company = $clean('company', 200);
$email   = $clean('email', 200);
$phone   = $clean('phone', 60);
$status  = $clean('status', 100);
$message = isset($_POST['message']) ? mb_substr(trim((string) $_POST['message']), 0, 5000) : '';

if ($name === '' || $message === '' || !filter_var($email, FILTER_VALIDATE_EMAIL)) {
    if (isset($_SERVER['HTTP_ACCEPT']) && strpos($_SERVER['HTTP_ACCEPT'], 'application/json') !== false) {
        header('Content-Type: application/json', true, 400);
        echo json_encode(['ok' => false]);
        exit;
    }
    header('Location: contact.html?error=1');
    exit;
}

$subject = 'Website enquiry from ' . $name . ($company !== '' ? ' (' . $company . ')' : '');
$body = "Name: $name\nCompany: $company\nEmail: $email\nPhone: $phone\nStatus: $status\n\nMessage:\n$message\n\nSent from www.aegiscomm.com.my on " . date('Y-m-d H:i');
$headers = "From: Aegis Website <no-reply@aegiscomm.com.my>\r\nReply-To: $email\r\nContent-Type: text/plain; charset=UTF-8\r\n";

// Keep a copy for the content backend (/aegis, Enquiries), so nothing is lost if the email fails.
$saved = false;
if (is_file(__DIR__ . '/aegis/lib.php')) {
    define('AEGIS', 1);
    require __DIR__ . '/aegis/lib.php';
    $saved = add_enquiry(['name' => $name, 'company' => $company, 'email' => $email, 'phone' => $phone, 'status' => $status, 'message' => $message]);
}

$sent = @mail($to, $subject, $body, $headers) || $saved;   // @: a mail warning must not corrupt the JSON reply
// Async submission from site.js expects JSON; plain form posts get the redirect.
$wantsJson = isset($_SERVER['HTTP_ACCEPT']) && strpos($_SERVER['HTTP_ACCEPT'], 'application/json') !== false;
if ($wantsJson) {
    header('Content-Type: application/json');
    echo json_encode(['ok' => (bool) $sent]);
    exit;
}
header('Location: contact.html?' . ($sent ? 'sent=1' : 'error=1'));
exit;
