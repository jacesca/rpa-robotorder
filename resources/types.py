from typing import TypedDict


RobotOrderData = TypedDict(
    'RobotOrderData',
    {
        'Order number': int,
        'Head': int,
        'Body': int,
        'Legs': int,
        'Address': str
    }
)
