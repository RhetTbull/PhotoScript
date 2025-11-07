"""Custom exceptions for PhotoScript."""


class AppleScriptError(Exception):
    def __init__(self, *message):
        super().__init__(*message)
