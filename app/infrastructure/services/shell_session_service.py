"""Shell session service implementation."""

import asyncio

from app.core.result import Err, Ok, Result
from app.domain.interfaces.session_service import ISessionService
from app.domain.value_objects.session_id import SessionId


class ShellSessionService(ISessionService):
    """Service for managing shell sessions."""

    async def start_session(self, session_id: SessionId) -> Result[None, Exception]:
        """Start a new screen session."""
        try:
            # -dmS: Start screen in detached mode with session name
            cmd = ["screen", "-dmS", str(session_id), "bash"]

            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            # Wait for process to start (screen returns immediately usually)
            # But wait check return code
            await process.wait()

            if process.returncode != 0:
                _, stderr = await process.communicate()
                error_msg = stderr.decode().strip() if stderr else "Unknown error"
                return Err(
                    Exception(
                        f"Screen failed with code {process.returncode}: {error_msg}"
                    )
                )

            # Send gemini command to the session
            # -p 0 target window 0, -X stuff send keystrokes
            cmd_gemini = [
                "screen",
                "-S",
                str(session_id),
                "-p",
                "0",
                "-X",
                "stuff",
                "gemini\n",
            ]

            process_gemini = await asyncio.create_subprocess_exec(
                *cmd_gemini,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            await process_gemini.wait()

            if process_gemini.returncode != 0:
                _, stderr = await process_gemini.communicate()
                error_msg = stderr.decode().strip() if stderr else "Unknown error"
                # Note: We don't fail the session creation if gemini fails to start,
                # but we could log it or return a warning if our Result type supported it.
                # For now, we'll let it pass but maybe we should error?
                # The requirement implies "execute gemini", if it fails, maybe the session is not useful as intended.
                # Let's return error to be safe and rigorous.
                return Err(
                    Exception(
                        f"Failed to start gemini in screen: {process_gemini.returncode}: {error_msg}"
                    )
                )

            return Ok(None)
        except Exception as e:
            return Err(e)
