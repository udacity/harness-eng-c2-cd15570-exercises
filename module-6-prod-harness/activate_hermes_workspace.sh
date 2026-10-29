#!/usr/bin/env bash
# Source this file before using Hermes in a no-sudo Module 6 workspace.

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
    echo "Source this file so its environment remains active:" >&2
    echo "  source '$0'" >&2
    exit 2
fi

module_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
atomic_dir="$module_dir/.runtime/libatomic"
library_cache=""
atomic_file="$(
    if [ -d "$atomic_dir" ]; then
        find "$atomic_dir" -name 'libatomic.so.1' -print -quit 2>/dev/null
    fi
)"

if [ -n "$atomic_file" ]; then
    atomic_library_dir="$(dirname "$atomic_file")"
    export LD_LIBRARY_PATH="${atomic_library_dir}${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
elif command -v ldconfig >/dev/null 2>&1; then
    library_cache="$(ldconfig -p 2>/dev/null || true)"
elif [ -x /sbin/ldconfig ]; then
    library_cache="$(/sbin/ldconfig -p 2>/dev/null || true)"
fi

if [ -z "$atomic_file" ] && [[ "$library_cache" != *libatomic.so.1* ]]; then
    echo "libatomic.so.1 is unavailable." >&2
    echo "Run '$module_dir/setup_hermes_workspace.sh' first." >&2
    return 1
fi

export PATH="$HOME/.local/bin:$PATH"
if ! command -v hermes >/dev/null 2>&1; then
    echo "Hermes is not installed. Run '$module_dir/setup_hermes_workspace.sh'." >&2
    return 1
fi
export HERMES_CLI="$(command -v hermes)"

unset module_dir atomic_dir atomic_file atomic_library_dir library_cache
