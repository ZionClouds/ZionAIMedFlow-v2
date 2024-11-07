#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Example to show sending message(s) to a Service Bus Queue asynchronously.
"""

from datetime import datetime, timezone
import os
import asyncio
from time import sleep
from azure.servicebus import ServiceBusMessage
from azure.servicebus.aio import ServiceBusClient
from azure.identity.aio import DefaultAzureCredential

# FULLY_QUALIFIED_NAMESPACE = os.environ['SERVICEBUS_FULLY_QUALIFIED_NAMESPACE']
QUEUE_NAME = "dips-messages"


async def send_single_message(sender):
    message = ServiceBusMessage("Single Message")
    await sender.send_messages(message)


async def send_a_list_of_messages(sender):
    messages = [ServiceBusMessage(
        f"{datetime.now(timezone.utc).timestamp()}:Message in list: {i}") for i in range(10)]
    await sender.send_messages(messages)


async def send_batch_message(sender):
    batch_message = await sender.create_message_batch()
    for _ in range(10):
        try:
            batch_message.add_message(ServiceBusMessage(
                "Message inside a ServiceBusMessageBatch"))
        except ValueError:
            # ServiceBusMessageBatch object reaches max_size.
            # New ServiceBusMessageBatch object can be created here to send more data.
            break
    await sender.send_messages(batch_message)


async def main():
    servicebus_client = ServiceBusClient.from_connection_string(
        "Endpoint=sb://sbdipsdevcus.servicebus.windows.net/;SharedAccessKeyName=DIPS_MANAGE;SharedAccessKey=pmyYzOdLGWtEjE3ZYqaJdkiEHkzRQJdyl+ASbJmNMo8=;EntityPath=dips-messages")

    async with servicebus_client:
        sender = servicebus_client.get_queue_sender(queue_name=QUEUE_NAME)
        async with sender:
            # await send_single_message(sender)
            await send_a_list_of_messages(sender)
            # await send_batch_message(sender)

    print("Send message is done.")


asyncio.run(main())
