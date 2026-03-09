<?php
declare(strict_types=1);

function clean_text(string $value, int $max = 500): string
{
    $value = trim(strip_tags($value));
    $value = preg_replace('/\s+/', ' ', $value) ?? '';
    if (function_exists('mb_substr')) {
        return mb_substr($value, 0, $max);
    }
    return substr($value, 0, $max);
}

function clean_multiline(string $value, int $max = 12000): string
{
    $value = str_replace("\r\n", "\n", trim(strip_tags($value)));
    $value = preg_replace("/\n{3,}/", "\n\n", $value) ?? '';
    if (function_exists('mb_substr')) {
        return mb_substr($value, 0, $max);
    }
    return substr($value, 0, $max);
}

function clean_url(string $value): string
{
    $value = trim($value);
    if ($value === '') {
        return '';
    }
    return filter_var($value, FILTER_VALIDATE_URL) ? $value : '';
}

function escape_html(string $value): string
{
    return htmlspecialchars($value, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    header('Location: agent_taskforce.html');
    exit;
}

$allowed_queues = [
    'review_correction',
    'youtube_video_brief',
    'site_update_sync',
    'site_issue',
    'seo_request',
    'general_request',
];

$queue = clean_text((string) ($_POST['queue'] ?? 'general_request'), 64);
if (!in_array($queue, $allowed_queues, true)) {
    $queue = 'general_request';
}

$request_id = gmdate('Ymd_His') . '-' . bin2hex(random_bytes(4));
$payload = [
    'request_id' => $request_id,
    'submitted_at' => gmdate('c'),
    'queue' => $queue,
    'request_title' => clean_text((string) ($_POST['request_title'] ?? ''), 180),
    'page_path' => clean_text((string) ($_POST['page_path'] ?? ''), 600),
    'doc_path' => clean_text((string) ($_POST['doc_path'] ?? ''), 600),
    'section' => clean_text((string) ($_POST['section'] ?? ''), 240),
    'claim' => clean_multiline((string) ($_POST['claim'] ?? ''), 6000),
    'proposed_correction' => clean_multiline((string) ($_POST['proposed_correction'] ?? ''), 8000),
    'request_details' => clean_multiline((string) ($_POST['request_details'] ?? ''), 12000),
    'evidence_url' => clean_url((string) ($_POST['evidence_url'] ?? '')),
    'preferred_contact' => clean_text((string) ($_POST['preferred_contact'] ?? ''), 240),
    'escalation_policy' => clean_text((string) ($_POST['escalation_policy'] ?? 'agent_only_unless_unverified'), 120),
    'source_page' => clean_text((string) ($_POST['source_page'] ?? ($_SERVER['HTTP_REFERER'] ?? '')), 800),
    'raw_payload_json' => clean_multiline((string) ($_POST['payload_json'] ?? ''), 30000),
    'user_agent' => clean_text((string) ($_SERVER['HTTP_USER_AGENT'] ?? ''), 400),
];

$storage_dir = __DIR__ . DIRECTORY_SEPARATOR . 'taskforce_submissions';
$write_error = '';

if (!is_dir($storage_dir) && !mkdir($storage_dir, 0755, true) && !is_dir($storage_dir)) {
    $write_error = 'Unable to create the taskforce storage directory.';
} else {
    $target = $storage_dir . DIRECTORY_SEPARATOR . $request_id . '.json';
    $encoded = json_encode($payload, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES);
    if ($encoded === false || file_put_contents($target, $encoded) === false) {
        $write_error = 'Unable to write the request to the taskforce queue.';
    }
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Taskforce Submission | CellNucleus.com</title>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    <style>
        .bg-slate-50 { background-color: #f8fafc; }
        .text-slate-950 { color: #020617; }
        .text-slate-900 { color: #0f172a; }
        .text-slate-700 { color: #334155; }
        .text-slate-600 { color: #475569; }
        .border-slate-300 { border-color: #cbd5e1; }
        .border-slate-200 { border-color: #e2e8f0; }
        .rounded-3xl { border-radius: 1.5rem; }
        .rounded-2xl { border-radius: 1rem; }
        .bg-slate-900 { background-color: #0f172a; }
    </style>
</head>
<body class="min-h-screen bg-slate-50 text-slate-900">
    <main class="mx-auto max-w-3xl px-4 py-16">
        <div class="rounded-3xl border border-slate-200 bg-white p-8 shadow-sm">
            <?php if ($write_error === ''): ?>
                <p class="text-sm font-semibold uppercase tracking-widest text-emerald-700">Queued</p>
                <h1 class="mt-3 text-3xl font-bold text-slate-950">Request sent to the agent taskforce</h1>
                <p class="mt-4 text-base text-slate-700">
                    The taskforce received this request as <strong><?php echo escape_html($request_id); ?></strong>.
                    Agents will verify what they can directly and only escalate unresolved issues to the site owner.
                </p>
                <div class="mt-6 rounded-2xl border border-emerald-200 bg-emerald-50 p-4 text-sm text-emerald-900">
                    <p><strong>Queue:</strong> <?php echo escape_html($payload['queue']); ?></p>
                    <p><strong>Title:</strong> <?php echo escape_html($payload['request_title'] ?: '(untitled request)'); ?></p>
                </div>
                <div class="mt-8 flex flex-wrap gap-3">
                    <a href="agent_taskforce.html" class="inline-flex items-center rounded-lg bg-slate-900 px-4 py-2 text-sm font-semibold text-white hover:bg-slate-800">Back to taskforce</a>
                    <a href="index.html" class="inline-flex items-center rounded-lg border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50">Home</a>
                </div>
            <?php else: ?>
                <p class="text-sm font-semibold uppercase tracking-widest text-red-700">Queue error</p>
                <h1 class="mt-3 text-3xl font-bold text-slate-950">The request could not be stored</h1>
                <p class="mt-4 text-base text-slate-700"><?php echo escape_html($write_error); ?></p>
                <p class="mt-3 text-sm text-slate-600">
                    The payload is shown below so it can be recovered manually if needed.
                </p>
                <pre class="mt-6 overflow-auto rounded-2xl border border-slate-200 bg-slate-50 p-4 text-xs text-slate-700"><?php echo escape_html((string) json_encode($payload, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES)); ?></pre>
                <div class="mt-8">
                    <a href="agent_taskforce.html" class="inline-flex items-center rounded-lg bg-slate-900 px-4 py-2 text-sm font-semibold text-white hover:bg-slate-800">Return to taskforce form</a>
                </div>
            <?php endif; ?>
        </div>
    </main>
</body>
</html>
