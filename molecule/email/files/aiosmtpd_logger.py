#!/usr/bin/env python3
"""Capture SMTP messages to a file for the Molecule e-mail scenario.

Start with: python3 aiosmtpd_logger.py </path/to/logfile>
"""
import asyncio
import email
import sys

from aiosmtpd.controller import Controller
from aiosmtpd.handlers import Sink


class FileHandler(Sink):
    def __init__(self, path):
        super().__init__()
        self.path = path

    async def handle_DATA(self, server, session, envelope):
        message = email.message_from_bytes(envelope.content)
        with open(self.path, "a") as log:
            log.write("=== MESSAGE ===\n")
            log.write(f"Mail From: {envelope.mail_from}\n")
            log.write(f"Rcpt To: {', '.join(envelope.rcpt_tos)}\n")
            log.write("--- RAW MESSAGE ---\n")
            log.write(envelope.content.decode("utf-8", "replace"))
            log.write("\n--- DECODED BODY ---\n")
            for part in message.walk():
                if part.get_content_type() == "text/html":
                    payload = part.get_payload(decode=True)
                    log.write(payload.decode("utf-8", "replace"))
            log.write("\n--- END OF MESSAGE ---\n")
        return "250 Message accepted"


def main():
    log_path = sys.argv[1] if len(sys.argv) > 1 else "/tmp/aiosmtpd_mail.log"
    controller = Controller(FileHandler(log_path), hostname="127.0.0.1", port=8025)
    controller.start()
    print(f"aiosmtpd listening on 127.0.0.1:8025, logging to {log_path}", flush=True)
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        controller.stop()


if __name__ == "__main__":
    main()