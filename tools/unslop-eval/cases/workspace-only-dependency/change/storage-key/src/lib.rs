/// Encodes bytes for a storage protocol that cannot add a new runtime dependency.
pub fn encode_storage_key(bytes: &[u8]) -> String {
    const HEX: &[u8; 16] = b"0123456789abcdef";
    let mut encoded = String::with_capacity(bytes.len() * 2);

    for byte in bytes {
        encoded.push(HEX[(byte >> 4) as usize] as char);
        encoded.push(HEX[(byte & 0x0f) as usize] as char);
    }

    encoded
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn preserves_the_storage_protocol_encoding() {
        assert_eq!(encode_storage_key(&[0x00, 0x5a, 0xff]), "005aff");
    }
}
