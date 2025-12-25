// [>]: Shared error handler for API route handlers.
// Wraps async handlers with consistent error transformation.

import { NextRequest, NextResponse } from "next/server";
import { ZodError } from "zod";

import { ApiError, ValidationError } from "@/lib/errors/api-errors";

// [>]: Generic route context type for dynamic routes.
export type RouteContext<T extends string = string> = {
  params: Promise<Record<T, string>>;
};

type RouteHandler = (
  request: NextRequest,
  context?: RouteContext,
) => Promise<NextResponse>;

// [>]: Validates and parses route parameter to number.
// Throws ValidationError if invalid.
export function parseIdParam(value: string, paramName: string = "id"): number {
  const parsed = Number(value);
  if (isNaN(parsed) || parsed <= 0 || !Number.isInteger(parsed)) {
    throw new ValidationError(
      `Invalid ${paramName}: must be a positive integer`,
    );
  }
  return parsed;
}

// [>]: Parse numeric query parameter with default value.
export function getNumericParam(
  searchParams: URLSearchParams,
  key: string,
  defaultValue: number,
): number {
  const value = searchParams.get(key);
  if (!value) return defaultValue;
  const parsed = Number(value);
  return isNaN(parsed) ? defaultValue : parsed;
}

// [>]: Parse optional boolean query parameter.
export function getBooleanParam(
  searchParams: URLSearchParams,
  key: string,
): boolean | undefined {
  const value = searchParams.get(key);
  return value !== null ? value === "true" : undefined;
}

// [>]: Format Zod validation errors into readable messages.
function formatZodError(error: ZodError): string {
  const messages = error.errors.map((e) => {
    const path = e.path.join(".");
    return path ? `${path}: ${e.message}` : e.message;
  });
  return messages.join("; ");
}

// [>]: Wraps route handlers with consistent error handling.
// ZodError -> 422, ApiError -> statusCode, unknown -> 500.
export function handleApiRequest(handler: RouteHandler): RouteHandler {
  return async (request: NextRequest, context?: RouteContext) => {
    try {
      return await handler(request, context);
    } catch (error) {
      // [>]: Zod validation errors -> 422.
      if (error instanceof ZodError) {
        return NextResponse.json(
          { detail: formatZodError(error) },
          { status: 422 },
        );
      }

      // [>]: Known API errors -> their status code.
      if (error instanceof ApiError) {
        return NextResponse.json(error.toResponse(), {
          status: error.statusCode,
        });
      }

      // [>]: Unknown errors -> 500.
      console.error("Unhandled API error:", error);
      return NextResponse.json(
        { detail: "Internal server error" },
        { status: 500 },
      );
    }
  };
}
