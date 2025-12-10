# exceptions.py

class BlockchainError(Exception):
    """Base exception for blockchain errors."""
    pass

class InvalidBlockError(BlockchainError):
    """Thrown when a block fails validation."""
    pass

class BlockchainIntegrityError(BlockchainError):
    """Thrown when blockchain validation fails."""
    pass
