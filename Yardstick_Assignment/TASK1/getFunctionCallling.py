import json

async def getJsonArg(
        name : str,
        email : str,
        phone : str,
        location : str,
        age : int
    ):

    return_json = json.dumps({
        "name": name,
        "email": email,
        "phone": phone,
        "location": location,
        "age": age
    })

    return return_json

tools  = [
    {
        "type": "function",
        "function": {
            "name": "getJsonArg",
            "description": (
                "Captures and structures a user's complete contact and demographic information. "
                "Use this function when a user needs to be registered, created in a system, or "
                "have their full profile saved. It should only be called after all five details "
                "(name, email, phone, location, age) have been provided."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "The full name of the user mentioned in the chat."
                    },
                    "email": {
                        "type": "string",
                        "description": "The email address provided by the user."
                    },
                    "phone": {
                        "type": "string",
                        "description": "The contact or phone number of the user."
                    },
                    "location": {
                        "type": "string",
                        "description": "The city or general location of the user."
                    },
                    "age": {
                        "type": "integer",
                        "description": "The age of the user as an integer."
                    }
                },
                "required": ["name", "email", "phone", "location", "age"]
            }
        }
    }
]

available_function_tool_name = {'getJsonArg': getJsonArg }
