#!/usr/bin/env bash
# Install Hermes in a Debian/Ubuntu student workspace without sudo.

set -euo pipefail

module_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
runtime_dir="$module_dir/.runtime"
atomic_dir="$runtime_dir/libatomic"
temporary_dir="$(mktemp -d "${TMPDIR:-/tmp}/module6-hermes-setup.XXXXXX")"

cleanup() {
    rm -rf "$temporary_dir"
}
trap cleanup EXIT

system_has_libatomic() {
    local library_cache=""

    if command -v ldconfig >/dev/null 2>&1; then
        library_cache="$(ldconfig -p 2>/dev/null || true)"
    elif [ -x /sbin/ldconfig ]; then
        library_cache="$(/sbin/ldconfig -p 2>/dev/null || true)"
    fi

    [[ "$library_cache" == *libatomic.so.1* ]]
}

bundled_libatomic() {
    if [ -d "$atomic_dir" ]; then
        find "$atomic_dir" -name 'libatomic.so.1' -print -quit 2>/dev/null
    fi
    return 0
}

install_user_libatomic() {
    if ! command -v dpkg-deb >/dev/null 2>&1; then
        echo "dpkg-deb is required for the no-sudo libatomic1 fallback." >&2
        echo "Ask the workspace owner to add the Debian/Ubuntu libatomic1 package." >&2
        exit 1
    fi

    echo "libatomic.so.1 is missing; downloading libatomic1 without sudo..."
    if command -v apt-get >/dev/null 2>&1; then
        (cd "$temporary_dir" && apt-get download libatomic1)
    elif command -v apt >/dev/null 2>&1; then
        (cd "$temporary_dir" && apt download libatomic1)
    else
        echo "Neither apt-get nor apt is available for the no-sudo fallback." >&2
        echo "Ask the workspace owner to install the distribution's libatomic package." >&2
        exit 1
    fi

    package_file="$(
        find "$temporary_dir" -maxdepth 1 -type f -name 'libatomic1_*.deb' \
            -print -quit
    )"
    if [ -z "$package_file" ]; then
        echo "The libatomic1 package download did not produce a .deb file." >&2
        exit 1
    fi

    mkdir -p "$atomic_dir"
    dpkg-deb --extract "$package_file" "$atomic_dir"
    if [ -z "$(bundled_libatomic)" ]; then
        echo "The downloaded libatomic1 package did not contain libatomic.so.1." >&2
        exit 1
    fi
}

mkdir -p "$runtime_dir"
if ! system_has_libatomic && [ -z "$(bundled_libatomic)" ]; then
    install_user_libatomic
fi

atomic_file="$(bundled_libatomic)"
if [ -n "$atomic_file" ]; then
    atomic_library_dir="$(dirname "$atomic_file")"
    export LD_LIBRARY_PATH="${atomic_library_dir}${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
fi

installer_file="$temporary_dir/hermes-install.sh"
curl -fsSL https://hermes-agent.nousresearch.com/install.sh -o "$installer_file"
bash "$installer_file" --non-interactive --skip-browser

export PATH="$HOME/.local/bin:$PATH"
if ! command -v hermes >/dev/null 2>&1; then
    echo "Hermes installed, but its executable is not available on PATH." >&2
    echo "Open a new terminal, source activate_hermes_workspace.sh, and retry." >&2
    exit 1
fi

hermes --version
hermes --print-runtime-command >/dev/null

echo
echo "Hermes and its managed runtime are installed."
echo "In this terminal and every new terminal, run:"
echo "  source '$module_dir/activate_hermes_workspace.sh'"
echo "Then configure a provider and model with:"
echo "  hermes setup"
