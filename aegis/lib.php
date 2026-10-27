<?php
// Shared code for the content backend. Loaded by index.php and ../contact.php only.
if (!defined('AEGIS')) { http_response_code(404); exit; }

const GUARD = "<?php exit; ?>\n";
define('SITE_ROOT', dirname(__DIR__));
define('DATA_DIR', __DIR__ . '/data');

// ---------- flat-file storage (each file starts with a PHP exit line so it can never be served) ----------

function store_read(string $name, $default = []) {
    $f = DATA_DIR . "/$name.php";
    if (!is_file($f)) return $default;
    $raw = file_get_contents($f);
    if (strncmp($raw, '<?php', 5) === 0) $raw = substr($raw, strpos($raw, "
") + 1);   // skip the exit line
    $v = json_decode($raw, true);
    return $v === null ? $default : $v;
}

function store_write(string $name, $data): bool {
    $f = DATA_DIR . "/$name.php";
    $tmp = $f . '.' . bin2hex(random_bytes(4)) . '.tmp';
    if (@file_put_contents($tmp, GUARD . json_encode($data, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES), LOCK_EX) === false) return false;
    return @rename($tmp, $f) || (@unlink($tmp) && false);
}

function manifest(): array {
    static $m = null;
    if ($m === null) $m = store_read('manifest', ['pages' => [], 'site' => []]);
    return $m;
}

function manifest_page(string $path): ?array {
    foreach (manifest()['pages'] as $p) if ($p['path'] === $path) return $p;
    return null;
}

// ---------- applying edits to the built pages (mirrors _src/cms.py) ----------

// Stored text uses site-root links; turn them back into links relative to the page at $path.
function denorm(string $s, string $path): string {
    $d = strpos($path, '/') !== false ? substr($path, 0, strrpos($path, '/') + 1) : '';
    if ($d === '') return $s;
    $depth = substr_count($d, '/');
    return preg_replace_callback('/((?:href|src)=")(?!https?:|mailto:|tel:|#|\/|data:|javascript:)([^"]*)/', function ($m) use ($d, $depth) {
        return $m[1] . (strncmp($m[2], $d, strlen($d)) === 0 ? substr($m[2], strlen($d)) : str_repeat('../', $depth) . $m[2]);
    }, $s);
}

function find_block(string $doc, string $k, int $pos) {
    if (!preg_match('/<([a-zA-Z0-9]+)\b[^>]*\sdata-e="' . $k . '"[^>]*>/', $doc, $m, PREG_OFFSET_CAPTURE, $pos)) return null;
    $tag = strtolower($m[1][0]);
    $s = $m[0][1];
    $se = $s + strlen($m[0][0]);
    $depth = 1; $p = $se;
    while ($depth) {
        if (!preg_match('/<(\/?)' . $tag . '\b[^>]*>/i', $doc, $t, PREG_OFFSET_CAPTURE, $p)) return null;
        $depth += $t[1][0] === '/' ? -1 : 1;
        $p = $t[0][1] + strlen($t[0][0]);
    }
    return [$s, $se, $t[0][1]];
}

function apply_page(string $doc, array $page, array $store): string {
    $texts = $store['texts'] ?? [];
    $items = array_merge($page['items'], manifest()['site']);
    foreach ($items as $it) {
        $ov = $texts[$it['scope']][$it['k']] ?? [];
        $inner = denorm($ov['html'] ?? $it['html'], $page['path']);
        $hidden = !empty($ov['hidden']);
        $pos = 0;
        while ($b = find_block($doc, $it['k'], $pos)) {
            [$s, $se, $es] = $b;
            $start = preg_replace('/\shidden(?=[\s>])/', '', substr($doc, $s, $se - $s));
            if ($hidden) $start = substr($start, 0, -1) . ' hidden>';
            $doc = substr($doc, 0, $s) . $start . $inner . substr($doc, $es);
            $pos = $s + strlen($start) + strlen($inner);
        }
    }
    $meta = $store['meta'][$page['path']] ?? [];
    $t = htmlspecialchars($meta['title'] ?? $page['title'], ENT_COMPAT, 'UTF-8', false);
    $d = htmlspecialchars($meta['description'] ?? $page['description'], ENT_COMPAT, 'UTF-8', false);
    $doc = preg_replace_callback('/<title>.*?<\/title>/s', fn() => '<title>' . $t . '</title>', $doc, 1);
    $doc = preg_replace_callback('/(<meta property="og:title" content=")[^"]*/', fn($m) => $m[1] . $t, $doc, 1);
    $doc = preg_replace_callback('/(<meta name="description" content=")[^"]*/', fn($m) => $m[1] . $d, $doc, 1);
    $doc = preg_replace_callback('/(<meta property="og:description" content=")[^"]*/', fn($m) => $m[1] . $d, $doc, 1);
    foreach ($page['images'] as $img) {
        $alt = htmlspecialchars($store['alts'][$img['k']] ?? $img['alt'], ENT_QUOTES);
        $doc = preg_replace_callback('/<img\b[^>]*\sdata-i="' . $img['k'] . '"[^>]*>/', function ($m) use ($alt) {
            return preg_match('/\salt="/', $m[0]) ? preg_replace('/\salt="[^"]*"/', ' alt="' . $alt . '"', $m[0]) : str_replace('<img', '<img alt="' . $alt . '"', $m[0]);
        }, $doc);
    }
    // every section is set from the store, so switching one back on removes its hidden flag
    $off = $store['sections'][$page['path']] ?? [];
    foreach ($page['sections'] ?? [] as $sec) {
        $hide = ($off[$sec['k']] ?? true) === false;
        $doc = preg_replace_callback('/(<section\b[^>]*\sdata-s="' . $sec['k'] . '")([^>]*)>/', function ($m) use ($hide) {
            return $m[1] . preg_replace('/\shidden\b/', '', $m[2]) . ($hide ? ' hidden' : '') . '>';
        }, $doc);
    }
    foreach (($store['imgver'] ?? []) as $src => $ver) {
        $doc = preg_replace('/((?:\.\.\/)*' . preg_quote($src, '/') . ')(?:\?v=\d+)?(?=["\')\s,])/', '${1}?v=' . (int) $ver, $doc);
    }
    return $doc;
}

// Rewrite every built page from the manifest and the saved edits. Returns the pages that failed.
function publish_all(): array {
    $store = store_read('content');
    $failed = [];
    if (@file_put_contents(SITE_ROOT . '/assets/theme.css', theme_css($store['design'] ?? []), LOCK_EX) === false) $failed[] = 'assets/theme.css';
    foreach (manifest()['pages'] as $page) {
        $file = SITE_ROOT . '/' . $page['path'];
        $doc = @file_get_contents($file);
        if ($doc === false) { $failed[] = $page['path']; continue; }
        $new = apply_page($doc, $page, $store);
        if ($new !== $doc && @file_put_contents($file, $new, LOCK_EX) === false) $failed[] = $page['path'];
    }
    return $failed;
}

// ---------- cleaning text typed into the editor ----------

const ALLOWED_TAGS = ['strong', 'b', 'em', 'i', 'a', 'br', 'span', 'small', 'sup', 'sub'];

function clean_html(string $html): string {
    $html = str_replace(["\xc2\xa0", '&nbsp;'], ' ', $html);
    $dom = new DOMDocument();
    libxml_use_internal_errors(true);
    $dom->loadHTML('<?xml encoding="UTF-8"><div id="r">' . $html . '</div>', LIBXML_HTML_NOIMPLIED | LIBXML_HTML_NODEFDTD);
    libxml_clear_errors();
    $root = $dom->getElementById('r');
    if (!$root) return htmlspecialchars(trim(strip_tags($html)), ENT_NOQUOTES);
    clean_node($root);
    $out = '';
    foreach ($root->childNodes as $c) $out .= $dom->saveHTML($c);
    $out = preg_replace('/(<br>\s*)+$/', '', $out);
    return trim(preg_replace('/\s+/', ' ', $out));
}

function clean_node(DOMNode $node): void {
    for ($c = $node->firstChild; $c; $c = $next) {
        $next = $c->nextSibling;
        if ($c instanceof DOMElement) {
            $tag = strtolower($c->tagName);
            clean_node($c);
            if (in_array($tag, ['div', 'p'], true)) {          // editor line breaks become <br>
                if ($c->previousSibling) $node->insertBefore($c->ownerDocument->createElement('br'), $c);
            }
            if (!in_array($tag, ALLOWED_TAGS, true)) {
                while ($c->firstChild) $node->insertBefore($c->firstChild, $c);
                $node->removeChild($c);
                continue;
            }
            foreach (iterator_to_array($c->attributes) as $a) {
                $keep = ($tag === 'a' && $a->name === 'href' && !preg_match('/^\s*(javascript|data|vbscript):/i', $a->value))
                     || ($tag === 'span' && $a->name === 'class');
                if (!$keep) $c->removeAttribute($a->name);
            }
        } elseif ($c->nodeType === XML_COMMENT_NODE) {
            $node->removeChild($c);
        }
    }
}

// Blocks whose markup the editor can't keep (icons, images, nested layout) are shown read-only.
function editable_markup(string $html): bool {
    return !preg_match('/<(?!\/?(?:' . implode('|', ALLOWED_TAGS) . ')\b)[a-z]/i', $html);
}

function plain(string $html): string {
    return trim(html_entity_decode(strip_tags($html), ENT_QUOTES, 'UTF-8'));
}

// ---------- enquiries (written by ../contact.php) ----------

function enquiries(): array {
    return store_read('enquiries', []);
}

function add_enquiry(array $e): bool {
    $f = DATA_DIR . '/enquiries.php';
    $h = @fopen($f, 'c+');
    if (!$h) return false;
    flock($h, LOCK_EX);
    $raw = stream_get_contents($h);
    if (strncmp($raw, '<?php', 5) === 0) $raw = substr($raw, strpos($raw, "
") + 1);
    $all = json_decode($raw, true) ?: [];
    array_unshift($all, $e + ['id' => bin2hex(random_bytes(6)), 'date' => date('c'), 'state' => 'new']);
    ftruncate($h, 0); rewind($h);
    fwrite($h, GUARD . json_encode($all, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES));
    flock($h, LOCK_UN); fclose($h);
    return true;
}

// ---------- sign-in ----------

function start_session(): void {
    $https = (!empty($_SERVER['HTTPS']) && $_SERVER['HTTPS'] !== 'off') || (($_SERVER['HTTP_X_FORWARDED_PROTO'] ?? '') === 'https');
    session_name('aegis_admin');
    session_set_cookie_params(['lifetime' => 0, 'path' => '/', 'secure' => $https, 'httponly' => true, 'samesite' => 'Strict']);
    session_start();
    if (empty($_SESSION['csrf'])) $_SESSION['csrf'] = bin2hex(random_bytes(16));
    // sign out after 2 hours without activity
    if (!empty($_SESSION['user']) && time() - ($_SESSION['seen'] ?? 0) > 7200) { $_SESSION = []; session_regenerate_id(true); }
    $_SESSION['seen'] = time();
}

function signed_in(): bool { return !empty($_SESSION['user']); }

function csrf_ok(): bool { return hash_equals($_SESSION['csrf'] ?? '', (string) ($_POST['csrf'] ?? '')); }

function too_many_attempts(string $ip): bool {
    $a = store_read('attempts', []);
    $recent = array_filter($a[$ip] ?? [], fn($t) => $t > time() - 900);
    return count($recent) >= 5;
}

function note_attempt(string $ip, bool $ok): void {
    $a = store_read('attempts', []);
    foreach ($a as $k => $ts) { $a[$k] = array_values(array_filter($ts, fn($t) => $t > time() - 900)); if (!$a[$k]) unset($a[$k]); }
    if ($ok) unset($a[$ip]); else $a[$ip][] = time();
    store_write('attempts', $a);
}

function h($s): string { return htmlspecialchars((string) $s, ENT_QUOTES, 'UTF-8'); }

// ---------- design settings -> assets/theme.css ----------

const DESIGN_DEFAULTS = ['navy' => '#0F172A', 'blue' => '#0E6BB4', 'teal' => '#1AB191', 'size' => 'medium', 'head' => 'serif', 'buttons' => 'square'];

function design(array $d): array {
    $out = DESIGN_DEFAULTS;
    foreach (['navy', 'blue', 'teal'] as $c) if (isset($d[$c]) && preg_match('/^#[0-9a-fA-F]{6}$/', $d[$c])) $out[$c] = strtoupper($d[$c]);
    if (in_array($d['size'] ?? '', ['small', 'medium', 'large'], true)) $out['size'] = $d['size'];
    if (in_array($d['head'] ?? '', ['serif', 'sans'], true)) $out['head'] = $d['head'];
    if (in_array($d['buttons'] ?? '', ['square', 'rounded'], true)) $out['buttons'] = $d['buttons'];
    return $out;
}

// mix a colour toward black (amount < 0) or white (amount > 0)
function shade(string $hex, float $amount): string {
    $rgb = array_map('hexdec', str_split(ltrim($hex, '#'), 2));
    $t = $amount < 0 ? 0 : 255;
    $a = abs($amount);
    return sprintf('#%02X%02X%02X', ...array_map(fn($v) => (int) round($v + ($t - $v) * $a), $rgb));
}

function theme_css(array $raw): string {
    $d = design($raw);
    $css = "/* Design settings from the content backend (/aegis, Design). Written by the backend; leave empty here. */\n";
    if ($d == DESIGN_DEFAULTS) return $css;
    $css .= ':root{';
    if ($d['navy'] !== DESIGN_DEFAULTS['navy']) $css .= '--navy:' . $d['navy'] . ';--ink:' . $d['navy'] . ';--navy-2:' . shade($d['navy'], .06) . ';';
    if ($d['blue'] !== DESIGN_DEFAULTS['blue']) $css .= '--blue:' . $d['blue'] . ';--blue-deep:' . $d['blue'] . ';--aud-plc:' . $d['blue'] . ';';
    if ($d['teal'] !== DESIGN_DEFAULTS['teal']) $css .= '--teal:' . $d['teal'] . ';--teal-bright:' . $d['teal'] . ';--green:' . $d['teal'] . ';--aud-ipo:' . $d['teal'] . ';--teal-text:' . shade($d['teal'], -.42) . ';';
    if ($d['blue'] !== DESIGN_DEFAULTS['blue'] || $d['teal'] !== DESIGN_DEFAULTS['teal']) $css .= '--grad:linear-gradient(90deg,' . shade($d['teal'], -.2) . ' 0%,' . $d['blue'] . ' 100%);';
    if ($d['head'] === 'sans') $css .= '--font-head:"Inter",Arial,Helvetica,sans-serif;';
    $css .= "}\n";
    if ($d['size'] !== 'medium') $css .= 'html{font-size:' . ($d['size'] === 'small' ? '93.75%' : '106.25%') . "}\n";
    if ($d['head'] === 'sans') $css .= "h1,h2,h3,.quote{letter-spacing:-.025em;font-weight:600}\n";
    if ($d['buttons'] === 'rounded') $css .= ".btn,.nav .btn{border-radius:10px}\n";
    return $css;
}
