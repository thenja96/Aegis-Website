<?php
// Aegis website content backend. Reached at /aegis/ only; nothing on the public site links here.
define('AEGIS', 1);
require __DIR__ . '/lib.php';

header('X-Robots-Tag: noindex, nofollow');
header('X-Frame-Options: DENY');
header('X-Content-Type-Options: nosniff');
header('Referrer-Policy: same-origin');
header('Cache-Control: no-store');
header("Content-Security-Policy: default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; script-src 'self'; frame-ancestors 'none'; form-action 'self'");

start_session();
$p = $_GET['p'] ?? 'dashboard';
$users = store_read('users', []);
$ip = $_SERVER['REMOTE_ADDR'] ?? '0';
$flash = $_SESSION['flash'] ?? null;
unset($_SESSION['flash']);

function go(string $to, string $msg = '', string $kind = 'ok'): void {
    if ($msg !== '') $_SESSION['flash'] = [$kind, $msg];
    header('Location: ./' . ($to === '' ? '' : '?' . $to));
    exit;
}

// ---------- first-time setup, sign in, sign out ----------

if (!$users) {
    $setup = store_read('setup', []);
    // first visit on a fresh install: create the one-time key on the server, never in the repository
    if (empty($setup['key'])) { $setup = ['key' => bin2hex(random_bytes(12))]; if (!store_write('setup', $setup)) $setup = []; }
    $err = '';
    if ($_SERVER['REQUEST_METHOD'] === 'POST' && csrf_ok()) {
        $u = trim($_POST['user'] ?? '');
        $pw = (string) ($_POST['pass'] ?? '');
        if (empty($setup['key']) || !hash_equals($setup['key'], trim($_POST['key'] ?? ''))) $err = 'The setup key is not correct.';
        elseif (!preg_match('/^[A-Za-z0-9._-]{3,40}$/', $u)) $err = 'Username: 3 to 40 letters, numbers, dots, dashes or underscores.';
        elseif (strlen($pw) < 10) $err = 'Password must be at least 10 characters.';
        elseif ($pw !== ($_POST['pass2'] ?? '')) $err = 'The two passwords do not match.';
        else {
            store_write('users', [$u => password_hash($pw, PASSWORD_DEFAULT)]);
            @unlink(DATA_DIR . '/setup.php');
            session_regenerate_id(true);
            $_SESSION['user'] = $u;
            go('', 'Account created. You are signed in.');
        }
    }
    page_start('Set up', false);
    echo '<div class="auth"><h1>Set up the content backend</h1><p>Create the admin account. The setup key is in <code>aegis/data/setup.php</code> on the hosting (open it in the Plesk File Manager).</p>';
    if (empty($setup['key'])) echo '<p class="msg err">The setup key could not be created because PHP cannot write to the <code>aegis/data</code> folder. In Plesk File Manager, open its permissions and allow the site user to write to it, then reload this page.</p>';
    if ($err) echo '<p class="msg err">' . h($err) . '</p>';
    echo '<form method="post">' . csrf_field() . '
      <label>Setup key<input name="key" autocomplete="off" required></label>
      <label>Username<input name="user" autocomplete="username" required></label>
      <label>Password<input type="password" name="pass" autocomplete="new-password" minlength="10" required></label>
      <label>Repeat password<input type="password" name="pass2" autocomplete="new-password" minlength="10" required></label>
      <button class="btn">Create account</button></form></div>';
    page_end();
}

if ($p === 'logout' && $_SERVER['REQUEST_METHOD'] === 'POST' && csrf_ok()) {
    $_SESSION = [];
    session_regenerate_id(true);
    go('p=login', 'Signed out.');
}

if (!signed_in()) {
    $err = '';
    if ($_SERVER['REQUEST_METHOD'] === 'POST' && csrf_ok()) {
        if (too_many_attempts($ip)) $err = 'Too many attempts. Try again in 15 minutes.';
        else {
            $u = trim($_POST['user'] ?? '');
            $ok = isset($users[$u]) && password_verify((string) ($_POST['pass'] ?? ''), $users[$u]);
            note_attempt($ip, $ok);
            if ($ok) {
                session_regenerate_id(true);
                $_SESSION['user'] = $u;
                go('');
            }
            $err = 'Username or password is not correct.';
        }
    }
    page_start('Sign in', false);
    echo '<div class="auth"><h1 class="sr-only">Sign in</h1>';
    if ($flash) echo '<p class="msg ' . h($flash[0]) . '">' . h($flash[1]) . '</p>';
    if ($err) echo '<p class="msg err">' . h($err) . '</p>';
    echo '<form method="post" action="./?p=login">' . csrf_field() . '
      <label>Username<input name="user" autocomplete="username" required autofocus></label>
      <label>Password<input type="password" name="pass" autocomplete="current-password" required></label>
      <button class="btn">Sign in</button></form></div>';
    page_end();
}

// ---------- saving ----------

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    if (!csrf_ok()) go($_SERVER['QUERY_STRING'] ?? '', 'Your session expired. Please try again.', 'err');
    $act = $_POST['action'] ?? '';

    if ($act === 'save_text') {
        $scope = (string) ($_POST['scope'] ?? '');
        $items = $scope === '*' ? manifest()['site'] : (manifest_page($scope)['items'] ?? null);
        if ($items === null) go('p=pages', 'Page not found.', 'err');
        $store = store_read('content');
        $changed = 0;
        foreach ($items as $it) {
            $k = $it['k'];
            $cur = $store['texts'][$scope][$k] ?? [];
            if (isset($_POST['reset'][$k])) { $next = []; }
            else {
                $next = $cur;
                $html = $_POST['e'][$k] ?? '';
                if ($html !== '' && editable_markup($it['html'])) {
                    $clean = clean_html($html);
                    if (plain($clean) === '') $clean = $cur['html'] ?? $it['html'];
                    if ($clean === clean_html($it['html'])) unset($next['html']); else $next['html'] = $clean;
                }
                if (!empty($_POST['hide'][$k])) $next['hidden'] = true; else unset($next['hidden']);
            }
            if ($next != $cur) $changed++;
            if ($next) $store['texts'][$scope][$k] = $next; else unset($store['texts'][$scope][$k]);
        }
        if ($scope !== '*') {
            $mp = manifest_page($scope);
            $meta = [];
            foreach (['title', 'description'] as $f) {
                $v = trim(preg_replace('/\s+/', ' ', (string) ($_POST['meta'][$f] ?? '')));
                if ($v !== '' && $v !== $mp[$f]) $meta[$f] = mb_substr($v, 0, $f === 'title' ? 120 : 300);
            }
            if (($store['meta'][$scope] ?? []) != $meta) $changed++;
            if ($meta) $store['meta'][$scope] = $meta; else unset($store['meta'][$scope]);
        }
        store_write('content', $store);
        $failed = publish_all();
        $back = $scope === '*' ? 'p=site' : 'p=edit&path=' . rawurlencode($scope);
        if ($failed) go($back, 'Saved, but these pages could not be written (check file permissions): ' . implode(', ', $failed), 'err');
        go($back, $changed ? 'Saved and published. ' . $changed . ' change' . ($changed > 1 ? 's' : '') . ' now live.' : 'No changes to save.');
    }

    if ($act === 'design') {
        $store = store_read('content');
        if (!empty($_POST['reset_design'])) unset($store['design']);
        else {
            $d = design([
                'navy' => $_POST['navy'] ?? '', 'blue' => $_POST['blue'] ?? '', 'teal' => $_POST['teal'] ?? '',
                'size' => $_POST['size'] ?? '', 'head' => $_POST['head'] ?? '', 'buttons' => $_POST['buttons'] ?? '',
            ]);
            if ($d == DESIGN_DEFAULTS) unset($store['design']); else $store['design'] = $d;
        }
        // sections: a ticked box means shown; only store the ones switched off
        $store['sections'] = [];
        foreach (manifest()['pages'] as $pg) {
            foreach ($pg['sections'] ?? [] as $sec) {
                if (empty($_POST['show'][$pg['path']][$sec['k']])) $store['sections'][$pg['path']][$sec['k']] = false;
            }
        }
        if (!$store['sections']) unset($store['sections']);
        $store['imgver']['assets/theme.css'] = time();
        store_write('content', $store);
        $failed = publish_all();
        if ($failed) go('p=design', 'Saved, but these files could not be written (check permissions): ' . implode(', ', $failed), 'err');
        go('p=design', 'Design saved and published.');
    }

    if ($act === 'image_alt') {
        $k = (string) ($_POST['k'] ?? '');
        $img = find_image($k);
        if (!$img) go('p=images', 'Image not found.', 'err');
        $store = store_read('content');
        $alt = trim(preg_replace('/\s+/', ' ', (string) ($_POST['alt'] ?? '')));
        if ($alt === $img['alt']) unset($store['alts'][$k]); else $store['alts'][$k] = mb_substr($alt, 0, 200);
        store_write('content', $store);
        publish_all();
        go('p=images#i' . $k, 'Description saved.');
    }

    if ($act === 'image_upload') {
        $k = (string) ($_POST['k'] ?? '');
        $img = find_image($k);
        $f = $_FILES['file'] ?? null;
        if (!$img) go('p=images', 'Image not found.', 'err');
        if (!$f || $f['error'] !== UPLOAD_ERR_OK) go('p=images#i' . $k, 'Upload failed. Choose a JPG, PNG or WebP file under 8 MB.', 'err');
        $msg = replace_image($img['src'], $f['tmp_name'], (int) $f['size']);
        if ($msg !== '') go('p=images#i' . $k, $msg, 'err');
        publish_all();
        go('p=images#i' . $k, 'Image replaced and published.');
    }

    if ($act === 'enquiry') {
        $id = (string) ($_POST['id'] ?? '');
        $all = enquiries();
        foreach ($all as $i => $e) {
            if ($e['id'] !== $id) continue;
            if (($_POST['do'] ?? '') === 'delete') { array_splice($all, $i, 1); store_write('enquiries', $all); go('p=enquiries', 'Enquiry deleted.'); }
            $all[$i]['state'] = ($_POST['do'] ?? '') === 'unread' ? 'new' : 'read';
            store_write('enquiries', $all);
            go('p=enquiries', 'Enquiry updated.');
        }
        go('p=enquiries', 'Enquiry not found.', 'err');
    }

    if ($act === 'password') {
        $u = $_SESSION['user'];
        $new = (string) ($_POST['new'] ?? '');
        if (!password_verify((string) ($_POST['current'] ?? ''), $users[$u] ?? '')) go('p=account', 'Current password is not correct.', 'err');
        if (strlen($new) < 10) go('p=account', 'New password must be at least 10 characters.', 'err');
        if ($new !== ($_POST['new2'] ?? '')) go('p=account', 'The two new passwords do not match.', 'err');
        $users[$u] = password_hash($new, PASSWORD_DEFAULT);
        store_write('users', $users);
        session_regenerate_id(true);
        go('p=account', 'Password changed.');
    }
    go('', 'Unknown action.', 'err');
}

function find_image(string $k): ?array {
    foreach (manifest()['pages'] as $pg) foreach ($pg['images'] as $img) if ($img['k'] === $k) return $img;
    return null;
}

function replace_image(string $src, string $tmp, int $size): string {
    if ($size > 8 * 1024 * 1024) return 'That file is over 8 MB.';
    $info = @getimagesize($tmp);
    if (!$info || !in_array($info[2], [IMAGETYPE_JPEG, IMAGETYPE_PNG, IMAGETYPE_WEBP], true)) return 'Choose a JPG, PNG or WebP image.';
    $target = SITE_ROOT . '/' . $src;
    if (strpos(realpath(dirname($target)) ?: '', realpath(SITE_ROOT . '/assets')) !== 0) return 'That image cannot be replaced here.';
    $ext = strtolower(pathinfo($src, PATHINFO_EXTENSION));
    if (!in_array($ext, ['jpg', 'jpeg', 'png', 'webp'], true)) return 'Only JPG, PNG and WebP images can be replaced.';
    $webp = preg_replace('/\.(jpe?g|png)$/i', '.webp', $target);
    $hasWebp = $webp !== $target && is_file($webp);
    if (!function_exists('imagecreatefromstring')) {
        $same = ['jpg' => IMAGETYPE_JPEG, 'jpeg' => IMAGETYPE_JPEG, 'png' => IMAGETYPE_PNG, 'webp' => IMAGETYPE_WEBP][$ext];
        if ($info[2] !== $same || $hasWebp) return 'This server cannot convert images. Upload the same file type, or ask your developer.';
        return move_uploaded_file($tmp, $target) ? bump([$src]) : 'Could not save the file (check folder permissions).';
    }
    $im = @imagecreatefromstring(file_get_contents($tmp));
    if (!$im) return 'That image could not be read.';
    // keep files light: nothing wider than 1600px
    if (imagesx($im) > 1600) { $im2 = imagescale($im, 1600); imagedestroy($im); $im = $im2; }
    if ($ext === 'png' || $ext === 'webp') { imagealphablending($im, false); imagesavealpha($im, true); }
    $ok = $ext === 'png' ? imagepng($im, $target, 8) : ($ext === 'webp' ? imagewebp($im, $target, 82) : imagejpeg($im, $target, 86));
    $done = [$src];
    if ($ok && $hasWebp && function_exists('imagewebp')) { imagewebp($im, $webp, 82); $done[] = substr($webp, strlen(SITE_ROOT) + 1); }
    imagedestroy($im);
    return $ok ? bump($done) : 'Could not save the file (check folder permissions).';
}

// New query string on the image address so visitors' browsers fetch the new file.
function bump(array $srcs): string {
    $store = store_read('content');
    foreach ($srcs as $s) $store['imgver'][str_replace('\\', '/', $s)] = time();
    store_write('content', $store);
    return '';
}

function csrf_field(): string { return '<input type="hidden" name="csrf" value="' . h($_SESSION['csrf']) . '">'; }

// ---------- layout ----------

function page_start(string $title, bool $nav = true, string $active = ''): void {
    echo '<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
       . '<meta name="robots" content="noindex, nofollow"><title>' . h($title) . ' | Aegis content admin</title>'
       . '<link rel="icon" href="../assets/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="../assets/fonts/fonts.css">'
       . '<link rel="stylesheet" href="admin.css?v=' . filemtime(__DIR__ . '/admin.css') . '"></head><body class="' . ($nav ? 'app' : 'plain') . '">';
    if (!$nav) { echo '<main class="solo"><div class="auth-brand"><img class="logo" src="logo-light.png" alt="Aegis Communication"></div>'; return; }
    $unread = count(array_filter(enquiries(), fn($e) => ($e['state'] ?? '') === 'new'));
    $groups = ['Content' => ['dashboard' => 'Dashboard', 'pages' => 'Pages', 'site' => 'Menu and footer', 'images' => 'Images', 'design' => 'Design'],
               'Inbox' => ['enquiries' => 'Enquiries'], 'Settings' => ['account' => 'Account', 'guide' => 'User guide']];
    echo '<aside class="side"><a class="brand" href="./"><img class="logo" src="logo-light.png" alt="Aegis Communication"></a><nav>';
    foreach ($groups as $g => $links) {
        echo '<span class="nav-label">' . $g . '</span>';
        foreach ($links as $k => $label) {
            $badge = $k === 'enquiries' && $unread ? ' <em>' . $unread . '</em>' : '';
            echo '<a href="./?p=' . $k . '"' . ($active === $k ? ' class="on" aria-current="page"' : '') . '>' . $label . $badge . '</a>';
        }
    }
    echo '</nav><form method="post" action="./?p=logout" class="out">' . csrf_field() . '<span>' . h($_SESSION['user']) . '</span><button>Sign out</button></form></aside>';
    echo '<main class="body"><header class="top"><div><span class="eyebrow">Aegis website</span><h1>' . h($title) . '</h1></div><a class="ghost" href="../" target="_blank" rel="noopener">View website ↗</a></header><div class="wrap">';
    global $flash;
    if ($flash) echo '<p class="msg ' . h($flash[0]) . '">' . h($flash[1]) . '</p>';
}

function page_end(): void {
    echo '</div></main><script src="admin.js?v=' . filemtime(__DIR__ . '/admin.js') . '"></script></body></html>';
    exit;
}

const KIND = ['h1' => 'Page headline', 'h2' => 'Section headline', 'h3' => 'Heading', 'h4' => 'Heading', 'h5' => 'Heading',
    'p' => 'Paragraph', 'li' => 'List item', 'a' => 'Link or button', 'button' => 'Button', 'small' => 'Small text',
    'figcaption' => 'Photo caption', 'b' => 'Bold text', 'strong' => 'Bold text', 'td' => 'Table cell', 'th' => 'Table heading',
    'option' => 'Form option', 'label' => 'Form label', 'span' => 'Text', 'div' => 'Text', 'em' => 'Text', 'dt' => 'Term', 'dd' => 'Description', 'blockquote' => 'Quote'];

function kind(array $it): string {
    if (strpos($it['cls'], 'eyebrow') !== false) return 'Section label';
    if (strpos($it['cls'], 'btn') !== false) return 'Button';
    if (strpos($it['cls'], 'lede') !== false) return 'Intro paragraph';
    return KIND[$it['tag']] ?? 'Text';
}

function editor(string $scope, array $items, ?array $page): void {
    $store = store_read('content');
    $texts = $store['texts'][$scope] ?? [];
    echo '<form method="post" class="editor" id="editor">' . csrf_field() . '<input type="hidden" name="action" value="save_text"><input type="hidden" name="scope" value="' . h($scope) . '">';
    echo '<div class="savebar"><span class="status" id="status">No unsaved changes</span><button class="btn" id="save">Save and publish</button></div>';
    if ($page) {
        $meta = $store['meta'][$scope] ?? [];
        echo '<section class="group"><h2>Search and sharing</h2><p class="hint">Shown in Google results and when the page is shared.</p>'
           . '<label class="meta">Page title<input name="meta[title]" maxlength="120" value="' . h($meta['title'] ?? $page['title']) . '"></label>'
           . '<label class="meta">Description<textarea name="meta[description]" rows="2" maxlength="300">' . h($meta['description'] ?? $page['description']) . '</textarea></label></section>';
    }
    $group = null;
    foreach ($items as $it) {
        $sec = $it['section'] !== '' ? $it['section'] : ($scope === '*' ? 'Menu, footer and side button' : 'Top of page');
        if ($sec !== $group) {
            if ($group !== null) echo '</section>';
            echo '<section class="group"><h2>' . h($sec) . '</h2>';
            $group = $sec;
        }
        $k = $it['k'];
        $ov = $texts[$k] ?? [];
        $cur = $ov['html'] ?? $it['html'];
        $edited = isset($ov['html']);
        $hidden = !empty($ov['hidden']);
        $ok = editable_markup($it['html']);
        echo '<div class="item' . ($hidden ? ' is-hidden' : '') . ($edited ? ' is-edited' : '') . '">';
        echo '<div class="meta-row"><span class="kind">' . h(kind($it)) . '</span>';
        if ($it['count'] > 1) echo '<span class="count">Used ' . (int) $it['count'] . ' times ' . ($scope === '*' ? 'across the menu and footer' : 'on this page') . ', edits apply to all</span>';
        if ($edited) echo '<span class="flag">Edited</span>';
        echo '<label class="opt"><input type="checkbox" name="hide[' . $k . ']" value="1"' . ($hidden ? ' checked' : '') . '> Hide</label>';
        if ($edited || $hidden) echo '<label class="opt"><input type="checkbox" name="reset[' . $k . ']" value="1"> Reset to original</label>';
        echo '</div>';
        if ($ok) {
            echo '<div class="field ' . h($it['tag']) . '" contenteditable="true" data-k="' . $k . '" spellcheck="true">' . $cur . '</div>'
               . '<input type="hidden" name="e[' . $k . ']" value="">';
        } else {
            echo '<div class="field locked" title="Contains icons or layout; ask your developer to change this one.">' . h(plain($cur)) . '</div>';
        }
        echo '</div>';
    }
    if ($group !== null) echo '</section>';
    echo '</form>';
}

// ---------- screens ----------

$m = manifest();

if ($p === 'dashboard') {
    $store = store_read('content');
    $blocks = count($m['site']) + array_sum(array_map(fn($pg) => count($pg['items']), $m['pages']));
    $edited = 0;
    foreach (($store['texts'] ?? []) as $t) $edited += count($t);
    $imgs = [];
    foreach ($m['pages'] as $pg) foreach ($pg['images'] as $i) $imgs[$i['k']] = 1;
    $all = enquiries();
    $unread = count(array_filter($all, fn($e) => ($e['state'] ?? '') === 'new'));
    page_start('Dashboard', true, 'dashboard');
    echo '<p class="note">Signed in as <b>' . h($_SESSION['user']) . '</b>. Every change you save here goes live on the <a href="../" target="_blank" rel="noopener">website</a> straight away. New here? Read the <a href="./?p=guide">user guide</a>.</p>';
    echo '<div class="stats">'
       . '<a href="./?p=pages"><b>' . count($m['pages']) . '</b>Pages</a>'
       . '<a href="./?p=pages"><b>' . $blocks . '</b>Text blocks</a>'
       . '<a href="./?p=pages"><b>' . $edited . '</b>Edited blocks</a>'
       . '<a href="./?p=images"><b>' . count($imgs) . '</b>Images</a>'
       . '<a href="./?p=enquiries"><b>' . $unread . '</b>Unread enquiries</a></div>';
    echo '<section class="panel"><h2>Quick links</h2><div class="quick">';
    foreach (['index.html' => 'Edit home page', 'people.html' => 'Edit people', 'services/ipo-communications.html' => 'Edit IPO page', 'contact.html' => 'Edit contact page'] as $path => $label)
        echo '<a class="ghost" href="./?p=edit&amp;path=' . rawurlencode($path) . '">' . $label . '</a>';
    echo '<a class="ghost" href="./?p=site">Edit menu and footer</a><a class="ghost" href="./?p=images">Replace a photo or logo</a></div></section>';
    echo '<section class="panel"><h2>Recent enquiries</h2>';
    enquiry_table(array_slice($all, 0, 5));
    echo '<p><a href="./?p=enquiries">View all enquiries →</a></p></section>';
    page_end();
}

function enquiry_table(array $rows): void {
    if (!$rows) { echo '<p class="hint">No enquiries yet. Messages sent from the website contact form appear here.</p>'; return; }
    echo '<table class="tbl"><thead><tr><th>Date</th><th>Name</th><th>Company</th><th>Email</th><th>Status</th></tr></thead><tbody>';
    foreach ($rows as $e) {
        echo '<tr><td><a href="./?p=enquiry&amp;id=' . h($e['id']) . '">' . h(date('j M Y, H:i', strtotime($e['date']))) . '</a></td><td><a href="./?p=enquiry&amp;id=' . h($e['id']) . '"><b>' . h($e['name']) . '</b></a></td><td>' . h($e['company']) . '</td><td><a href="mailto:' . h($e['email']) . '">' . h($e['email']) . '</a></td><td><span class="tag ' . (($e['state'] ?? '') === 'new' ? 'new' : '') . '">' . (($e['state'] ?? '') === 'new' ? 'New' : 'Read') . '</span></td></tr>';
    }
    echo '</tbody></table>';
}

if ($p === 'pages') {
    $store = store_read('content');
    page_start('Pages', true, 'pages');
    echo '<p class="note">Choose a page to edit its text. Menu and footer text is the same on every page, so it has its own screen: <a href="./?p=site">Menu and footer</a>.</p><table class="tbl"><thead><tr><th>Page</th><th>Address</th><th>Text blocks</th><th>Edited</th><th></th></tr></thead><tbody>';
    // same order as the site menu, home first and the error page last
    $order = ['index.html', 'about.html', 'people.html', 'approach.html', 'track-record.html', 'services/investor-relations.html', 'services/public-relations.html', 'services/ipo-communications.html', 'services/events.html', 'services/creative-digital.html', 'contact.html', '404.html'];
    $list = $m['pages'];
    usort($list, fn($a, $b) => (array_search($a['path'], $order) === false ? 99 : array_search($a['path'], $order)) <=> (array_search($b['path'], $order) === false ? 99 : array_search($b['path'], $order)));
    foreach ($list as $pg) {
        $n = count($store['texts'][$pg['path']] ?? []);
        $name = $pg['path'] === 'index.html' ? 'Home' : preg_replace('/\s*\|.*$/', '', $store['meta'][$pg['path']]['title'] ?? $pg['title']);
        echo '<tr><td><a href="./?p=edit&amp;path=' . rawurlencode($pg['path']) . '"><b>' . h($name) . '</b></a></td><td><code>/' . h($pg['path'] === 'index.html' ? '' : $pg['path']) . '</code></td><td>' . count($pg['items']) . '</td><td>' . ($n ?: '–') . '</td><td><a class="ghost sm" href="./?p=edit&amp;path=' . rawurlencode($pg['path']) . '">Edit</a> <a class="ghost sm" href="../' . h($pg['path']) . '" target="_blank" rel="noopener">View ↗</a></td></tr>';
    }
    echo '</tbody></table>';
    page_end();
}

if ($p === 'edit') {
    $pg = manifest_page((string) ($_GET['path'] ?? ''));
    if (!$pg) go('p=pages', 'Page not found.', 'err');
    page_start(preg_replace('/\s*\|.*$/', '', $pg['title']), true, 'pages');
    echo '<p class="note">Click any text below to change it, then press <b>Save and publish</b>. <a href="../' . h($pg['path']) . '" target="_blank" rel="noopener">Open this page ↗</a></p>';
    editor($pg['path'], $pg['items'], $pg);
    page_end();
}

if ($p === 'site') {
    page_start('Menu and footer', true, 'site');
    echo '<p class="note">These words appear on every page: the top menu, the footer and the side contact button. A change here updates all pages.</p>';
    editor('*', $m['site'], null);
    page_end();
}

if ($p === 'design') {
    $store = store_read('content');
    $d = design($store['design'] ?? []);
    $off = $store['sections'] ?? [];
    $radio = function (string $name, array $opts) use ($d) {
        $h = '<div class="choices">';
        foreach ($opts as $v => $label) $h .= '<label class="choice"><input type="radio" name="' . $name . '" value="' . $v . '"' . ($d[$name] === $v ? ' checked' : '') . '><span>' . $label . '</span></label>';
        return $h . '</div>';
    };
    page_start('Design', true, 'design');
    echo '<p class="note">Change the look of the whole website. Press <b>Save and publish</b> and the changes go live straight away. <b>Reset design</b> returns to the original look.</p>';
    echo '<form method="post" id="design">' . csrf_field() . '<input type="hidden" name="action" value="design">';
    echo '<div class="savebar"><span class="status">Changes apply to every page</span><button class="ghost" name="reset_design" value="1" data-confirm-click="Reset colours, text size, heading font and buttons to the original design?">Reset design</button><button class="btn">Save and publish</button></div>';

    echo '<section class="group"><h2>Brand colours</h2><p class="hint">Used for headings, dark sections, links, buttons and accent lines. Pick a colour or type a code such as #0E6BB4.</p><div class="swatches">';
    foreach (['navy' => ['Dark', 'Dark sections, headings and the footer'], 'blue' => ['Blue', 'Links and the blue end of buttons and lines'], 'teal' => ['Teal', 'Labels and the green end of buttons and lines']] as $k => [$label, $help]) {
        echo '<label class="swatch"><span class="name">' . $label . '</span><span class="pick"><input type="color" value="' . h($d[$k]) . '" data-for="' . $k . '"><input name="' . $k . '" value="' . h($d[$k]) . '" pattern="#[0-9A-Fa-f]{6}" maxlength="7" spellcheck="false"></span><small>' . $help . '</small></label>';
    }
    echo '</div><div class="preview" id="preview"><span class="pv-dark">Dark section</span><span class="pv-label">Section label</span><a class="pv-link">A text link</a><span class="pv-btn">Contact us →</span><span class="pv-line"></span></div></section>';

    echo '<section class="group"><h2>Text</h2><div class="opts"><div><h3>Text size</h3>' . $radio('size', ['small' => 'Small', 'medium' => 'Medium', 'large' => 'Large']) . '</div>'
       . '<div><h3>Heading font</h3>' . $radio('head', ['serif' => '<span class="f-serif">Serif</span>', 'sans' => '<span class="f-sans">Sans serif</span>']) . '</div>'
       . '<div><h3>Button corners</h3>' . $radio('buttons', ['square' => 'Square', 'rounded' => 'Rounded']) . '</div></div></section>';

    echo '<section class="group"><h2>Sections on each page</h2><p class="hint">Untick a section to remove it from the page. Nothing is deleted; tick it again to bring it back. The top banner of each page always stays.</p>';
    $order = ['index.html', 'about.html', 'people.html', 'approach.html', 'track-record.html', 'services/investor-relations.html', 'services/public-relations.html', 'services/ipo-communications.html', 'services/events.html', 'services/creative-digital.html', 'contact.html'];
    $pages = array_filter(manifest()['pages'], fn($pg) => !empty($pg['sections']));
    usort($pages, fn($a, $b) => (array_search($a['path'], $order) === false ? 99 : array_search($a['path'], $order)) <=> (array_search($b['path'], $order) === false ? 99 : array_search($b['path'], $order)));
    foreach ($pages as $pg) {
        $name = $pg['path'] === 'index.html' ? 'Home' : preg_replace('/\s*\|.*$/', '', $pg['title']);
        $hidden = count($off[$pg['path']] ?? []);
        echo '<details class="secpage"' . ($hidden ? ' open' : '') . '><summary><b>' . h($name) . '</b><span>' . count($pg['sections']) . ' sections' . ($hidden ? ', ' . $hidden . ' hidden' : '') . '</span></summary><ul>';
        foreach ($pg['sections'] as $sec) {
            $on = !isset($off[$pg['path']][$sec['k']]);
            echo '<li><label><input type="checkbox" name="show[' . h($pg['path']) . '][' . $sec['k'] . ']" value="1"' . ($on ? ' checked' : '') . '> <span>' . h($sec['name']) . '</span>' . ($sec['label'] ? ' <small>' . h($sec['label']) . '</small>' : '') . '</label></li>';
        }
        echo '</ul></details>';
    }
    echo '</section></form>';
    page_end();
}

if ($p === 'images') {
    $store = store_read('content');
    $imgs = [];
    foreach ($m['pages'] as $pg) foreach ($pg['images'] as $i) { $imgs[$i['k']] = $imgs[$i['k']] ?? $i + ['pages' => []]; $imgs[$i['k']]['pages'][] = $pg['path']; }
    // group by folder so a long list is easy to scan
    $groups = ['team' => 'Team portraits', 'photos' => 'Photos', 'clients' => 'Client logos', 'network' => 'Media and network logos', '' => 'Brand'];
    $by = [];
    foreach ($imgs as $k => $i) { $f = preg_match('#^assets/([^/]+)/#', $i['src'], $mm) && isset($groups[$mm[1]]) ? $mm[1] : ''; $by[$f][$k] = $i; }
    page_start('Images', true, 'images');
    echo '<p class="note">Upload a new file to replace a photo or logo. It keeps the same place on the site. JPG, PNG or WebP, under 8 MB. Team portraits: square, head and shoulders, plain background.</p>';
    echo '<nav class="jump">';
    foreach ($groups as $f => $label) if (!empty($by[$f])) echo '<a href="#g-' . ($f ?: 'brand') . '">' . $label . ' <span>' . count($by[$f]) . '</span></a>';
    echo '</nav>';
    foreach ($groups as $f => $label) {
        if (empty($by[$f])) continue;
        echo '<h2 class="img-group" id="g-' . ($f ?: 'brand') . '">' . $label . '</h2><div class="imgs">';
        foreach ($by[$f] as $k => $i) {
            $v = $store['imgver'][$i['src']] ?? '';
            $alt = $store['alts'][$k] ?? $i['alt'];
            $pages = array_values(array_unique($i['pages']));
            $used = count($pages) > 2 ? 'Used on ' . count($pages) . ' pages' : 'Used on ' . implode(', ', array_map(fn($x) => $x === 'index.html' ? 'Home' : preg_replace('#^services/|\.html$#', '', $x), $pages));
            $thumb = is_file(SITE_ROOT . '/' . $i['src']) ? '<img src="../' . h($i['src']) . ($v ? '?v=' . (int) $v : '') . '" alt="" loading="lazy">' : '<span class="none">No photo yet</span>';
            echo '<div class="img" id="i' . $k . '"><div class="thumb">' . $thumb . '</div><div class="info">'
               . '<div class="name"><code>' . h(basename($i['src'])) . '</code><small>' . h($used) . '</small></div>'
               . '<form method="post" class="inline">' . csrf_field() . '<input type="hidden" name="action" value="image_alt"><input type="hidden" name="k" value="' . $k . '"><input name="alt" value="' . h($alt) . '" aria-label="Description for screen readers and search" placeholder="Description"><button class="ghost sm">Save</button></form>'
               . '<form method="post" enctype="multipart/form-data" class="inline">' . csrf_field() . '<input type="hidden" name="action" value="image_upload"><input type="hidden" name="k" value="' . $k . '"><input type="file" name="file" accept="image/jpeg,image/png,image/webp" required aria-label="Replacement image"><button class="btn sm">Upload</button></form></div></div>';
        }
        echo '</div>';
    }
    page_end();
}

if ($p === 'enquiries') {
    page_start('Enquiries', true, 'enquiries');
    echo '<p class="note">Messages sent from the website contact form. Each one is also emailed to the office mailbox.</p>';
    enquiry_table(enquiries());
    page_end();
}

if ($p === 'enquiry') {
    $id = (string) ($_GET['id'] ?? '');
    $all = enquiries();
    $e = null;
    foreach ($all as $i => $row) if ($row['id'] === $id) { $e = $row; if (($row['state'] ?? '') === 'new') { $all[$i]['state'] = 'read'; store_write('enquiries', $all); } }
    if (!$e) go('p=enquiries', 'Enquiry not found.', 'err');
    page_start('Enquiry from ' . $e['name'], true, 'enquiries');
    echo '<section class="panel"><dl class="dl">';
    foreach (['Date' => date('j M Y, H:i', strtotime($e['date'])), 'Name' => $e['name'], 'Company' => $e['company'], 'Email' => $e['email'], 'Phone' => $e['phone'], 'Contacting as' => $e['status']] as $l => $v)
        echo '<dt>' . $l . '</dt><dd>' . ($l === 'Email' ? '<a href="mailto:' . h($v) . '">' . h($v) . '</a>' : h($v ?: '–')) . '</dd>';
    echo '</dl><h2>Message</h2><p class="message">' . nl2br(h($e['message'])) . '</p>';
    echo '<div class="row"><a class="btn" href="mailto:' . h($e['email']) . '?subject=' . rawurlencode('Re: your enquiry to Aegis Communication') . '">Reply by email</a><form method="post">' . csrf_field() . '<input type="hidden" name="action" value="enquiry"><input type="hidden" name="id" value="' . h($id) . '"><input type="hidden" name="do" value="unread"><button class="ghost">Mark as unread</button></form>'
       . '<form method="post" data-confirm="Delete this enquiry permanently? This cannot be undone.">' . csrf_field() . '<input type="hidden" name="action" value="enquiry"><input type="hidden" name="id" value="' . h($id) . '"><input type="hidden" name="do" value="delete"><button class="danger">Delete</button></form>'
       . '<a class="ghost" href="./?p=enquiries">Back to all enquiries</a></div></section>';
    page_end();
}

if ($p === 'account') {
    page_start('Account', true, 'account');
    echo '<section class="panel narrow"><h2>Change password</h2><form method="post">' . csrf_field() . '<input type="hidden" name="action" value="password">
      <label>Current password<input type="password" name="current" autocomplete="current-password" required></label>
      <label>New password (at least 10 characters)<input type="password" name="new" autocomplete="new-password" minlength="10" required></label>
      <label>Repeat new password<input type="password" name="new2" autocomplete="new-password" minlength="10" required></label>
      <button class="btn">Change password</button></form></section>';
    page_end();
}

if ($p === 'guide') {
    page_start('User guide', true, 'guide');
    echo '<section class="panel guide">
    <h2>Signing in</h2><p>Go to <code>/aegis</code> on the website address. There is no link to it from the public site. You are signed out after two hours without activity. After five wrong passwords, sign-in pauses for 15 minutes.</p>
    <h2>Changing text</h2><ol><li>Open <b>Pages</b> and choose a page.</li><li>Text is listed in the same order as on the page, grouped under each section heading.</li><li>Click into a box and type. Press <b>Save and publish</b> at the top. The change is live straight away.</li></ol>
    <p>To make text bold, select it and press Ctrl+B (Cmd+B on Mac). To add a link, select the text and press Ctrl+K, then type the address, for example <code>contact.html</code> or a full <code>https://</code> address. Enter does not start a new line, because each box is one heading, line or list item. Use Shift+Enter for a line break inside a paragraph.</p>
    <p><b>Hide</b> removes the item from the website without deleting it. Untick it to bring it back. <b>Reset to original</b> puts back the wording the site was built with.</p>
    <p>Some boxes are grey and locked. They contain icons or layout that the editor cannot keep, so they are changed by your developer.</p>
    <p>Text that appears more than once on a page, such as a button label, is edited once and updates everywhere on that page.</p>
    <h2>Design</h2><p>Under <b>Design</b> you can change the three brand colours, the text size, the heading font (serif or sans serif) and the button corners for the whole site, and switch whole sections of any page off or on. A small preview shows the colours before you save. <b>Reset design</b> returns to the original look; sections you switched off are not affected by reset.</p>
    <h2>Menu and footer</h2><p>Top menu labels, footer text, office address and phone number are the same on every page, so they are edited once under <b>Menu and footer</b>, split into Top menu and Footer. Words used in both, such as a service name, are one box: changing it updates the menu and the footer together.</p>
    <h2>Search and sharing</h2><p>Each page has a title and a short description at the top of its editor. Google shows these in search results. Keep the title under 60 characters and the description under 160.</p>
    <h2>Photos and logos</h2><p>Under <b>Images</b>, grouped into team portraits, photos and logos, upload a replacement for any photo or logo. It keeps its place and size on the site. For team portraits use a square, head-and-shoulders photo with a plain background, at least 600 × 600 pixels. The description field is read aloud by screen readers; describe the person or the logo in a few words.</p>
    <h2>Enquiries</h2><p>Every message from the contact form is listed under <b>Enquiries</b> and is also emailed to the office mailbox. Opening one marks it as read. <b>Reply by email</b> opens your email program with the address filled in. Deleting is permanent.</p>
    <h2>What needs your developer</h2><p>Adding a new page, a new section, a new team member or a new service, and changing the layout or colours. These are structural changes made in the site source, then uploaded.</p>
    </section>';
    page_end();
}

go('', 'Page not found.', 'err');
