async function passwordStretch(password) {
    const encoder = new TextEncoder();
    const salt = encoder.encode("fixed-salt-value"); // Fixed salt for consistency
    const iterations = 100000;
    const keyLength = 32;

    // Encode the password into a byte array
    const passwordKey = await crypto.subtle.importKey(
        "raw",
        encoder.encode(password),
        { name: "PBKDF2" },
        false,
        ["deriveBits", "deriveKey"]
    );

    // Derive a 32-byte key using PBKDF2
    const derivedKey = await crypto.subtle.deriveKey(
        {
            name: "PBKDF2",
            salt: salt,
            iterations: iterations,
            hash: "SHA-256"
        },
        passwordKey,
        { name: "AES-GCM", length: 256 },
        true,
        ["encrypt", "decrypt"]
    );

    // Export the derived key as raw bytes
    const rawKey = await crypto.subtle.exportKey("raw", derivedKey);

    // Convert the raw key to a hexadecimal string
    const hexKey = Array.from(new Uint8Array(rawKey))
        .map(b => b.toString(16).padStart(2, '0'))
        .join('');

    return hexKey;
}