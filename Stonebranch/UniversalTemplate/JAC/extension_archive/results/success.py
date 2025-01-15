from ue_framework.results import SuccessJSONResult


class SuccessResult(SuccessJSONResult):
    exit_code: int = 0
    message: str = "SUCCESS: Task executed successfully."


class DataSyncResult(SuccessJSONResult):
    exit_code: int = 21
    message: str = "Some errors where produced during data synchronization process: Task completed with failures. See Extension Output for more details."
