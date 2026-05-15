class BaseService:
    """Lớp nền chung cho các service.

    Ghi chú: Giữ lớp này thật mỏng để dễ test và dễ ghi đè khi cần.
    """

    @staticmethod
    def serialize_message(msg):
        """Chuyển một `Message` thành dữ liệu phù hợp để trả JSON.

        Ghi chú: Giữ hàm này hẹp để API và test dùng chung một dạng dữ liệu
        mà không phải lặp lại logic ánh xạ trường.
        """
        return {
            'id': msg.id,
            'sender': msg.sender.username,
            'recipient': msg.recipient.username,
            'content': msg.content,
            'timestamp': msg.timestamp.isoformat() if hasattr(msg, 'timestamp') else None,
        }
