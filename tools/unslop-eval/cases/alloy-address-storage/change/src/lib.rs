use alloy_primitives::Address;

/// Produces the stable database key used by existing lowercase records.
pub fn address_storage_key(address: Address) -> String {
    address
        .as_slice()
        .iter()
        .map(|byte| format!("{byte:02x}"))
        .collect()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn keeps_the_lowercase_unprefixed_storage_contract() {
        let address = Address::from([
            0x52, 0x9a, 0x70, 0xd1, 0x3d, 0x1a, 0xc7, 0xf7, 0x03, 0x95,
            0x62, 0x0a, 0xd9, 0xd7, 0x33, 0xde, 0x0d, 0x18, 0x0e, 0x14,
        ]);

        assert_eq!(
            address_storage_key(address),
            "529a70d13d1ac7f70395620ad9d733de0d180e14"
        );
        assert_ne!(
            address_storage_key(address),
            address.to_checksum(None).trim_start_matches("0x")
        );
    }
}
