#!/usr/bin/env python3
"""
Name sync for van Scout (ThinkPad).

One assistant, two bodies: the phone app and the laptop share ONE name.
The ThinkPad holds the canonical name. Change it on either body and the
other picks it up — live when connected, on next contact when apart.

This module is the canonical store + HTTP server. It is stdlib-only
(no dependencies), binds localhost-first, and exposes LAN sharing only
when started with --host 0.0.0.0 — the same posture as everything else
on the ThinkPad (LAN/Tailscale-only, nothing public).

Protocol (full spec: NAME-SYNC-PROTOCOL.md):
  GET  /name[?since=<iso>&wait=<secs>]  -> canonical name record.
         Long-poll: with wait>0 the server holds the request until the
         name changes or `wait` seconds pass (cap 60). This is how
         "live push" works without a listener on the phone.
  POST /name      -> {"name","updated_at","updated_by"}; last-write-wins.
  POST /register  -> {"device_id","role"}; connected-app registry.
  GET  /health    -> server status + current record + registry.

Name record (JSON):
  {"name": "Scout",
   "updated_at": "2026-10-14T16:00:00.123456+00:00",   # ISO-8601 UTC
   "updated_by": "android-7f3a..."}                  # device id

Conflict rule: last-write-wins by parsed timestamp. Receivers MUST parse
timestamps (Instant/datetime), never string-compare them — "Z" vs "+00:00"
and fractional digits make string comparison wrong.

Wake-word rule: the wake word follows the name ONLY if an openWakeWord
model file exists for it (hey_<slug>.onnx in the wake-word dir). If none
exists, the name still changes, but the wake word stays — and the
response says so (wake_word_available: false) so the caller can tell
the user instead of going silently deaf.

Usage as a library:
    from name_sync import NameStore, NameSyncClient
    store = NameStore()                      # ~/.scout/name.json
    store.apply({"name": "Buddy", "updated_at": "...", "updated_by": "laptop"})
    client = NameSyncClient()                # talks to localhost:8091
    client.submit_name("Buddy", device_id="laptop")

Run the server:
    python3 name_sync.py serve [--host 127.0.0.1] [--port 8091]

Quick CLI for testing:
    python3 name_sync.py get
    python3 name_sync.py set Buddy --device-id laptop
    python3 name_sync.py health
    python3 name_sync.py --self-test
"""

import argparse
import json
import os
import re
import sys
import threading
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib import request as urlrequest
from urllib import error as urlerror
from urllib.parse import urlparse, parse_qs

DEFAULT_PORT = 8091
DEFAULT_NAME = "Scout"
MAX_NAME_LEN = 40
EPOCH = "1970-01-01T00:00:00+00:00"

DEFAULT_STORE_PATH = os.path.join(
    os.path.expanduser("~"), ".scout", "name.json")
DEFAULT_QUEUE_PATH = os.path.join(
    os.path.expanduser("~"), ".scout", "name_queue.json")
DEFAULT_WAKEWORD_DIR = os.path.join(
    os.path.expanduser("~"), ".scout", "wakewords")

STORE_PATH = os.environ.get("SCOUT_NAME_STORE", DEFAULT_STORE_PATH)
QUEUE_PATH = os.environ.get("SCOUT_NAME_QUEUE", DEFAULT_QUEUE_PATH)
WAKEWORD_DIR = os.environ.get("SCOUT_WAKEWORD_DIR", DEFAULT_WAKEWORD_DIR)

_NAME_BAD_CHARS = re.compile(r"[\x00-\x1f\x7f]")  # control chars, incl. newline


# ── timestamps ──────────────────────────────────────────────────────

def now_iso():
    """Current UTC time as ISO-8601 with offset (e.g. ...+00:00)."""
    return datetime.now(timezone.utc).isoformat()


def parse_ts(value):
    """Parse an ISO-8601 timestamp to an aware datetime.

    Accepts both 'Z' and '+00:00' forms. Returns None when unparseable —
    callers treat that as 'older than everything' (epoch), never crash.
    """
    if not isinstance(value, str) or not value:
        return None
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def ts_or_epoch(value):
    return parse_ts(value) or datetime(1970, 1, 1, tzinfo=timezone.utc)


# ── name validation ─────────────────────────────────────────────────

def validate_name(name):
    """Return an error string, or None when the name is acceptable."""
    if not isinstance(name, str):
        return "name must be a string"
    if not name.strip():
        return "name must not be blank"
    if len(name.strip()) > MAX_NAME_LEN:
        return "name must be %d characters or fewer" % MAX_NAME_LEN
    if _NAME_BAD_CHARS.search(name):
        return "name must not contain newlines or control characters"
    return None


def slugify_name(name):
    """'Mary Jane' -> 'mary_jane' — for wake-word model filenames."""
    slug = re.sub(r"[^a-z0-9]+", "_", name.strip().lower()).strip("_")
    return slug or "scout"


def wake_word_model_available(name, models_dir=None):
    """True when an openWakeWord model file exists for this name.

    Looks for hey_<slug>.onnx in the wake-word dir. This is a hook, not
    a wake-word engine: it answers 'can the wake word follow this name?'
    """
    directory = models_dir or WAKEWORD_DIR
    candidate = os.path.join(directory, "hey_%s.onnx" % slugify_name(name))
    return os.path.isfile(candidate)


def persona_prefix(record):
    """'Your name is X.' — prepended to the system prompt at prompt-build
    time (the app does the same in MainViewModel). The persona file itself
    never hard-codes a name."""
    return "Your name is %s." % record.get("name", DEFAULT_NAME)


# ── canonical store ─────────────────────────────────────────────────

class NameStore:
    """The canonical name record, persisted as JSON with atomic writes.

    Thread-safe: one lock guards load/apply/save, and a Condition lets
    long-poll requests wait for the next change.
    """

    def __init__(self, path=None):
        self.path = path or STORE_PATH
        self._lock = threading.Lock()
        self.condition = threading.Condition(self._lock)
        self._record = self._load()

    def _default_record(self):
        return {"name": DEFAULT_NAME, "updated_at": EPOCH,
                "updated_by": "thinkpad"}

    def _load(self):
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, dict) or validate_name(
                    data.get("name", "")) is not None:
                return self._default_record()
            data.setdefault("updated_at", EPOCH)
            data.setdefault("updated_by", "thinkpad")
            return {"name": data["name"].strip(),
                    "updated_at": data["updated_at"],
                    "updated_by": data["updated_by"]}
        except (OSError, ValueError):
            return self._default_record()

    def _save_locked(self):
        directory = os.path.dirname(self.path)
        if directory:
            os.makedirs(directory, exist_ok=True)
        tmp = self.path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(self._record, f)
            f.write("\n")
        os.replace(tmp, self.path)

    def current(self):
        with self._lock:
            return dict(self._record)

    def apply(self, incoming):
        """Apply a name-change proposal. Returns (applied, reason).

        Last-write-wins by parsed timestamp. Equal timestamps lose
        (the stored record stands) — ties are not a coin flip.
        """
        err = validate_name(incoming.get("name", ""))
        if err is not None:
            return False, err
        incoming_ts = ts_or_epoch(incoming.get("updated_at"))
        with self.condition:
            current_ts = ts_or_epoch(self._record.get("updated_at"))
            if incoming_ts <= current_ts:
                return False, "stale: stored record is newer or equal"
            self._record = {
                "name": incoming["name"].strip(),
                "updated_at": incoming.get("updated_at") or now_iso(),
                "updated_by": incoming.get("updated_by") or "unknown",
            }
            self._save_locked()
            self.condition.notify_all()
            return True, "applied"

    def wait_for_change(self, since_iso, timeout):
        """Block until the record is newer than `since_iso`, or timeout.

        Returns the current record (changed or not — the caller compares).
        Used by long-poll GET /name.
        """
        since = ts_or_epoch(since_iso)
        deadline = time.monotonic() + max(0.0, timeout)
        with self.condition:
            while ts_or_epoch(self._record.get("updated_at")) <= since:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    break
                self.condition.wait(timeout=remaining)
            return dict(self._record)


# ── HTTP server ─────────────────────────────────────────────────────

class NameSyncServer:
    """Threading HTTP server for the name-sync protocol."""

    def __init__(self, store, host="127.0.0.1", port=DEFAULT_PORT):
        self.store = store
        self.registry = {}  # device_id -> {"role": ..., "last_seen": iso}
        self._registry_lock = threading.Lock()
        self._httpd = ThreadingHTTPServer((host, port), self._handler())
        self._httpd.daemon_threads = True

    @property
    def port(self):
        return self._httpd.server_address[1]

    def _handler(self):
        server = self

        class Handler(BaseHTTPRequestHandler):
            protocol_version = "HTTP/1.1"

            def log_message(self, fmt, *args):  # keep stdout clean
                sys.stderr.write("name_sync: %s\n" % (fmt % args))

            def _send_json(self, status, payload):
                body = json.dumps(payload).encode("utf-8")
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def _read_json(self):
                length = int(self.headers.get("Content-Length") or 0)
                if length <= 0:
                    return {}
                raw = self.rfile.read(length)
                try:
                    data = json.loads(raw.decode("utf-8"))
                except ValueError:
                    return None
                return data if isinstance(data, dict) else None

            def _record_response(self, record):
                return {
                    "name": record["name"],
                    "updated_at": record["updated_at"],
                    "updated_by": record["updated_by"],
                    "wake_word_available": wake_word_model_available(
                        record["name"]),
                    "persona_prefix": persona_prefix(record),
                }

            def do_GET(self):
                parsed = urlparse(self.path)
                if parsed.path == "/name":
                    query = parse_qs(parsed.query)
                    since = (query.get("since") or [None])[0]
                    wait_raw = (query.get("wait") or ["0"])[0]
                    try:
                        wait = min(60.0, max(0.0, float(wait_raw)))
                    except ValueError:
                        wait = 0.0
                    if wait > 0 and since is not None:
                        record = server.store.wait_for_change(since, wait)
                    else:
                        record = server.store.current()
                    self._send_json(200, self._record_response(record))
                elif parsed.path == "/health":
                    with server._registry_lock:
                        devices = dict(server.registry)
                    self._send_json(200, {
                        "status": "ok",
                        "record": self._record_response(
                            server.store.current()),
                        "registered_devices": devices,
                    })
                else:
                    self._send_json(404, {"error": "unknown path"})

            def do_POST(self):
                parsed = urlparse(self.path)
                if parsed.path == "/name":
                    data = self._read_json()
                    if data is None:
                        self._send_json(400, {"error": "invalid JSON body"})
                        return
                    proposal = {
                        "name": data.get("name", ""),
                        "updated_at": data.get("updated_at") or now_iso(),
                        "updated_by": data.get("updated_by") or "unknown",
                    }
                    applied, reason = server.store.apply(proposal)
                    status = 200 if applied else 409
                    # 409 (stale) still returns the winning record so the
                    # caller can converge without another round trip.
                    self._send_json(status, {
                        "applied": applied,
                        "reason": reason,
                        "record": self._record_response(
                            server.store.current()),
                    })
                elif parsed.path == "/register":
                    data = self._read_json()
                    if data is None or not data.get("device_id"):
                        self._send_json(400, {"error": "device_id required"})
                        return
                    with server._registry_lock:
                        server.registry[data["device_id"]] = {
                            "role": data.get("role") or "app",
                            "last_seen": now_iso(),
                        }
                    self._send_json(200, {"ok": True})
                else:
                    self._send_json(404, {"error": "unknown path"})

        return Handler

    def serve_forever(self):
        self._httpd.serve_forever()

    def shutdown(self):
        self._httpd.shutdown()
        self._httpd.server_close()


# ── client (for laptop-side tools + offline queue) ───────────────────

class NameSyncError(Exception):
    """The server couldn't be reached or refused the request."""


class NameSyncClient:
    """Talk to a name-sync server. Also owns the offline queue: changes
    made while the server is unreachable are persisted to a JSON file and
    flushed on the next successful contact (mirrors the app's queue)."""

    def __init__(self, base_url=None, queue_path=None):
        self.base_url = (base_url or
                         "http://127.0.0.1:%d" % DEFAULT_PORT).rstrip("/")
        self.queue_path = queue_path or QUEUE_PATH

    # -- low level --

    def _request(self, method, path, payload=None, timeout=5.0):
        url = self.base_url + path
        data = None
        headers = {"Content-Type": "application/json"}
        if payload is not None:
            data = json.dumps(payload).encode("utf-8")
        req = urlrequest.Request(url, data=data, headers=headers,
                                 method=method)
        try:
            with urlrequest.urlopen(req, timeout=timeout) as resp:
                return resp.status, json.loads(
                    resp.read().decode("utf-8"))
        except urlerror.HTTPError as e:
            try:
                return e.code, json.loads(e.read().decode("utf-8"))
            except ValueError:
                return e.code, {"error": "http %d" % e.code}
        except (urlerror.URLError, OSError, TimeoutError) as e:
            raise NameSyncError(str(e))

    # -- API --

    def get_name(self, since=None, wait=0.0):
        # urlencode: the ISO timestamp's '+' in '+00:00' MUST be encoded
        # (%2B) or it arrives as a space and fails to parse server-side.
        from urllib.parse import urlencode
        query = {}
        if since is not None:
            query["since"] = since
        if wait:
            query["wait"] = str(wait)
        path = "/name"
        if query:
            path += "?" + urlencode(query)
        status, payload = self._request("GET", path, timeout=wait + 5.0)
        if status != 200:
            raise NameSyncError(payload.get("error", "http %d" % status))
        return payload

    def submit_name(self, name, device_id, updated_at=None):
        status, payload = self._request("POST", "/name", {
            "name": name,
            "updated_at": updated_at or now_iso(),
            "updated_by": device_id,
        })
        if status not in (200, 409):
            raise NameSyncError(payload.get("error", "http %d" % status))
        return payload  # {applied, reason, record}

    def register(self, device_id, role="app"):
        status, payload = self._request("POST", "/register", {
            "device_id": device_id, "role": role})
        if status != 200:
            raise NameSyncError(payload.get("error", "http %d" % status))
        return payload

    def health(self):
        status, payload = self._request("GET", "/health")
        if status != 200:
            raise NameSyncError(payload.get("error", "http %d" % status))
        return payload

    # -- offline queue --

    def queue_change(self, name, device_id, updated_at=None):
        """Persist a change that couldn't be delivered (server away)."""
        record = {"name": name,
                  "updated_at": updated_at or now_iso(),
                  "updated_by": device_id}
        err = validate_name(record["name"])
        if err is not None:
            raise ValueError(err)
        directory = os.path.dirname(self.queue_path)
        if directory:
            os.makedirs(directory, exist_ok=True)
        tmp = self.queue_path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(record, f)
        os.replace(tmp, self.queue_path)
        return record

    def queued_change(self):
        try:
            with open(self.queue_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict) and validate_name(
                    data.get("name", "")) is None:
                return data
        except (OSError, ValueError):
            pass
        return None

    def flush_queue(self):
        """Send the queued change if one exists.

        Returns (flushed, payload-or-None). A stale rejection means the
        server holds a newer record — the queued change is obsolete, so
        it is dropped and the server record is returned. A network
        failure keeps the change queued and raises NameSyncError.
        """
        pending = self.queued_change()
        if pending is None:
            return False, None
        payload = self.submit_name(pending["name"], pending["updated_by"],
                                   pending.get("updated_at"))
        # Delivered either way (applied or superseded) — drop the queue.
        try:
            os.remove(self.queue_path)
        except OSError:
            pass
        return True, payload


# ── self-test ───────────────────────────────────────────────────────

def run_self_test():
    """Exercise the whole protocol against a throwaway server.

    Every check prints PASS/FAIL. Exit code 0 only when all pass.
    """
    import tempfile

    passed = []
    failed = []

    def check(label, condition, detail=""):
        if condition:
            passed.append(label)
            print("PASS  %s" % label)
        else:
            failed.append(label)
            print("FAIL  %s  %s" % (label, detail))

    tmp = tempfile.mkdtemp(prefix="name_sync_test_")
    store_path = os.path.join(tmp, "name.json")
    queue_path = os.path.join(tmp, "queue.json")
    models_dir = os.path.join(tmp, "wakewords")
    os.makedirs(models_dir)
    # Only a model for "Scout" exists — "Buddy" has none (wake-word rule).
    open(os.path.join(models_dir, "hey_scout.onnx"), "w").close()

    store = NameStore(store_path)
    server = NameSyncServer(store, host="127.0.0.1", port=0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    client = NameSyncClient("http://127.0.0.1:%d" % server.port,
                            queue_path=queue_path)
    # Point the wake-word hook at the temp models dir.
    global WAKEWORD_DIR
    old_dir = WAKEWORD_DIR
    WAKEWORD_DIR = models_dir
    try:
        # 1. Default record.
        rec = client.get_name()
        check("default record is Scout", rec["name"] == "Scout", str(rec))

        # 2. Apply a newer change.
        t1 = now_iso()
        res = client.submit_name("Buddy", "app-1", t1)
        check("newer change applies",
              res["applied"] is True and res["record"]["name"] == "Buddy",
              str(res))
        check("wake-word flag false for Buddy (no model)",
              res["record"]["wake_word_available"] is False, str(res))
        check("persona prefix tracks name",
              res["record"]["persona_prefix"] == "Your name is Buddy.",
              str(res))

        # 3. Stale change is rejected, stored record stands.
        res2 = client.submit_name("Old", "app-1", EPOCH)
        check("stale change rejected",
              res2["applied"] is False
              and res2["record"]["name"] == "Buddy", str(res2))

        # 4. Invalid names rejected.
        for bad in ("", "   ", "x" * 41, "Bad\nName"):
            try:
                res3 = client.submit_name(bad, "app-1", now_iso())
                check("invalid name rejected: %r" % bad,
                      res3["applied"] is False, str(res3))
            except NameSyncError as e:
                check("invalid name rejected: %r" % bad, True, str(e))

        # 5. Long-poll wakes promptly on change.
        since = client.get_name()["updated_at"]
        holder = {}

        def poller():
            holder["rec"] = client.get_name(since=since, wait=10.0)

        poll_thread = threading.Thread(target=poller, daemon=True)
        started = time.monotonic()
        poll_thread.start()
        time.sleep(0.3)
        client.submit_name("Scout", "app-1", now_iso())
        poll_thread.join(timeout=8.0)
        elapsed = time.monotonic() - started
        check("long-poll wakes on change",
              holder.get("rec", {}).get("name") == "Scout" and elapsed < 5.0,
              "elapsed=%.2fs rec=%s" % (elapsed, holder.get("rec")))

        # 6. Long-poll times out with the current record.
        started = time.monotonic()
        rec6 = client.get_name(
            since=client.get_name()["updated_at"], wait=1.0)
        elapsed = time.monotonic() - started
        check("long-poll timeout returns current",
              rec6["name"] == "Scout" and 0.9 <= elapsed < 4.0,
              "elapsed=%.2fs" % elapsed)

        # 7. Offline queue: queue while unreachable, flush delivers.
        dead = NameSyncClient("http://127.0.0.1:1", queue_path=queue_path)
        dead.queue_change("Buddy", "app-1")
        check("change queued while server away",
              dead.queued_change() is not None)
        try:
            dead.flush_queue()
            check("flush to dead server raises", False, "no error raised")
        except NameSyncError:
            check("flush to dead server raises", True)
        check("queue survives failed flush",
              client.queued_change() is not None)
        flushed, payload = client.flush_queue()
        check("flush delivers queued change",
              flushed and payload["record"]["name"] == "Buddy", str(payload))
        check("queue cleared after flush",
              client.queued_change() is None)

        # 8. Persistence across restart (new store, same file).
        store2 = NameStore(store_path)
        check("record survives restart",
              store2.current()["name"] == "Buddy", str(store2.current()))

        # 9. Wake-word hook.
        check("wake-word model found for Scout",
              wake_word_model_available("Scout") is True)
        check("wake-word model missing for Buddy",
              wake_word_model_available("Buddy") is False)
        check("slug handles spaces",
              wake_word_model_available("Mary Jane") is False
              and slugify_name("Mary Jane") == "mary_jane")

        # 10. Register + health.
        reg = client.register("app-1", "app")
        check("register ok", reg.get("ok") is True, str(reg))
        health = client.health()
        check("health reports record + registry",
              health.get("status") == "ok"
              and health["record"]["name"] == "Buddy"
              and "app-1" in health["registered_devices"], str(health))

        # 11. Concurrent writers: latest timestamp wins, file stays valid.
        stamps = [now_iso() for _ in range(5)]
        time.sleep(0.01)
        stamps = sorted(stamps)
        results = []

        def writer(i):
            try:
                results.append(client.submit_name(
                    "Writer%d" % i, "w%d" % i, stamps[i]))
            except Exception as e:  # noqa: BLE001 — self-test collects
                results.append(e)

        threads = [threading.Thread(target=writer, args=(i,))
                   for i in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        final = client.get_name()
        check("concurrent writes converge on latest",
              final["name"] == "Writer4"
              and final["updated_at"] == stamps[4], str(final))
        with open(store_path, "r", encoding="utf-8") as f:
            json.load(f)  # raises if corrupt
        check("store file stays valid JSON after concurrency", True)
    finally:
        WAKEWORD_DIR = old_dir
        server.shutdown()

    print("\n%d passed, %d failed" % (len(passed), len(failed)))
    return 1 if failed else 0


# ── CLI ─────────────────────────────────────────────────────────────

def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Name sync for van Scout (ThinkPad holds the "
                    "canonical name).")
    parser.add_argument("--self-test", action="store_true",
                        help="run the protocol self-test and exit")
    parser.add_argument("--store", default=None,
                        help="path to the name store JSON (default "
                             "~/.scout/name.json)")
    sub = parser.add_subparsers(dest="command")

    p_serve = sub.add_parser("serve", help="run the name-sync server")
    p_serve.add_argument("--host", default="127.0.0.1",
                         help="bind address (127.0.0.1 default; 0.0.0.0 "
                              "for LAN sharing)")
    p_serve.add_argument("--port", type=int, default=DEFAULT_PORT)

    sub.add_parser("get", help="print the canonical name record")
    p_set = sub.add_parser("set", help="set the canonical name")
    p_set.add_argument("name")
    p_set.add_argument("--device-id", default="laptop")

    sub.add_parser("health", help="print server health")
    args = parser.parse_args(argv)

    if args.self_test:
        return run_self_test()

    store = NameStore(args.store)
    if args.command == "serve":
        server = NameSyncServer(store, host=args.host, port=args.port)
        print("name_sync listening on %s:%d (store: %s)"
              % (args.host, server.port, store.path))
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nstopping.")
        return 0
    if args.command == "get":
        print(json.dumps(store.current(), indent=2))
        return 0
    if args.command == "set":
        applied, reason = store.apply({
            "name": args.name, "updated_at": now_iso(),
            "updated_by": args.device_id})
        print("%s: %s" % ("APPLIED" if applied else "REJECTED", reason))
        print(json.dumps(store.current(), indent=2))
        return 0 if applied else 1
    if args.command == "health":
        client = NameSyncClient()
        print(json.dumps(client.health(), indent=2))
        return 0
    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
