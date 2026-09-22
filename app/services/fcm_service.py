from firebase_admin import messaging

from app.repositories.device_token_repository import DeviceTokenRepository


class FcmService:
    def __init__(self, device_token_repository: DeviceTokenRepository):
        self.device_token_repository = device_token_repository

    def send_to_user(self, user_id: str, title: str, body: str, data: dict) -> int:
        tokens: list[str] = []
        for device_token in self.device_token_repository.get_tokens_for_user(user_id):
            tokens.append(device_token.token)

        if len(tokens) == 0:
            return 0

        message = messaging.MulticastMessage(
            notification=messaging.Notification(title=title, body=body),
            data=data,
            tokens=tokens,
        )
        response = messaging.send_each_for_multicast(message)

        self.remove_invalid_tokens(tokens, response)
        return response.success_count

    def remove_invalid_tokens(self, tokens: list[str], response) -> None:
        for index, send_response in enumerate(response.responses):
            if send_response.success:
                continue

            exception = send_response.exception
            is_unregistered = isinstance(exception, messaging.UnregisteredError)
            is_mismatch = isinstance(exception, messaging.InvalidArgumentError) and "MismatchSenderId" in str(exception)
            if is_unregistered or is_mismatch:
                self.device_token_repository.delete_token(tokens[index])
