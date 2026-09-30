import asyncio
import sys


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if len(sys.argv) < 2:
        print('usage: genflow serve | research|chat "<query>"')
        return 1
    flow = sys.argv[1]
    if flow == "serve":
        import uvicorn

        host = sys.argv[2] if len(sys.argv) > 2 else "127.0.0.1"
        port = int(sys.argv[3]) if len(sys.argv) > 3 else 8000
        print(f"GenFlow-AI UI: http://{host}:{port}")
        uvicorn.run("genflow.ui.server:app", host=host, port=port)
        return 0
    if len(sys.argv) < 3:
        print('usage: genflow serve | research|chat "<query>"')
        return 1
    query = " ".join(sys.argv[2:])
    from genflow.flows.research_flow import run_chat_flow, run_research_flow

    if flow == "research":
        print(asyncio.run(run_research_flow(query)))
    elif flow == "chat":
        print(asyncio.run(run_chat_flow(query)))
    else:
        print(f"unknown flow: {flow}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
