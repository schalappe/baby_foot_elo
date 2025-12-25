// [>]: Error hierarchy matching Python backend exceptions.

/**
 * Base error class for API errors with status code and detail.
 */
export class ApiError extends Error {
  readonly statusCode: number;
  readonly detail: string;

  constructor(statusCode: number, detail: string) {
    super(detail);
    this.name = this.constructor.name;
    this.statusCode = statusCode;
    this.detail = detail;
  }

  toResponse(): { detail: string } {
    return { detail: this.detail };
  }
}

// [>]: Standard HTTP error types.

export class NotFoundError extends ApiError {
  constructor(detail: string) {
    super(404, detail);
  }
}

export class ConflictError extends ApiError {
  constructor(detail: string) {
    super(409, detail);
  }
}

export class ValidationError extends ApiError {
  constructor(detail: string) {
    super(422, detail);
  }
}

export class OperationError extends ApiError {
  constructor(detail: string) {
    super(500, detail);
  }
}

// [>]: Domain-specific errors for players.

export class PlayerNotFoundError extends NotFoundError {
  constructor(identifier: string | number) {
    super(`Player not found: ${identifier}`);
  }
}

export class PlayerAlreadyExistsError extends ConflictError {
  constructor(name: string) {
    super(`A player with the name '${name}' already exists`);
  }
}

export class InvalidPlayerDataError extends ValidationError {
  constructor(detail: string) {
    super(detail);
  }
}

export class PlayerOperationError extends OperationError {
  constructor(detail: string) {
    super(`Player operation failed: ${detail}`);
  }
}

// [>]: Domain-specific errors for teams.

export class TeamNotFoundError extends NotFoundError {
  constructor(identifier: string | number) {
    super(`Team not found: ${identifier}`);
  }
}

export class TeamAlreadyExistsError extends ConflictError {
  constructor() {
    super("A team with these players already exists");
  }
}

export class InvalidTeamDataError extends ValidationError {
  constructor(detail: string) {
    super(detail);
  }
}

export class TeamOperationError extends OperationError {
  constructor(detail: string) {
    super(`Team operation failed: ${detail}`);
  }
}

// [>]: Domain-specific errors for matches.

export class MatchNotFoundError extends NotFoundError {
  constructor(identifier: string | number) {
    super(`Match not found: ${identifier}`);
  }
}

export class InvalidMatchTeamsError extends ApiError {
  constructor(detail: string) {
    super(400, detail);
  }
}

export class MatchCreationError extends OperationError {
  constructor(detail: string) {
    super(`Match creation failed: ${detail}`);
  }
}

export class MatchDeletionError extends OperationError {
  constructor(detail: string) {
    super(`Match deletion failed: ${detail}`);
  }
}

export class MatchUpdateError extends OperationError {
  constructor(detail: string) {
    super(`Match update failed: ${detail}`);
  }
}
