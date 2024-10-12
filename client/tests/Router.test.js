import { createParams } from "./Router";

describe("Router", () => {
  test.each([
    [
        "/api/game/159/status",
        "express:/api/game/:gamePk/status",
      { gamePk: "159" },
    ],
    ["/api/game/159", "express:/api/game/:gamePk", { gamePk: "159" }],
    [
        "/api/game/159/ticket/ticket-3483.pdf",
        /\/api\/game\/(?<gamePk>\d+)\/ticket\/ticket-(?<ticketPk>\d+)\.pdf/,
      { gamePk: "159", ticketPk: "3483" },
    ],
  ])("parsing %s", (url, urlPattern, expectedParams) => {
    const params = createParams(url, urlPattern);
    expect(params).toEqual(expectedParams);
  });
});
