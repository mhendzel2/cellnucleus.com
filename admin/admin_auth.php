<?php
declare(strict_types=1);

function admin_parse_env_file(string $path): array
{
    if (!is_file($path)) {
        return [];
    }

    $lines = file($path, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES);
    if ($lines === false) {
        return [];
    }

    $values = [];
    foreach ($lines as $line) {
        $line = trim($line);
        if ($line === '' || $line[0] === '#') {
            continue;
        }

        $delimiter = strpos($line, '=');
        if ($delimiter === false) {
            $delimiter = strpos($line, ':');
        }
        if ($delimiter === false) {
            continue;
        }

        $key = strtoupper(trim(substr($line, 0, $delimiter)));
        $value = trim(substr($line, $delimiter + 1));
        if ($value !== '' && strlen($value) >= 2 && $value[0] === $value[strlen($value) - 1] && ($value[0] === '"' || $value[0] === "'")) {
            $value = substr($value, 1, -1);
        }
        if ($key !== '' && $value !== '') {
            $values[$key] = $value;
        }
    }

    return $values;
}

function admin_secret_paths(): array
{
    $root = dirname(__DIR__);
    $paths = [];
    $custom = getenv('CELLNUCLEUS_ADMIN_ENV_PATH');
    if (is_string($custom) && $custom !== '') {
        $paths[] = $custom;
    }

    return [
        ...$paths,
        $root . '/../.secrets/.env',
        $root . '/../private/cellnucleus_admin.env',
        $root . '/.secrets/.env',
    ];
}

function admin_load_credentials(): array
{
    $secrets = [];
    foreach (admin_secret_paths() as $path) {
        $secrets = array_merge($secrets, admin_parse_env_file($path));
    }

    $user = getenv('CELLNUCLEUS_ADMIN_USER') ?: getenv('TASKFORCE_ADMIN_USER') ?: ($secrets['CELLNUCLEUS_ADMIN_USER'] ?? '') ?: ($secrets['TASKFORCE_ADMIN_USER'] ?? '');
    $password = getenv('CELLNUCLEUS_ADMIN_PASSWORD') ?: getenv('TASKFORCE_ADMIN_PASSWORD') ?: ($secrets['CELLNUCLEUS_ADMIN_PASSWORD'] ?? '') ?: ($secrets['TASKFORCE_ADMIN_PASSWORD'] ?? '');

    return [
        'user' => is_string($user) ? $user : '',
        'password' => is_string($password) ? $password : '',
    ];
}

function admin_read_basic_auth(): array
{
    $user = $_SERVER['PHP_AUTH_USER'] ?? '';
    $password = $_SERVER['PHP_AUTH_PW'] ?? '';
    if ($user !== '' || $password !== '') {
        return [(string) $user, (string) $password];
    }

    $header = $_SERVER['HTTP_AUTHORIZATION'] ?? $_SERVER['REDIRECT_HTTP_AUTHORIZATION'] ?? '';
    if (!is_string($header) || stripos($header, 'basic ') !== 0) {
        return ['', ''];
    }

    $decoded = base64_decode(substr($header, 6), true);
    if ($decoded === false || strpos($decoded, ':') === false) {
        return ['', ''];
    }

    [$user, $password] = explode(':', $decoded, 2);
    return [$user, $password];
}

function admin_config_error(): never
{
    http_response_code(503);
    header('Content-Type: text/html; charset=UTF-8');
    header('X-Robots-Tag: noindex, nofollow, noarchive', true);
    echo '<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="robots" content="noindex,nofollow,noarchive"><title>Admin Unavailable</title></head><body><p>Administration is not configured.</p></body></html>';
    exit;
}

function admin_unauthorized(): never
{
    http_response_code(401);
    header('WWW-Authenticate: Basic realm="CellNucleus Administration"');
    header('Content-Type: text/html; charset=UTF-8');
    header('X-Robots-Tag: noindex, nofollow, noarchive', true);
    echo '<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="robots" content="noindex,nofollow,noarchive"><title>Authorization Required</title></head><body><p>Authorization required.</p></body></html>';
    exit;
}

function require_admin_auth(): void
{
    header('X-Robots-Tag: noindex, nofollow, noarchive', true);

    $credentials = admin_load_credentials();
    if ($credentials['user'] === '' || $credentials['password'] === '') {
        admin_config_error();
    }

    [$provided_user, $provided_password] = admin_read_basic_auth();
    if (!hash_equals($credentials['user'], (string) $provided_user) || !hash_equals($credentials['password'], (string) $provided_password)) {
        admin_unauthorized();
    }
}
