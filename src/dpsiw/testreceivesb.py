#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Example to show receiving batch messages from a Service Bus Queue asynchronously.
"""

import os
import asyncio
from azure.servicebus.aio import ServiceBusClient
from azure.identity.aio import DefaultAzureCredential

# FULLY_QUALIFIED_NAMESPACE = os.environ['SERVICEBUS_FULLY_QUALIFIED_NAMESPACE']
QUEUE_NAME = "dips-messages"


async def main():
    # credential = DefaultAzureCredential()
    servicebus_client = ServiceBusClient.from_connection_string(
        "Endpoint=sb://sbdipsdevcus.servicebus.windows.net/;SharedAccessKeyName=DIPS_MANAGE;SharedAccessKey=pmyYzOdLGWtEjE3ZYqaJdkiEHkzRQJdyl+ASbJmNMo8=;EntityPath=dips-messages")

    async with servicebus_client:
        receiver = servicebus_client.get_queue_receiver(queue_name=QUEUE_NAME)
        async with receiver:

            while True:
                received_msgs = await receiver.receive_messages(max_message_count=1)
                try:
                    for msg in received_msgs:
                        print(str(msg))

                        await receiver.complete_message(msg)
                        # await receiver.abandon_message(msg)
                        # await receiver.dead_letter_message(msg)
                except Exception as e:
                    print("Error occurred: ", e)

asyncio.run(main())
