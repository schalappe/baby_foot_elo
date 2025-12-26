import { describe, expect, it } from "vitest";
import {
  ApiError,
  NotFoundError,
  ConflictError,
  ValidationError,
  PlayerNotFoundError,
  TeamNotFoundError,
  MatchNotFoundError,
  PlayerAlreadyExistsError,
  TeamAlreadyExistsError,
} from "@/lib/errors/api-errors";

describe("ApiError", () => {
  it("should create error with statusCode and detail", () => {
    const error = new ApiError(500, "Internal server error");

    expect(error.statusCode).toBe(500);
    expect(error.detail).toBe("Internal server error");
    expect(error.message).toBe("Internal server error");
    expect(error.name).toBe("ApiError");
  });

  it("should return correct response format", () => {
    const error = new ApiError(400, "Bad request");

    expect(error.toResponse()).toEqual({ detail: "Bad request" });
  });
});

describe("NotFoundError", () => {
  it("should have status code 404", () => {
    const error = new NotFoundError("Resource not found");

    expect(error.statusCode).toBe(404);
    expect(error.detail).toBe("Resource not found");
  });
});

describe("ConflictError", () => {
  it("should have status code 409", () => {
    const error = new ConflictError("Resource already exists");

    expect(error.statusCode).toBe(409);
    expect(error.detail).toBe("Resource already exists");
  });
});

describe("ValidationError", () => {
  it("should have status code 422", () => {
    const error = new ValidationError("Invalid data");

    expect(error.statusCode).toBe(422);
    expect(error.detail).toBe("Invalid data");
  });
});

describe("Domain-specific errors", () => {
  it("PlayerNotFoundError should format message correctly", () => {
    const error = new PlayerNotFoundError(123);

    expect(error.statusCode).toBe(404);
    expect(error.detail).toBe("Player not found: 123");
    expect(error.name).toBe("PlayerNotFoundError");
  });

  it("TeamNotFoundError should format message correctly", () => {
    const error = new TeamNotFoundError("team-abc");

    expect(error.statusCode).toBe(404);
    expect(error.detail).toBe("Team not found: team-abc");
  });

  it("MatchNotFoundError should format message correctly", () => {
    const error = new MatchNotFoundError(456);

    expect(error.statusCode).toBe(404);
    expect(error.detail).toBe("Match not found: 456");
  });

  it("PlayerAlreadyExistsError should format message correctly", () => {
    const error = new PlayerAlreadyExistsError("John Doe");

    expect(error.statusCode).toBe(409);
    expect(error.detail).toBe(
      "A player with the name 'John Doe' already exists",
    );
  });

  it("TeamAlreadyExistsError should format message correctly", () => {
    const error = new TeamAlreadyExistsError();

    expect(error.statusCode).toBe(409);
    expect(error.detail).toBe("A team with these players already exists");
  });
});
