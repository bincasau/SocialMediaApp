class BaseService:
    """Common base for services. Keep thin to allow testing and overrides."""

    @staticmethod
    def serialize_message(msg):
        return {
            'id': msg.id,
            'sender': msg.sender.username,
            'recipient': msg.recipient.username,
            'content': msg.content,
            'timestamp': msg.timestamp.isoformat() if hasattr(msg, 'timestamp') else None,
        }
