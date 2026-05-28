import type { ChatStreamPacket } from "./types";

/** Parse a single SSE packet of the form `event: <name>\ndata: <json>`. */
export function parseSsePacket(packet: string): ChatStreamPacket | null {
  const eventMatch = packet.match(/^event: (.+)$/m);
  const dataMatch = packet.match(/^data: (.+)$/m);
  if (!eventMatch || !dataMatch) return null;
  try {
    return { event: eventMatch[1], data: JSON.parse(dataMatch[1]) };
  } catch {
    return null;
  }
}

/**
 * Buffer-aware iterator: given a stream of chunked SSE text, produce parsed
 * packets and return the unfinished tail so the caller can pass it back in.
 */
export function drainSseBuffer(buffer: string): {
  packets: ChatStreamPacket[];
  rest: string;
} {
  const fragments = buffer.split("\n\n");
  const rest = fragments.pop() ?? "";
  const packets: ChatStreamPacket[] = [];
  for (const fragment of fragments) {
    const parsed = parseSsePacket(fragment);
    if (parsed) packets.push(parsed);
  }
  return { packets, rest };
}
