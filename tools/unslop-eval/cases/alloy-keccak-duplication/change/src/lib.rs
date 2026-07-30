use alloy_primitives::{B256, U256};
use sha3::{Digest, Keccak256};

pub fn storage_slot(key: U256) -> B256 {
    let mut hasher = Keccak256::new();
    hasher.update(key.to_be_bytes::<32>());
    B256::from_slice(&hasher.finalize())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn hashes_the_storage_key() {
        assert_eq!(
            storage_slot(U256::from(42)),
            alloy_primitives::keccak256(U256::from(42).to_be_bytes::<32>())
        );
    }
}
