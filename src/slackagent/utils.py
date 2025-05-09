from agents import TResponseInputItem


def remove_tool_messages(messages: list[TResponseInputItem]) -> list[TResponseInputItem]:
    filtered_messages = []
    tool_types = [
        "function_call",
        "function_call_output",
        "computer_call",
        "computer_call_output",
        "file_search_call",
        "web_search_call",
    ]
    for msg in messages:
        msg_type = msg.get("type")
        if msg_type in tool_types:
            continue
        filtered_messages.append(msg)
    return filtered_messages
