import { describe, expect, it } from "vitest";

import { drainSseBuffer, parseSsePacket } from "./sse";

describe("parseSsePacket", () => {
  it("parses a well-formed packet", () => {
    const packet = `event: text_delta\ndata: ${JSON.stringify({ delta: "hi" })}`;
    expect(parseSsePacket(packet)).toEqual({ event: "text_delta", data: { delta: "hi" } });
  });

  it("returns null when fields are missing", () => {
    expect(parseSsePacket("event: text_delta")).toBeNull();
    expect(parseSsePacket("data: 123")).toBeNull();
  });

  it("returns null on malformed JSON", () => {
    expect(parseSsePacket("event: x\ndata: {not-json}")).toBeNull();
  });
});

describe("drainSseBuffer", () => {
  it("returns parsed packets and an empty tail when the buffer ends with double newline", () => {
    const buffer = [
      "event: a\ndata: 1",
      "event: b\ndata: 2",
      "",
    ].join("\n\n");
    const { packets, rest } = drainSseBuffer(buffer);
    expect(packets).toHaveLength(2);
    expect(packets[0]).toEqual({ event: "a", data: 1 });
    expect(packets[1]).toEqual({ event: "b", data: 2 });
    expect(rest).toBe("");
  });

  it("keeps the trailing fragment for the next chunk", () => {
    const buffer = "event: a\ndata: 1\n\nevent: b\ndata:";
    const { packets, rest } = drainSseBuffer(buffer);
    expect(packets).toHaveLength(1);
    expect(rest).toBe("event: b\ndata:");
  });

  it("silently drops malformed packets and keeps the rest", () => {
    const buffer = "garbage\n\nevent: ok\ndata: 42\n\n";
    const { packets } = drainSseBuffer(buffer);
    expect(packets).toEqual([{ event: "ok", data: 42 }]);
  });
});
